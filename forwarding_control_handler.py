#!/usr/bin/env python3
"""
Module for handling forwarding control functionality in the Telegram bot.
This module contains all functions related to enabling/disabling message forwarding.
"""
import logging
import json
import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def toggle_forwarding_status(update, context):
    """Toggle the forwarding feature on/off."""
    try:
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Toggle the forwarding status
        current_status = config.get('forwarding_enabled', True)
        new_status = not current_status
        config['forwarding_enabled'] = new_status
        
        # Save the updated configuration
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        # Create a status message
        status_text = "تم تمكين توجيه الرسائل" if new_status else "تم تعطيل توجيه الرسائل"
        
        # Check if this is from a button press or command
        query = update.callback_query
        if query:
            query.answer()
            
            # Use the same keyboard as the forwarding_control_menu function
            keyboard = [
                [InlineKeyboardButton("حالة التوجيه: " + ("✅ مفعل" if new_status else "❌ معطل"), 
                                     callback_data="forwarding_toggle")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Update the message
            query.edit_message_text(
                text=f"*إدارة توجيه الرسائل*\n\n{status_text}",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Command-based toggle
            update.message.reply_text(
                f"*حالة التوجيه*\n\n{status_text}",
                parse_mode=ParseMode.MARKDOWN
            )
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error toggling forwarding status: {str(e)}")
        if update.callback_query:
            update.callback_query.answer("حدث خطأ أثناء تبديل حالة التوجيه")
        else:
            update.message.reply_text("حدث خطأ أثناء تبديل حالة التوجيه")
        return ConversationHandler.END

def forwarding_control_menu(update, context):
    """Show the forwarding control menu."""
    try:
        query = update.callback_query
        if query:
            query.answer()
        
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Get the current forwarding status
        forwarding_status = config.get('forwarding_enabled', True)
        
        # Create the keyboard for the forwarding control menu
        keyboard = [
            [InlineKeyboardButton("حالة التوجيه: " + ("✅ مفعل" if forwarding_status else "❌ معطل"), 
                                 callback_data="forwarding_toggle")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send or update the message
        message_text = "*إدارة توجيه الرسائل*\n\n"
        message_text += "من هنا يمكنك التحكم في حالة توجيه الرسائل (تشغيل/إيقاف).\n\n"
        message_text += "عند إيقاف التوجيه، لن يتم توجيه أي رسائل جديدة حتى يتم إعادة تفعيله."
        
        if query:
            query.edit_message_text(
                text=message_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            update.message.reply_text(
                text=message_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error displaying forwarding control menu: {str(e)}")
        if update.callback_query:
            update.callback_query.answer("حدث خطأ أثناء عرض قائمة التحكم في التوجيه")
        else:
            update.message.reply_text("حدث خطأ أثناء عرض قائمة التحكم في التوجيه")
        return ConversationHandler.END

def should_forward_message(message_date):
    """Check if a message should be forwarded based on forwarding status and message date."""
    try:
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Check if forwarding is enabled
        forwarding_enabled = config.get('forwarding_enabled', True)
        
        if not forwarding_enabled:
            return False
        
        # If forwarding is enabled, the message should be forwarded
        return True
        
    except Exception as e:
        logger.error(f"Error checking if message should be forwarded: {str(e)}")
        # Default to True in case of error to avoid losing messages
        return True

def get_forwarding_status():
    """Get the current forwarding status for display."""
    try:
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Get the forwarding status
        forwarding_enabled = config.get('forwarding_enabled', True)
        
        return "✅ مفعل" if forwarding_enabled else "❌ معطل"
        
    except Exception as e:
        logger.error(f"Error getting forwarding status: {str(e)}")
        return "❓ غير معروف"