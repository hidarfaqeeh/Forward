import logging
import json
import os
import sys
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler
import main
import whitelist_handler
import char_limit_handler
import delay_handler
import translation_handler

# Configure logging
logger = logging.getLogger(__name__)

# Conversation states
WAITING_SOURCE = 1
WAITING_TARGET = 2
WAITING_ADMIN = 3
WAITING_DEVELOPER = 4
WAITING_MEDIA_FILTER = 5
WAITING_REPLACEMENT_PATTERN = 6
WAITING_REPLACEMENT_TEXT = 7

# Developer ID storage
DEVELOPER_ID = 485527614

# Statistics tracking
stats = {
    "started_at": None,
    "messages_forwarded": 0,
    "last_forwarded": None,
    "errors": 0
}

def set_developer_id(developer_id):
    """Set the developer ID for admin authorization."""
    global DEVELOPER_ID
    try:
        DEVELOPER_ID = int(developer_id)
        logger.info(f"Developer ID set: {DEVELOPER_ID}")
    except ValueError:
        logger.error(f"Invalid developer ID format: {developer_id}")

def is_admin(user_id):
    """Check if a user is an admin of the bot."""
    # Hard-coded developer ID
    if user_id == 485527614:
        return True

    # Check if user is the configured developer
    if DEVELOPER_ID and user_id == DEVELOPER_ID:
        return True

    # Check admin list
    return user_id in main.ADMIN_LIST

def admin_command(update, context, callback_func):
    """Wrapper for admin-only commands."""
    user_id = update.effective_user.id

    if is_admin(user_id):
        return callback_func(update, context)
    else:
        update.message.reply_text(
            "⛔️ *عذراً!* هذا الأمر متاح فقط للمشرفين ومطور البوت.",
            parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END

def send_notification(update, context, notification_type, message):
    """إرسال إشعار للمشرفين."""
    try:
        # تحميل الإعدادات
        config = main.load_config()
        admin_users = config.get("admin_users", [])

        # تنسيق الإشعار
        notification_icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }

        icon = notification_icons.get(notification_type, "ℹ️")
        notification_text = f"{icon} *إشعار*\n\n{message}"

        # إرسال الإشعار لجميع المشرفين
        for admin_id in admin_users:
            try:
                context.bot.send_message(
                    chat_id=admin_id,
                    text=notification_text,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"خطأ في إرسال الإشعار للمشرف {admin_id}: {str(e)}")

    except Exception as e:
        logger.error(f"خطأ في نظام الإشعارات: {str(e)}")
        return ConversationHandler.END

def start_command(update, context):
    """Send a message when the command /start is issued."""
    user = update.effective_user

    # Import user settings handler
    import user_settings_handler
    import translations

    # Get user's preferred language
    language = user_settings_handler.get_user_language(user.id)

    # Get welcome message in user's language
    welcome_text = "👋 *مرحباً بك في بوت التوجيه!*\n\n" \
                  "أنا بوت متخصص في توجيه المحتوى من قناة إلى أخرى.\n" \
                  "يمكنني إدارة المحتوى وتخصيصه بشكل احترافي."

    # Get channel info from config
    config = main.load_config()
    source_channel = config.get("source_channel", "غير محدد")
    target_channel = config.get("target_channel", "غير محدد")

    # Check if user is admin to customize message
    if is_admin(user.id):
        keyboard = [
            [InlineKeyboardButton("🤖 معلومات البوت", url="https://t.me/your_bot?start=info")],
            [InlineKeyboardButton("📢 قناة المصدر", url=f"https://t.me/{source_channel}")],
            [InlineKeyboardButton("📣 قناة الهدف", url=f"https://t.me/{target_channel}")],
            [InlineKeyboardButton("🛠 لوحة التحكم", callback_data='admin_panel')],
            [InlineKeyboardButton("🌐 تغيير اللغة", callback_data='language_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # For callback queries (when returning from language menu)
        if update.callback_query:
            query = update.callback_query
            query.answer()
            query.edit_message_text(
                text=welcome_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            # For direct /start command
            update.message.reply_text(
                text=welcome_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    else:
        keyboard = [
            [InlineKeyboardButton("🤖 معلومات البوت", url="https://t.me/your_bot?start=info")],
            [InlineKeyboardButton("🌐 تغيير اللغة", callback_data='language_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Non-admin message
        non_admin_message = welcome_text + "\n\n⚠️ هذا البوت متاح فقط للمشرفين."

        # For callback queries (when returning from language menu)
        if update.callback_query:
            query = update.callback_query
            query.answer()
            query.edit_message_text(
                text=non_admin_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            # For direct /start command
            update.message.reply_text(
                text=non_admin_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )

def toggle_forward_mode_command(update, context):
    """Command to toggle between forward and copy modes."""
    # Load config
    config = main.load_config()
    current_mode = config.get("forward_mode", "forward")

    # Toggle the mode
    new_mode = "copy" if current_mode == "forward" else "forward"
    config["forward_mode"] = new_mode
    success = main.save_config(config)

    if success:
        # Show success message
        if new_mode == "forward":
            mode_description = "توجيه الرسائل مع علامة 'موجه من'"
        else:
            mode_description = "نسخ الرسائل بدون علامة 'موجه من'"

        update.message.reply_text(
            f'✅ *تم تغيير طريقة النشر بنجاح!*\n\n'
            f'طريقة النشر الحالية: *{mode_description}*',
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        # Show error message
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء تغيير طريقة النشر. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN
        )

def help_command(update, context):
    """Send a message when the command /help is issued."""
    user_id = update.effective_user.id

    # Import user settings handler
    import user_settings_handler
    import translations

    # Get user's preferred language
    language = user_settings_handler.get_user_language(user_id)

    # Get help message in user's language
    help_text = translations.get_text("help", language)

    # Add language button
    keyboard = [
        [InlineKeyboardButton("🌐 تغيير اللغة / Change Language", callback_data='language_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

def status_command(update, context):
    """Send a message when the command /status is issued."""
    import rate_limit_handler
    import forwarding_control_handler

    if stats["started_at"] is None:
        stats["started_at"] = datetime.now()

    uptime = datetime.now() - stats["started_at"]
    uptime_str = str(uptime).split('.')[0]  # Remove microseconds

    last_forwarded = "لم يتم بعد" if stats["last_forwarded"] is None else stats["last_forwarded"].strftime("%Y-%m-%d %H:%M:%S")

    # Load config to show current channels
    config = main.load_config()
    source_channel = config.get("source_channel", "غير محدد")
    target_channel = config.get("target_channel", "غير محدد")

    # Get current forward mode
    forward_mode = config.get("forward_mode", "forward")
    if forward_mode == "forward":
        forward_mode_text = "توجيه (مع علامة التوجيه)"
    else:
        forward_mode_text = "نسخ (بدون علامة التوجيه)"

    # Get rate limit status
    rate_limit_status = rate_limit_handler.get_rate_limit_status()

    # Get forwarding status
    forwarding_status = forwarding_control_handler.get_forwarding_status()

    update.message.reply_text(
        f'🤖 *حالة البوت*\n\n'
        f'▶️ *يعمل منذ:* {stats["started_at"].strftime("%Y-%m-%d %H:%M:%S")}\n'
        f'⏱ *مدة التشغيل:* {uptime_str}\n'
        f'✉️ *الرسائل الموجهة:* {stats["messages_forwarded"]}\n'
        f'🕒 *آخر توجيه:* {last_forwarded}\n'
        f'📡 *قناة المصدر:* {source_channel}\n'
        f'📡 *قناة الهدف:* {target_channel}\n'
        f'📝 *طريقة النشر:* {forward_mode_text}\n'
        f'⚙️ *حالة التوجيه:* {forwarding_status}\n'
        f'⏱ *حد الرسائل:* {rate_limit_status}\n'
        f'❌ *الأخطاء:* {stats["errors"]}',
        parse_mode=ParseMode.MARKDOWN
    )

def advanced_features_menu(update, context):
    """Display advanced features menu."""
    keyboard = [
        [
            InlineKeyboardButton("🔄 وقت التأخير", callback_data='delay_menu'),
            InlineKeyboardButton("🔢 حد الأحرف", callback_data='char_limit_menu')
        ],
        [
            InlineKeyboardButton("🌐 الترجمة التلقائية", callback_data='translation_menu'),
            InlineKeyboardButton("👁 فلتر اللغة", callback_data='language_filter_menu')
        ],
        [
            InlineKeyboardButton("🔗 تنظيف الروابط", callback_data='link_cleaner_menu'),
            InlineKeyboardButton("🚫 فلتر الروابط", callback_data='link_filter_menu')
        ],
        [
            InlineKeyboardButton("♻️ فلتر التكرار", callback_data='duplicate_filter_menu'),
            InlineKeyboardButton("🔄 فلتر المعاد توجيهه", callback_data='forwarded_filter_menu')
        ],
        [
            InlineKeyboardButton("🔘 فلتر الأزرار الشفافة", callback_data='inline_button_filter_menu'),
            InlineKeyboardButton("💬 حذف الأزرار الشفافة", callback_data='button_removal_menu')
        ],
        [
            InlineKeyboardButton("⏰ ساعات العمل", callback_data='working_hours_menu'),
            InlineKeyboardButton("📅 النشر التلقائي", callback_data='autopost_menu')
        ],
        [
            InlineKeyboardButton("📝 تنسيق النصوص", callback_data='text_format_menu')
        ],
        [
            InlineKeyboardButton("🔙 رجوع", callback_data='admin_panel')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # For callback queries
    if update.callback_query:
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            '🔧 *الميزات المتقدمة*\n\n'
            'هنا يمكنك إدارة الميزات المتقدمة المتاحة في البوت:',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    # For direct command
    else:
        update.message.reply_text(
            '🔧 *الميزات المتقدمة*\n\n'
            'هنا يمكنك إدارة الميزات المتقدمة المتاحة في البوت:',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

def admin_panel(update, context):
    """Display admin control panel."""
    # Import user settings and translations
    import user_settings_handler
    import translations

    # Get the user's language preference
    user_id = update.effective_user.id
    language = user_settings_handler.get_user_language(user_id)

    # Get translated text for menu items
    admin_panel_text = translations.get_text("admin_panel", language)
    channels_admins_text = translations.get_text("button_channels_admins", language)
    forwarding_filters_text = translations.get_text("button_forwarding_filters", language)
    message_customization_text = translations.get_text("button_message_customization", language)
    advanced_filters_text = translations.get_text("button_advanced_filters", language)
    scheduling_text = translations.get_text("button_scheduling", language)
    stats_text = translations.get_text("button_stats", language)
    change_language_text = translations.get_text("button_change_language", language)

    keyboard = [
        [
            InlineKeyboardButton("⚙️ حالة التوجيه", callback_data='forwarding_control_menu'),
            InlineKeyboardButton("📝 طريقة النشر", callback_data='toggle_forward_mode')
        ],
        [
            InlineKeyboardButton("📡 تغيير قناة الهدف", callback_data='set_target'),
            InlineKeyboardButton("📡 تغيير قناة المصدر", callback_data='set_source')
        ],
        [
            InlineKeyboardButton("🎬 فلتر الوسائط", callback_data='media_filters')
        ],
        [
            InlineKeyboardButton("🔄 إعادة تشغيل البوت", callback_data='restart_bot')
        ],
        [
            InlineKeyboardButton("📝 رأس الرسالة", callback_data='header_menu'),
            InlineKeyboardButton("📝 تذييل الرسالة", callback_data='footer_menu')
        ],
        [
            InlineKeyboardButton("🔄 الاستبدال", callback_data='text_replacements'),
            InlineKeyboardButton("💬 زر شفاف", callback_data='button_menu')
        ],
        [
            InlineKeyboardButton("⛔️ القائمة السوداء", callback_data='blacklist_menu'),
            InlineKeyboardButton("✅ القائمة البيضاء", callback_data='whitelist_menu')
        ],
        [
            InlineKeyboardButton("⏱ حد الرسائل", callback_data='rate_limit_menu'),
            InlineKeyboardButton("⏰ وقت التأخير", callback_data='delay_menu')
        ],
        [
            InlineKeyboardButton("🔢 حد الأحرف", callback_data='char_limit_menu'),
            InlineKeyboardButton("♻️ فلتر التكرار", callback_data='duplicate_filter_menu')
        ],
        [
            InlineKeyboardButton("🌐 الترجمة التلقائية", callback_data='translation_menu'),
            InlineKeyboardButton("👁 فلتر اللغة", callback_data='language_filter_menu')
        ],
        [
            InlineKeyboardButton("🔗 تنظيف الروابط", callback_data='link_cleaner_menu'),
            InlineKeyboardButton("🚫 فلتر الروابط", callback_data='link_filter_menu')
        ],
        [
            InlineKeyboardButton("🔄 فلتر المعاد توجيهه", callback_data='forwarded_filter_menu'),
            InlineKeyboardButton("🔘 فلتر الأزرار الشفافة", callback_data='inline_button_filter_menu')
        ],
        [
            InlineKeyboardButton("💬 حذف الأزرار الشفافة", callback_data='button_removal_menu'),
            InlineKeyboardButton("📝 تنسيق النصوص", callback_data='text_format_menu')
        ],
        [
            InlineKeyboardButton("📅 النشر التلقائي", callback_data='autopost_menu'),
            InlineKeyboardButton("⏰ ساعات العمل", callback_data='working_hours_menu')
        ],
        [
            InlineKeyboardButton("🔄 إعادة تشغيل البوت", callback_data='restart_bot')
        ],
        [
            InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data='start_message')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # For direct command
    if update.message:
        update.message.reply_text(
            admin_panel_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    # For callback queries
    else:
        query = update.callback_query
        query.edit_message_text(
            admin_panel_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

def button_handler(update, context):
    """Handle button presses in inline keyboards."""
    # Import all the required handlers
    import command_handlers
    import media_filters_handler
    import replacements_handler
    import blacklist_handler
    import whitelist_handler
    import rate_limit_handler
    import forwarding_control_handler
    import message_customization_handler
    import link_cleaner_handler
    import char_limit_handler
    import delay_handler
    import translation_handler
    import forwarded_filter_handler
    import duplicate_filter_handler
    import inline_button_filter_handler
    import language_filter_handler
    import autopost_handler
    import working_hours_handler
    import text_format_handler
    import button_removal_handler
    import user_settings_handler

    query = update.callback_query
    user_id = query.from_user.id

    # Handle language selection button for all users
    if query.data == 'language_menu':
        user_settings_handler.language_menu(update, context)
        return

    # Handle language selection callbacks
    if query.data.startswith('lang_'):
        user_settings_handler.handle_language_selection(update, context)
        return

    # For other admin-only buttons, check if the user is an admin
    if not is_admin(user_id):
        query.answer("غير مصرح لك باستخدام هذه الميزة.", show_alert=True)
        return

    # Answer the callback query for admin functions
    query.answer()

    # Handle different button callbacks
    if query.data == 'admin_panel':
        admin_panel(update, context)

    elif query.data == 'channels_admins_menu':
        # Import user settings and translations
        import user_settings_handler
        import translations

        # Get the user's language preference
        user_id = update.effective_user.id
        language = user_settings_handler.get_user_language(user_id)

        # Get translated text
        menu_text = translations.get_text("channels_admins_menu", language)
        back_button = translations.get_text("button_back", language)

        keyboard = [
            [
                InlineKeyboardButton("📡 تغيير قناة المصدر", callback_data='set_source'),
                InlineKeyboardButton("📡 تغيير قناة الهدف", callback_data='set_target')
            ],
            [
                InlineKeyboardButton("👤 إضافة مشرف", callback_data='add_admin'),
                InlineKeyboardButton("🔐 تعيين المطور", callback_data='set_developer')
            ],
            [
                InlineKeyboardButton(back_button, callback_data='admin_panel')
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            menu_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    elif query.data == 'forwarding_filters_menu':
        # Import user settings and translations
        import user_settings_handler
        import translations

        # Get the user's language preference
        user_id = update.effective_user.id
        language = user_settings_handler.get_user_language(user_id)

        # Get translated text
        menu_text = translations.get_text("forwarding_filters_menu", language)
        back_button = translations.get_text("button_back", language)

        # Get current forward mode to show in button
        config = main.load_config()
        forward_mode = config.get("forward_mode", "forward")

        # Set button text based on current mode
        if forward_mode == "forward":
            forward_mode_text = "🔄 طريقة النشر: توجيه"
        else:
            forward_mode_text = "📝 طريقة النشر: نسخ"

        keyboard = [
            [
                InlineKeyboardButton(forward_mode_text, callback_data='toggle_forward_mode')
            ],
            [
                InlineKeyboardButton("⚙️ حالة التوجيه", callback_data='forwarding_control_menu')
            ],
            [
                InlineKeyboardButton("🎬 فلتر الوسائط", callback_data='media_filters')
            ],
            [
                InlineKeyboardButton("⛔ القائمة السوداء", callback_data='blacklist_menu')
            ],
            [
                InlineKeyboardButton("✅ القائمة البيضاء", callback_data='whitelist_menu')
            ],
            [
                InlineKeyboardButton("⏱ حد الرسائل", callback_data='rate_limit_menu')
            ],
            [
                InlineKeyboardButton(back_button, callback_data='admin_panel')
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            menu_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    elif query.data == 'message_customization_menu':
        # Import user settings and translations
        import user_settings_handler
        import translations

        # Get the user's language preference
        user_id = update.effective_user.id
        language = user_settings_handler.get_user_language(user_id)

        # Get translated text
        menu_text = translations.get_text("message_customization_menu", language)
        back_button = translations.get_text("button_back", language)

        keyboard = [
            [
                InlineKeyboardButton("✏️ تخصيص الرسائل", callback_data='customization_menu')
            ],
            [
                InlineKeyboardButton("🔄 تحديث الرسائل", callback_data='update_menu')
            ],
            [
                InlineKeyboardButton("📝 إضافة استبدال", callback_data='add_replacement')
            ],
            [
                InlineKeyboardButton("📋 قائمة الاستبدالات", callback_data='text_replacements')
            ],
            [
                InlineKeyboardButton(back_button, callback_data='admin_panel')
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            menu_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    elif query.data == 'advanced_filters_menu':
        # Import user settings and translations
        import user_settings_handler
        import translations

        # Get the user's language preference
        user_id = update.effective_user.id
        language = user_settings_handler.get_user_language(user_id)

        # Get translated text
        menu_text = translations.get_text("advanced_filters_menu", language)
        back_button = translations.get_text("button_back", language)

        keyboard = [
            [
                InlineKeyboardButton("🔄 وقت التأخير", callback_data='delay_menu')
            ],
            [
                InlineKeyboardButton("🔢 حد الأحرف", callback_data='char_limit_menu')
            ],
            [
                InlineKeyboardButton("🌐 الترجمة التلقائية", callback_data='translation_menu')
            ],
            [
                InlineKeyboardButton("👁 فلتر اللغة", callback_data='language_filter_menu')
            ],
            [
                InlineKeyboardButton("🔗 تنظيف الروابط", callback_data='link_cleaner_menu')
            ],
            [
                InlineKeyboardButton("🚫 فلتر الروابط", callback_data='link_filter_menu')
            ],
            [
                InlineKeyboardButton("♻️ فلتر التكرار", callback_data='duplicate_filter_menu')
            ],
            [
                InlineKeyboardButton("🔄 فلتر المعاد توجيهه", callback_data='forwarded_filter_menu')
            ],
            [
                InlineKeyboardButton("🔘 فلتر الأزرار الشفافة", callback_data='inline_button_filter_menu')
            ],
            [
                InlineKeyboardButton("💬 حذف الأزرار الشفافة", callback_data='button_removal_menu')
            ],
            [
                InlineKeyboardButton("📝 تنسيق النصوص", callback_data='text_format_menu')
            ],
            [
                InlineKeyboardButton(back_button, callback_data='admin_panel')
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            menu_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    elif query.data == 'scheduling_menu':
        # Import user settings and translations
        import user_settings_handler
        import translations

        # Get the user's language preference
        user_id = update.effective_user.id
        language = user_settings_handler.get_user_language(user_id)

        # Get translated text
        menu_text = translations.get_text("scheduling_menu", language)
        back_button = translations.get_text("button_back", language)

        keyboard = [
            [
                InlineKeyboardButton("⏰ ساعات العمل", callback_data='working_hours_menu')
            ],
            [
                InlineKeyboardButton("📅 النشر التلقائي", callback_data='autopost_menu')
            ],
            [
                InlineKeyboardButton(back_button, callback_data='admin_panel')
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            menu_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    elif query.data == 'stats_menu':
        # Import user settings and translations
        import user_settings_handler
        import translations
        import show_stats_handler

        # Get the user's language preference
        user_id = update.effective_user.id
        language = user_settings_handler.get_user_language(user_id)

        # Get translated text
        menu_text = translations.get_text("stats_menu", language)
        back_button = translations.get_text("button_back", language)

        # Load current stats
        stats_text = show_stats_handler.generate_stats_text()

        keyboard = [
            [
                InlineKeyboardButton("🔄 تحديث الإحصائيات", callback_data='refresh_stats')
            ],
            [
                InlineKeyboardButton(back_button, callback_data='admin_panel')
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            menu_text + stats_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    elif query.data == 'set_source':
        query.edit_message_text(
            '📡 *تغيير قناة المصدر*\n\n'
            'الرجاء إرسال معرّف قناة المصدر الجديدة.\n'
            'يجب أن يبدأ بـ `-100` متبوعاً بالأرقام، مثل: `-1001234567890`\n\n'
            'استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_SOURCE

    elif query.data == 'set_target':
        query.edit_message_text(
            '📡 *تغيير قناة الهدف*\n\n'
            'الرجاء إرسال معرّف قناة الهدف الجديدة.\n'
            'يجب أن يبدأ بـ `-100` متبوعاً بالأرقام، مثل: `-1001234567890`\n\n'
            'استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_TARGET

    elif query.data == 'add_admin':
        query.edit_message_text(
            '👤 *إضافة مشرف جديد*\n\n'
            'الرجاء إرسال معرّف المستخدم (User ID) للمشرف الجديد.\n'
            'يمكن للمستخدم معرفة معرّفه عن طريق إرسال رسالة إلى بوت مثل @userinfobot\n\n'
            'استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_ADMIN

    elif query.data == 'set_developer':
        query.edit_message_text(
            '🔐 *تعيين معرّف مطور البوت*\n\n'
            'الرجاء إرسال معرّف المستخدم (User ID) الخاص بمطور البوت.\n'
            'يمكن للمستخدم معرفة معرّفه عن طريق إرسال رسالة إلى بوت مثل @userinfobot\n\n'
            'المطور لديه صلاحيات مطلقة على البوت.\n'
            'استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_DEVELOPER

    elif query.data == 'toggle_forward_mode':
        # Load config and toggle forward mode
        config = main.load_config()
        current_mode = config.get("forward_mode", "forward")

        # Toggle the mode
        new_mode = "copy" if current_mode == "forward" else "forward"
        config["forward_mode"] = new_mode
        success = main.save_config(config)

        if success:
            # Set message and button text based on the new mode
            if new_mode == "forward":
                mode_description = "توجيه الرسائل مع علامة 'موجه من'"
                button_text = "🔄 طريقة النشر: توجيه"
            else:
                mode_description = "نسخ الرسائل بدون علامة 'موجه من'"
                button_text = "📝 طريقة النشر: نسخ"

            # Create updated keyboard with new button text
            keyboard = [
                [
                    InlineKeyboardButton("⚙️ حالة التوجيه", callback_data='forwarding_control_menu'),
                    InlineKeyboardButton(button_text, callback_data='toggle_forward_mode')
                ],
                [
                    InlineKeyboardButton("📡 تغيير قناة المصدر", callback_data='set_source'),
                    InlineKeyboardButton("📡 تغيير قناة الهدف", callback_data='set_target')
                ],
                [
                    InlineKeyboardButton("🔙 رجوع", callback_data='start')
                ],
                [
                    InlineKeyboardButton("🎬 فلتر الوسائط", callback_data='media_filters')
                ],
                [
                    InlineKeyboardButton("📝 رأس الرسالة", callback_data='header_menu'),
                    InlineKeyboardButton("📝 تذييل الرسالة", callback_data='footer_menu')
                ],
                [
                    InlineKeyboardButton("🔄 الاستبدال", callback_data='text_replacements'),
                    InlineKeyboardButton("💬 زر شفاف", callback_data='button_menu')
                ],
                [
                    InlineKeyboardButton("⛔️ القائمة السوداء", callback_data='blacklist_menu'),
                    InlineKeyboardButton("✅ القائمة البيضاء", callback_data='whitelist_menu')
                ],
                [
                    InlineKeyboardButton("⏱ حد الرسائل", callback_data='rate_limit_menu'),
                    InlineKeyboardButton("⏰ وقت التأخير", callback_data='delay_menu')
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            query.edit_message_text(
                f'✅ *تم تغيير طريقة النشر بنجاح!*\n\n'
                f'طريقة النشر الحالية: *{mode_description}*\n\n'
                f'يمكنك العودة إلى لوحة التحكم أو الاستمرار في تعديل الإعدادات.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            # Show error message
            query.edit_message_text(
                '❌ *خطأ!*\n\n'
                'حدث خطأ أثناء تغيير طريقة النشر. الرجاء المحاولة مرة أخرى.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة للوحةالتحكم", callback_data='admin_panel')
                ]])
            )

    elif query.data == 'media_filters':
        # Load current media filters
        config = main.load_config()

        # Initialize media filters if not exists
        if 'media_filters' not in config:
            config['media_filters'] = {
                "text": True,
                "photo": True,
                "video": True,
                "document": True,
                "audio": True,
                "voice": True,
                "video_note": True,
                "animation": True,
                "sticker": True,
                "poll": True,
                "game": True,
                "contact": True,
                "location": True,
                "venue": True
            }
            main.save_config(config)

        # Create the media filters menu
        media_filters = config.get('media_filters', {})

        # Create a keyboard with toggle buttons for each media type
        keyboard = []

        # Mapping of media types to display names in Arabic
        media_type_names = {
            "text": "📝 نص",
            "photo": "🖼 صورة",
            "video": "🎥 فيديو",
            "document": "📄 ملف",
            "audio": "🎵 صوت",
            "voice": "🎤 رسالة صوتية",
            "video_note": "⭕ رسالة فيديو مستديرة",
            "animation": "🎞 صور متحركة",
            "sticker": "😃 ملصق",
            "poll": "📊 استبيان",
            "game": "🎮 لعبة","contact": "📱 جهة اتصال",
            "location": "📍 موقع",
            "venue": "🏢 مكان"
        }

        # Create rows with two buttons each for all media types
        media_types = list(media_type_names.keys())
        for i in range(0, len(media_types), 2):
            row = []
            for media_type in media_types[i:i+2]:
                if i + 1 < len(media_types) or media_type == media_types[-1]:
                    status = "✅" if media_filters.get(media_type, True) else "❌"
                    row.append(InlineKeyboardButton(
                        f"{status} {media_type_names[media_type]}",
                        callback_data=f'toggle_media_{media_type}'
                    ))
            keyboard.append(row)

        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')])

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            '🎬 *إعدادات فلتر الوسائط*\n\n'
            'اضغط على أي نوع وسائط لتفعيل أو تعطيل توجيهه.\n'
            '✅ = مسموح بالتوجيه\n'
            '❌ = ممنوع التوجيه\n\n'
            'يمكنك اختيار ما تريد توجيهه من القناة المصدر إلى قناة الهدف.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    # Text replacements main menu
    elif query.data == 'text_replacements':
        # Create a keyboard with options for replacement submenu
        keyboard = [
            [InlineKeyboardButton("➕ إضافة استبدال جديد", callback_data='add_replacement')],
            [InlineKeyboardButton("📋 عرض قائمة الاستبدالات", callback_data='view_replacements')],
            [InlineKeyboardButton("🗑 حذف كل الاستبدالات", callback_data='delete_all_replacements')],
            [InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            '📝 *قائمة الاستبدال*\n\n'
            'يمكنك إدارة الاستبدالات من هنا.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    # View list of all current replacements
    elif query.data == 'view_replacements':
        # Load current text replacements
        config = main.load_config()

        # Initialize text replacements if not exists
        if 'text_replacements' not in config:
            config['text_replacements'] = []
            main.save_config(config)

        # Create the text replacements menu
        text_replacements = config.get('text_replacements', [])

        # Create a list of current replacements
        replacements_text = ""
        for i, replacement in enumerate(text_replacements):
            pattern = replacement.get('pattern', '')
            replacement_text = replacement.get('replacement', '')
            if not replacement_text:
                replacement_text = replacement.get('replace_with', '')
            replacements_text += f"{i+1}. '{pattern}' ⟹ '{replacement_text}'\n"

        if not replacements_text:
            replacements_text = "لا يوجد استبدالات حالياً."

        # Create a keyboard with options
        keyboard = [
            [InlineKeyboardButton("➕ إضافة استبدال جديد", callback_data='add_replacement')],
            [InlineKeyboardButton("🗑 حذف كل الاستبدالات", callback_data='delete_all_replacements')],
            [InlineKeyboardButton("🔙 العودة لقائمة الاستبدال", callback_data='text_replacements')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            '📋 *قائمة الاستبدالات الحالية*\n\n'
            f"{replacements_text}\n\n"
            'يمكنك إضافة استبدالات جديدة أو حذف الموجودة.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    # Add a new text replacement
    elif query.data == 'add_replacement':
        query.edit_message_text(
            '📝 *إضافة استبدال نصّي جديد*\n\n'
            'الرجاء إرسال النص الذي تريد استبداله.\n'
            'مثال: الولايات المتحدة\n\n'
            'استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_REPLACEMENT_PATTERN

    # Delete all text replacements
    elif query.data == 'delete_all_replacements':
        # Load config
        config = main.load_config()

        # Clear all replacements
        config['text_replacements'] = []

        # Save config
        success = main.save_config(config)

        if success:
            # Show success message
            query.edit_message_text(
                '✅ *تم حذف جميع الاستبدالات بنجاح!*\n\n'
                'تم حذف جميع قواعد استبدال النص من النظام.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة لإعدادات الاستبدال", callback_data='text_replacements')
                ]])
            )
        else:
            # Show error message
            query.edit_message_text(
                '❌ *خطأ!*\n\n'
                'حدث خطأ أثناء حذف الاستبدالات. الرجاء المحاولة مرة أخرى.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة لإعدادات الاستبدال", callback_data='text_replacements')
                ]])
            )

    # Handle all media filter toggle buttons
    elif query.data.startswith('toggle_media_'):
        media_type = query.data.replace('toggle_media_', '')

        # Load config
        config = main.load_config()
        if 'media_filters' not in config:
            config['media_filters'] = {}

        # Toggle the media filter
        current_value = config['media_filters'].get(media_type, True)
        config['media_filters'][media_type] = not current_value

        # Save config
        success = main.save_config(config)

        if success:
            # Refresh the media filters menu
            # Create the media filters menu
            media_filters = config.get('media_filters', {})

            # Create a keyboard with toggle buttons for each media type
            keyboard = []

            # Mapping of media types to display names in Arabic
            media_type_names = {
                "text": "📝 نص",
                "photo": "🖼 صورة",
                "video": "🎥 فيديو",
                "document": "📄 ملف",
                "audio": "🎵 صوت",
                "voice": "🎤 رسالة صوتية",
                "video_note": "⭕ رسالة فيديو مستديرة",
                "animation": "🎞 صور متحركة",
                "sticker": "😃 ملصق",
                "poll": "📊 استبيان",
                "game": "🎮 لعبة",
                "contact": "📱 جهة اتصال",
                "location": "📍 موقع",
                "venue": "🏢 مكان"
            }

            # Create rows with two buttons each for all media types
            media_types = list(media_type_names.keys())
            for i in range(0, len(media_types), 2):
                row = []
                for media_type in media_types[i:i+2]:
                    if i + 1 < len(media_types) or media_type == media_types[-1]:
                        status = "✅" if media_filters.get(media_type, True) else "❌"
                        row.append(InlineKeyboardButton(
                            f"{status} {media_type_names[media_type]}",
                            callback_data=f'toggle_media_{media_type}'
                        ))
                keyboard.append(row)

            # Add back button
            keyboard.append([InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')])

            reply_markup = InlineKeyboardMarkup(keyboard)

            query.edit_message_text(
                '🎬 *إعدادات فلتر الوسائط*\n\n'
                'اضغط على أي نوع وسائط لتفعيل أو تعطيل توجيهه.\n'
                '✅ = مسموح بالتوجيه\n'
                '❌ = ممنوع التوجيه\n\n'
                'تم تحديث الإعدادات بنجاح!',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            # Show error message
            query.edit_message_text(
                '❌ *خطأ!*\n\n'
                'حدث خطأ أثناء تحديث إعدادات فلتر الوسائط. الرجاء المحاولة مرة أخرى.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')
                ]])
            )

    elif query.data == 'view_replacements_list':
        # Load current text replacements
        config = main.load_config()

        # Initialize text replacements if not exists
        if 'text_replacements' not in config:
            config['text_replacements'] = []
            main.save_config(config)

        # Create the text replacements menu
        replacements = config.get('text_replacements', [])

        # Create a keyboard with all current replacements and options to manage them
        keyboard = []

        # Add button to add new replacement
        keyboard.append([InlineKeyboardButton("➕ إضافة استبدال جديد", callback_data='add_replacement')])

        # List current replacements (if any)
        if replacements:
            for i, replacement in enumerate(replacements):
                # Display pattern and replacement text (truncated if too long)
                pattern = replacement.get('pattern', '')
                replace_with = replacement.get('replace_with', '')
                if not replace_with:
                    replace_with = replacement.get('replacement', '')

                # Truncate if too long for display
                if len(pattern) > 15:
                    pattern = pattern[:15] + '...'
                if len(replace_with) > 15:
                    replace_with = replace_with[:15] + '...'

                keyboard.append([
                    InlineKeyboardButton(
                        f"❌ {pattern} ➡️ {replace_with}",
                        callback_data=f'delete_replacement_{i}'
                    )
                ])
        else:
            # No replacements yet
            keyboard.append([InlineKeyboardButton("لا توجد استبدالات حالياً", callback_data='no_action')])

        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 العودة لقائمة الاستبدال", callback_data='text_replacements')])

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            '📋 *قائمة الاستبدالات الحالية*\n\n'
            'يمكنك إضافة استبدالات للنصوص ليتم تطبيقها على الرسائل المرسلة.\n'
            'كل استبدال يتكون من نص للبحث عنه ونص للاستبدال به.\n\n'
            'اضغط على "➕ إضافة استبدال جديد" لإضافة استبدال جديد.\n'
            'اضغط على أي استبدال موجود لحذفه.\n\n'
            'ملاحظة: الاستبدالات تعمل فقط على النصوص والتعليقات في الصور والفيديوهات وغيرها.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    elif query.data == 'add_replacement':
        # Set the conversation state and ask for the pattern
        query.edit_message_text(
            '📝 *إضافة استبدال جديد - الخطوة 1/2*\n\n'
            'الرجاء إرسال النص الذي تريد البحث عنه (النمط).\n\n'
            'على سبيل المثال، إذا كنت تريد استبدال كلمة "مرحباً" بكلمة "أهلاً"،\n'
            'أرسل "مرحباً" في هذه الخطوة.\n\n'
            'استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='text_replacements')
            ]])
        )
        return WAITING_REPLACEMENT_PATTERN

    elif query.data.startswith('delete_replacement_'):
        try:
            # Extract index
            index = int(query.data.replace('delete_replacement_', ''))

            # Load config
            config = main.load_config()
            replacements = config.get('text_replacements', [])

            # Check if index is valid
            if 0 <= index < len(replacements):
                # Store the deleted replacement details for confirmation message
                deleted_pattern = replacements[index].get('pattern', '')
                deleted_replacement = replacements[index].get('replace_with', '')
                if not deleted_replacement:
                    deleted_replacement = replacements[index].get('replacement', '')

                # Remove the replacement
                del replacements[index]
                config['text_replacements'] = replacements
                success = main.save_config(config)

                if success:
                    # Return to the text replacements menu with success message
                    # Create updated keyboard
                    keyboard = []

                    # Add button to add new replacement
                    keyboard.append([InlineKeyboardButton("➕ إضافة استبدال جديد", callback_data='add_replacement')])

                    # List current replacements (if any)
                    if replacements:
                        for i, replacement in enumerate(replacements):
                            # Display pattern and replacement text (truncated if too long)
                            pattern = replacement.get('pattern', '')
                            replace_with = replacement.get('replace_with', '')
                            if not replace_with:
                                replace_with = replacement.get('replacement', '')

                            # Truncate if too long for display
                            if len(pattern) > 15:
                                pattern = pattern[:15] + '...'
                            if len(replace_with) > 15:
                                replace_with = replace_with[:15] + '...'

                            keyboard.append([
                                InlineKeyboardButton(
                                    f"❌ {pattern} ➡️ {replace_with}",
                                    callback_data=f'delete_replacement_{i}'
                                )
                            ])
                    else:
                        # No replacements left
                        keyboard.append([InlineKeyboardButton("لا توجد استبدالات حالياً", callback_data='no_action')])

                    # Add back button
                    keyboard.append([InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')])

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    query.edit_message_text(
                        f'✅ *تم حذف الاستبدال بنجاح!*\n\n'
                        f'تم حذف الاستبدال:\n'
                        f'من: `{deleted_pattern}`\n'
                        f'إلى: `{deleted_replacement}`\n\n'
                        f'📝 *إعدادات الاستبدال*\n\n'
                        f'يمكنك إضافة استبدالات للنصوص ليتم تطبيقها على الرسائل المرسلة.\n'
                        f'كل استبدال يتكون من نص للبحث عنه ونص للاستبدال به.',
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=reply_markup
                    )
                else:
                    # Show error message
                    query.edit_message_text(
                        '❌ *خطأ!*\n\n'
                        'حدث خطأ أثناء حذف الاستبدال. الرجاء المحاولة مرة أخرى.',
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 العودة", callback_data='text_replacements')
                        ]])
                    )
            else:
                # Invalid index
                query.edit_message_text(
                    '❌ *خطأ!*\n\n'
                    'الاستبدال المحدد غير موجود. ربما تم حذفه بالفعل.',
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 العودة", callback_data='text_replacements')
                    ]])
                )
        except Exception as e:
            # Show error message
            query.edit_message_text(
                f'❌ *خطأ!*\n\n'
                f'حدث خطأ أثناء حذف الاستبدال: {str(e)}',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data='text_replacements')
                ]])
            )

    elif query.data == 'no_action':
        # Do nothing, this is a placeholder for informational buttons
        pass

    elif query.data == 'advanced_features_menu':
        # Show advanced features menu
        advanced_features_menu(update, context)

    # Autopost menu handlers
    elif query.data == 'autopost_menu':
        autopost_handler.autopost_menu(update, context)
    elif query.data == 'toggle_autopost':
        autopost_handler.toggle_autopost_status(update, context)
    elif query.data == 'add_scheduled_post':
        return autopost_handler.add_scheduled_post(update, context)
    elif query.data == 'view_scheduled_posts':
        autopost_handler.view_scheduled_posts(update, context)
    elif query.data == 'delete_post_menu':
        autopost_handler.delete_post_menu(update, context)
    elif query.data == 'delete_all_scheduled_posts':
        autopost_handler.delete_all_scheduled_posts(update, context)
    elif query.data == 'confirm_delete_all_posts':
        autopost_handler.confirm_delete_all_posts(update, context)
    elif query.data.startswith('delete_post_'):
        autopost_handler.delete_post(update, context)

    # Working hours menu handlers
    elif query.data == 'working_hours_menu':
        working_hours_handler.working_hours_menu(update, context)
    elif query.data == 'toggle_working_hours':
        working_hours_handler.toggle_working_hours_status(update, context)
    elif query.data == 'set_start_hour':
        working_hours_handler.set_start_hour(update, context)
    elif query.data == 'set_end_hour':
        working_hours_handler.set_end_hour(update, context)
    elif query.data.startswith('start_hour_'):
        working_hours_handler.set_start_hour_callback(update, context)
    elif query.data.startswith('end_hour_'):
        working_hours_handler.set_end_hour_callback(update, context)

    # Text format menu handlers
    elif query.data == 'text_format_menu':
        text_format_handler.text_format_menu(update, context)
    elif query.data == 'toggle_plain_text':
        text_format_handler.toggle_plain_text_status(update, context)
    elif query.data == 'toggle_bold_text':
        text_format_handler.toggle_bold_text_status(update, context)

    # UserBot client handlers
    # تمت إزالة معالجات UserBot من هنا

    # Button removal menu handlers
    elif query.data == 'button_removal_menu':
        button_removal_handler.button_removal_menu(update, context)
    elif query.data == 'toggle_button_removal':
        button_removal_handler.toggle_button_removal_status(update, context)

    elif query.data == 'delay_menu':
        # Show delay settings menu
        delay_handler.delay_menu(update, context)

    elif query.data == 'char_limit_menu':
        # Show character limit menu
        char_limit_handler.char_limit_menu(update, context)

    elif query.data == 'translation_menu':
        # Show translation settings menu
        translation_handler.translation_menu(update, context)

    elif query.data == 'link_cleaner_menu':
        # Show link cleaner menu
        link_cleaner_handler.link_cleaner_menu(update, context)

    elif query.data == 'link_filter_menu':
        # Show link filter menu
        link_cleaner_handler.link_filter_menu(update, context)

    elif query.data == 'toggle_link_filter':
        # Toggle link filter status
        link_cleaner_handler.toggle_link_filter_status(update, context)

    elif query.data == 'forwarded_filter_menu':
        # Show forwarded filter menu
        forwarded_filter_handler.forwarded_filter_menu(update, context)

    elif query.data == 'toggle_forwarded_filter':
        # Toggle forwarded filter status
        forwarded_filter_handler.toggle_forwarded_filter_status(update, context)

    elif query.data == 'duplicate_filter_menu':
        # Show duplicate filter menu
        duplicate_filter_handler.duplicate_filter_menu(update, context)

    elif query.data == 'toggle_duplicate_filter':
        # Toggle duplicate filter status
        duplicate_filter_handler.toggle_duplicate_filter_status(update, context)

    elif query.data == 'clear_message_memory':
        # Clear stored message hashes
        duplicate_filter_handler.clear_message_memory(update, context)

    elif query.data == 'language_filter_menu':
        # Show language filter menu
        language_filter_handler.language_filter_menu(update, context)

    elif query.data == 'toggle_language_filter':
        # Toggle language filter status
        language_filter_handler.toggle_language_filter_status(update, context)

    elif query.data == 'toggle_language_filter_mode':
        # Toggle language filter mode
        language_filter_handler.toggle_language_filter_mode(update, context)

    elif query.data == 'set_language_filter_language':
        # Show language selection interface
        language_filter_handler.set_language_filter_language(update, context)

    elif query.data.startswith('set_language_'):
        # Handle specific language selection
        language_code = query.data.replace('set_language_', '')
        language_filter_handler.set_language(update, context, language_code)

    elif query.data == 'inline_button_filter_menu':
        # Show inline button filter menu
        inline_button_filter_handler.inline_button_filter_menu(update, context)

    elif query.data == 'toggle_inline_button_filter':
        # Toggle inline button filter status
        inline_button_filter_handler.toggle_inline_button_filter_status(update, context)

    elif query.data == 'show_stats' or query.data == 'refresh_stats':
        # Import the stats handler
        import show_stats_handler
        show_stats_handler.show_stats(update, context)

    elif query.data == 'setup_command':
        setup_command(update, context)

    elif query.data == 'set_source':
        set_source_command(update, context)

    elif query.data == 'set_target':
        set_target_command(update, context)

    elif query.data == 'add_admin':
        add_admin_command(update, context)

    elif query.data == 'set_developer':
        # المطور هو المستخدم ذو الصلاحيات الكاملة
        query.edit_message_text(
            '🔐 *تعيين معرّف مطور البوت*\n\n'
            'الرجاء إرسال معرّف المستخدم (User ID) الخاص بمطور البوت.\n'
            'المطور لديه صلاحيات كاملة على البوت.\n\n'
            'استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_DEVELOPER

    elif query.data == 'header_menu':
        message_customization_handler.header_menu(update,context)

    elif query.data == 'footer_menu':
        message_customization_handler.footer_menu(update, context)
    elif query.data == 'button_menu':
        message_customization_handler.button_menu(update, context)

    # تمت إزالة ميزة نسخ البوت

    elif query.data == 'restart_bot':
        restart_bot(update, context)
        
    elif query.data == 'about_bot':
        query.edit_message_text(
            "ℹ️ *حول البوت*\n\n"
            "هذا بوت متخصص لتوجيه الرسائل من قناة إلى أخرى مع إمكانية تصفية المحتوى وتخصيصه.\n\n"
            "*المميزات الرئيسية:*\n"
            "• توجيه الرسائل تلقائياً بين القنوات\n"
            "• تصفية الرسائل حسب المحتوى واللغة\n"
            "• إضافة رأس وتذييل مخصص للرسائل\n"
            "• تعديل النصوص واستبدال الكلمات تلقائياً\n"
            "• جدولة منشورات تلقائية\n"
            "• تحديد ساعات عمل للبوت\n\n"
            "*طوّر بواسطة:* @odaygholy\n"
            "*قناة البوت:* @ZawamlAnsarallah",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='start_message')]])
        )
        
    elif query.data == 'help_menu':
        query.edit_message_text(
            "❓ *المساعدة*\n\n"
            "*الأوامر المتاحة:*\n"
            "/start - بدء البوت\n"
            "/help - عرض هذه المساعدة\n"
            "/admin - عرض لوحة التحكم (للمشرفين فقط)\n"
            "/status - عرض حالة البوت (للمشرفين فقط)\n"
            "/setup - بدء معالج الإعداد (للمشرفين فقط)\n\n"
            "*المتطلبات:*\n"
            "• يجب أن يكون البوت مشرفاً في القناتين المصدر والهدف\n"
            "• في قناة المصدر يحتاج صلاحية قراءة الرسائل\n"
            "• في قناة الهدف يحتاج صلاحية إرسال الرسائل\n\n"
            "للمزيد من المساعدة، تواصل مع مطور البوت @odaygholy",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data='start_message')]])
        )
        
    elif query.data == 'start_message':
        # إعادة توجيه إلى رسالة البداية
        command_handlers.start_command(update, context)


def setup_command(update, context):
    """Setup wizard for the bot."""
    keyboard = [
        [
            InlineKeyboardButton("📡 تعيين قناة المصدر", callback_data='set_source'),
            InlineKeyboardButton("📡 تعيين قناة الهدف", callback_data='set_target')
        ],
        [
            InlineKeyboardButton("👤 إضافة مشرف", callback_data='add_admin')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        '🛠 *معالج الإعداد*\n\n'
        'مرحباً بك في معالج إعداد البوت. الرجاء اختيار ما تريد إعداده:',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

def set_source_command(update, context):
    """Command to set the source channel."""
    update.message.reply_text(
        '📡 *تغيير قناة المصدر*\n\n'
        'الرجاء إرسال معرّف قناة المصدر الجديدة.\n'
        'يجب أن يبدأ بـ `-100` متبوعاً بالأرقام، مثل: `-1001234567890`\n\n'
        'استخدم /cancel للإلغاء.',
        parse_mode=ParseMode.MARKDOWN
    )
    return WAITING_SOURCE

def set_target_command(update, context):
    """Command to set the target channel."""
    update.message.reply_text(
        '📡 *تغيير قناة الهدف*\n\n'
        'الرجاء إرسال معرّف قناة الهدف الجديدة.\n'
        'يجب أن يبدأ بـ `-100` متبوعاً بالأرقام، مثل: `-1001234567890`\n\n'
        'استخدم /cancel للإلغاء.',
        parse_mode=ParseMode.MARKDOWN
    )
    return WAITING_TARGET

def add_admin_command(update, context):
    """Command to add a new admin."""
    update.message.reply_text(
        '👤 *إضافة مشرف جديد*\n\n'
        'الرجاء إرسال معرّف المستخدم (User ID) للمشرف الجديد.\n'
        'يمكن للمستخدم معرفة معرّفه عن طريق إرسال رسالة إلى بوت مثل @userinfobot\n\n'
        'استخدم /cancel للإلغاء.',
        parse_mode=ParseMode.MARKDOWN
    )
    return WAITING_ADMIN

def receive_source(update, context):
    """Process received source channel ID."""
    source_id = update.message.text.strip()

    # Validate source ID format (simple validation)
    if not source_id.startswith('-100') or not source_id[4:].isdigit():
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'تنسيق معرّف القناة غير صحيح. يجب أن يبدأ بـ `-100` متبوعاً بالأرقام.\n'
            'مثال: `-1001234567890`\n\n'
            'الرجاء المحاولة مرة أخرى أو استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_SOURCE

    # Load config, update and save
    config = main.load_config()
    old_source = config.get("source_channel", "غير محدد")
    config["source_channel"] = source_id
    success = main.save_config(config)

    if success:
        # إرسال رسالة النجاح للمستخدم
        update.message.reply_text(
            f'✅ *تم بنجاح!*\n\n'
            f'تم تغيير قناة المصدر من:\n'
            f'`{old_source}`\n'
            f'إلى:\n'
            f'`{source_id}`\n\n'
            f'⚠️ لتفعيل التغييرات، قد تحتاج إلى إعادة تشغيل البوت.',
            parse_mode=ParseMode.MARKDOWN
        )

        # إرسال إشعار للمشرفين
        notification_message = f"تم تغيير قناة المصدر\nمن: {old_source}\nإلى: {source_id}\nبواسطة المستخدم: {update.effective_user.id}"
        send_notification(update, context, "success", notification_message)
    else:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN
        )

    return ConversationHandler.END

def receive_target(update, context):
    """Process received target channel ID."""
    target_id = update.message.text.strip()

    # Validate target ID format (simple validation)
    if not target_id.startswith('-100') or not target_id[4:].isdigit():
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'تنسيق معرّف القناة غير صحيح. يجب أن يبدأ بـ `-100` متبوعاً بالأرقام.\n'
            'مثال: `-1001234567890`\n\n'
            'الرجاء المحاولة مرة أخرى أو استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_TARGET

    # Load config, update and save
    config = main.load_config()
    old_target = config.get("target_channel", "غير محدد")
    config["target_channel"] = target_id
    success = main.save_config(config)

    if success:
        update.message.reply_text(
            f'✅ *تم بنجاح!*\n\n'
            f'تم تغيير قناة الهدف من:\n'
            f'`{old_target}`\n'
            f'إلى:\n'
            f'`{target_id}`\n\n'
            f'⚠️ لتفعيل التغييرات، قد تحتاج إلى إعادة تشغيل البوت.',
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN
        )

    return ConversationHandler.END

def receive_admin(update, context):
    """Process received admin user ID."""
    try:
        admin_id = int(update.message.text.strip())
    except ValueError:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'معرّف المستخدم يجب أن يكون رقماً صحيحاً.\n'
            'الرجاء المحاولة مرة أخرى أو استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_ADMIN

    # Load config, update and save
    config = main.load_config()
    admin_users = config.get("admin_users", [])

    # Check if admin already exists
    if admin_id in admin_users:
        update.message.reply_text(
            f'⚠️ *تنبيه!*\n\n'
            f'المستخدم `{admin_id}` مشرف بالفعل.',
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END

    # Add new admin
    admin_users.append(admin_id)
    config["admin_users"] = admin_users
    success = main.save_config(config)

    # Update the global admin list
    main.ADMIN_LIST = admin_users

    if success:
        update.message.reply_text(
            f'✅ *تم بنجاح!*\n\n'
            f'تمت إضافة المستخدم `{admin_id}` كمشرف للبوت.',
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN
        )

    return ConversationHandler.END

def add_replacement_button(update, context):
    """Handle add replacement button press specifically for conversation handlers."""
    query = update.callback_query
    query.answer()

    # Set the conversation state and ask for the pattern
    query.edit_message_text(
        '📝 *إضافة استبدالات جديدة*\n\n'
        'أرسل الاستبدالات بالصيغة التالية (كل سطر يمثل استبدالاً):\n'
        '`نص1 : نص1 بديل`\n'
        '`نص2 : نص2 بديل`\n'
        '`نص3 : نص3 بديل`\n\n'
        'يمكنك إضافة استبدال واحد فقط أو عدة استبدالات دفعة واحدة.\n\n'
        'استخدم /cancel للإلغاء.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 العودة", callback_data='text_replacements')
        ]])
    )
    return WAITING_REPLACEMENT_PATTERN

def receive_replacement_pattern(update, context):
    """Process received replacement pattern."""
    input_text = update.message.text.strip()

    if input_text == '/cancel':
        return cancel_command(update, context)

    # Always use the "text : replacement" format
    replacements_added = 0
    error_lines = []

    # Load config for adding replacements
    config = main.load_config()
    if 'text_replacements' not in config:
        config['text_replacements'] = []

    # Check if multiple lines or single line
    lines = input_text.split('\n')

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:  # Skip empty lines
            continue

        # If line doesn't have delimiter, assume it's a single replacement
        # and prompt for second part
        if ' : ' not in line and len(lines) == 1:
            # Store the pattern in user data
            context.user_data['replacement_pattern'] = input_text

            # Ask for the replacement text
            update.message.reply_text(
                '📝 *إضافة استبدال جديد - الخطوة 2/2*\n\n'
                'أرسل النص الذي تريد استبداله به بصيغة:\n'
                f'`{input_text} : النص البديل`\n\n'
                'استخدم /cancel للإلغاء.',
                parse_mode=ParseMode.MARKDOWN
            )
            return WAITING_REPLACEMENT_TEXT

        # Otherwise, try to parse as "text : replacement"
        if ' : ' in line:
            parts = line.split(' : ', 1)
            if len(parts) == 2:
                pattern = parts[0].strip()
                replacement = parts[1].strip()

                if pattern and replacement:
                    # Add this replacement
                    config['text_replacements'].append({
                        'pattern': pattern,
                        'replacement': replacement
                    })
                    replacements_added += 1
                else:
                    error_lines.append(i + 1)
            else:
                error_lines.append(i + 1)
        else:
            error_lines.append(i + 1)

    # If we processed something, save the config
    if replacements_added > 0:
        # Save the updated config
        success = main.save_config(config)

        if success:
            # Create success message
            if len(error_lines) > 0:
                error_msg = f"\n⚠️ لم يتم إضافة الاستبدالات في السطور التالية بسبب خطأ في الصيغة: {', '.join(map(str, error_lines))}"
            else:
                error_msg = ""

            # Format success message with keyboard
            replacements = config.get('text_replacements', [])
            keyboard = []

            # Add button to add new replacement
            keyboard.append([InlineKeyboardButton("➕ إضافة استبدال جديد", callback_data='add_replacement')])

            # List current replacements
            for i, replacement in enumerate(replacements):
                # Display pattern and replacement text (truncated if too long)
                pattern_text = replacement.get('pattern', '')
                replace_with_text = replacement.get('replace_with', '')
                if not replace_with_text:
                    replace_with_text = replacement.get('replacement', '')

                # Truncate if too long for display
                if len(pattern_text) > 15:
                    pattern_text = pattern_text[:15] + '...'
                if len(replace_with_text) > 15:
                    replace_with_text = replace_with_text[:15] + '...'

                keyboard.append([
                    InlineKeyboardButton(
                        f"❌ {pattern_text} ➡️ {replace_with_text}",
                        callback_data=f'delete_replacement_{i}'
                    )
                ])

            # Add back button
            keyboard.append([InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')])

            reply_markup = InlineKeyboardMarkup(keyboard)

            update.message.reply_text(
                f'✅ *تم إضافة الاستبدالات بنجاح!*\n\n'
                f'تم إضافة {replacements_added} استبدال(ات).{error_msg}\n\n'
                f'سيتم تطبيق هذه الاستبدالات على جميع الرسائل الجديدة.',
                parse_mode=ParseMode.MARKDOWN
            )

            # Send a new message with the replacements menu
            update.message.reply_text(
                '📝 *قائمة الاستبدالات*\n\n'
                'يمكنك إدارة قائمة الاستبدالات من هنا:',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )

            return ConversationHandler.END

    # If we got here and there was an error or nothing added, show it
    if len(lines) > 1 or ' : ' in input_text:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'لم يتم إضافة أي استبدالات. تأكد من استخدام الصيغة الصحيحة:\n'
            '`نص : نص بديل`\n'
            'لكل سطر من الاستبدالات.',
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END

def receive_replacement_text(update, context):
    """Process received replacement text."""
    replace_with = update.message.text.strip()

    if replace_with == '/cancel':
        return cancel_command(update, context)

    # Get the pattern from user data
    pattern = context.user_data.get('replacement_pattern', '')

    if not pattern:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الاستبدال. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END

    # Load config, add new replacement, and save
    config = main.load_config()
    if 'text_replacements' not in config:
        config['text_replacements'] = []

    # Add the new replacement
    config['text_replacements'].append({
        'pattern': pattern,
        'replacement': replace_with
    })

    success = main.save_config(config)

    if success:
        # Format success message
        # Create a keyboard with all current replacements
        replacements = config.get('text_replacements', [])
        keyboard = []

        # Add button to add new replacement
        keyboard.append([InlineKeyboardButton("➕ إضافة استبدال جديد", callback_data='add_replacement')])

        # List current replacements
        for i, replacement in enumerate(replacements):
            # Display pattern and replacement text (truncated if too long)
            pattern_text = replacement.get('pattern', '')
            replace_with_text = replacement.get('replace_with', '')
            if not replace_with_text:
                replace_with_text = replacement.get('replacement', '')

            # Truncate if too long for display
            if len(pattern_text) > 15:
                pattern_text = pattern_text[:15] + '...'
            if len(replace_with_text) > 15:
                replace_with_text = replace_with_text[:15] + '...'

            keyboard.append([
                InlineKeyboardButton(
                    f"❌ {pattern_text} ➡️ {replace_with_text}",
                    callback_data=f'delete_replacement_{i}'
                )
            ])

        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')])

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(
            f'✅ *تم إضافة الاستبدال بنجاح!*\n\n'
            f'من: "{pattern}"\n'
            f'إلى: "{replace_with}"\n\n'
            f'سيتم تطبيق هذا الاستبدال على جميع الرسائل الجديدة.',
            parse_mode=ParseMode.MARKDOWN
        )

        # Send a new message with the replacements menu
        update.message.reply_text(
            '📝 *قائمة الاستبدالات*\n\n'
            'يمكنك إدارة قائمة الاستبدالات من هنا:',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الاستبدال. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN
        )

    # Clear user data
    if 'replacement_pattern' in context.user_data:
        del context.user_data['replacement_pattern']

    return ConversationHandler.END

def receive_developer(update, context):
    """Process received developer user ID."""
    try:
        developer_id = int(update.message.text.strip())
    except ValueError:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'معرّف المستخدم يجب أن يكون رقماً صحيحاً.\n'
            'الرجاء المحاولة مرة أخرى أو استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_DEVELOPER

    # Load config, update and save
    config = main.load_config()
    old_developer = config.get("developer_id", "غير محدد")
    config["developer_id"] = developer_id
    success = main.save_config(config)

    # Update the global developer ID
    set_developer_id(developer_id)

    if success:
        update.message.reply_text(
            f'✅ *تم بنجاح!*\n\n'
            f'تم تعيين معرّف المطور من:\n'
            f'`{old_developer}`\n'
            f'إلى:\n'
            f'`{developer_id}`\n\n'
            f'المطور لديه صلاحيات مطلقة على البوت.',
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN
        )

    return ConversationHandler.END

def cancel_command(update, context):
    """Cancel current conversation."""
    update.message.reply_text(
        '🚫 *تم الإلغاء*\n\n'
        'تم إلغاء العملية الحالية.',
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END

def apply_text_replacements(text, replacements):
    """Apply text replacements to a string."""
    if not text or not replacements:
        return text

    result = text
    for replacement in replacements:
        pattern = replacement.get('pattern', '')

        # Support both key names: 'replace_with' and 'replacement'
        replace_with = replacement.get('replace_with', '')
        if not replace_with:
            replace_with = replacement.get('replacement', '')

        if pattern and isinstance(result, str):
            result = result.replace(pattern, replace_with)

    return result

def forward_message(update, context, target_channel_id):
    """Forward messages from source channel to target channel."""
    # Import all the required handlers
    import media_filters_handler
    import replacements_handler
    import blacklist_handler
    import whitelist_handler
    import rate_limit_handler
    import forwarding_control_handler
    import message_customization_handler
    import link_cleaner_handler
    import forwarded_filter_handler
    import duplicate_filter_handler
    import language_filter_handler
    import inline_button_filter_handler
    import char_limit_handler
    import delay_handler
    import translation_handler
    import working_hours_handler
    import text_format_handler
    import button_removal_handler
    try:
        message = update.message or update.channel_post

        if not message:
            logger.warning("Received update with no message")
            return

        logger.info(f"Forwarding message from channel {message.chat_id} to {target_channel_id}")

        # Check if forwarding is enabled
        if not forwarding_control_handler.should_forward_message(message.date):
            logger.info(f"Forwarding is disabled. Skipping message {message.message_id}.")
            return

        # Check if current time is within working hours
        if not working_hours_handler.is_within_working_hours():
            logger.info(f"Outside of working hours. Skipping message {message.message_id}.")
            return

        # Check rate limit
        if not rate_limit_handler.should_forward_message():
            logger.info(f"Rate limit reached. Skipping message {message.message_id}.")
            return

        # Check character limit
        message_text = message.text or message.caption or ""
        if not char_limit_handler.should_forward_message_by_length(message_text):
            logger.info(f"Message exceeds character limit. Skipping message {message.message_id}.")
            return

        # Apply delay if enabled
        delay_handler.should_delay_message()

        # Get current forward mode, media filters, text replacements, and blacklist from config
        config = main.load_config()
        forward_mode = config.get("forward_mode", "forward")
        media_filters = config.get("media_filters", {})
        text_replacements = config.get("text_replacements", [])
        blacklist = config.get("blacklist", [])

        # Determine message type for filtering
        message_type = None

        if message.text and not message.photo and not message.video and not message.audio and not message.voice and not message.document and not message.animation and not message.sticker and not message.video_note and not message.game and not message.poll and not message.contact and not message.location and not message.venue:
            message_type = "text"
        elif message.photo:
            message_type = "photo"
        elif message.video:
            message_type = "video"
        elif message.audio:
            message_type = "audio"
        elif message.voice:
            message_type = "voice"
        elif message.document:
            message_type = "document"
        elif message.animation:
            message_type = "animation"
        elif message.sticker:
            message_type = "sticker"
        elif message.video_note:
            message_type = "video_note"
        elif message.poll:
            message_type = "poll"
        elif message.game:
            message_type = "game"
        elif message.contact:
            message_type = "contact"
        elif message.location:
            message_type = "location"
        elif message.venue:
            message_type = "venue"

        # Check if this message type should be forwarded
        if message_type:
            is_allowed = media_filters.get(message_type, True)
            if not is_allowed:
                logger.info(f"Message type '{message_type}' is filtered out. Skipping message {message.message_id}")
                return

        # Check if message contains blacklisted words (only if blacklist is enabled)
        blacklist_enabled = config.get('blacklist_enabled', True)
        message_text = message.text or message.caption or ""

        if blacklist_enabled and blacklist_handler.contains_blacklisted_words(message_text, blacklist):
            logger.info(f"Message {message.message_id} contains blacklisted words. Skipping message.")
            return

        # Check whitelist if enabled (only forward if message contains whitelisted words)
        whitelist_enabled = config.get('whitelist_enabled', False)
        whitelist = config.get('whitelist', [])

        if whitelist_enabled and whitelist and not whitelist_handler.contains_whitelisted_words(message_text, whitelist):
            logger.info(f"Message {message.message_id} does not contain any whitelisted words. Skipping message.")
            return

        # Check forwarded message filter (skip messages forwarded from other channels if enabled)
        if not forwarded_filter_handler.should_forward_forwarded_message(message):
            logger.info(f"Message {message.message_id} is forwarded from another source. Skipping message.")
            return

        # Check duplicate message filter (skip if duplicate content)
        if not duplicate_filter_handler.should_forward_duplicate_message(message):
            logger.info(f"Message {message.message_id} is a duplicate. Skipping message.")
            return

        # Check language filter (skip based on language detection)
        if not language_filter_handler.should_forward_by_language(message):
            logger.info(f"Message {message.message_id} filtered by language settings. Skipping message.")
            return

        # Check link filter (skip messages with links if enabled)
        if not link_cleaner_handler.should_forward_message_with_links(message):
            logger.info(f"Message {message.message_id} contains links and link filter is enabled. Skipping message.")
            return

        # Check inline button filter (skip messages with inline buttons if enabled)
        if not inline_button_filter_handler.should_forward_message_with_buttons(message):
            logger.info(f"Message {message.message_id} contains inline buttons and button filter is enabled. Skipping message.")
            return

        # Forward based on selected mode
        if forward_mode == "forward":
            # Forward the message to the target channel (with "Forwarded from" tag)
            context.bot.forward_message(
                chat_id=target_channel_id,
                from_chat_id=message.chat_id,
                message_id=message.message_id
            )
            logger.info(f"Successfully forwarded message {message.message_id} with 'forwarded from' tag")
        else:
            # Copy and send the message as a new message (without "Forwarded from" tag)
            # Handle different message types
            if message.text and not message.photo and not message.video and not message.audio and not message.document:
                # Text message
                # Apply text replacements
                modified_text = apply_text_replacements(message.text, text_replacements)

                # Apply link cleaning if enabled
                link_cleaner_enabled = config.get("link_cleaner_enabled", False)
                if link_cleaner_enabled:
                    modified_text = link_cleaner_handler.clean_links(modified_text)
                    logger.info(f"Applied link cleaning to message {message.message_id}")

                # Apply automatic translation if enabled
                auto_translate_enabled = config.get("auto_translate_enabled", False)
                if auto_translate_enabled:
                    modified_text = translation_handler.translate_text(modified_text, config)
                    logger.info(f"Applied automatic translation to message {message.message_id}")

                # Apply text formatting (plain text or bold)
                modified_text = text_format_handler.apply_text_formatting(modified_text, config)

                # Apply header and footer customization
                modified_text = message_customization_handler.customize_message_text(modified_text, config)

                # Get inline button if enabled
                reply_markup = message_customization_handler.create_inline_button(config)

                # Remove buttons if button removal is enabled
                if button_removal_handler.should_remove_buttons() and reply_markup:
                    reply_markup = None
                    logger.info(f"Removed inline buttons from message {message.message_id}")

                # Send message with customizations
                context.bot.send_message(
                    chat_id=target_channel_id,
                    text=modified_text,
                    disable_web_page_preview=getattr(message, 'disable_web_page_preview', None),
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            elif message.photo:
                # Photo message
                photo = message.photo[-1]  # Get the largest photo
                # Apply text replacements to caption
                modified_caption = apply_text_replacements(message.caption, text_replacements)

                # Apply link cleaning if enabled
                link_cleaner_enabled = config.get("link_cleaner_enabled", False)
                if modified_caption and link_cleaner_enabled:
                    modified_caption = link_cleaner_handler.clean_links(modified_caption)
                    logger.info(f"Applied link cleaning to caption of message {message.message_id}")

                # Apply automatic translation if enabled
                auto_translate_enabled = config.get("auto_translate_enabled", False)
                if modified_caption and auto_translate_enabled:
                    modified_caption = translation_handler.translate_text(modified_caption, config)
                    logger.info(f"Applied automatic translation to caption of message {message.message_id}")

                # Apply text formatting if there's a caption
                if modified_caption:
                    modified_caption = text_format_handler.apply_text_formatting(modified_caption, config)

                # Apply header and footer customization
                if modified_caption:
                    modified_caption = message_customization_handler.customize_message_text(modified_caption, config)

                # Get inline button if enabled
                reply_markup = message_customization_handler.create_inline_button(config)

                # Remove buttons if button removal is enabled
                if button_removal_handler.should_remove_buttons() and reply_markup:
                    reply_markup = None
                    logger.info(f"Removed inline buttons from message {message.message_id}")

                # Send message with customizations
                context.bot.send_photo(
                    chat_id=target_channel_id,
                    photo=photo.file_id,
                    caption=modified_caption,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            elif message.video:
                # Video message
                # Apply text replacements to caption
                modified_caption = apply_text_replacements(message.caption, text_replacements)
                context.bot.send_video(
                    chat_id=target_channel_id,
                    video=message.video.file_id,
                    caption=modified_caption
                )
            elif message.document:
                # Document message
                # Apply text replacements to caption
                modified_caption = apply_text_replacements(message.caption, text_replacements)
                context.bot.send_document(
                    chat_id=target_channel_id,
                    document=message.document.file_id,
                    caption=modified_caption
                )
            elif message.audio:
                # Audio message
                # Apply text replacements to caption
                modified_caption = apply_text_replacements(message.caption, text_replacements)
                context.bot.send_audio(
                    chat_id=target_channel_id,
                    audio=message.audio.file_id,
                    caption=modified_caption
                )
            elif message.voice:
                # Voice message
                # Apply text replacements to caption
                modified_caption = apply_text_replacements(message.caption, text_replacements)
                context.bot.send_voice(
                    chat_id=target_channel_id,
                    voice=message.voice.file_id,
                    caption=modified_caption
                )
            elif message.sticker:
                # Sticker message
                context.bot.send_sticker(
                    chat_id=target_channel_id,
                    sticker=message.sticker.file_id
                )
            elif message.animation:
                # Animation/GIF message
                # Apply text replacements to caption
                modified_caption = apply_text_replacements(message.caption, text_replacements)
                context.bot.send_animation(
                    chat_id=target_channel_id,
                    animation=message.animation.file_id,
                    caption=modified_caption
                )
            elif message.video_note:
                # Video note (round video) message
                context.bot.send_video_note(
                    chat_id=target_channel_id,
                    video_note=message.video_note.file_id
                )
            elif message.poll:
                # Poll message - needs to be recreated since polls can't be copied directly
                # Apply text replacements to poll question and options
                modified_question = apply_text_replacements(message.poll.question, text_replacements)
                modified_options = [apply_text_replacements(option.text, text_replacements) for option in message.poll.options]
                context.bot.send_poll(
                    chat_id=target_channel_id,
                    question=modified_question,
                    options=modified_options,
                    is_anonymous=message.poll.is_anonymous,
                    allows_multiple_answers=message.poll.allows_multiple_answers,
                    type=message.poll.type
                )
            elif message.contact:
                # Contact message
                context.bot.send_contact(
                    chat_id=target_channel_id,
                    phone_number=message.contact.phone_number,
                    first_name=message.contact.first_name,
                    last_name=message.contact.last_name
                )
            elif message.location:
                # Location message
                context.bot.send_location(
                    chat_id=target_channel_id,
                    latitude=message.location.latitude,
                    longitude=message.location.longitude
                )
            elif message.venue:
                # Venue message
                # Apply text replacements to venue title and address
                modified_title = apply_text_replacements(message.venue.title, text_replacements)
                modified_address = apply_text_replacements(message.venue.address, text_replacements)
                context.bot.send_venue(
                    chat_id=target_channel_id,
                    latitude=message.venue.location.latitude,
                    longitude=message.venue.location.longitude,
                    title=modified_title,
                    address=modified_address
                )
            else:
                # Unsupported message type, use fallback to forward
                context.bot.forward_message(
                    chat_id=target_channel_id,
                    from_chat_id=message.chat_id,
                    message_id=message.message_id
                )
                logger.info(f"Unsupported message type, falling back to regular forwarding for message {message.message_id}")

            logger.info(f"Successfully copied and sent message {message.message_id} without 'forwarded from' tag")

        # Get the sent message object to store mapping
        sent_message = None
        if forward_mode == "forward":
            # For forwarded messages, get the message ID
            sent_message = context.bot.forward_message(
                chat_id=target_channel_id,
                from_chat_id=message.chat_id,
                message_id=message.message_id
            )
        else:
            # For copied messages, save the result based on message type
            if message.text and not message.photo and not message.video and not message.audio and not message.document:
                # Text message
                modified_text = apply_text_replacements(message.text, text_replacements)

                # Apply header and footer customization
                modified_text = message_customization_handler.customize_message_text(modified_text, config)

                # Get inline button if enabled
                reply_markup = message_customization_handler.create_inline_button(config)

                # Send message with customizations
                sent_message = context.bot.send_message(
                    chat_id=target_channel_id,
                    text=modified_text,
                    disable_web_page_preview=getattr(message, 'disable_web_page_preview', None),
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            elif message.photo:
                # Photo message
                photo = message.photo[-1]  # Get the largest photo
                modified_caption = apply_text_replacements(message.caption, text_replacements)

                # Apply header and footer customization
                if modified_caption:
                    modified_caption = message_customization_handler.customize_message_text(modified_caption, config)

                # Get inline button if enabled
                reply_markup = message_customization_handler.create_inline_button(config)

                # Send message with customizations
                sent_message = context.bot.send_photo(
                    chat_id=target_channel_id,
                    photo=photo.file_id,
                    caption=modified_caption,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            elif message.video:
                # Video message
                modified_caption = apply_text_replacements(message.caption, text_replacements)
                sent_message = context.bot.send_video(
                    chat_id=target_channel_id,
                    video=message.video.file_id,
                    caption=modified_caption
                )
            elif message.document:
                # Document message
                modified_caption = apply_text_replacements(message.caption, text_replacements)
                sent_message = context.bot.send_document(
                    chat_id=target_channel_id,
                    document=message.document.file_id,
                    caption=modified_caption
                )
            elif message.audio:
                # Audio message
                modified_caption = apply_text_replacements(message.caption, text_replacements)
                sent_message = context.bot.send_audio(
                    chat_id=target_channel_id,
                    audio=message.audio.file_id,
                    caption=modified_caption
                )
            elif message.voice:
                # Voice message
                modified_caption = apply_text_replacements(message.caption, text_replacements)
                sent_message = context.bot.send_voice(
                    chat_id=target_channel_id,
                    voice=message.voice.file_id,
                    caption=modified_caption
                )
            elif message.sticker:
                # Sticker message
                sent_message = context.bot.send_sticker(
                    chat_id=target_channel_id,
                    sticker=message.sticker.file_id
                )
            elif message.animation:
                # Animation/GIF message
                modified_caption = apply_text_replacements(message.caption, text_replacements)
                sent_message = context.bot.send_animation(
                    chat_id=target_channel_id,
                    animation=message.animation.file_id,
                    caption=modified_caption
                )
            elif message.video_note:
                # Video note (round video) message
                sent_message = context.bot.send_video_note(
                    chat_id=target_channel_id,
                    video_note=message.video_note.file_id
                )
            elif message.poll:
                # Poll message
                modified_question = apply_text_replacements(message.poll.question, text_replacements)
                modified_options = [apply_text_replacements(option.text, text_replacements) for option in message.poll.options]
                sent_message = context.bot.send_poll(
                    chat_id=target_channel_id,
                    question=modified_question,
                    options=modified_options,
                    is_anonymous=message.poll.is_anonymous,
                    allows_multiple_answers=message.poll.allows_multiple_answers,
                    type=message.poll.type
                )
            elif message.contact:
                # Contact message
                sent_message = context.bot.send_contact(
                    chat_id=target_channel_id,
                    phone_number=message.contact.phone_number,
                    first_name=message.contact.first_name,
                    last_name=message.contact.last_name
                )
            elif message.location:
                # Location message
                sent_message = context.bot.send_location(
                    chat_id=target_channel_id,
                    latitude=message.location.latitude,
                    longitude=message.location.longitude
                )
            elif message.venue:
                # Venue message
                modified_title = apply_text_replacements(message.venue.title, text_replacements)
                modified_address = apply_text_replacements(message.venue.address, text_replacements)
                sent_message = context.bot.send_venue(
                    chat_id=target_channel_id,
                    latitude=message.venue.location.latitude,
                    longitude=message.venue.location.longitude,
                    title=modified_title,
                    address=modified_address
                )
            else:
                # Unsupported message type, use fallback to forward
                sent_message = context.bot.forward_message(
                    chat_id=target_channel_id,
                    from_chat_id=message.chat_id,
                    message_id=message.message_id
                )

        # Update statistics
        stats["messages_forwarded"] += 1
        stats["last_forwarded"] = datetime.now()

    except Exception as e:
        stats["errors"] += 1
        logger.error(f"Error forwarding message: {str(e)}")

# تمت إزالة دالة forward_message_from_userbot كجزء من عملية إزالة ميزة UserBot

def restart_bot(update, context):
    """إعادة تشغيل البوت"""
    query = update.callback_query
    query.answer()

    # إرسال رسالة إعادة التشغيل
    query.edit_message_text(
        '🔄 *جاري إعادة تشغيل البوت...*\n\n'
        'سيتم إعادة تشغيل البوت خلال ثوانٍ قليلة.',
        parse_mode=ParseMode.MARKDOWN
    )

    # إرسال إشعار للمشرفين
    notification_message = "جاري إعادة تشغيل البوت بواسطة المستخدم: " + str(update.effective_user.id)
    send_notification(update, context, "info", notification_message)

    # إعادة تشغيل البوت
    os.execl(sys.executable, sys.executable, *sys.argv)

def error_handler(update, context):
    """معالجة الأخطاء وإرسال إشعارات."""
    stats["errors"] += 1
    error_message = f"Update {update} caused error: {context.error}"
    logger.error(error_message)

    # إرسال إشعار بالخطأ للمشرفين
    try:
        notification_message = f"حدث خطأ في البوت:\n{str(context.error)}"
        if update and update.effective_user:
            notification_message += f"\nالمستخدم: {update.effective_user.id}"
        send_notification(update, context, "error", notification_message)
    except Exception as e:
        logger.error(f"خطأ في إرسال إشعار الخطأ: {str(e)}")