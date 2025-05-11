"""
Module for handling text formatting functionality in the Telegram bot.
This module contains functions for plain text conversion and bold text conversion.
"""

import json
import logging
import re
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

def text_format_menu(update, context):
    """Show the text formatting menu."""
    config = load_config()
    
    # Get current status for plain text conversion
    plain_text_enabled = config.get("plain_text_conversion_enabled", False)
    plain_status = "✅ مفعّل" if plain_text_enabled else "❌ معطّل"
    
    # Get current status for bold text conversion
    bold_text_enabled = config.get("bold_text_conversion_enabled", False)
    bold_status = "✅ مفعّل" if bold_text_enabled else "❌ معطّل"
    
    # Create keyboard with options
    keyboard = [
        [InlineKeyboardButton(
            f"تحويل إلى نص عادي: {plain_status}", 
            callback_data='toggle_plain_text'
        )],
        [InlineKeyboardButton(
            f"تحويل إلى نص عريض: {bold_status}", 
            callback_data='toggle_bold_text'
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
            '📝 *تنسيق النصوص*\n\n'
            'تحكم في تنسيق النصوص قبل إعادة توجيهها.\n\n'
            f'تحويل إلى نص عادي: *{plain_status}*\n'
            'عند تفعيل هذه الميزة، سيتم تحويل جميع النصوص الغنية (روابط، نص عريض، إلخ) إلى نص عادي.\n\n'
            f'تحويل إلى نص عريض: *{bold_status}*\n'
            'عند تفعيل هذه الميزة، سيتم تحويل جميع النصوص إلى نص عريض قبل إعادة توجيهها.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    # For direct commands
    else:
        update.message.reply_text(
            '📝 *تنسيق النصوص*\n\n'
            'تحكم في تنسيق النصوص قبل إعادة توجيهها.\n\n'
            f'تحويل إلى نص عادي: *{plain_status}*\n'
            'عند تفعيل هذه الميزة، سيتم تحويل جميع النصوص الغنية (روابط، نص عريض، إلخ) إلى نص عادي.\n\n'
            f'تحويل إلى نص عريض: *{bold_status}*\n'
            'عند تفعيل هذه الميزة، سيتم تحويل جميع النصوص إلى نص عريض قبل إعادة توجيهها.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

def toggle_plain_text_status(update, context):
    """Toggle the plain text conversion feature on/off."""
    query = update.callback_query
    query.answer()
    
    # Load config
    config = load_config()
    
    # Toggle setting
    current_status = config.get("plain_text_conversion_enabled", False)
    config["plain_text_conversion_enabled"] = not current_status
    
    # If enabling plain text, disable bold text (they are mutually exclusive)
    if not current_status:
        config["bold_text_conversion_enabled"] = False
    
    # Save config
    success = save_config(config)
    
    if success:
        # Show the menu again with updated status
        text_format_menu(update, context)
    else:
        # Show error
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='text_format_menu')
            ]])
        )

def toggle_bold_text_status(update, context):
    """Toggle the bold text conversion feature on/off."""
    query = update.callback_query
    query.answer()
    
    # Load config
    config = load_config()
    
    # Toggle setting
    current_status = config.get("bold_text_conversion_enabled", False)
    config["bold_text_conversion_enabled"] = not current_status
    
    # If enabling bold text, disable plain text (they are mutually exclusive)
    if not current_status:
        config["plain_text_conversion_enabled"] = False
    
    # Save config
    success = save_config(config)
    
    if success:
        # Show the menu again with updated status
        text_format_menu(update, context)
    else:
        # Show error
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='text_format_menu')
            ]])
        )

def convert_to_plain_text(text):
    """Convert rich text (Markdown/HTML) to plain text.
    
    Args:
        text (str): The text to convert
        
    Returns:
        str: Plain text without formatting
    """
    if not text:
        return text
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove Markdown formatting
    # Remove bold
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    
    # Remove italic
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    
    # Remove code
    text = re.sub(r'```(.*?)```', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'`(.*?)`', r'\1', text)
    
    # Remove blockquotes
    text = re.sub(r'> ', '', text)
    
    # Remove URL formatting but keep the URL
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1 (\2)', text)
    
    return text

def convert_to_bold_text(text):
    """Convert plain text to bold text using HTML formatting.
    
    Args:
        text (str): The text to convert
        
    Returns:
        str: Text with bold formatting
    """
    if not text:
        return text
    
    # First convert to plain text to remove any existing formatting
    text = convert_to_plain_text(text)
    
    # Wrap the entire text in bold tags
    return f"<b>{text}</b>"

def apply_text_formatting(text, config):
    """Apply text formatting based on configuration.
    
    Args:
        text (str): The original text
        config (dict): The bot configuration
        
    Returns:
        str: The formatted text
    """
    if not text:
        return text
    
    # Check if plain text conversion is enabled
    if config.get("plain_text_conversion_enabled", False):
        return convert_to_plain_text(text)
    
    # Check if bold text conversion is enabled
    if config.get("bold_text_conversion_enabled", False):
        return convert_to_bold_text(text)
    
    # If no formatting is enabled, return the original text
    return text