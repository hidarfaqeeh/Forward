"""
Module for handling working hours functionality in the Telegram bot.
This module contains all functions related to setting active and inactive hours for the bot.
"""

import json
import logging
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler

# Configure logging
logger = logging.getLogger(__name__)

# Conversation states
WAITING_START_HOUR = 1
WAITING_END_HOUR = 2

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

def working_hours_menu(update, context):
    """Show the working hours menu."""
    config = load_config()
    
    # Get current status
    working_hours_enabled = config.get("working_hours_enabled", False)
    status = "✅ مفعّل" if working_hours_enabled else "❌ معطّل"
    
    # Get current working hours
    start_hour = config.get("working_hours_start", 9)
    end_hour = config.get("working_hours_end", 21)
    
    # Create keyboard with options
    keyboard = [
        [InlineKeyboardButton(
            f"حالة ساعات العمل: {status}", 
            callback_data='toggle_working_hours'
        )],
        [InlineKeyboardButton(
            f"⏰ تغيير ساعة البدء ({start_hour}:00)", 
            callback_data='set_start_hour'
        )],
        [InlineKeyboardButton(
            f"⏰ تغيير ساعة الانتهاء ({end_hour}:00)", 
            callback_data='set_end_hour'
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
            '⏰ *ساعات العمل*\n\n'
            'تحكم بأوقات عمل البوت خلال اليوم.\n\n'
            f'الحالة الحالية: *{status}*\n'
            f'ساعات العمل: من *{start_hour}:00* حتى *{end_hour}:00*\n\n'
            'عند تفعيل هذه الميزة، سيعمل البوت فقط خلال ساعات العمل المحددة.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    # For direct commands
    else:
        update.message.reply_text(
            '⏰ *ساعات العمل*\n\n'
            'تحكم بأوقات عمل البوت خلال اليوم.\n\n'
            f'الحالة الحالية: *{status}*\n'
            f'ساعات العمل: من *{start_hour}:00* حتى *{end_hour}:00*\n\n'
            'عند تفعيل هذه الميزة، سيعمل البوت فقط خلال ساعات العمل المحددة.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

def toggle_working_hours_status(update, context):
    """Toggle the working hours feature on/off."""
    query = update.callback_query
    query.answer()
    
    # Load config
    config = load_config()
    
    # Toggle setting
    current_status = config.get("working_hours_enabled", False)
    config["working_hours_enabled"] = not current_status
    
    # Save config
    success = save_config(config)
    
    if success:
        # Show the menu again with updated status
        working_hours_menu(update, context)
    else:
        # Show error
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='working_hours_menu')
            ]])
        )

def set_start_hour(update, context):
    """Start the process of setting the start working hour."""
    query = update.callback_query
    query.answer()
    
    # Create keyboard with hour options
    keyboard = []
    row = []
    
    # Add buttons for hours 0-23
    for hour in range(24):
        # Add 4 buttons per row
        row.append(InlineKeyboardButton(f"{hour}:00", callback_data=f'start_hour_{hour}'))
        
        if len(row) == 4 or hour == 23:
            keyboard.append(row)
            row = []
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton("🔙 العودة", callback_data='working_hours_menu')
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        '⏰ *تعيين ساعة بدء العمل*\n\n'
        'اختر الساعة التي يبدأ عندها البوت بالعمل:',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

def set_end_hour(update, context):
    """Start the process of setting the end working hour."""
    query = update.callback_query
    query.answer()
    
    # Create keyboard with hour options
    keyboard = []
    row = []
    
    # Add buttons for hours 0-23
    for hour in range(24):
        # Add 4 buttons per row
        row.append(InlineKeyboardButton(f"{hour}:00", callback_data=f'end_hour_{hour}'))
        
        if len(row) == 4 or hour == 23:
            keyboard.append(row)
            row = []
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton("🔙 العودة", callback_data='working_hours_menu')
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        '⏰ *تعيين ساعة انتهاء العمل*\n\n'
        'اختر الساعة التي يتوقف عندها البوت عن العمل:',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

def set_start_hour_callback(update, context):
    """Process the selected start hour."""
    query = update.callback_query
    query.answer()
    
    # Get selected hour from callback data
    hour = int(query.data.split('_')[-1])
    
    # Load config
    config = load_config()
    
    # Update start hour
    config["working_hours_start"] = hour
    
    # Save config
    success = save_config(config)
    
    if success:
        # Show the menu again with updated hours
        working_hours_menu(update, context)
    else:
        # Show error
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='working_hours_menu')
            ]])
        )

def set_end_hour_callback(update, context):
    """Process the selected end hour."""
    query = update.callback_query
    query.answer()
    
    # Get selected hour from callback data
    hour = int(query.data.split('_')[-1])
    
    # Load config
    config = load_config()
    
    # Update end hour
    config["working_hours_end"] = hour
    
    # Save config
    success = save_config(config)
    
    if success:
        # Show the menu again with updated hours
        working_hours_menu(update, context)
    else:
        # Show error
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='working_hours_menu')
            ]])
        )

def is_within_working_hours():
    """Check if current time is within working hours.
    
    Returns:
        bool: True if current time is within working hours, False otherwise
    """
    # Load config
    config = load_config()
    
    # Check if feature is enabled
    if not config.get("working_hours_enabled", False):
        return True  # If feature is disabled, always return True
    
    # Get working hours
    start_hour = config.get("working_hours_start", 9)
    end_hour = config.get("working_hours_end", 21)
    
    # Get current hour
    current_hour = datetime.now().hour
    
    # Handle cases where end_hour is before start_hour (overnight)
    if start_hour <= end_hour:
        # Normal case (e.g., 9:00 to 17:00)
        return start_hour <= current_hour < end_hour
    else:
        # Overnight case (e.g., 22:00 to 6:00)
        return current_hour >= start_hour or current_hour < end_hour