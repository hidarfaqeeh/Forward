"""
Module for handling inline button filter functionality in the Telegram bot.
This module contains all functions related to filtering messages with inline buttons.
"""

import json
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext

# Configure logging
logger = logging.getLogger(__name__)

def load_config():
    """Load bot configuration from config.json file"""
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            config = json.load(file)
            return config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading config: {e}")
        return {}

def save_config(config):
    """Save configuration to config.json file"""
    try:
        with open('config.json', 'w', encoding='utf-8') as file:
            json.dump(config, file, ensure_ascii=False, indent=2)
            return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

def inline_button_filter_menu(update, context):
    """Show the inline button filter menu."""
    config = load_config()
    
    # Get current status
    inline_button_filter_enabled = config.get("inline_button_filter_enabled", False)
    status = "✅ مفعّل" if inline_button_filter_enabled else "❌ معطّل"
    
    # Create keyboard with options
    keyboard = [
        [InlineKeyboardButton(
            f"حالة الفلتر: {status}", 
            callback_data='toggle_inline_button_filter'
        )],
        [InlineKeyboardButton(
            "🔙 العودة للميزات المتقدمة", 
            callback_data='advanced_features_menu'
        )]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # For callback queries
    if update.callback_query:
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            '🔘 *فلتر الأزرار الشفافة*\n\n'
            'تحكم بتوجيه الرسائل التي تحتوي على أزرار شفافة.\n\n'
            f'الحالة الحالية: *{status}*\n\n'
            'عند تفعيل هذه الميزة، سيتجاهل البوت أي رسالة تحتوي على أزرار شفافة (Inline Buttons).',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    # For direct commands
    else:
        update.message.reply_text(
            '🔘 *فلتر الأزرار الشفافة*\n\n'
            'تحكم بتوجيه الرسائل التي تحتوي على أزرار شفافة.\n\n'
            f'الحالة الحالية: *{status}*\n\n'
            'عند تفعيل هذه الميزة، سيتجاهل البوت أي رسالة تحتوي على أزرار شفافة (Inline Buttons).',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

def toggle_inline_button_filter_status(update, context):
    """Toggle the inline button filter feature on/off."""
    query = update.callback_query
    query.answer()
    
    # Load config
    config = load_config()
    
    # Toggle setting
    current_status = config.get("inline_button_filter_enabled", False)
    config["inline_button_filter_enabled"] = not current_status
    
    # Save config
    success = save_config(config)
    
    if success:
        # Show the menu again with updated status
        inline_button_filter_menu(update, context)
    else:
        # Show error
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='inline_button_filter_menu')
            ]])
        )

def has_inline_keyboard(message):
    """Check if a message has an inline keyboard attached.
    
    Args:
        message: A Telegram message object
        
    Returns:
        bool: True if the message has inline keyboard buttons, False otherwise
    """
    # Check if the message has a reply markup with inline keyboard
    return (hasattr(message, 'reply_markup') and 
            message.reply_markup and 
            hasattr(message.reply_markup, 'inline_keyboard') and
            message.reply_markup.inline_keyboard)

def should_forward_message_with_buttons(message):
    """Check if a message with inline buttons should be forwarded.
    
    Args:
        message: A Telegram message object
        
    Returns:
        bool: True if the message should be forwarded, False otherwise
    """
    # Load config to check if this feature is enabled
    config = load_config()
    inline_button_filter_enabled = config.get("inline_button_filter_enabled", False)
    
    # If feature is disabled, always forward
    if not inline_button_filter_enabled:
        return True
    
    # Check if message has inline buttons
    if has_inline_keyboard(message):
        return False
    
    # Otherwise, forward the message
    return True