"""
Module for handling rate limiting functionality in the Telegram bot.
This module contains all functions related to message rate limiting.
"""
import logging
import json
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler

import main

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_MESSAGES_PER_MINUTE = 1

# Message timestamps for rate limiting
message_timestamps = []

def toggle_rate_limit_status(update, context):
    """Toggle the rate limit feature on/off."""
    query = update.callback_query
    query.answer()
    
    # Load config and toggle rate limit status
    config = main.load_config()
    current_status = config.get("rate_limit_enabled", False)
    
    # Toggle the status
    new_status = not current_status
    config["rate_limit_enabled"] = new_status
    success = main.save_config(config)
    
    if success:
        status_text = "مفعّلة ✅" if new_status else "معطلة ❌"
        
        keyboard = [
            [InlineKeyboardButton("🔄 تغيير الحد: " + str(config.get("messages_per_minute", 20)) + " رسالة/دقيقة", callback_data='change_rate_limit')],
            [InlineKeyboardButton("🔄 الحالة: " + status_text, callback_data='toggle_rate_limit_status')],
            [InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            f'⏱ *إدارة حد الرسائل*\n\n'
            f'الحالة: {status_text}\n'
            f'الحد الحالي: *{config.get("messages_per_minute", 20)}* رسالة في الدقيقة\n\n'
            f'استخدم هذه الميزة لتحديد عدد الرسائل المسموح بتوجيهها في الدقيقة الواحدة لتجنب الحظر أو الإزعاج.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        query.edit_message_text(
            '❌ *خطأ*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN
        )

def rate_limit_menu(update, context):
    """Show the rate limit management menu."""
    query = update.callback_query
    query.answer()
    
    # Load current config
    config = main.load_config()
    rate_limit_enabled = config.get("rate_limit_enabled", False)
    messages_per_minute = config.get("messages_per_minute", 20)
    
    status_text = "مفعّلة ✅" if rate_limit_enabled else "معطلة ❌"
    
    keyboard = [
        [InlineKeyboardButton("🔄 تغيير الحد: " + str(messages_per_minute) + " رسالة/دقيقة", callback_data='change_rate_limit')],
        [InlineKeyboardButton("🔄 الحالة: " + status_text, callback_data='toggle_rate_limit_status')],
        [InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        f'⏱ *إدارة حد الرسائل*\n\n'
        f'الحالة: {status_text}\n'
        f'الحد الحالي: *{messages_per_minute}* رسالة في الدقيقة\n\n'
        f'استخدم هذه الميزة لتحديد عدد الرسائل المسموح بتوجيهها في الدقيقة الواحدة لتجنب الحظر أو الإزعاج.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

def change_rate_limit(update, context):
    """Start the process of changing the rate limit."""
    query = update.callback_query
    query.answer()
    
    # Load current config
    config = main.load_config()
    current_limit = config.get("messages_per_minute", 20)
    
    query.edit_message_text(
        f'⏱ *تغيير حد الرسائل في الدقيقة*\n\n'
        f'الحد الحالي: *{current_limit}* رسالة في الدقيقة\n\n'
        f'الرجاء إرسال عدد الرسائل المسموح بتوجيهها في الدقيقة الواحدة (رقم بين 1 و 60).\n\n'
        f'استخدم /cancel للإلغاء.',
        parse_mode=ParseMode.MARKDOWN
    )
    
    return WAITING_MESSAGES_PER_MINUTE

def receive_messages_per_minute(update, context):
    """Process received message rate limit."""
    try:
        limit = int(update.message.text.strip())
        
        # Validate the limit
        if limit < 1 or limit > 60:
            update.message.reply_text(
                '❌ *خطأ*\n\n'
                'الرجاء إدخال رقم بين 1 و 60.',
                parse_mode=ParseMode.MARKDOWN
            )
            return WAITING_MESSAGES_PER_MINUTE
        
        # Load config and update
        config = main.load_config()
        config["messages_per_minute"] = limit
        success = main.save_config(config)
        
        if success:
            rate_limit_enabled = config.get("rate_limit_enabled", False)
            status_text = "مفعّلة ✅" if rate_limit_enabled else "معطلة ❌"
            
            keyboard = [
                [InlineKeyboardButton("🔄 تغيير الحد: " + str(limit) + " رسالة/دقيقة", callback_data='change_rate_limit')],
                [InlineKeyboardButton("🔄 الحالة: " + status_text, callback_data='toggle_rate_limit_status')],
                [InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            update.message.reply_text(
                f'✅ *تم التعديل بنجاح*\n\n'
                f'تم تغيير حد عدد الرسائل إلى *{limit}* رسالة في الدقيقة.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            update.message.reply_text(
                '❌ *خطأ*\n\n'
                'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
                parse_mode=ParseMode.MARKDOWN
            )
        
        return ConversationHandler.END
    except ValueError:
        update.message.reply_text(
            '❌ *خطأ*\n\n'
            'الرجاء إدخال رقم صحيح.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_MESSAGES_PER_MINUTE

def should_forward_message():
    """Check if a message should be forwarded based on rate limit."""
    global message_timestamps
    
    # Load config
    config = main.load_config()
    rate_limit_enabled = config.get("rate_limit_enabled", False)
    
    # If rate limiting is disabled, always forward
    if not rate_limit_enabled:
        return True
    
    # Get the rate limit
    messages_per_minute = config.get("messages_per_minute", 20)
    
    # Current time
    current_time = datetime.now()
    
    # Clean up old timestamps (older than 1 minute)
    message_timestamps = [ts for ts in message_timestamps if (current_time - ts).total_seconds() < 60]
    
    # Check if we're under the limit
    if len(message_timestamps) < messages_per_minute:
        # Add current timestamp
        message_timestamps.append(current_time)
        return True
    else:
        # We're over the limit
        logger.info(f"Rate limit reached ({messages_per_minute} messages per minute). Skipping message.")
        return False

def get_rate_limit_status():
    """Get the current rate limit status for display."""
    config = main.load_config()
    rate_limit_enabled = config.get("rate_limit_enabled", False)
    messages_per_minute = config.get("messages_per_minute", 20)
    
    if rate_limit_enabled:
        return f"مفعّل ({messages_per_minute} رسالة/دقيقة)"
    else:
        return "معطّل"