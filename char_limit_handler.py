"""
Module for handling character limit functionality in the Telegram bot.
This module contains all functions related to filtering messages based on character count.
"""

import logging
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler

# Configure logging
logger = logging.getLogger(__name__)

# State constants for conversation handlers
WAITING_CHAR_LIMIT = range(1)

def load_config():
    """Load bot configuration from config.json file"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.error("Failed to load config.json")
        return {}

def save_config(config):
    """Save configuration to config.json file"""
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")
        return False

def char_limit_menu(update, context):
    """Show the character limit menu."""
    config = load_config()
    
    # Initialize char_limit settings if not exists
    if 'char_limit_enabled' not in config:
        config['char_limit_enabled'] = False
        config['char_limit_count'] = 1000
        save_config(config)
    
    char_limit_status = "مفعّل ✅" if config.get("char_limit_enabled", False) else "معطّل ❌"
    char_limit_count = config.get("char_limit_count", 1000)
    
    keyboard = [
        [InlineKeyboardButton(f"الحالة: {char_limit_status}", callback_data="toggle_char_limit")],
        [InlineKeyboardButton(f"الحد الأقصى للأحرف: {char_limit_count}", callback_data="change_char_limit")],
        [InlineKeyboardButton("عودة ↩️", callback_data="admin_panel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "📏 *إعدادات حد الأحرف*\n\n" \
              "هذه الميزة تسمح للرسائل بالتوجيه فقط إذا كان عدد أحرفها يتناسب مع الحد المعين.\n\n" \
              f"الحالة الحالية: {char_limit_status}\n" \
              f"الحد الأقصى للأحرف: {char_limit_count}\n\n" \
              "الرسائل التي تزيد عن هذا الحد لن يتم توجيهها."
    
    # Edit message if it exists, otherwise send new message
    if update.callback_query:
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    return

def toggle_char_limit_status(update, context):
    """Toggle the character limit feature on/off."""
    config = load_config()
    
    # Toggle status
    current_status = config.get("char_limit_enabled", False)
    config["char_limit_enabled"] = not current_status
    
    # Save config
    save_config(config)
    
    # Return to char limit menu
    char_limit_menu(update, context)

def change_char_limit(update, context):
    """Start the process of changing the character limit."""
    update.callback_query.answer()
    
    message = "📏 *تغيير الحد الأقصى للأحرف*\n\n" \
              "الرجاء إرسال رقم للحد الأقصى للأحرف المسموح به للرسائل.\n" \
              "مثال: `1000` لقبول الرسائل التي لا تزيد عن 1000 حرف.\n\n" \
              "استخدم /cancel للإلغاء."
    
    update.callback_query.edit_message_text(
        text=message,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return WAITING_CHAR_LIMIT

def receive_char_limit(update, context):
    """Process received character limit."""
    try:
        char_limit = int(update.message.text.strip())
        
        if update.message.text.strip() == '/cancel':
            update.message.reply_text(
                '🚫 *تم الإلغاء*\n\n'
                'تم إلغاء العملية الحالية.',
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END
        
        if char_limit <= 0:
            update.message.reply_text(
                '❌ *خطأ!*\n\n'
                'يجب أن يكون الحد الأقصى للأحرف رقمًا موجبًا.\n'
                'الرجاء المحاولة مرة أخرى أو استخدم /cancel للإلغاء.',
                parse_mode=ParseMode.MARKDOWN
            )
            return WAITING_CHAR_LIMIT
        
        # Load config and update character limit
        config = load_config()
        old_limit = config.get("char_limit_count", 1000)
        config["char_limit_count"] = char_limit
        
        # Save config
        success = save_config(config)
        
        if success:
            # Show success message with keyboard to return to char limit menu
            keyboard = [[InlineKeyboardButton("العودة إلى إعدادات حد الأحرف", callback_data="char_limit_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            update.message.reply_text(
                f'✅ *تم بنجاح!*\n\n'
                f'تم تغيير الحد الأقصى للأحرف من {old_limit} إلى {char_limit}.\n\n'
                f'الرسائل التي تزيد عن {char_limit} حرف لن يتم توجيهها.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            update.message.reply_text(
                '❌ *خطأ!*\n\n'
                'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
                parse_mode=ParseMode.MARKDOWN
            )
            return WAITING_CHAR_LIMIT
            
    except ValueError:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'يجب إدخال رقم صحيح فقط.\n'
            'الرجاء المحاولة مرة أخرى أو استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_CHAR_LIMIT
    
    return ConversationHandler.END

def should_forward_message_by_length(message_text):
    """Check if a message should be forwarded based on character count."""
    config = load_config()
    char_limit_enabled = config.get("char_limit_enabled", False)
    
    # If feature is disabled, always forward
    if not char_limit_enabled:
        return True
    
    # If no text, always forward (media without caption, etc.)
    if not message_text:
        return True
    
    char_limit_count = config.get("char_limit_count", 1000)
    message_length = len(message_text)
    
    should_forward = message_length <= char_limit_count
    
    if not should_forward:
        logger.info(f"Message exceeds character limit ({message_length} > {char_limit_count}). Skipping message.")
    
    return should_forward