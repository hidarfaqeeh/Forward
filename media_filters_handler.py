"""
Module for handling media filters in the Telegram bot.
This module contains all functions related to media filtering functionality.
"""

import logging
import main
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Media filter function
def should_forward_media_type(media_type, config):
    """Check if a particular media type should be forwarded based on config."""
    # Get media filters from config
    media_filters = config.get('media_filters', {})
    
    # Default to True if filter is not set
    return media_filters.get(media_type, True)

# Media filters menu
def media_filters_menu(update, context):
    """Show the media filters menu."""
    # Determine if this is called from a command or callback query
    if update.callback_query:
        query = update.callback_query
        query.answer()
        
        # Load current media filters
        config = main.load_config()
        
        # Initialize media filters if not exists
        if 'media_filters' not in config:
            config['media_filters'] = {
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
            }
            main.save_config(config)
        
        # Create the media filters menu
        media_filters = config.get('media_filters', {})
        
        # Create a keyboard with toggle buttons for each media type
        keyboard = []
        
        # Mapping of media types to display names in Arabic
        media_type_names = {
            "text": "📝 نص",
            "photo": "🖼 صورة",
            "video": "🎥 فيديو",
            "document": "📄 ملف",
            "audio": "🎵 صوت",
            "voice": "🎤 رسالة صوتية",
            "video_note": "⭕ رسالة فيديو مستديرة",
            "animation": "🎞 صور متحركة",
            "sticker": "😃 ملصق",
            "poll": "📊 استبيان",
            "game": "🎮 لعبة",
            "contact": "📱 جهة اتصال",
            "location": "📍 موقع",
            "venue": "🏢 مكان"
        }
        
        # Create rows with two buttons each for all media types
        media_types = list(media_type_names.keys())
        for i in range(0, len(media_types), 2):
            row = []
            for media_type in media_types[i:i+2]:
                if i + 1 < len(media_types) or media_type == media_types[-1]:
                    status = "✅" if media_filters.get(media_type, True) else "❌"
                    row.append(InlineKeyboardButton(
                        f"{status} {media_type_names[media_type]}",
                        callback_data=f'toggle_media_{media_type}'
                    ))
            keyboard.append(row)
        
        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            '🎬 *إعدادات فلتر الوسائط*\n\n'
            'اضغط على أي نوع وسائط لتفعيل أو تعطيل توجيهه.\n'
            '✅ = مسموح بالتوجيه\n'
            '❌ = ممنوع التوجيه\n\n'
            'يمكنك اختيار ما تريد توجيهه من القناة المصدر إلى قناة الهدف.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        # Called from a text command
        # Load current media filters
        config = main.load_config()
        
        # Initialize media filters if not exists
        if 'media_filters' not in config:
            config['media_filters'] = {
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
            }
            main.save_config(config)
        
        # Create the media filters menu
        media_filters = config.get('media_filters', {})
        
        # Create a keyboard with toggle buttons for each media type
        keyboard = []
        
        # Mapping of media types to display names in Arabic
        media_type_names = {
            "text": "📝 نص",
            "photo": "🖼 صورة",
            "video": "🎥 فيديو",
            "document": "📄 ملف",
            "audio": "🎵 صوت",
            "voice": "🎤 رسالة صوتية",
            "video_note": "⭕ رسالة فيديو مستديرة",
            "animation": "🎞 صور متحركة",
            "sticker": "😃 ملصق",
            "poll": "📊 استبيان",
            "game": "🎮 لعبة",
            "contact": "📱 جهة اتصال",
            "location": "📍 موقع",
            "venue": "🏢 مكان"
        }
        
        # Create rows with two buttons each for all media types
        media_types = list(media_type_names.keys())
        for i in range(0, len(media_types), 2):
            row = []
            for media_type in media_types[i:i+2]:
                if i + 1 < len(media_types) or media_type == media_types[-1]:
                    status = "✅" if media_filters.get(media_type, True) else "❌"
                    row.append(InlineKeyboardButton(
                        f"{status} {media_type_names[media_type]}",
                        callback_data=f'toggle_media_{media_type}'
                    ))
            keyboard.append(row)
        
        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            '🎬 *إعدادات فلتر الوسائط*\n\n'
            'اضغط على أي نوع وسائط لتفعيل أو تعطيل توجيهه.\n'
            '✅ = مسموح بالتوجيه\n'
            '❌ = ممنوع التوجيه\n\n'
            'يمكنك اختيار ما تريد توجيهه من القناة المصدر إلى قناة الهدف.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    return None

# Toggle media filter
def toggle_media_filter(update, context, media_type):
    """Toggle a specific media type filter."""
    query = update.callback_query
    query.answer()
    
    # Load config
    config = main.load_config()
    if 'media_filters' not in config:
        config['media_filters'] = {}
    
    # Toggle the media filter
    current_value = config['media_filters'].get(media_type, True)
    config['media_filters'][media_type] = not current_value
    
    # Save config
    success = main.save_config(config)
    
    if success:
        # Call media_filters_menu to refresh the view with updated filters
        media_filters = config.get('media_filters', {})
        
        # Create a keyboard with toggle buttons for each media type
        keyboard = []
        
        # Mapping of media types to display names in Arabic
        media_type_names = {
            "text": "📝 نص",
            "photo": "🖼 صورة",
            "video": "🎥 فيديو",
            "document": "📄 ملف",
            "audio": "🎵 صوت",
            "voice": "🎤 رسالة صوتية",
            "video_note": "⭕ رسالة فيديو مستديرة",
            "animation": "🎞 صور متحركة",
            "sticker": "😃 ملصق",
            "poll": "📊 استبيان",
            "game": "🎮 لعبة",
            "contact": "📱 جهة اتصال",
            "location": "📍 موقع",
            "venue": "🏢 مكان"
        }
        
        # Create rows with two buttons each for all media types
        media_types = list(media_type_names.keys())
        for i in range(0, len(media_types), 2):
            row = []
            for media_type in media_types[i:i+2]:
                if i + 1 < len(media_types) or media_type == media_types[-1]:
                    status = "✅" if media_filters.get(media_type, True) else "❌"
                    row.append(InlineKeyboardButton(
                        f"{status} {media_type_names[media_type]}",
                        callback_data=f'toggle_media_{media_type}'
                    ))
            keyboard.append(row)
        
        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            '🎬 *إعدادات فلتر الوسائط*\n\n'
            'اضغط على أي نوع وسائط لتفعيل أو تعطيل توجيهه.\n'
            '✅ = مسموح بالتوجيه\n'
            '❌ = ممنوع التوجيه\n\n'
            'تم تحديث الإعدادات بنجاح!',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        # Show error message
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء تحديث إعدادات فلتر الوسائط. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')
            ]])
        )
    return None