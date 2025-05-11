"""
Module for handling inline button removal functionality in the Telegram bot.
This module contains functions for removing inline buttons from messages before forwarding.
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

def button_removal_menu(update, context):
    """Show the button removal menu."""
    config = load_config()
    
    # Get current status
    button_removal_enabled = config.get("button_removal_enabled", False)
    status = "✅ مفعّل" if button_removal_enabled else "❌ معطّل"
    
    # Create keyboard with options
    keyboard = [
        [InlineKeyboardButton(
            f"حذف الأزرار الشفافة: {status}", 
            callback_data='toggle_button_removal'
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
            '🔘 *حذف الأزرار الشفافة*\n\n'
            'تحكم في حذف الأزرار الشفافة من الرسائل قبل إعادة توجيهها.\n\n'
            f'الحالة الحالية: *{status}*\n\n'
            'عند تفعيل هذه الميزة، سيتم حذف جميع الأزرار الشفافة من الرسائل قبل إعادة توجيهها.\n\n'
            'ملاحظة: هذه الميزة مختلفة عن فلتر الأزرار الشفافة. فلتر الأزرار الشفافة يمنع توجيه الرسائل التي تحتوي على أزرار، أما هذه الميزة فتحذف الأزرار وتوجه الرسالة بدون الأزرار.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    # For direct commands
    else:
        update.message.reply_text(
            '🔘 *حذف الأزرار الشفافة*\n\n'
            'تحكم في حذف الأزرار الشفافة من الرسائل قبل إعادة توجيهها.\n\n'
            f'الحالة الحالية: *{status}*\n\n'
            'عند تفعيل هذه الميزة، سيتم حذف جميع الأزرار الشفافة من الرسائل قبل إعادة توجيهها.\n\n'
            'ملاحظة: هذه الميزة مختلفة عن فلتر الأزرار الشفافة. فلتر الأزرار الشفافة يمنع توجيه الرسائل التي تحتوي على أزرار، أما هذه الميزة فتحذف الأزرار وتوجه الرسالة بدون الأزرار.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

def toggle_button_removal_status(update, context):
    """Toggle the button removal feature on/off."""
    query = update.callback_query
    query.answer()
    
    # Load config
    config = load_config()
    
    # Toggle setting
    current_status = config.get("button_removal_enabled", False)
    config["button_removal_enabled"] = not current_status
    
    # Save config
    success = save_config(config)
    
    if success:
        # Show the menu again with updated status
        button_removal_menu(update, context)
    else:
        # Show error
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='button_removal_menu')
            ]])
        )

def should_remove_buttons():
    """Check if buttons should be removed from messages.
    
    Returns:
        bool: True if buttons should be removed, False otherwise
    """
    # Load config
    config = load_config()
    
    # Check if feature is enabled
    return config.get("button_removal_enabled", False)