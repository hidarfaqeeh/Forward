"""
Main entry point for the Telegram forwarding bot.
This module initializes the bot, handlers, and starts the bot.
"""

import os
import json
import logging
from datetime import datetime

from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler, 
    MessageHandler, Filters, ConversationHandler
)
from telegram import ParseMode

# Import handlers from separate modules
import bot_handler
import command_handlers
import replacements_handler
import media_filters_handler
import blacklist_handler

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration file path
CONFIG_FILE = 'config.json'

def load_config():
    """Load bot configuration from config.json file"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            # Default configuration
            default_config = {
                "source_channel": None,
                "target_channel": None,
                "developer_id": None,
                "admin_users": [],
                "forward_mode": "forward",  # "forward" or "copy"
                "media_filters": {
                    "text": True,
                    "photo": True,
                    "video": True,
                    "document": True,
                    "audio": True,
                    "voice": True,
                    "video_note": True,
                    "animation": True,
                    "sticker": True,
                    "poll": True,
                    "game": True,
                    "contact": True,
                    "location": True,
                    "venue": True
                },
                "text_replacements": [],
                "blacklist": [],
                "blacklist_enabled": True
            }
            with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
                json.dump(default_config, file, ensure_ascii=False, indent=2)
            return default_config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}

def save_config(config):
    """Save configuration to config.json file"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
            json.dump(config, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

def main():
    """Start the bot"""
    # Load configuration
    config = load_config()
    
    # Set up the bot
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN environment variable found")
        return
    
    # Initialize the updater
    updater = Updater(token)
    dispatcher = updater.dispatcher
    
    # Set the developer ID
    developer_id = config.get("developer_id")
    if developer_id:
        bot_handler.set_developer_id(developer_id)
    
    # Log what we're monitoring
    source_channel = config.get("source_channel")
    target_channel = config.get("target_channel")
    logger.info(f"Starting Telegram forwarding bot")
    logger.info(f"Monitoring source channel: {source_channel}")
    logger.info(f"Forwarding to target channel: {target_channel}")
    
    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", command_handlers.start_command))
    dispatcher.add_handler(CommandHandler("help", command_handlers.help_command))
    dispatcher.add_handler(CommandHandler("status", command_handlers.status_command))
    dispatcher.add_handler(CommandHandler("admin", command_handlers.admin_panel))
    
    # Conversation handlers for setup and admin tasks
    # Source channel setup
    source_handler = ConversationHandler(
        entry_points=[
            CommandHandler("setsource", command_handlers.set_source_command),
            CallbackQueryHandler(
                command_handlers.set_source_command, pattern='^set_source$'
            )
        ],
        states={
            command_handlers.WAITING_SOURCE: [MessageHandler(Filters.text, command_handlers.receive_source)]
        },
        fallbacks=[CommandHandler("cancel", command_handlers.cancel_command)]
    )
    dispatcher.add_handler(source_handler)
    
    # Target channel setup
    target_handler = ConversationHandler(
        entry_points=[
            CommandHandler("settarget", command_handlers.set_target_command),
            CallbackQueryHandler(
                command_handlers.set_target_command, pattern='^set_target$'
            )
        ],
        states={
            command_handlers.WAITING_TARGET: [MessageHandler(Filters.text, command_handlers.receive_target)]
        },
        fallbacks=[CommandHandler("cancel", command_handlers.cancel_command)]
    )
    dispatcher.add_handler(target_handler)
    
    # Add admin setup
    admin_handler = ConversationHandler(
        entry_points=[
            CommandHandler("addadmin", command_handlers.add_admin_command),
            CallbackQueryHandler(
                command_handlers.add_admin_command, pattern='^add_admin$'
            )
        ],
        states={
            command_handlers.WAITING_ADMIN: [MessageHandler(Filters.text, command_handlers.receive_admin)]
        },
        fallbacks=[CommandHandler("cancel", command_handlers.cancel_command)]
    )
    dispatcher.add_handler(admin_handler)
    
    # Set developer
    developer_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                command_handlers.set_developer_button, pattern='^set_developer$'
            )
        ],
        states={
            command_handlers.WAITING_DEVELOPER: [MessageHandler(Filters.text, command_handlers.receive_developer)]
        },
        fallbacks=[CommandHandler("cancel", command_handlers.cancel_command)]
    )
    dispatcher.add_handler(developer_handler)
    
    # Text replacements conversation handler
    replacements_handler_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                replacements_handler.add_replacement, pattern='^add_replacement$'
            )
        ],
        states={
            replacements_handler.WAITING_REPLACEMENT_PATTERN: [
                MessageHandler(Filters.text, replacements_handler.receive_replacement_pattern)
            ],
            replacements_handler.WAITING_REPLACEMENT_TEXT: [
                MessageHandler(Filters.text, replacements_handler.receive_replacement_text)
            ]
        },
        fallbacks=[CommandHandler("cancel", command_handlers.cancel_command)]
    )
    dispatcher.add_handler(replacements_handler_conv)
    
    # Setup command handler
    dispatcher.add_handler(CommandHandler("setup", command_handlers.setup_command))
    
    # Button handlers
    # Callback query handlers for the admin panel
    dispatcher.add_handler(CallbackQueryHandler(
        command_handlers.admin_panel, pattern='^admin_panel$'))
    dispatcher.add_handler(CallbackQueryHandler(
        command_handlers.toggle_forward_mode, pattern='^toggle_forward_mode$'))
    dispatcher.add_handler(CallbackQueryHandler(
        command_handlers.show_stats, pattern='^show_stats$'))
    
    # Media filter handlers
    dispatcher.add_handler(CallbackQueryHandler(
        media_filters_handler.media_filters_menu, pattern='^media_filters$'))
    # Media toggle handlers
    dispatcher.add_handler(CallbackQueryHandler(
        lambda update, context: media_filters_handler.toggle_media_filter(
            update, context, update.callback_query.data.replace('toggle_media_', '')
        ), 
        pattern='^toggle_media_'
    ))
    
    # Text replacement menu handlers
    dispatcher.add_handler(CallbackQueryHandler(
        replacements_handler.text_replacements_menu, pattern='^text_replacements$'))
    dispatcher.add_handler(CallbackQueryHandler(
        replacements_handler.view_replacements, pattern='^view_replacements$'))
    dispatcher.add_handler(CallbackQueryHandler(
        replacements_handler.delete_all_replacements, pattern='^delete_all_replacements$'))
    # Single replacement delete handler
    dispatcher.add_handler(CallbackQueryHandler(
        lambda update, context: replacements_handler.delete_replacement(
            update, context, update.callback_query.data.replace('delete_replacement_', '')
        ),
        pattern='^delete_replacement_'
    ))
    
    # Blacklist handlers
    dispatcher.add_handler(CallbackQueryHandler(
        blacklist_handler.blacklist_menu, pattern='^blacklist_menu$'))
    dispatcher.add_handler(CallbackQueryHandler(
        blacklist_handler.view_blacklist, pattern='^view_blacklist$'))
    dispatcher.add_handler(CallbackQueryHandler(
        blacklist_handler.delete_all_blacklist, pattern='^delete_all_blacklist$'))
    dispatcher.add_handler(CallbackQueryHandler(
        blacklist_handler.toggle_blacklist_status, pattern='^toggle_blacklist_status$'))
    
    # Blacklist words conversation handler
    blacklist_handler_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                blacklist_handler.add_blacklist_words, pattern='^add_blacklist_words$'
            )
        ],
        states={
            blacklist_handler.WAITING_BLACKLIST_WORDS: [
                MessageHandler(Filters.text, blacklist_handler.receive_blacklist_words)
            ]
        },
        fallbacks=[CommandHandler("cancel", command_handlers.cancel_command)]
    )
    dispatcher.add_handler(blacklist_handler_conv)
    
    # No action handler for informational buttons
    dispatcher.add_handler(CallbackQueryHandler(lambda u, c: None, pattern='^no_action$'))
    
    # Message handler for channel posts - Only if we have source and target channels configured
    if source_channel and target_channel:
        dispatcher.add_handler(
            MessageHandler(
                Filters.chat(int(source_channel)) & Filters.update.channel_post,
                lambda update, context: bot_handler.forward_message(update, context, target_channel)
            )
        )
    
    # Add error handler
    dispatcher.add_error_handler(bot_handler.error_handler)
    
    # Start the bot
    updater.start_polling()
    logger.info("Bot started successfully. Press Ctrl+C to stop.")
    updater.idle()

if __name__ == '__main__':
    main()