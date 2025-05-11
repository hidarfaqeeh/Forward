"""
Module for handling duplicate message filter functionality in the Telegram bot.
This module contains all functions related to preventing duplicate messages.
"""

import json
import logging
import hashlib
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext

# Configure logging
logger = logging.getLogger(__name__)

# Store message hashes for checking duplicates (in-memory for simplicity)
# In a production environment, this should be a persistent storage
message_hashes = set()
# Maximum number of messages to remember (to prevent unlimited memory growth)
MAX_MESSAGE_MEMORY = 1000

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

def duplicate_filter_menu(update, context):
    """Show the duplicate messages filter menu."""
    config = load_config()
    
    # Get current status
    duplicate_filter_enabled = config.get("duplicate_filter_enabled", False)
    status = "✅ مفعّل" if duplicate_filter_enabled else "❌ معطّل"
    
    # Create keyboard with options
    keyboard = [
        [InlineKeyboardButton(
            f"حالة الفلتر: {status}", 
            callback_data='toggle_duplicate_filter'
        )],
        [InlineKeyboardButton(
            "🗑️ مسح ذاكرة الرسائل", 
            callback_data='clear_message_memory'
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
            '♻️ *فلتر الرسائل المكررة*\n\n'
            'تحكم بتوجيه الرسائل المكررة (تم نشرها سابقاً).\n\n'
            f'الحالة الحالية: *{status}*\n\n'
            'عند تفعيل هذه الميزة، سيتجاهل البوت أي رسالة تم نشرها مسبقاً لتجنب التكرار.\n\n'
            f'عدد الرسائل المخزنة في الذاكرة: {len(message_hashes)}/{MAX_MESSAGE_MEMORY}',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    # For direct commands
    else:
        update.message.reply_text(
            '♻️ *فلتر الرسائل المكررة*\n\n'
            'تحكم بتوجيه الرسائل المكررة (تم نشرها سابقاً).\n\n'
            f'الحالة الحالية: *{status}*\n\n'
            'عند تفعيل هذه الميزة، سيتجاهل البوت أي رسالة تم نشرها مسبقاً لتجنب التكرار.\n\n'
            f'عدد الرسائل المخزنة في الذاكرة: {len(message_hashes)}/{MAX_MESSAGE_MEMORY}',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

def toggle_duplicate_filter_status(update, context):
    """Toggle the duplicate messages filter feature on/off."""
    query = update.callback_query
    query.answer()
    
    # Load config
    config = load_config()
    
    # Toggle setting
    current_status = config.get("duplicate_filter_enabled", False)
    config["duplicate_filter_enabled"] = not current_status
    
    # Save config
    success = save_config(config)
    
    if success:
        # Show the menu again with updated status
        duplicate_filter_menu(update, context)
    else:
        # Show error
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='duplicate_filter_menu')
            ]])
        )

def clear_message_memory(update, context):
    """Clear the stored message hashes."""
    query = update.callback_query
    query.answer()
    
    # Clear the set of message hashes
    global message_hashes
    message_hashes.clear()
    
    # Show success message
    query.edit_message_text(
        '✅ *تم بنجاح!*\n\n'
        'تم مسح ذاكرة الرسائل المخزنة. يمكن الآن استقبال الرسائل السابقة من جديد.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 العودة", callback_data='duplicate_filter_menu')
        ]])
    )

def get_message_hash(message):
    """Generate a hash for the message content to identify duplicates.
    
    Args:
        message: A Telegram message object
        
    Returns:
        str: A hash string representing the message content
    """
    # Create a string with the important content of the message
    content = ""
    
    # Add text or caption if available
    if message.text:
        content += message.text
    elif message.caption:
        content += message.caption
    
    # For media messages, add file unique identifier
    if message.photo and message.photo:
        content += message.photo[-1].file_unique_id  # Use largest photo
    if message.video:
        content += message.video.file_unique_id
    if message.audio:
        content += message.audio.file_unique_id
    if message.document:
        content += message.document.file_unique_id
    if message.animation:
        content += message.animation.file_unique_id
    if message.voice:
        content += message.voice.file_unique_id
    if message.video_note:
        content += message.video_note.file_unique_id
    if message.sticker:
        content += message.sticker.file_unique_id
    
    # Add poll question if it's a poll
    if message.poll:
        content += message.poll.question
        for option in message.poll.options:
            content += option.text
    
    # Generate a hash of the content
    if content:
        m = hashlib.md5()
        m.update(content.encode('utf-8'))
        return m.hexdigest()
    
    return None

def should_forward_duplicate_message(message):
    """Check if a message should be forwarded based on duplicate status.
    
    Args:
        message: A Telegram message object
        
    Returns:
        bool: True if the message should be forwarded, False otherwise
    """
    global message_hashes
    
    # Load config to check if this feature is enabled
    config = load_config()
    duplicate_filter_enabled = config.get("duplicate_filter_enabled", False)
    
    # If feature is disabled, always forward
    if not duplicate_filter_enabled:
        return True
    
    # Generate hash for the message
    message_hash = get_message_hash(message)
    
    # If couldn't generate hash, forward the message
    if not message_hash:
        return True
    
    # Check if this message is a duplicate
    if message_hash in message_hashes:
        logger.info(f"Duplicate message detected, hash: {message_hash}")
        return False
    
    # If not a duplicate, add to memory and forward
    message_hashes.add(message_hash)
    
    # If memory is full, remove oldest entries (simplified approach)
    if len(message_hashes) > MAX_MESSAGE_MEMORY:
        # Convert to list, sort by time (this is simplified and not optimal in production)
        # In production, use a proper time-based cache mechanism
        message_hashes = set(list(message_hashes)[-MAX_MESSAGE_MEMORY:])
    
    return True