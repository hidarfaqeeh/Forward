"""
Module for handling time delay functionality in the Telegram bot.
This module contains all functions related to adding time delay between forwarded messages.
"""

import logging
import json
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler

# Configure logging
logger = logging.getLogger(__name__)

# State constants for conversation handlers
WAITING_DELAY_SECONDS = range(1)

# Variable to store the timestamp of the last forwarded message
last_forwarded_time = 0

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

def delay_menu(update, context):
    """Show the delay settings menu."""
    config = load_config()
    
    # Initialize delay settings if not exists
    if 'delay_enabled' not in config:
        config['delay_enabled'] = False
        config['delay_seconds'] = 5
        save_config(config)
    
    delay_status = "مفعّل ✅" if config.get("delay_enabled", False) else "معطّل ❌"
    delay_seconds = config.get("delay_seconds", 5)
    
    keyboard = [
        [InlineKeyboardButton(f"الحالة: {delay_status}", callback_data="toggle_delay")],
        [InlineKeyboardButton(f"مدة التأخير: {delay_seconds} ثانية", callback_data="change_delay")],
        [InlineKeyboardButton("عودة ↩️", callback_data="admin_panel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "⏱ *إعدادات التأخير*\n\n" \
              "هذه الميزة تضيف تأخير زمني بين الرسائل المعاد توجيهها.\n\n" \
              f"الحالة الحالية: {delay_status}\n" \
              f"مدة التأخير: {delay_seconds} ثانية\n\n" \
              "يساعد التأخير في تجنب قيود التيليجرام عند إرسال رسائل متعددة بسرعة."
    
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

def toggle_delay_status(update, context):
    """Toggle the delay feature on/off."""
    config = load_config()
    
    # Toggle status
    current_status = config.get("delay_enabled", False)
    config["delay_enabled"] = not current_status
    
    # Save config
    save_config(config)
    
    # Return to delay menu
    delay_menu(update, context)

def change_delay(update, context):
    """Start the process of changing the delay time."""
    update.callback_query.answer()
    
    message = "⏱ *تغيير مدة التأخير*\n\n" \
              "الرجاء إرسال عدد الثواني للتأخير بين الرسائل.\n" \
              "مثال: `5` لتأخير 5 ثوانٍ بين كل رسالة.\n\n" \
              "استخدم /cancel للإلغاء."
    
    update.callback_query.edit_message_text(
        text=message,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return WAITING_DELAY_SECONDS

def receive_delay_seconds(update, context):
    """Process received delay seconds."""
    try:
        delay_seconds = int(update.message.text.strip())
        
        if update.message.text.strip() == '/cancel':
            update.message.reply_text(
                '🚫 *تم الإلغاء*\n\n'
                'تم إلغاء العملية الحالية.',
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END
        
        if delay_seconds < 0:
            update.message.reply_text(
                '❌ *خطأ!*\n\n'
                'يجب أن تكون مدة التأخير رقمًا موجبًا.\n'
                'الرجاء المحاولة مرة أخرى أو استخدم /cancel للإلغاء.',
                parse_mode=ParseMode.MARKDOWN
            )
            return WAITING_DELAY_SECONDS
        
        # Load config and update delay seconds
        config = load_config()
        old_delay = config.get("delay_seconds", 5)
        config["delay_seconds"] = delay_seconds
        
        # Save config
        success = save_config(config)
        
        if success:
            # Show success message with keyboard to return to delay menu
            keyboard = [[InlineKeyboardButton("العودة إلى إعدادات التأخير", callback_data="delay_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            update.message.reply_text(
                f'✅ *تم بنجاح!*\n\n'
                f'تم تغيير مدة التأخير من {old_delay} ثانية إلى {delay_seconds} ثانية.\n\n'
                f'سيتم الانتظار {delay_seconds} ثانية بين كل رسالة يتم توجيهها.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            update.message.reply_text(
                '❌ *خطأ!*\n\n'
                'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
                parse_mode=ParseMode.MARKDOWN
            )
            return WAITING_DELAY_SECONDS
            
    except ValueError:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'يجب إدخال رقم صحيح فقط.\n'
            'الرجاء المحاولة مرة أخرى أو استخدم /cancel للإلغاء.',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_DELAY_SECONDS
    
    return ConversationHandler.END

def should_delay_message():
    """Check if there should be a delay before forwarding the current message."""
    global last_forwarded_time
    
    config = load_config()
    delay_enabled = config.get("delay_enabled", False)
    
    # If delay is disabled, always forward immediately
    if not delay_enabled:
        # Update last forwarded time without delay
        last_forwarded_time = time.time()
        return False
    
    delay_seconds = config.get("delay_seconds", 5)
    current_time = time.time()
    time_since_last_message = current_time - last_forwarded_time
    
    # If enough time has passed since the last message, no need for delay
    if time_since_last_message >= delay_seconds:
        last_forwarded_time = current_time
        return False
    
    # Calculate how much more time to wait
    wait_time = delay_seconds - time_since_last_message
    logger.info(f"Delaying message for {wait_time:.2f} seconds")
    
    # Sleep for the required delay
    time.sleep(wait_time)
    
    # Update the last forwarded time
    last_forwarded_time = time.time()
    
    return True