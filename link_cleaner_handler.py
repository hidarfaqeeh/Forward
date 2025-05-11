"""
Module for handling link cleaning functionality in the Telegram bot.
This module contains all functions related to removing links and usernames from messages.
"""

import logging
import json
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

# Configure logging
logger = logging.getLogger(__name__)

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

def contains_links(text):
    """Check if text contains links or usernames.
    
    Args:
        text (str): The text to check
        
    Returns:
        bool: True if the text contains links or usernames, False otherwise
    """
    if not text:
        return False
        
    # Check for Telegram URLs (t.me, telegram.me, telegram.dog)
    if re.search(r'https?://(?:t(?:elegram)?\.(?:me|dog)|telegram\.me)/[^\s]+', text):
        return True
    
    # Check for other URLs
    if re.search(r'https?://[^\s]+', text):
        return True
    
    # Check for markdown URLs [text](url)
    if re.search(r'\[([^\]]+)\]\(https?://[^\)]+\)', text):
        return True
    
    # Check for HTML links <a href="url">text</a>
    if re.search(r'<a\s+(?:[^>]*?\s+)?href=(["\'])(?:https?://)?(?:[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|])\1[^>]*>(.*?)</a>', text):
        return True
    
    # Check for usernames (@username)
    if re.search(r'@([A-Za-z0-9_]+)', text):
        return True
    
    # Check for channel names
    if re.search(r't\.me/([A-Za-z0-9_]+)', text):
        return True
    
    # Check for any remaining URLs with parameters
    if re.search(r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)', text):
        return True
    
    return False

def clean_links(text):
    """Remove all links and usernames from the text."""
    if not text:
        return text
        
    # Clean Telegram URLs (t.me, telegram.me, telegram.dog)
    text = re.sub(r'https?://(?:t(?:elegram)?\.(?:me|dog)|telegram\.me)/[^\s]+', '', text)
    
    # Clean other URLs
    text = re.sub(r'https?://[^\s]+', '', text)
    
    # Clean markdown URLs [text](url)
    text = re.sub(r'\[([^\]]+)\]\(https?://[^\)]+\)', r'\1', text)
    
    # Clean HTML links <a href="url">text</a>
    text = re.sub(r'<a\s+(?:[^>]*?\s+)?href=(["\'])(?:https?://)?(?:[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|])\1[^>]*>(.*?)</a>', r'\2', text)
    
    # Clean usernames (@username)
    text = re.sub(r'@([A-Za-z0-9_]+)', '', text)
    
    # Clean channel names
    text = re.sub(r't\.me/([A-Za-z0-9_]+)', '', text)
    
    # Remove any remaining URLs with parameters
    text = re.sub(r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)', '', text)
    
    # Remove doubled whitespace from cleanup
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def link_cleaner_menu(update, context):
    """Show the link cleaner menu."""
    config = load_config()
    
    # Initialize link_cleaner_enabled if not exists
    if 'link_cleaner_enabled' not in config:
        config['link_cleaner_enabled'] = False
        save_config(config)
    
    status = "تفعيل ✅" if config.get("link_cleaner_enabled", False) else "تعطيل ❌"
    
    keyboard = [
        [InlineKeyboardButton(f"الحالة: {status}", callback_data="toggle_link_cleaner")],
        [InlineKeyboardButton("⚙️ اختبار تنظيف الروابط", callback_data="test_link_cleaner")],
        [InlineKeyboardButton("عودة ↩️", callback_data="admin_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "🧹 *إعدادات تنظيف الروابط*\n\n" \
              "هذه الميزة تقوم بإزالة الروابط ومعرفات المستخدمين من الرسائل قبل توجيهها.\n\n" \
              "ستتم إزالة:\n" \
              "- جميع الروابط (URLs)\n" \
              "- روابط تيليجرام (t.me)\n" \
              "- معرفات المستخدمين (@username)\n" \
              "- الروابط المخفية في HTML و Markdown"
    
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

def toggle_link_cleaner_status(update, context):
    """Toggle the link cleaner feature on/off."""
    config = load_config()
    
    # Toggle status
    current_status = config.get("link_cleaner_enabled", False)
    config["link_cleaner_enabled"] = not current_status
    
    # Save config
    save_config(config)
    
    # Return to link cleaner menu
    link_cleaner_menu(update, context)
    
def toggle_link_filter_status(update, context):
    """Toggle the link filter feature on/off."""
    config = load_config()
    
    # Toggle status
    current_status = config.get("link_filter_enabled", False)
    config["link_filter_enabled"] = not current_status
    
    # Save config
    save_config(config)
    
    # Return to link cleaner menu
    link_filter_menu(update, context)
    
def link_filter_menu(update, context):
    """Show the link filter menu."""
    config = load_config()
    
    # Initialize link_filter_enabled if not exists
    if 'link_filter_enabled' not in config:
        config['link_filter_enabled'] = False
        save_config(config)
    
    status = "✅ مفعّل" if config.get("link_filter_enabled", False) else "❌ معطّل"
    
    keyboard = [
        [InlineKeyboardButton(
            f"حالة الفلتر: {status}", 
            callback_data='toggle_link_filter'
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
            '🔗 *فلتر الروابط*\n\n'
            'تحكم بتوجيه الرسائل التي تحتوي على روابط أو معرفات مستخدمين.\n\n'
            f'الحالة الحالية: *{status}*\n\n'
            'عند تفعيل هذه الميزة، سيتجاهل البوت أي رسالة تحتوي على روابط أو معرفات مستخدمين.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    # For direct commands
    else:
        update.message.reply_text(
            '🔗 *فلتر الروابط*\n\n'
            'تحكم بتوجيه الرسائل التي تحتوي على روابط أو معرفات مستخدمين.\n\n'
            f'الحالة الحالية: *{status}*\n\n'
            'عند تفعيل هذه الميزة، سيتجاهل البوت أي رسالة تحتوي على روابط أو معرفات مستخدمين.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

def should_forward_message_with_links(message):
    """Check if a message with links should be forwarded.
    
    Args:
        message: A Telegram message object
        
    Returns:
        bool: True if the message should be forwarded, False otherwise
    """
    # Load config to check if this feature is enabled
    config = load_config()
    link_filter_enabled = config.get("link_filter_enabled", False)
    
    # If feature is disabled, always forward
    if not link_filter_enabled:
        return True
    
    # Check message text and caption for links
    text = None
    if message.text:
        text = message.text
    elif message.caption:
        text = message.caption
    
    # If no text, forward the message
    if not text:
        return True
    
    # If text contains links and filter is enabled, don't forward
    if contains_links(text):
        return False
    
    # Otherwise, forward the message
    return True

def test_link_cleaner(update, context):
    """Show a test interface for the link cleaner."""
    update.callback_query.answer()
    
    keyboard = [
        [InlineKeyboardButton("العودة إلى إعدادات تنظيف الروابط", callback_data="link_cleaner_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    test_message = "مرحبًا! يرجى زيارة موقعنا على https://example.com أو التواصل معنا عبر @username أو t.me/channel.\n" \
                  "يمكنك أيضًا [النقر هنا](https://hidden.link) أو <a href='https://html.link'>هنا</a> للمزيد من المعلومات."
    
    cleaned_message = clean_links(test_message)
    
    message = "🧪 *اختبار تنظيف الروابط*\n\n" \
              "الرسالة الأصلية:\n" \
              f"```\n{test_message}\n```\n\n" \
              "الرسالة بعد التنظيف:\n" \
              f"```\n{cleaned_message}\n```\n\n" \
              "يمكنك تجربة الميزة بإرسال نص يحتوي على روابط وسيقوم البوت بتنظيفه وإرجاعه إليك."
    
    update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )