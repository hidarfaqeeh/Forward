"""
Module for handling message customization features in the Telegram bot.
This module contains all functions related to adding headers, footers, and inline buttons to messages.
"""

import logging
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

# Configure logging
logger = logging.getLogger(__name__)

# Conversation states
WAITING_HEADER_TEXT = 1
WAITING_FOOTER_TEXT = 2
WAITING_BUTTON_TEXT = 3
WAITING_BUTTON_URL = 4

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

def customize_message_text(message_text, config):
    """Add header and footer to message text"""
    if not message_text:
        message_text = ""
    
    # Add header if enabled
    if config.get("header_enabled", False) and config.get("header_text"):
        header = config.get("header_text")
        message_text = f"{header}\n\n{message_text}"
    
    # Add footer if enabled
    if config.get("footer_enabled", False) and config.get("footer_text"):
        footer = config.get("footer_text")
        message_text = f"{message_text}\n\n{footer}"
    
    return message_text

def create_inline_button(config):
    """Create inline button if enabled"""
    if config.get("inline_button_enabled", False) and config.get("inline_button_text") and config.get("inline_button_url"):
        button_text = config.get("inline_button_text")
        button_url = config.get("inline_button_url")
        keyboard = [[InlineKeyboardButton(button_text, url=button_url)]]
        return InlineKeyboardMarkup(keyboard)
    return None

def message_customization_menu(update, context):
    """Show the message customization menu."""
    config = load_config()
    
    header_status = "تفعيل ✅" if config.get("header_enabled", False) else "تعطيل ❌"
    footer_status = "تفعيل ✅" if config.get("footer_enabled", False) else "تعطيل ❌"
    button_status = "تفعيل ✅" if config.get("inline_button_enabled", False) else "تعطيل ❌"
    
    keyboard = [
        [InlineKeyboardButton(f"رأس الرسالة: {header_status}", callback_data="header_menu")],
        [InlineKeyboardButton(f"تذييل الرسالة: {footer_status}", callback_data="footer_menu")],
        [InlineKeyboardButton(f"زر شفاف: {button_status}", callback_data="button_menu")],
        [InlineKeyboardButton("عودة ↩️", callback_data="admin_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "⚙️ *إعدادات تخصيص الرسائل*\n\n" \
              "من هنا يمكنك تخصيص الرسائل المعاد توجيهها بإضافة نص في البداية أو النهاية أو أزرار شفافة."
    
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

def header_menu(update, context):
    """Show the header settings menu."""
    config = load_config()
    
    header_status = "تفعيل ✅" if config.get("header_enabled", False) else "تعطيل ❌"
    current_header = config.get("header_text", "")
    
    keyboard = [
        [InlineKeyboardButton(f"الحالة: {header_status}", callback_data="toggle_header")],
        [InlineKeyboardButton("تعديل نص الرأس", callback_data="set_header_text")],
        [InlineKeyboardButton("عودة ↩️", callback_data="customization_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "⚙️ *إعدادات رأس الرسالة*\n\n" \
              "من هنا يمكنك تفعيل/تعطيل وتعديل نص يظهر في بداية كل رسالة.\n\n"
    
    if current_header:
        message += f"النص الحالي:\n`{current_header}`"
    else:
        message += "لم يتم تعيين نص بعد."
    
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return

def footer_menu(update, context):
    """Show the footer settings menu."""
    config = load_config()
    
    footer_status = "تفعيل ✅" if config.get("footer_enabled", False) else "تعطيل ❌"
    current_footer = config.get("footer_text", "")
    
    keyboard = [
        [InlineKeyboardButton(f"الحالة: {footer_status}", callback_data="toggle_footer")],
        [InlineKeyboardButton("تعديل نص التذييل", callback_data="set_footer_text")],
        [InlineKeyboardButton("عودة ↩️", callback_data="customization_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "⚙️ *إعدادات تذييل الرسالة*\n\n" \
              "من هنا يمكنك تفعيل/تعطيل وتعديل نص يظهر في نهاية كل رسالة.\n\n"
    
    if current_footer:
        message += f"النص الحالي:\n`{current_footer}`"
    else:
        message += "لم يتم تعيين نص بعد."
    
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return

def button_menu(update, context):
    """Show the inline button settings menu."""
    config = load_config()
    
    button_status = "تفعيل ✅" if config.get("inline_button_enabled", False) else "تعطيل ❌"
    current_button_text = config.get("inline_button_text", "")
    current_button_url = config.get("inline_button_url", "")
    
    keyboard = [
        [InlineKeyboardButton(f"الحالة: {button_status}", callback_data="toggle_button")],
        [InlineKeyboardButton("تعديل نص الزر", callback_data="set_button_text")],
        [InlineKeyboardButton("تعديل رابط الزر", callback_data="set_button_url")],
        [InlineKeyboardButton("عودة ↩️", callback_data="customization_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = "⚙️ *إعدادات الزر الشفاف*\n\n" \
              "من هنا يمكنك تفعيل/تعطيل وتعديل زر نصي يظهر أسفل كل رسالة.\n\n"
    
    if current_button_text:
        message += f"النص الحالي: `{current_button_text}`\n"
    else:
        message += "لم يتم تعيين نص الزر بعد.\n"
    
    if current_button_url:
        message += f"الرابط الحالي: `{current_button_url}`"
    else:
        message += "لم يتم تعيين رابط الزر بعد."
    
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return

def toggle_header_status(update, context):
    """Toggle the header feature on/off."""
    config = load_config()
    
    # Toggle status
    current_status = config.get("header_enabled", False)
    config["header_enabled"] = not current_status
    
    # Save config
    save_config(config)
    
    # Return to header menu
    header_menu(update, context)

def toggle_footer_status(update, context):
    """Toggle the footer feature on/off."""
    config = load_config()
    
    # Toggle status
    current_status = config.get("footer_enabled", False)
    config["footer_enabled"] = not current_status
    
    # Save config
    save_config(config)
    
    # Return to footer menu
    footer_menu(update, context)

def toggle_button_status(update, context):
    """Toggle the inline button feature on/off."""
    config = load_config()
    
    # Toggle status
    current_status = config.get("inline_button_enabled", False)
    config["inline_button_enabled"] = not current_status
    
    # Save config
    save_config(config)
    
    # Return to button menu
    button_menu(update, context)

def set_header_text(update, context):
    """Start the process of setting header text."""
    update.callback_query.answer()
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="أرسل النص الذي تريد إضافته كرأس للرسائل.\n"
             "يمكنك استخدام تنسيق HTML مثل <b>عريض</b> و <i>مائل</i>.\n\n"
             "أرسل /cancel للإلغاء."
    )
    
    return WAITING_HEADER_TEXT

def set_footer_text(update, context):
    """Start the process of setting footer text."""
    update.callback_query.answer()
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="أرسل النص الذي تريد إضافته كتذييل للرسائل.\n"
             "يمكنك استخدام تنسيق HTML مثل <b>عريض</b> و <i>مائل</i>.\n\n"
             "أرسل /cancel للإلغاء."
    )
    
    return WAITING_FOOTER_TEXT

def set_button_text(update, context):
    """Start the process of setting button text."""
    update.callback_query.answer()
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="أرسل النص الذي تريد أن يظهر على الزر.\n\n"
             "أرسل /cancel للإلغاء."
    )
    
    return WAITING_BUTTON_TEXT

def set_button_url(update, context):
    """Start the process of setting button URL."""
    update.callback_query.answer()
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="أرسل رابط الزر (يجب أن يبدأ بـ https:// أو http://).\n\n"
             "أرسل /cancel للإلغاء."
    )
    
    return WAITING_BUTTON_URL

def receive_header_text(update, context):
    """Process received header text."""
    config = load_config()
    
    # Save header text
    config["header_text"] = update.message.text
    save_config(config)
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ تم حفظ نص الرأس بنجاح!"
    )
    
    # Show header menu
    keyboard = [
        [InlineKeyboardButton("العودة إلى قائمة الرأس", callback_data="header_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="اختر الخطوة التالية:",
        reply_markup=reply_markup
    )
    
    return -1  # End conversation

def receive_footer_text(update, context):
    """Process received footer text."""
    config = load_config()
    
    # Save footer text
    config["footer_text"] = update.message.text
    save_config(config)
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ تم حفظ نص التذييل بنجاح!"
    )
    
    # Show footer menu
    keyboard = [
        [InlineKeyboardButton("العودة إلى قائمة التذييل", callback_data="footer_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="اختر الخطوة التالية:",
        reply_markup=reply_markup
    )
    
    return -1  # End conversation

def receive_button_text(update, context):
    """Process received button text."""
    config = load_config()
    
    # Save button text
    config["inline_button_text"] = update.message.text
    save_config(config)
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ تم حفظ نص الزر بنجاح!"
    )
    
    # Show button menu
    keyboard = [
        [InlineKeyboardButton("العودة إلى قائمة الزر", callback_data="button_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="اختر الخطوة التالية:",
        reply_markup=reply_markup
    )
    
    return -1  # End conversation

def receive_button_url(update, context):
    """Process received button URL."""
    config = load_config()
    url = update.message.text
    
    # Basic URL validation
    if not (url.startswith("http://") or url.startswith("https://")):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ الرابط غير صالح. يجب أن يبدأ بـ http:// أو https://\n\n"
                 "أرسل رابط صالح أو أرسل /cancel للإلغاء."
        )
        return WAITING_BUTTON_URL
    
    # Save button URL
    config["inline_button_url"] = url
    save_config(config)
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ تم حفظ رابط الزر بنجاح!"
    )
    
    # Show button menu
    keyboard = [
        [InlineKeyboardButton("العودة إلى قائمة الزر", callback_data="button_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="اختر الخطوة التالية:",
        reply_markup=reply_markup
    )
    
    return -1  # End conversation