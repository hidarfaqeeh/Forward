"""
Module for handling forwarded messages filter functionality in the Telegram bot.
This module contains all functions related to filtering forwarded messages.
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

def forwarded_filter_menu(update, context):
    """Show the forwarded messages filter menu."""
    config = load_config()
    
    # Get current status
    forwarded_filter_enabled = config.get("forwarded_filter_enabled", False)
    status = "✅ مفعّل" if forwarded_filter_enabled else "❌ معطّل"
    
    # Create keyboard with options
    keyboard = [
        [InlineKeyboardButton(
            f"حالة الفلتر: {status}", 
            callback_data='toggle_forwarded_filter'
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
            '🔄 *فلتر الرسائل المعاد توجيهها*\n\n'
            'تحكم بتوجيه الرسائل التي تم إعادة توجيهها سابقاً.\n\n'
            f'الحالة الحالية: *{status}*\n\n'
            'عند تفعيل هذه الميزة، سيتجاهل البوت أي رسالة تم إعادة توجيهها مسبقاً من قنوات أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    # For direct commands
    else:
        update.message.reply_text(
            '🔄 *فلتر الرسائل المعاد توجيهها*\n\n'
            'تحكم بتوجيه الرسائل التي تم إعادة توجيهها سابقاً.\n\n'
            f'الحالة الحالية: *{status}*\n\n'
            'عند تفعيل هذه الميزة، سيتجاهل البوت أي رسالة تم إعادة توجيهها مسبقاً من قنوات أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

def toggle_forwarded_filter_status(update, context):
    """Toggle the forwarded messages filter feature on/off."""
    query = update.callback_query
    query.answer()
    
    # Load config
    config = load_config()
    
    # Toggle setting
    current_status = config.get("forwarded_filter_enabled", False)
    config["forwarded_filter_enabled"] = not current_status
    
    # Save config
    success = save_config(config)
    
    if success:
        # Show the menu again with updated status
        forwarded_filter_menu(update, context)
    else:
        # Show error
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='forwarded_filter_menu')
            ]])
        )

def should_forward_forwarded_message(message):
    """Check if a forwarded message should be forwarded based on config.
    
    Returns:
        bool: True if the message should be forwarded, False otherwise.
    """
    # Load config to check if this feature is enabled
    config = load_config()
    forwarded_filter_enabled = config.get("forwarded_filter_enabled", False)
    
    # If feature is disabled, always forward
    if not forwarded_filter_enabled:
        return True
    
    # Check if the message is a forwarded message
    if message.forward_from or message.forward_from_chat:
        return False
    
    # Otherwise, forward the message
    return True