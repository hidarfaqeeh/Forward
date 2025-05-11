"""
Module for handling the display of bot statistics in the Telegram bot.
This module contains functions for generating and displaying statistics about the bot's operation.
"""

import logging
import main
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def generate_stats_text(language="ar"):
    """Generate statistics text for the bot.
    
    Args:
        language (str): Language code for translations (default: "ar" for Arabic)
    
    Returns:
        str: Formatted text with statistics
    """
    # Import translations module
    import translations
    
    # Get stats from bot_handler
    import bot_handler
    stats = bot_handler.stats
    
    # Ensure started_at exists
    if stats["started_at"] is None:
        stats["started_at"] = datetime.now()
    
    # Calculate uptime
    uptime = datetime.now() - stats["started_at"]
    uptime_str = str(uptime).split('.')[0]  # Remove microseconds
    
    # Format last forwarded time
    last_forwarded_text = translations.get_text("stats_not_yet", language)
    last_forwarded = last_forwarded_text if stats["last_forwarded"] is None else stats["last_forwarded"].strftime("%Y-%m-%d %H:%M:%S")
    
    # Load config to show current channels
    config = main.load_config()
    not_set_text = translations.get_text("stats_not_set", language)
    source_channel = config.get("source_channel", not_set_text)
    target_channel = config.get("target_channel", not_set_text)
    
    # Get current forward mode
    forward_mode = config.get("forward_mode", "forward")
    if forward_mode == "forward":
        forward_mode_text = translations.get_text("forward_mode_with_tag", language)
    else:
        forward_mode_text = translations.get_text("forward_mode_copy", language)
    
    # Get forwarding status
    import forwarding_control_handler
    forwarding_status = forwarding_control_handler.get_forwarding_status()
    
    # Get rate limit status
    import rate_limit_handler
    rate_limit_status = rate_limit_handler.get_rate_limit_status()
    
    # Get translated labels
    running_since = translations.get_text("stats_running_since", language)
    uptime_label = translations.get_text("stats_uptime", language)
    messages_forwarded = translations.get_text("stats_messages_forwarded", language)
    last_forwarded_label = translations.get_text("stats_last_forwarded", language)
    source_channel_label = translations.get_text("stats_source_channel", language)
    target_channel_label = translations.get_text("stats_target_channel", language)
    forward_mode_label = translations.get_text("stats_forward_mode", language)
    forwarding_status_label = translations.get_text("stats_forwarding_status", language)
    rate_limit_label = translations.get_text("stats_rate_limit", language)
    errors_label = translations.get_text("stats_errors", language)
    
    # Generate the stats text
    stats_text = (
        f'{running_since} {stats["started_at"].strftime("%Y-%m-%d %H:%M:%S")}\n'
        f'{uptime_label} {uptime_str}\n'
        f'{messages_forwarded} {stats["messages_forwarded"]}\n'
        f'{last_forwarded_label} {last_forwarded}\n'
        f'{source_channel_label} {source_channel}\n'
        f'{target_channel_label} {target_channel}\n'
        f'{forward_mode_label} {forward_mode_text}\n'
        f'{forwarding_status_label} {forwarding_status}\n'
        f'{rate_limit_label} {rate_limit_status}\n'
        f'{errors_label} {stats["errors"]}'
    )
    
    return stats_text

def show_stats(update, context):
    """Show bot statistics."""
    # Import user settings and translations
    import user_settings_handler
    import translations
    
    # Get the user's language preference
    user_id = update.effective_user.id
    language = user_settings_handler.get_user_language(user_id)
    
    # Get translated text
    menu_text = translations.get_text("stats_menu", language)
    back_button = translations.get_text("button_back", language)
    
    # Generate stats text
    stats_text = generate_stats_text(language)
    
    # Create keyboard
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    refresh_button = translations.get_text("button_refresh_stats", language)
    keyboard = [
        [
            InlineKeyboardButton(refresh_button, callback_data='refresh_stats')
        ],
        [
            InlineKeyboardButton(back_button, callback_data='admin_panel')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # For callback queries
    if update.callback_query:
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            menu_text + stats_text,
            parse_mode='MARKDOWN',
            reply_markup=reply_markup
        )
    # For direct command
    else:
        update.message.reply_text(
            menu_text + stats_text,
            parse_mode='MARKDOWN',
            reply_markup=reply_markup
        )