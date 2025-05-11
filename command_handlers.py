"""
Module for handling commands and admin panel in the Telegram bot.
This module contains handlers for bot commands like /start, /help, and the admin panel.
"""

import logging
from datetime import datetime
import main
import bot_handler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler

# Conversation states
WAITING_SOURCE = 1
WAITING_TARGET = 2
WAITING_ADMIN = 3
WAITING_DEVELOPER = 4

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start_command(update, context):
    """Send a message when the command /start is issued."""
    # Check if user is admin
    is_admin = bot_handler.is_admin(update.effective_user.id)

    # Basic welcome message
    welcome_message = (
        '👋 *مرحباً بك في بوت التوجيه!*\n\n'
        'هذا البوت يقوم بتوجيه الرسائل من قناة المصدر إلى قناة الهدف.\n\n'
    )

    # Admin-specific message and buttons
    if is_admin:
        welcome_message += (
            '🛠 *أنت مسؤول في هذا البوت!*\n'
            'يمكنك استخدام الأوامر التالية:\n'
            '/admin - عرض لوحة التحكم\n'
            '/setup - بدء معالج الإعداد\n'
            '/help - عرض المساعدة\n'
            '/status - عرض حالة البوت\n\n'
            'يمكنك ضبط قنوات المصدر والهدف من لوحة التحكم.'
        )
        
        # Create keyboard with all requested buttons
        keyboard = [
            [InlineKeyboardButton("🛠 لوحة التحكم", callback_data='admin_panel')],
            [InlineKeyboardButton("📡 قناة البوت", url='https://t.me/ZawamlAnsarallah')],
            [InlineKeyboardButton("👨‍💻 مطور البوت", url='https://t.me/odaygholy')],
            [
                InlineKeyboardButton("ℹ️ حول البوت", callback_data='about_bot'),
                InlineKeyboardButton("❓ المساعدة", callback_data='help_menu')
            ]
        ]
    else:
        welcome_message += (
            'هذا البوت للمسؤولين فقط.\n'
            'إذا كنت مسؤولاً، يرجى التواصل مع المسؤول الرئيسي لإضافتك.'
        )
        
        # Create keyboard with only public information buttons for non-admins
        keyboard = [
            [InlineKeyboardButton("📡 قناة البوت", url='https://t.me/ZawamlAnsarallah')],
            [InlineKeyboardButton("👨‍💻 مطور البوت", url='https://t.me/odaygholy')],
            [
                InlineKeyboardButton("ℹ️ حول البوت", callback_data='about_bot'),
                InlineKeyboardButton("❓ المساعدة", callback_data='help_menu')
            ]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message
    if is_admin:
        update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )

def help_command(update, context):
    """Send a message when the command /help is issued."""
    # Check if user is admin
    is_admin = bot_handler.is_admin(update.effective_user.id)

    if is_admin:
        # Admin help message
        help_message = (
            '🔍 *دليل المساعدة*\n\n'
            '*الأوامر المتاحة:*\n'
            '/start - بدء البوت\n'
            '/help - عرض هذه المساعدة\n'
            '/admin - عرض لوحة التحكم\n'
            '/status - عرض حالة البوت\n'
            '/setup - بدء معالج الإعداد\n\n'
            '*الإعدادات:*\n'
            '- عليك تعيين قناة المصدر وقناة الهدف لكي يعمل البوت.\n'
            '- يجب أن يكون البوت مشرفاً في كلا القناتين.\n'
            '- يمكنك اختيار طريقة النشر: توجيه أو نسخ.\n'
            '- يمكنك تحديد أنواع الوسائط المسموح بتوجيهها.\n'
            '- يمكنك تعريف استبدالات نصية لتعديل محتوى الرسائل.\n\n'
            '*متطلبات:*\n'
            '- البوت يجب أن يكون مشرفاً في القناتين (المصدر والهدف).\n'
            '- في قناة المصدر يحتاج صلاحية قراءة الرسائل.\n'
            '- في قناة الهدف يحتاج صلاحية نشر الرسائل.\n\n'
            'للمزيد من المساعدة، استخدم /admin للوصول إلى لوحة التحكم.'
        )
    else:
        # Non-admin help message
        help_message = (
            '🔍 *دليل المساعدة*\n\n'
            'هذا البوت مخصص للمسؤولين فقط.\n'
            'إذا كنت مسؤولاً، يرجى التواصل مع المسؤول الرئيسي لإضافتك.\n\n'
            '/start - بدء البوت\n'
            '/help - عرض هذه المساعدة'
        )

    # Send the message
    update.message.reply_text(
        help_message,
        parse_mode=ParseMode.MARKDOWN
    )

def status_command(update, context):
    """Send a message when the command /status is issued."""
    # Check if user is admin
    if not bot_handler.is_admin(update.effective_user.id):
        update.message.reply_text(
            '⛔ *غير مصرح*\n\n'
            'فقط المسؤولون يمكنهم استخدام هذا الأمر.',
            parse_mode=ParseMode.MARKDOWN
        )
        return
    stats = bot_handler.stats

    # Set started_at if not already set
    if stats["started_at"] is None:
        stats["started_at"] = datetime.now()

    # Calculate uptime
    uptime = datetime.now() - stats["started_at"]
    uptime_str = str(uptime).split('.')[0]  # Remove microseconds

    # Format last_forwarded
    last_forwarded = "لم يتم بعد" if stats["last_forwarded"] is None else stats["last_forwarded"].strftime("%Y-%m-%d %H:%M:%S")

    # Load config to show current channels
    config = main.load_config()
    source_channel = config.get("source_channel", "غير محدد")
    target_channel = config.get("target_channel", "غير محدد")

    # Get forward mode
    forward_mode = config.get("forward_mode", "forward")
    if forward_mode == "forward":
        forward_mode_text = "توجيه (مع علامة التوجيه)"
    else:
        forward_mode_text = "نسخ (بدون علامة التوجيه)"

    # Send status message
    update.message.reply_text(
        f'📊 *حالة البوت*\n\n'
        f'▶️ *يعمل منذ:* {stats["started_at"].strftime("%Y-%m-%d %H:%M:%S")}\n'
        f'⏱ *مدة التشغيل:* {uptime_str}\n'
        f'✉️ *الرسائل الموجهة:* {stats["messages_forwarded"]}\n'
        f'🕒 *آخر توجيه:* {last_forwarded}\n'
        f'📡 *قناة المصدر:* {source_channel}\n'
        f'📡 *قناة الهدف:* {target_channel}\n'
        f'📝 *طريقة النشر:* {forward_mode_text}\n'
        f'❌ *الأخطاء:* {stats["errors"]}',
        parse_mode=ParseMode.MARKDOWN
    )

def admin_panel(update, context):
    """Display admin control panel."""
    # Check if command or callback
    if update.callback_query:
        query = update.callback_query
        query.answer()

        # Create keyboard with admin options
        keyboard = create_admin_keyboard()

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            '🛠 *لوحة التحكم*\n\n'
            'مرحباً بك في لوحة تحكم البوت. يمكنك إدارة البوت من هنا.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        # Check if user is admin
        if not bot_handler.is_admin(update.effective_user.id):
            update.message.reply_text(
                '⛔ *غير مصرح*\n\n'
                'فقط المسؤولون يمكنهم استخدام هذا الأمر.',
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Create keyboard with admin options
        keyboard = create_admin_keyboard()

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(
            '🛠 *لوحة التحكم*\n\n'
            'مرحباً بك في لوحة تحكم البوت. يمكنك إدارة البوت من هنا.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    return None

def create_admin_keyboard():
    """Create the admin panel keyboard with all options."""
    config = main.load_config()

    # Set the button text for forward mode based on current setting
    forward_mode = config.get("forward_mode", "forward")
    if forward_mode == "forward":
        forward_mode_text = "🔄 طريقة النشر: توجيه"
    else:
        forward_mode_text = "📝 طريقة النشر: نسخ"

    # Create the keyboard with unified layout
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
        ]
    ]

    return keyboard

def setup_command(update, context):
    """Setup wizard for the bot."""
    # Check if user is admin
    if not bot_handler.is_admin(update.effective_user.id):
        update.message.reply_text(
            '⛔ *غير مصرح*\n\n'
            'فقط المسؤولون يمكنهم استخدام هذا الأمر.',
            parse_mode=ParseMode.MARKDOWN
        )
        return
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
    # Check if user is admin
    if not bot_handler.is_admin(update.effective_user.id):
        update.message.reply_text(
            '⛔ *غير مصرح*\n\n'
            'فقط المسؤولون يمكنهم استخدام هذا الأمر.',
            parse_mode=ParseMode.MARKDOWN
        )
        return
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
    # Check if user is admin
    if not bot_handler.is_admin(update.effective_user.id):
        update.message.reply_text(
            '⛔ *غير مصرح*\n\n'
            'فقط المسؤولون يمكنهم استخدام هذا الأمر.',
            parse_mode=ParseMode.MARKDOWN
        )
        return
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
    # Check if user is admin
    if not bot_handler.is_admin(update.effective_user.id):
        update.message.reply_text(
            '⛔ *غير مصرح*\n\n'
            'فقط المسؤولون يمكنهم استخدام هذا الأمر.',
            parse_mode=ParseMode.MARKDOWN
        )
        return
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
    try:
        source_channel = update.message.text.strip()

        if source_channel == '/cancel':
            update.message.reply_text(
                '🚫 *تم الإلغاء*\n\n'
                'تم إلغاء العملية الحالية.',
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END

        # Make sure it starts with -100 and is all numbers after that
        if source_channel.startswith('-100') and source_channel[4:].isdigit():
            # Load config, update and save
            config = main.load_config()
            old_source = config.get("source_channel", "غير محدد")
            config["source_channel"] = source_channel
            success = main.save_config(config)

            if success:
                update.message.reply_text(
                    f'✅ *تم بنجاح!*\n\n'
                    f'تم تغيير قناة المصدر من:\n'
                    f'`{old_source}`\n'
                    f'إلى:\n'
                    f'`{source_channel}`\n\n'
                    f'سيتم نقل الرسائل من هذه القناة إلى قناة الهدف.',
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                update.message.reply_text(
                    '❌ *خطأ!*\n\n'
                    'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
                    parse_mode=ParseMode.MARKDOWN
                )
        else:
            update.message.reply_text(
                '❌ *خطأ!*\n\n'
                'صيغة معرّف القناة غير صحيحة. يجب أن تبدأ بـ `-100` متبوعاً بالأرقام.\n'
                'مثال: `-1001234567890`\n\n'
                'الرجاء المحاولة مرة أخرى أو استخدم /cancel للإلغاء.',
                parse_mode=ParseMode.MARKDOWN
            )
            return WAITING_SOURCE
    except Exception as e:
        update.message.reply_text(
            f'❌ *خطأ!*\n\n'
            f'حدث خطأ غير متوقع: {str(e)}\n'
            f'الرجاء المحاولة مرة أخرى أو استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_SOURCE

    return ConversationHandler.END

def receive_target(update, context):
    """Process received target channel ID."""
    try:
        target_channel = update.message.text.strip()

        if target_channel == '/cancel':
            update.message.reply_text(
                '🚫 *تم الإلغاء*\n\n'
                'تم إلغاء العملية الحالية.',
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END

        # Make sure it starts with -100 and is all numbers after that
        if target_channel.startswith('-100') and target_channel[4:].isdigit():
            # Load config, update and save
            config = main.load_config()
            old_target = config.get("target_channel", "غير محدد")
            config["target_channel"] = target_channel
            success = main.save_config(config)

            if success:
                update.message.reply_text(
                    f'✅ *تم بنجاح!*\n\n'
                    f'تم تغيير قناة الهدف من:\n'
                    f'`{old_target}`\n'
                    f'إلى:\n'
                    f'`{target_channel}`\n\n'
                    f'سيتم نقل الرسائل إلى هذه القناة من قناة المصدر.',
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                update.message.reply_text(
                    '❌ *خطأ!*\n\n'
                    'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
                    parse_mode=ParseMode.MARKDOWN
                )
        else:
            update.message.reply_text(
                '❌ *خطأ!*\n\n'
                'صيغة معرّف القناة غير صحيحة. يجب أن تبدأ بـ `-100` متبوعاً بالأرقام.\n'
                'مثال: `-1001234567890`\n\n'
                'الرجاء المحاولة مرة أخرى أو استخدم /cancel للإلغاء.',
                parse_mode=ParseMode.MARKDOWN
            )
            return WAITING_TARGET
    except Exception as e:
        update.message.reply_text(
            f'❌ *خطأ!*\n\n'
            f'حدث خطأ غير متوقع: {str(e)}\n'
            f'الرجاء المحاولة مرة أخرى أو استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_TARGET

    return ConversationHandler.END

def receive_admin(update, context):
    """Process received admin user ID."""
    try:
        admin_id = int(update.message.text.strip())

        if update.message.text.strip() == '/cancel':
            update.message.reply_text(
                '🚫 *تم الإلغاء*\n\n'
                'تم إلغاء العملية الحالية.',
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END

        # Load config and check if admin already exists
        config = main.load_config()
        if "admin_users" not in config:
            config["admin_users"] = []

        # Developer is always admin
        developer_id = config.get("developer_id", None)
        if developer_id == admin_id:
            update.message.reply_text(
                '⚠️ *تنبيه!*\n\n'
                'المستخدم المحدد هو مطور البوت بالفعل وله صلاحيات مطلقة.',
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END

        # Check if admin already exists
        if admin_id in config["admin_users"]:
            update.message.reply_text(
                '⚠️ *تنبيه!*\n\n'
                'المستخدم المحدد مضاف بالفعل كمشرف.',
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END

        # Add new admin and save
        config["admin_users"].append(admin_id)
        success = main.save_config(config)

        if success:
            update.message.reply_text(
                f'✅ *تم بنجاح!*\n\n'
                f'تم إضافة المستخدم `{admin_id}` كمشرف جديد.\n'
                f'يمكنه الآن استخدام أوامر المشرفين والوصول إلى لوحة التحكم.',
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            update.message.reply_text(
                '❌ *خطأ!*\n\n'
                'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
                parse_mode=ParseMode.MARKDOWN
            )
    except ValueError:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'معرّف المستخدم يجب أن يكون رقماً صحيحاً.\n'
            'الرجاء المحاولة مرة أخرى أو استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_ADMIN

    return ConversationHandler.END

def set_developer_button(update, context):
    """Show interface to set developer ID."""
    query = update.callback_query
    query.answer()

    query.edit_message_text(
        '🔐 *تعيين معرّف مطور البوت*\n\n'
        'الرجاء إرسال معرّف المستخدم (User ID) الخاص بمطور البوت.\n'
        'يمكن للمستخدم معرفة معرّفه عن طريق إرسال رسالة إلى بوت مثل @userinfobot\n\n'
        'المطور لديه صلاحيات مطلقة على البوت.\n'
        'استخدم /cancel للإلغاء.',
        parse_mode=ParseMode.MARKDOWN
    )
    return WAITING_DEVELOPER

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
    bot_handler.set_developer_id(developer_id)

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

def toggle_forward_mode(update, context):
    """Toggle between forward and copy modes."""
    # Determine if this is called from a command or callback query
    if update.callback_query:
        query = update.callback_query
        query.answer()

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

            # Create updated keyboard
            keyboard = create_admin_keyboard()
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
                    InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')
                ]])
            )
    else:
        # Called from a text command
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
            else:
                mode_description = "نسخ الرسائل بدون علامة 'موجه من'"

            # Create admin panel keyboard for the response
            keyboard = [
                [InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            update.message.reply_text(
                f'✅ *تم تغيير طريقة النشر بنجاح!*\n\n'
                f'طريقة النشر الحالية: *{mode_description}*\n\n',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            # Show error message
            update.message.reply_text(
                '❌ *خطأ!*\n\n'
                'حدث خطأ أثناء تغيير طريقة النشر. الرجاء المحاولة مرة أخرى.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')
                ]])
            )
    return None

def show_stats(update, context):
    """Show bot statistics."""
    query = update.callback_query
    query.answer()

    stats = bot_handler.stats

    if stats["started_at"] is None:
        stats["started_at"] = datetime.now()

    uptime = datetime.now() - stats["started_at"]
    uptime_str = str(uptime).split('.')[0]  # Remove microseconds

    last_forwarded = "لم يتم بعد" if stats["last_forwarded"] is None else stats["last_forwarded"].strftime("%Y-%m-%d %H:%M:%S")

    # Load config to show current channels
    config = main.load_config()
    source_channel = config.get("source_channel", "غير محدد")
    target_channel = config.get("target_channel", "غير محدد")
    admin_count = len(config.get("admin_users", []))

    # Get current forward mode
    forward_mode = config.get("forward_mode", "forward")
    if forward_mode == "forward":
        forward_mode_text = "توجيه (مع علامة التوجيه)"
    else:
        forward_mode_text = "نسخ (بدون علامة التوجيه)"

    # Add a back button
    keyboard = [[InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        f'📊 *إحصائيات البوت*\n\n'
        f'▶️ *يعمل منذ:* {stats["started_at"].strftime("%Y-%m-%d %H:%M:%S")}\n'
        f'⏱ *مدة التشغيل:* {uptime_str}\n'
        f'✉️ *الرسائل الموجهة:* {stats["messages_forwarded"]}\n'
        f'🕒 *آخر توجيه:* {last_forwarded}\n'
        f'📡 *قناة المصدر:* {source_channel}\n'
        f'📡 *قناة الهدف:* {target_channel}\n'
        f'📝 *طريقة النشر:* {forward_mode_text}\n'
        f'👥 *عدد المشرفين:* {admin_count}\n'
        f'❌ *الأخطاء:* {stats["errors"]}',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    return None

def cancel_command(update, context):
    """Cancel current conversation."""
    update.message.reply_text(
        '🚫 *تم الإلغاء*\n\n'
        'تم إلغاء العملية الحالية.',
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END