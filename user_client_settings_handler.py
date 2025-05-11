"""
Module for handling settings for the UserBot client functionality.
This module provides UI for configuring the Telethon client within the bot.
"""

import json
import logging
import main
import os
import user_client_handler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler

# Define conversation states
WAITING_SESSION_STRING = 1
WAITING_SOURCE_ENTITY = 2


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store user data during conversation
user_data_store = {}

def load_config():
    """Load bot configuration from config.json file"""
    return main.load_config()

def save_config(config):
    """Save configuration to config.json file"""
    return main.save_config(config)


def save_session_string(session_string):
    """Save the Telethon session string"""
    config = load_config()

    config['telethon_session_string'] = session_string

    return save_config(config)

def get_session_string():
    """Get the saved Telethon session string"""
    config = load_config()

    return config.get('telethon_session_string')

def save_source_entities(source_entities):
    """Save source entities for the UserBot"""
    config = load_config()

    config['telethon_source_entities'] = source_entities

    return save_config(config)

def get_source_entities():
    """Get the saved source entities"""
    config = load_config()

    return config.get('telethon_source_entities', [])

def user_client_menu(update, context):
    """Show the UserBot client settings menu."""
    import user_settings_handler
    import translations

    # Get the user's language preference
    user_id = update.effective_user.id
    language = user_settings_handler.get_user_language(user_id)

    # Get translated text
    menu_title = "🤖 *إعدادات UserBot*\n\nيمكنك من هنا إعداد UserBot للاستماع إلى القنوات والمحادثات التي ليس فيها البوت مشرف."
    back_button = translations.get_text("button_back", language)

    # Get client status
    client_status = user_client_handler.get_client_status()
    status_emoji = "✅" if client_status == "Running" else "❌"


    # Get source entities
    source_entities = get_source_entities()
    entities_count = len(source_entities)

    # Create keyboard
    keyboard = []

    #session string check
    session_string_set = bool(get_session_string())
    session_string_emoji = "✅" if session_string_set else "❌"

    if session_string_set:
        # API credentials are set, show start/stop button
        if client_status == "Running":
            keyboard.append([
                InlineKeyboardButton("⏹️ إيقاف UserBot", callback_data='stop_user_client')
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("▶️ تشغيل UserBot", callback_data='start_user_client')
            ])

        # Show source entities button
        keyboard.append([
            InlineKeyboardButton(f"📡 مصادر الاستماع ({entities_count})", callback_data='manage_source_entities')
        ])


    # Always show setup API credentials button
    setup_text = "⚙️ إعداد جلسة UserBot" if not session_string_set else "🔄 تغيير جلسة UserBot"
    keyboard.append([
        InlineKeyboardButton(setup_text, callback_data='setup_session_string')
    ])

    # Add back button
    keyboard.append([
        InlineKeyboardButton(back_button, callback_data='advanced_features_menu')
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Status text
    status_text = f"\n\n*حالة الإعداد:*\n" \
                  f"{session_string_emoji} جلسة UserBot: {'مُعدة' if session_string_set else 'غير مُعدة'}\n" \
                  f"📡 عدد المصادر: {entities_count}\n" \
                  f"{status_emoji} الحالة: {client_status}"

    # For callback queries
    if update.callback_query:
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            menu_title + status_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    # For direct command
    else:
        update.message.reply_text(
            menu_title + status_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

def setup_session_string(update, context):
    """Start the process of setting up session string."""
    query = update.callback_query
    query.answer()

    query.edit_message_text(
        '🔑 *إعداد جلسة UserBot*\n\n'
        'الرجاء إدخال string session الخاص بك:\n\n'
        'استخدم /cancel للإلغاء.',
        parse_mode=ParseMode.MARKDOWN
    )

    return WAITING_SESSION_STRING

def receive_session_string(update, context):
    session_string = update.message.text.strip()
    save_session_string(session_string)
    update.message.reply_text(
        '✅ *تم!*\n\n'
        'تم حفظ string session بنجاح.\n\n'
        'الآن يمكنك إضافة مصادر الاستماع من خلال قائمة إعدادات UserBot.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 العودة إلى قائمة UserBot", callback_data='user_client_menu')
        ]])
    )
    return ConversationHandler.END


def manage_source_entities(update, context):
    """Show the source entities management menu."""
    query = update.callback_query
    query.answer()

    source_entities = get_source_entities()

    # Prepare description text
    entities_text = "لا توجد مصادر مضافة."
    if source_entities:
        entities_text = "*المصادر المضافة:*\n"
        for i, entity in enumerate(source_entities, 1):
            entities_text += f"{i}. `{entity}`\n"

    # Create keyboard
    keyboard = [
        [
            InlineKeyboardButton("➕ إضافة مصدر جديد", callback_data='add_source_entity')
        ],
        [
            InlineKeyboardButton("🗑 حذف جميع المصادر", callback_data='clear_source_entities')
        ],
        [
            InlineKeyboardButton("🔙 العودة إلى قائمة UserBot", callback_data='user_client_menu')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        '📡 *إدارة مصادر الاستماع*\n\n'
        'قم بإضافة معرّفات القنوات أو المحادثات التي تريد الاستماع إليها.\n'
        'يمكنك إضافة:\n'
        '- معرّف عددي للقناة/المجموعة مثل `-1001234567890`\n'
        '- اسم مستخدم مثل `@username`\n'
        '- رابط t.me مثل `https://t.me/username`\n\n'
        f'{entities_text}',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

def add_source_entity(update, context):
    """Start the process of adding a source entity."""
    query = update.callback_query
    query.answer()

    query.edit_message_text(
        '📡 *إضافة مصدر استماع جديد*\n\n'
        'الرجاء إدخال معرّف أو اسم مستخدم أو رابط للقناة/المحادثة:\n\n'
        'أمثلة:\n'
        '- `-1001234567890`\n'
        '- `@username`\n'
        '- `https://t.me/username`\n\n'
        'استخدم /cancel للإلغاء.',
        parse_mode=ParseMode.MARKDOWN
    )

    return WAITING_SOURCE_ENTITY

def receive_source_entity(update, context):
    """Process received source entity."""
    entity = update.message.text.strip()

    # Simple validation
    if not entity:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'المعرّف لا يمكن أن يكون فارغًا. الرجاء المحاولة مرة أخرى:',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_SOURCE_ENTITY

    # Add entity to list
    source_entities = get_source_entities()

    # Check if already exists
    if entity in source_entities:
        update.message.reply_text(
            '⚠️ *تنبيه*\n\n'
            'هذا المصدر موجود بالفعل في القائمة.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة إلى قائمة المصادر", callback_data='manage_source_entities')
            ]])
        )
        return ConversationHandler.END

    # Add to list and save
    source_entities.append(entity)
    save_source_entities(source_entities)

    # Show success message
    update.message.reply_text(
        '✅ *تم!*\n\n'
        f'تمت إضافة المصدر `{entity}` بنجاح.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 العودة إلى قائمة المصادر", callback_data='manage_source_entities')
        ]])
    )

    return ConversationHandler.END

def clear_source_entities(update, context):
    """Clear all source entities."""
    query = update.callback_query
    query.answer()

    # Create confirmation keyboard
    keyboard = [
        [
            InlineKeyboardButton("✅ نعم، حذف الكل", callback_data='confirm_clear_entities')
        ],
        [
            InlineKeyboardButton("❌ لا، إلغاء", callback_data='manage_source_entities')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        '⚠️ *تأكيد الحذف*\n\n'
        'هل أنت متأكد من حذف جميع مصادر الاستماع؟\n'
        'هذا الإجراء لا يمكن التراجع عنه.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

def confirm_clear_entities(update, context):
    """Confirm and clear all source entities."""
    query = update.callback_query
    query.answer()

    # Clear the list
    save_source_entities([])

    # Show success message
    query.edit_message_text(
        '✅ *تم!*\n\n'
        'تم حذف جميع مصادر الاستماع بنجاح.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 العودة إلى قائمة UserBot", callback_data='user_client_menu')
        ]])
    )

def start_user_client_button(update, context):
    """Start the UserBot client."""
    query = update.callback_query
    query.answer()

    # Get session string
    session_string = get_session_string()

    # Get source entities
    source_entities = get_source_entities()

    # Validate
    if not session_string:
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'جلسة UserBot غير مُعدة. الرجاء إعداد جلسة UserBot أولاً.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة إلى قائمة UserBot", callback_data='user_client_menu')
            ]])
        )
        return

    if not source_entities:
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'لا توجد مصادر استماع. الرجاء إضافة مصدر واحد على الأقل.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة إلى قائمة UserBot", callback_data='user_client_menu')
            ]])
        )
        return

    # Register forward function to client handler
    import bot_handler
    user_client_handler.register_bot_forward_function(bot_handler.forward_message_from_userbot)

    # Start the client
    success = user_client_handler.start_user_client(
        session_string=session_string,
        source_entities=source_entities
    )

    if success:
        query.edit_message_text(
            '✅ *تم!*\n\n'
            'تم تشغيل UserBot بنجاح. الآن سيتم الاستماع إلى المصادر المضافة وتوجيه الرسائل.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة إلى قائمة UserBot", callback_data='user_client_menu')
            ]])
        )
    else:
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء تشغيل UserBot. الرجاء التحقق من السجلات لمزيد من المعلومات.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة إلى قائمة UserBot", callback_data='user_client_menu')
            ]])
        )

def stop_user_client_button(update, context):
    """Stop the UserBot client."""
    query = update.callback_query
    query.answer()

    # Stop the client
    success = user_client_handler.stop_user_client()

    if success:
        query.edit_message_text(
            '✅ *تم!*\n\n'
            'تم إيقاف UserBot بنجاح.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة إلى قائمة UserBot", callback_data='user_client_menu')
            ]])
        )
    else:
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء إيقاف UserBot.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة إلى قائمة UserBot", callback_data='user_client_menu')
            ]])
        )

def cancel_command(update, context):
    """Cancel current conversation."""
    # Clean up user data
    if update.effective_user.id in user_data_store:
        del user_data_store[update.effective_user.id]

    update.message.reply_text(
        '❌ *تم الإلغاء*\n\n'
        'تم إلغاء العملية الحالية.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 العودة إلى قائمة UserBot", callback_data='user_client_menu')
        ]])
    )

    return ConversationHandler.END