#!/usr/bin/env python3
"""
Module for handling message updates, edits, and deletions in the Telegram bot.
This module contains all functions related to propagating message edits and deletions.
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

# Dictionary to store message mapping between source and target channels
# Format: {source_message_id: target_message_id}
message_map = {}

def store_message_mapping(source_message_id, target_message_id):
    """Store mapping between source and target message IDs."""
    try:
        # Load the current message map from file
        try:
            with open('message_map.json', 'r') as f:
                message_map = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            message_map = {}
        
        # Add new mapping
        message_map[str(source_message_id)] = target_message_id
        
        # Save updated mapping
        with open('message_map.json', 'w') as f:
            json.dump(message_map, f, indent=4)
            
        logger.info(f"Stored message mapping: {source_message_id} -> {target_message_id}")
        return True
    except Exception as e:
        logger.error(f"Error storing message mapping: {str(e)}")
        return False

def get_target_message_id(source_message_id):
    """Get target message ID for a given source message ID."""
    try:
        # Load the message map from file
        with open('message_map.json', 'r') as f:
            message_map = json.load(f)
        
        # Get target message ID
        return message_map.get(str(source_message_id))
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning("Message map file not found or invalid")
        return None
    except Exception as e:
        logger.error(f"Error getting target message ID: {str(e)}")
        return None

def toggle_edit_propagation_status(update, context):
    """Toggle the edit propagation feature on/off."""
    try:
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Toggle the edit propagation status
        current_status = config.get('edit_propagation_enabled', True)
        new_status = not current_status
        config['edit_propagation_enabled'] = new_status
        
        # Save the updated configuration
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        # Create a status message
        status_text = "تم تمكين نقل التعديلات" if new_status else "تم تعطيل نقل التعديلات"
        
        # Check if this is from a button press or command
        query = update.callback_query
        if query:
            query.answer()
            
            # Use the same keyboard as the message_updates_menu function
            keyboard = [
                [InlineKeyboardButton("نقل التعديلات: " + ("✅ مفعل" if new_status else "❌ معطل"), 
                                     callback_data="edit_toggle")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="update_menu")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Update the message
            query.edit_message_text(
                text=f"*إدارة تعديل الرسائل*\n\n{status_text}",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Command-based toggle
            update.message.reply_text(
                f"*حالة نقل التعديلات*\n\n{status_text}",
                parse_mode=ParseMode.MARKDOWN
            )
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error toggling edit propagation status: {str(e)}")
        if update.callback_query:
            update.callback_query.answer("حدث خطأ أثناء تبديل حالة نقل التعديلات")
        else:
            update.message.reply_text("حدث خطأ أثناء تبديل حالة نقل التعديلات")
        return ConversationHandler.END

def toggle_delete_propagation_status(update, context):
    """Toggle the delete propagation feature on/off."""
    try:
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Toggle the delete propagation status
        current_status = config.get('delete_propagation_enabled', True)
        new_status = not current_status
        config['delete_propagation_enabled'] = new_status
        
        # Save the updated configuration
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        # Create a status message
        status_text = "تم تمكين نقل الحذف" if new_status else "تم تعطيل نقل الحذف"
        
        # Check if this is from a button press or command
        query = update.callback_query
        if query:
            query.answer()
            
            # Use the same keyboard as the message_updates_menu function
            keyboard = [
                [InlineKeyboardButton("نقل الحذف: " + ("✅ مفعل" if new_status else "❌ معطل"), 
                                     callback_data="delete_toggle")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="update_menu")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Update the message
            query.edit_message_text(
                text=f"*إدارة حذف الرسائل*\n\n{status_text}",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Command-based toggle
            update.message.reply_text(
                f"*حالة نقل الحذف*\n\n{status_text}",
                parse_mode=ParseMode.MARKDOWN
            )
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error toggling delete propagation status: {str(e)}")
        if update.callback_query:
            update.callback_query.answer("حدث خطأ أثناء تبديل حالة نقل الحذف")
        else:
            update.message.reply_text("حدث خطأ أثناء تبديل حالة نقل الحذف")
        return ConversationHandler.END

def toggle_reply_status(update, context):
    """Toggle the reply preservation feature on/off."""
    try:
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Toggle the reply preservation status
        current_status = config.get('preserve_reply_enabled', True)
        new_status = not current_status
        config['preserve_reply_enabled'] = new_status
        
        # Save the updated configuration
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        # Create a status message
        status_text = "تم تمكين الحفاظ على الردود" if new_status else "تم تعطيل الحفاظ على الردود"
        
        # Check if this is from a button press or command
        query = update.callback_query
        if query:
            query.answer()
            
            # Use the same keyboard as the message_updates_menu function
            keyboard = [
                [InlineKeyboardButton("الحفاظ على الردود: " + ("✅ مفعل" if new_status else "❌ معطل"), 
                                     callback_data="reply_toggle")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="update_menu")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Update the message
            query.edit_message_text(
                text=f"*إدارة الردود*\n\n{status_text}",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Command-based toggle
            update.message.reply_text(
                f"*حالة الحفاظ على الردود*\n\n{status_text}",
                parse_mode=ParseMode.MARKDOWN
            )
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error toggling reply preservation status: {str(e)}")
        if update.callback_query:
            update.callback_query.answer("حدث خطأ أثناء تبديل حالة الحفاظ على الردود")
        else:
            update.message.reply_text("حدث خطأ أثناء تبديل حالة الحفاظ على الردود")
        return ConversationHandler.END

def message_updates_menu(update, context):
    """Show the message updates menu."""
    try:
        query = update.callback_query
        if query:
            query.answer()
        
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Get the current statuses
        edit_status = config.get('edit_propagation_enabled', True)
        delete_status = config.get('delete_propagation_enabled', True)
        reply_status = config.get('preserve_reply_enabled', True)
        
        # Create the keyboard for the message updates menu
        keyboard = [
            [InlineKeyboardButton("تعديل الرسائل: " + ("✅ مفعل" if edit_status else "❌ معطل"), 
                                 callback_data="edit_menu")],
            [InlineKeyboardButton("حذف الرسائل: " + ("✅ مفعل" if delete_status else "❌ معطل"), 
                                 callback_data="delete_menu")],
            [InlineKeyboardButton("الحفاظ على الردود: " + ("✅ مفعل" if reply_status else "❌ معطل"), 
                                 callback_data="reply_menu")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send or update the message
        message_text = "*إدارة تحديثات الرسائل*\n\n"
        message_text += "من هنا يمكنك التحكم في الخيارات المتعلقة بتحديث الرسائل.\n\n"
        message_text += "- تعديل الرسائل: نقل التعديلات من المصدر إلى الهدف.\n"
        message_text += "- حذف الرسائل: حذف الرسائل في الهدف عند حذفها في المصدر.\n"
        message_text += "- الحفاظ على الردود: الحفاظ على شكل الرد كما هو في المصدر.\n"
        
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
        logger.error(f"Error displaying message updates menu: {str(e)}")
        if update.callback_query:
            update.callback_query.answer("حدث خطأ أثناء عرض قائمة تحديثات الرسائل")
        else:
            update.message.reply_text("حدث خطأ أثناء عرض قائمة تحديثات الرسائل")
        return ConversationHandler.END

def edit_menu(update, context):
    """Show the edit propagation menu."""
    try:
        query = update.callback_query
        if query:
            query.answer()
        
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Get the current status
        edit_status = config.get('edit_propagation_enabled', True)
        
        # Create the keyboard for the edit propagation menu
        keyboard = [
            [InlineKeyboardButton("حالة نقل التعديلات: " + ("✅ مفعل" if edit_status else "❌ معطل"), 
                                 callback_data="edit_toggle")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="update_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send or update the message
        message_text = "*إدارة تعديل الرسائل*\n\n"
        message_text += "عند تفعيل هذه الميزة، سيتم نقل تعديلات الرسائل من المصدر إلى الهدف.\n\n"
        message_text += "هذا يعني أنه عندما يتم تعديل رسالة في قناة المصدر، سيتم تعديل نفس الرسالة في قناة الهدف تلقائياً."
        
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
        logger.error(f"Error displaying edit propagation menu: {str(e)}")
        if update.callback_query:
            update.callback_query.answer("حدث خطأ أثناء عرض قائمة نقل التعديلات")
        else:
            update.message.reply_text("حدث خطأ أثناء عرض قائمة نقل التعديلات")
        return ConversationHandler.END

def delete_menu(update, context):
    """Show the delete propagation menu."""
    try:
        query = update.callback_query
        if query:
            query.answer()
        
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Get the current status
        delete_status = config.get('delete_propagation_enabled', True)
        
        # Create the keyboard for the delete propagation menu
        keyboard = [
            [InlineKeyboardButton("حالة نقل الحذف: " + ("✅ مفعل" if delete_status else "❌ معطل"), 
                                 callback_data="delete_toggle")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="update_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send or update the message
        message_text = "*إدارة حذف الرسائل*\n\n"
        message_text += "عند تفعيل هذه الميزة، سيتم حذف الرسائل من قناة الهدف عند حذفها من قناة المصدر.\n\n"
        message_text += "هذا يعني أنه عندما يتم حذف رسالة في قناة المصدر، سيتم حذف نفس الرسالة في قناة الهدف تلقائياً."
        
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
        logger.error(f"Error displaying delete propagation menu: {str(e)}")
        if update.callback_query:
            update.callback_query.answer("حدث خطأ أثناء عرض قائمة نقل الحذف")
        else:
            update.message.reply_text("حدث خطأ أثناء عرض قائمة نقل الحذف")
        return ConversationHandler.END

def reply_menu(update, context):
    """Show the reply preservation menu."""
    try:
        query = update.callback_query
        if query:
            query.answer()
        
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Get the current status
        reply_status = config.get('preserve_reply_enabled', True)
        
        # Create the keyboard for the reply preservation menu
        keyboard = [
            [InlineKeyboardButton("حالة الحفاظ على الردود: " + ("✅ مفعل" if reply_status else "❌ معطل"), 
                                 callback_data="reply_toggle")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="update_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send or update the message
        message_text = "*إدارة الردود*\n\n"
        message_text += "عند تفعيل هذه الميزة، سيتم الحفاظ على شكل الرد كما هو في قناة المصدر.\n\n"
        message_text += "هذا يعني أنه عندما تكون الرسالة في قناة المصدر عبارة عن رد على رسالة أخرى، سيتم إرسالها كرد على نفس الرسالة في قناة الهدف."
        
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
        logger.error(f"Error displaying reply preservation menu: {str(e)}")
        if update.callback_query:
            update.callback_query.answer("حدث خطأ أثناء عرض قائمة الحفاظ على الردود")
        else:
            update.message.reply_text("حدث خطأ أثناء عرض قائمة الحفاظ على الردود")
        return ConversationHandler.END

def is_edit_propagation_enabled():
    """Check if edit propagation is enabled."""
    try:
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Get the edit propagation status
        return config.get('edit_propagation_enabled', True)
    except Exception as e:
        logger.error(f"Error checking edit propagation status: {str(e)}")
        # Default to True in case of error
        return True

def is_delete_propagation_enabled():
    """Check if delete propagation is enabled."""
    try:
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Get the delete propagation status
        return config.get('delete_propagation_enabled', True)
    except Exception as e:
        logger.error(f"Error checking delete propagation status: {str(e)}")
        # Default to True in case of error
        return True

def is_preserve_reply_enabled():
    """Check if reply preservation is enabled."""
    try:
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Get the reply preservation status
        return config.get('preserve_reply_enabled', True)
    except Exception as e:
        logger.error(f"Error checking reply preservation status: {str(e)}")
        # Default to True in case of error
        return True

def get_edit_status():
    """Get the current edit propagation status for display."""
    try:
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Get the edit propagation status
        edit_enabled = config.get('edit_propagation_enabled', True)
        
        return "✅ مفعل" if edit_enabled else "❌ معطل"
        
    except Exception as e:
        logger.error(f"Error getting edit propagation status: {str(e)}")
        return "❓ غير معروف"

def get_delete_status():
    """Get the current delete propagation status for display."""
    try:
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Get the delete propagation status
        delete_enabled = config.get('delete_propagation_enabled', True)
        
        return "✅ مفعل" if delete_enabled else "❌ معطل"
        
    except Exception as e:
        logger.error(f"Error getting delete propagation status: {str(e)}")
        return "❓ غير معروف"

def get_reply_status():
    """Get the current reply preservation status for display."""
    try:
        # Load the current configuration
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Get the reply preservation status
        reply_enabled = config.get('preserve_reply_enabled', True)
        
        return "✅ مفعل" if reply_enabled else "❌ معطل"
        
    except Exception as e:
        logger.error(f"Error getting reply preservation status: {str(e)}")
        return "❓ غير معروف"