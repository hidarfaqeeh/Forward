"""
Module for handling user settings and preferences in the Telegram bot.
This module manages user language preferences and other settings.
"""

import json
import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
import translations

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
USER_SETTINGS_FILE = 'user_settings.json'

def load_user_settings():
    """Load user settings from the JSON file"""
    try:
        if os.path.exists(USER_SETTINGS_FILE):
            with open(USER_SETTINGS_FILE, 'r') as f:
                return json.load(f)
        else:
            # Create empty settings file
            default_settings = {}
            with open(USER_SETTINGS_FILE, 'w') as f:
                json.dump(default_settings, f, indent=4)
            return default_settings
    except Exception as e:
        logger.error(f"Error loading user settings: {str(e)}")
        return {}

def save_user_settings(settings):
    """Save user settings to the JSON file"""
    try:
        with open(USER_SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving user settings: {str(e)}")
        return False

def get_user_language(user_id):
    """Get the preferred language for a user.
    
    Args:
        user_id (int): The Telegram user ID
        
    Returns:
        str: The language code (default: "ar" for Arabic)
    """
    settings = load_user_settings()
    user_id_str = str(user_id)  # Convert to string for JSON keys
    
    if user_id_str in settings and "language" in settings[user_id_str]:
        return settings[user_id_str]["language"]
    
    # Default language is Arabic
    return "ar"

def set_user_language(user_id, language_code):
    """Set the preferred language for a user.
    
    Args:
        user_id (int): The Telegram user ID
        language_code (str): The language code to set
        
    Returns:
        bool: True if successful, False otherwise
    """
    settings = load_user_settings()
    user_id_str = str(user_id)  # Convert to string for JSON keys
    
    # Initialize user settings if not exists
    if user_id_str not in settings:
        settings[user_id_str] = {}
    
    # Set language preference
    settings[user_id_str]["language"] = language_code
    
    # Save updated settings
    return save_user_settings(settings)

def create_language_selection_keyboard():
    """Create an inline keyboard with language options.
    
    Returns:
        InlineKeyboardMarkup: Inline keyboard with language buttons
    """
    keyboard = []
    row = []
    count = 0
    
    # Create rows with 2 languages per row
    for lang_code, lang_name in translations.LANGUAGES.items():
        row.append(InlineKeyboardButton(lang_name, callback_data=f'lang_{lang_code}'))
        count += 1
        
        # Create a new row after every 2 buttons
        if count % 2 == 0:
            keyboard.append(row)
            row = []
    
    # Add any remaining buttons
    if row:
        keyboard.append(row)
    
    # Back button at the bottom
    keyboard.append([InlineKeyboardButton("🔙 Back / رجوع", callback_data='lang_back')])
    
    return InlineKeyboardMarkup(keyboard)

def language_menu(update, context):
    """Show the language selection menu."""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    
    # Create language selection keyboard
    reply_markup = create_language_selection_keyboard()
    
    # Get message in user's current language
    message = translations.get_text("language_selection", language)
    
    # For callback queries
    if update.callback_query:
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            text=message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        # For direct command
        update.message.reply_text(
            text=message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

def handle_language_selection(update, context):
    """Handle language selection from inline keyboard."""
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Extract language code from callback data
    language_code = query.data.replace('lang_', '')
    
    # Handle back button
    if language_code == 'back':
        # Go back to main menu or start screen
        from bot_handler import start_command
        return start_command(update, context)
    
    # Set user language
    success = set_user_language(user_id, language_code)
    
    if success:
        # Confirm language change
        confirmation_message = translations.get_text("language_changed", language_code)
        query.answer(confirmation_message)
        
        # Update the welcome message in the new language
        welcome_message = translations.get_text("welcome", language_code)
        
        # Create language button
        keyboard = [
            [InlineKeyboardButton("🌐 تغيير اللغة / Change Language", callback_data='language_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            text=welcome_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        query.answer("⚠️ حدث خطأ أثناء تغيير اللغة. يرجى المحاولة مرة أخرى.")