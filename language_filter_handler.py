"""
Module for handling language filter functionality in the Telegram bot.
This module contains all functions related to filtering messages by language.
"""

import json
import logging
import re
from langdetect import detect, LangDetectException
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler

# Configure logging
logger = logging.getLogger(__name__)

# Conversation states
WAITING_LANGUAGE = 1

# Language Names in Arabic
LANGUAGE_NAMES = {
    "ar": "العربية",
    "en": "الإنجليزية",
    "fr": "الفرنسية",
    "de": "الألمانية",
    "es": "الإسبانية",
    "ru": "الروسية",
    "it": "الإيطالية",
    "ja": "اليابانية",
    "ko": "الكورية",
    "zh-cn": "الصينية",
    "tr": "التركية",
    "fa": "الفارسية",
    "ur": "الأردية",
    "hi": "الهندية"
}

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

def language_filter_menu(update, context):
    """Show the language filter menu."""
    config = load_config()
    
    # Get current status
    language_filter_enabled = config.get("language_filter_enabled", False)
    language_filter_mode = config.get("language_filter_mode", "whitelist")
    target_language = config.get("language_filter_language", "ar")
    
    # Get the Arabic name of the language
    language_name = LANGUAGE_NAMES.get(target_language, target_language)
    
    # Determine current status text
    if language_filter_enabled:
        if language_filter_mode == "whitelist":
            status = f"✅ مفعّل (قبول {language_name} فقط)"
        else:
            status = f"✅ مفعّل (حظر {language_name})"
    else:
        status = "❌ معطّل"
    
    # Create keyboard with options
    keyboard = [
        [InlineKeyboardButton(
            f"حالة الفلتر: {status}", 
            callback_data='toggle_language_filter'
        )],
        [InlineKeyboardButton(
            "🔄 تغيير وضع الفلتر", 
            callback_data='toggle_language_filter_mode'
        )],
        [InlineKeyboardButton(
            f"🌐 تغيير اللغة ({language_name})", 
            callback_data='set_language_filter_language'
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
            '🌐 *فلتر اللغة*\n\n'
            'تحكم بتوجيه الرسائل بناءً على اللغة.\n\n'
            f'الحالة الحالية: *{status}*\n\n'
            'أوضاع الفلتر:\n'
            '- القائمة البيضاء: توجيه الرسائل باللغة المحددة فقط\n'
            '- القائمة السوداء: تجاهل الرسائل باللغة المحددة\n\n'
            'ملاحظة: يعمل فلتر اللغة فقط على الرسائل النصية.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    # For direct commands
    else:
        update.message.reply_text(
            '🌐 *فلتر اللغة*\n\n'
            'تحكم بتوجيه الرسائل بناءً على اللغة.\n\n'
            f'الحالة الحالية: *{status}*\n\n'
            'أوضاع الفلتر:\n'
            '- القائمة البيضاء: توجيه الرسائل باللغة المحددة فقط\n'
            '- القائمة السوداء: تجاهل الرسائل باللغة المحددة\n\n'
            'ملاحظة: يعمل فلتر اللغة فقط على الرسائل النصية.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

def toggle_language_filter_status(update, context):
    """Toggle the language filter feature on/off."""
    query = update.callback_query
    query.answer()
    
    # Load config
    config = load_config()
    
    # Toggle setting
    current_status = config.get("language_filter_enabled", False)
    config["language_filter_enabled"] = not current_status
    
    # Save config
    success = save_config(config)
    
    if success:
        # Show the menu again with updated status
        language_filter_menu(update, context)
    else:
        # Show error
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='language_filter_menu')
            ]])
        )

def toggle_language_filter_mode(update, context):
    """Toggle between whitelist and blacklist mode for language filter."""
    query = update.callback_query
    query.answer()
    
    # Load config
    config = load_config()
    
    # Toggle mode
    current_mode = config.get("language_filter_mode", "whitelist")
    new_mode = "blacklist" if current_mode == "whitelist" else "whitelist"
    config["language_filter_mode"] = new_mode
    
    # Save config
    success = save_config(config)
    
    if success:
        # Show the menu again with updated mode
        language_filter_menu(update, context)
    else:
        # Show error
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='language_filter_menu')
            ]])
        )

def set_language_filter_language(update, context):
    """Start the process of setting the target language for the filter."""
    query = update.callback_query
    query.answer()
    
    # Create keyboard with language options
    keyboard = []
    
    # Create rows with two buttons each for popular languages
    languages = list(LANGUAGE_NAMES.items())
    for i in range(0, len(languages), 2):
        row = []
        for code, name in languages[i:i+2]:
            if i + 1 < len(languages) or code == languages[-1][0]:
                row.append(InlineKeyboardButton(
                    name, 
                    callback_data=f'set_language_{code}'
                ))
        keyboard.append(row)
    
    # Add back button
    keyboard.append([InlineKeyboardButton(
        "🔙 العودة", 
        callback_data='language_filter_menu'
    )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        '🌐 *اختيار لغة الفلتر*\n\n'
        'اختر اللغة التي تريد استخدامها في فلتر اللغة:',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

def set_language(update, context, language_code):
    """Set the language for the language filter."""
    query = update.callback_query
    query.answer()
    
    # Load config
    config = load_config()
    
    # Update language
    config["language_filter_language"] = language_code
    
    # Save config
    success = save_config(config)
    
    if success:
        # Show the menu again with updated language
        language_filter_menu(update, context)
    else:
        # Show error
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='language_filter_menu')
            ]])
        )

def detect_language(text):
    """Detect the language of a text.
    
    Args:
        text (str): The text to detect language from
        
    Returns:
        str: The detected language code or None if detection failed
    """
    try:
        # Need minimum amount of text to detect language
        if len(text) < 10:
            return None
            
        return detect(text)
    except LangDetectException:
        logger.warning(f"Failed to detect language for text: {text[:30]}...")
        return None

def should_forward_by_language(message):
    """Check if a message should be forwarded based on language.
    
    Args:
        message: A Telegram message object
        
    Returns:
        bool: True if the message should be forwarded, False otherwise
    """
    # Load config to check if this feature is enabled
    config = load_config()
    language_filter_enabled = config.get("language_filter_enabled", False)
    
    # If feature is disabled, always forward
    if not language_filter_enabled:
        return True
    
    # Only apply filter to text messages
    text = None
    if message.text:
        text = message.text
    elif message.caption:
        text = message.caption
    
    # If no text, always forward
    if not text:
        return True
    
    # Get filter settings
    filter_mode = config.get("language_filter_mode", "whitelist")
    target_language = config.get("language_filter_language", "ar")
    
    # Detect message language
    detected_language = detect_language(text)
    
    # If language detection failed, always forward
    if not detected_language:
        return True
    
    # Apply filter based on mode
    if filter_mode == "whitelist":
        # In whitelist mode, only forward messages in the target language
        return detected_language == target_language
    else:
        # In blacklist mode, don't forward messages in the target language
        return detected_language != target_language