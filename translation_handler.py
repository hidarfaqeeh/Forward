"""
Module for handling automatic translation functionality in the Telegram bot.
This module contains all functions related to translating messages before forwarding.
"""

import logging
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler
from googletrans import Translator, LANGUAGES

# Configure logging
logger = logging.getLogger(__name__)

# Create a global translator instance
translator = Translator()

# State constants for conversation handlers
WAITING_TRANSLATE_SOURCE = range(1)
WAITING_TRANSLATE_TARGET = range(1)

# List of supported languages with Arabic names
LANGUAGES_AR = {
    'auto': 'تلقائي',
    'ar': 'العربية',
    'en': 'الإنجليزية',
    'fr': 'الفرنسية',
    'de': 'الألمانية',
    'es': 'الإسبانية',
    'it': 'الإيطالية',
    'ja': 'اليابانية',
    'ko': 'الكورية',
    'ru': 'الروسية',
    'zh-cn': 'الصينية المبسطة',
    'zh-tw': 'الصينية التقليدية',
    'tr': 'التركية',
    'fa': 'الفارسية',
    'ur': 'الأردية',
    'hi': 'الهندية',
    'pt': 'البرتغالية',
    'nl': 'الهولندية',
    'pl': 'البولندية',
    'th': 'التايلاندية',
    'he': 'العبرية'
}

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

def translation_menu(update, context):
    """Show the translation settings menu."""
    config = load_config()
    
    # Initialize translation settings if not exists
    if 'auto_translate_enabled' not in config:
        config['auto_translate_enabled'] = False
        config['translate_source'] = 'auto'
        config['translate_target'] = 'ar'
        save_config(config)
    
    translation_status = "مفعّل ✅" if config.get("auto_translate_enabled", False) else "معطّل ❌"
    source_lang = config.get("translate_source", "auto")
    target_lang = config.get("translate_target", "ar")
    
    source_lang_name = LANGUAGES_AR.get(source_lang, source_lang)
    target_lang_name = LANGUAGES_AR.get(target_lang, target_lang)
    
    keyboard = [
        [InlineKeyboardButton(f"الحالة: {translation_status}", callback_data="toggle_translation")],
        [InlineKeyboardButton(f"اللغة المصدر: {source_lang_name}", callback_data="set_source_lang")],
        [InlineKeyboardButton(f"اللغة الهدف: {target_lang_name}", callback_data="set_target_lang")],
        [InlineKeyboardButton("اختبار الترجمة", callback_data="test_translation")],
        [InlineKeyboardButton("عودة ↩️", callback_data="admin_panel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "🌐 *إعدادات الترجمة التلقائية*\n\n" \
              "هذه الميزة تقوم بترجمة الرسائل تلقائياً قبل توجيهها.\n\n" \
              f"الحالة الحالية: {translation_status}\n" \
              f"اللغة المصدر: {source_lang_name}\n" \
              f"اللغة الهدف: {target_lang_name}\n\n" \
              "ملاحظة: اختيار 'تلقائي' للغة المصدر يسمح بالكشف التلقائي عن لغة الرسالة."
    
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

def toggle_translation_status(update, context):
    """Toggle the automatic translation feature on/off."""
    config = load_config()
    
    # Toggle status
    current_status = config.get("auto_translate_enabled", False)
    config["auto_translate_enabled"] = not current_status
    
    # Save config
    save_config(config)
    
    # Return to translation menu
    translation_menu(update, context)

def set_source_language(update, context):
    """Show options for setting source language."""
    update.callback_query.answer()
    
    # Create keyboard with language options
    keyboard = []
    
    # Add automatic detection option
    keyboard.append([InlineKeyboardButton("تلقائي (كشف تلقائي)", callback_data="set_source_auto")])
    
    # Add common languages
    common_langs = ['en', 'ar', 'fr', 'de', 'es', 'ru', 'zh-cn', 'ja', 'ko', 'tr']
    for i in range(0, len(common_langs), 2):
        row = []
        for lang in common_langs[i:i+2]:
            if i + 1 < len(common_langs) or lang == common_langs[-1]:
                lang_name = LANGUAGES_AR.get(lang, LANGUAGES.get(lang, lang))
                row.append(InlineKeyboardButton(f"{lang_name}", callback_data=f"set_source_{lang}"))
        keyboard.append(row)
    
    # Add back button
    keyboard.append([InlineKeyboardButton("عودة ↩️", callback_data="translation_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "🌐 *اختيار لغة المصدر*\n\n" \
              "اختر لغة النصوص المصدر التي سيتم ترجمتها:\n\n" \
              "'تلقائي' تعني أن البوت سيحاول كشف لغة الرسالة تلقائياً."
    
    update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

def set_target_language(update, context):
    """Show options for setting target language."""
    update.callback_query.answer()
    
    # Create keyboard with language options
    keyboard = []
    
    # Add common languages
    common_langs = ['en', 'ar', 'fr', 'de', 'es', 'ru', 'zh-cn', 'ja', 'ko', 'tr']
    for i in range(0, len(common_langs), 2):
        row = []
        for lang in common_langs[i:i+2]:
            if i + 1 < len(common_langs) or lang == common_langs[-1]:
                lang_name = LANGUAGES_AR.get(lang, LANGUAGES.get(lang, lang))
                row.append(InlineKeyboardButton(f"{lang_name}", callback_data=f"set_target_{lang}"))
        keyboard.append(row)
    
    # Add back button
    keyboard.append([InlineKeyboardButton("عودة ↩️", callback_data="translation_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "🌐 *اختيار لغة الهدف*\n\n" \
              "اختر اللغة التي تريد الترجمة إليها."
    
    update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

def set_source_callback(update, context):
    """Handle callback for setting source language."""
    query = update.callback_query
    query.answer()
    
    # Extract language code from callback data
    lang_code = query.data.replace("set_source_", "")
    
    # Load config and update source language
    config = load_config()
    old_lang = config.get("translate_source", "auto")
    config["translate_source"] = lang_code
    
    # Save config
    success = save_config(config)
    
    if success:
        old_lang_name = LANGUAGES_AR.get(old_lang, old_lang)
        new_lang_name = LANGUAGES_AR.get(lang_code, lang_code)
        
        message = f'✅ *تم بنجاح!*\n\n' \
                 f'تم تغيير لغة المصدر من {old_lang_name} إلى {new_lang_name}.'
        
        # Show success message and return to translation menu
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Return to translation menu
        translation_menu(update, context)
    else:
        message = '❌ *خطأ!*\n\n' \
                 'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.'
                 
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )

def set_target_callback(update, context):
    """Handle callback for setting target language."""
    query = update.callback_query
    query.answer()
    
    # Extract language code from callback data
    lang_code = query.data.replace("set_target_", "")
    
    # Load config and update target language
    config = load_config()
    old_lang = config.get("translate_target", "ar")
    config["translate_target"] = lang_code
    
    # Save config
    success = save_config(config)
    
    if success:
        old_lang_name = LANGUAGES_AR.get(old_lang, old_lang)
        new_lang_name = LANGUAGES_AR.get(lang_code, lang_code)
        
        message = f'✅ *تم بنجاح!*\n\n' \
                 f'تم تغيير لغة الهدف من {old_lang_name} إلى {new_lang_name}.'
        
        # Show success message and return to translation menu
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Return to translation menu
        translation_menu(update, context)
    else:
        message = '❌ *خطأ!*\n\n' \
                 'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.'
                 
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )

def test_translation(update, context):
    """Show interface for testing translation."""
    update.callback_query.answer()
    
    config = load_config()
    source_lang = config.get("translate_source", "auto")
    target_lang = config.get("translate_target", "ar")
    
    source_lang_name = LANGUAGES_AR.get(source_lang, source_lang)
    target_lang_name = LANGUAGES_AR.get(target_lang, target_lang)
    
    keyboard = [[InlineKeyboardButton("العودة إلى إعدادات الترجمة", callback_data="translation_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Test text in English
    test_text = "Hello, this is a test of the automatic translation feature."
    
    try:
        # Translate the test text
        if source_lang == 'auto':
            translated = translator.translate(test_text, dest=target_lang)
        else:
            translated = translator.translate(test_text, src=source_lang, dest=target_lang)
        
        message = "🌐 *اختبار الترجمة*\n\n" \
                 f"النص الأصلي:\n" \
                 f"`{test_text}`\n\n" \
                 f"اللغة المصدر: {source_lang_name}\n" \
                 f"اللغة الهدف: {target_lang_name}\n\n" \
                 f"النص المترجم:\n" \
                 f"`{translated.text}`\n\n" \
                 f"لتغيير إعدادات الترجمة، عد إلى قائمة الترجمة."
    except Exception as e:
        message = "❌ *خطأ في الترجمة*\n\n" \
                 f"حدث خطأ أثناء ترجمة النص: {str(e)}\n\n" \
                 f"تأكد من صحة إعدادات الترجمة واتصال الإنترنت."
    
    update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

def translate_text(text, config=None):
    """Translate text according to configuration."""
    if not text:
        return text
        
    if not config:
        config = load_config()
    
    # Check if translation is enabled
    if not config.get("auto_translate_enabled", False):
        return text
    
    source_lang = config.get("translate_source", "auto")
    target_lang = config.get("translate_target", "ar")
    
    try:
        if source_lang == 'auto':
            translated = translator.translate(text, dest=target_lang)
        else:
            translated = translator.translate(text, src=source_lang, dest=target_lang)
            
        logger.info(f"Translated text from {translated.src} to {target_lang}")
        return translated.text
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return text  # Return original text if translation fails