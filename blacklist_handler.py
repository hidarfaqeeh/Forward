"""
Module for handling the blacklist functionality in the Telegram bot.
This module contains all functions related to blacklisted words and phrases.
"""

import logging
import main
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler

# Conversation states
WAITING_BLACKLIST_WORDS = 1

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Helper function to check if a message contains blacklisted words
def contains_blacklisted_words(text, blacklist):
    """Check if a message contains any blacklisted words."""
    if not text or not blacklist:
        return False
    
    text_lower = text.lower()
    for word in blacklist:
        if word.lower() in text_lower:
            return True
    
    return False

# Main menu for blacklist management
def toggle_blacklist_status(update, context):
    """Toggle the blacklist feature on/off."""
    # Determine if this is called from a command or callback query
    if update.callback_query:
        query = update.callback_query
        query.answer()
        
        # Load config
        config = main.load_config()
        
        # Toggle blacklist status
        current_status = config.get('blacklist_enabled', True)
        config['blacklist_enabled'] = not current_status
        
        # Save config
        success = main.save_config(config)
        
        if success:
            # Show success message
            new_status = config.get('blacklist_enabled', True)
            status_text = "مفعّلة ✅" if new_status else "معطّلة ❌"
            
            query.edit_message_text(
                f'✅ *تم تغيير حالة القائمة السوداء بنجاح!*\n\n'
                f'حالة القائمة السوداء الآن: {status_text}',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة للقائمة السوداء", callback_data='blacklist_menu')
                ]])
            )
        else:
            # Show error message
            query.edit_message_text(
                '❌ *خطأ!*\n\n'
                'حدث خطأ أثناء تغيير حالة القائمة السوداء. الرجاء المحاولة مرة أخرى.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة للقائمة السوداء", callback_data='blacklist_menu')
                ]])
            )
    else:
        # Called from a text command
        # Load config
        config = main.load_config()
        
        # Toggle blacklist status
        current_status = config.get('blacklist_enabled', True)
        config['blacklist_enabled'] = not current_status
        
        # Save config
        success = main.save_config(config)
        
        if success:
            # Show success message
            new_status = config.get('blacklist_enabled', True)
            status_text = "مفعّلة ✅" if new_status else "معطّلة ❌"
            
            update.message.reply_text(
                f'✅ *تم تغيير حالة القائمة السوداء بنجاح!*\n\n'
                f'حالة القائمة السوداء الآن: {status_text}',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة للقائمة السوداء", callback_data='blacklist_menu')
                ]])
            )
        else:
            # Show error message
            update.message.reply_text(
                '❌ *خطأ!*\n\n'
                'حدث خطأ أثناء تغيير حالة القائمة السوداء. الرجاء المحاولة مرة أخرى.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة للقائمة السوداء", callback_data='blacklist_menu')
                ]])
            )
    return None

def blacklist_menu(update, context):
    """Show the blacklist management menu."""
    # Determine if this is called from a command or callback query
    if update.callback_query:
        query = update.callback_query
        query.answer()
        
        # Load config to get current status
        config = main.load_config()
        is_enabled = config.get('blacklist_enabled', True)
        status_text = "مفعّلة ✅" if is_enabled else "معطّلة ❌"
        toggle_text = "تعطيل القائمة السوداء ❌" if is_enabled else "تفعيل القائمة السوداء ✅"
        
        # Create a keyboard with options for blacklist submenu
        keyboard = [
            [InlineKeyboardButton(f"حالة القائمة السوداء: {status_text}", callback_data='no_action')],
            [InlineKeyboardButton(toggle_text, callback_data='toggle_blacklist_status')],
            [InlineKeyboardButton("➕ إضافة كلمات محظورة", callback_data='add_blacklist_words')],
            [InlineKeyboardButton("📋 عرض قائمة الكلمات المحظورة", callback_data='view_blacklist')],
            [InlineKeyboardButton("🗑 حذف كل الكلمات المحظورة", callback_data='delete_all_blacklist')],
            [InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            '⛔ *القائمة السوداء*\n\n'
            'يمكنك إدارة قائمة الكلمات المحظورة من هنا.\n'
            'الرسائل التي تحتوي على كلمات من القائمة السوداء لن يتم توجيهها.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        # Called from a text command
        # Load config to get current status
        config = main.load_config()
        is_enabled = config.get('blacklist_enabled', True)
        status_text = "مفعّلة ✅" if is_enabled else "معطّلة ❌"
        toggle_text = "تعطيل القائمة السوداء ❌" if is_enabled else "تفعيل القائمة السوداء ✅"
        
        # Create a keyboard with options for blacklist submenu
        keyboard = [
            [InlineKeyboardButton(f"حالة القائمة السوداء: {status_text}", callback_data='no_action')],
            [InlineKeyboardButton(toggle_text, callback_data='toggle_blacklist_status')],
            [InlineKeyboardButton("➕ إضافة كلمات محظورة", callback_data='add_blacklist_words')],
            [InlineKeyboardButton("📋 عرض قائمة الكلمات المحظورة", callback_data='view_blacklist')],
            [InlineKeyboardButton("🗑 حذف كل الكلمات المحظورة", callback_data='delete_all_blacklist')],
            [InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            '⛔ *القائمة السوداء*\n\n'
            'يمكنك إدارة قائمة الكلمات المحظورة من هنا.\n'
            'الرسائل التي تحتوي على كلمات من القائمة السوداء لن يتم توجيهها.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    return None

# View blacklist
def view_blacklist(update, context):
    """Show the list of all blacklisted words."""
    query = update.callback_query
    query.answer()
    
    # Load current blacklist
    config = main.load_config()
    
    # Initialize blacklist if not exists
    if 'blacklist' not in config:
        config['blacklist'] = []
        main.save_config(config)
    
    # Create the blacklist display
    blacklist = config.get('blacklist', [])
    
    # Create a formatted list of blacklisted words
    blacklist_text = ""
    for i, word in enumerate(blacklist):
        blacklist_text += f"{i+1}. '{word}'\n"
    
    if not blacklist_text:
        blacklist_text = "لا توجد كلمات محظورة حالياً."
    
    # Create a keyboard with options
    keyboard = [
        [InlineKeyboardButton("➕ إضافة كلمات محظورة", callback_data='add_blacklist_words')],
        [InlineKeyboardButton("🗑 حذف كل الكلمات المحظورة", callback_data='delete_all_blacklist')],
        [InlineKeyboardButton("🔙 العودة للقائمة السوداء", callback_data='blacklist_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        '📋 *قائمة الكلمات المحظورة*\n\n'
        f"{blacklist_text}\n\n"
        'الرسائل التي تحتوي على هذه الكلمات لن يتم توجيهها.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    return None

# Add blacklist words
def add_blacklist_words(update, context):
    """Start the process of adding blacklisted words."""
    query = update.callback_query
    query.answer()
    
    # Set the conversation state and ask for the blacklisted words
    query.edit_message_text(
        '⛔ *إضافة كلمات محظورة*\n\n'
        'أرسل الكلمات المحظورة التي تريد إضافتها.\n'
        'كل سطر يمثل كلمة أو عبارة محظورة.\n\n'
        'مثال:\n'
        '`كلمة محظورة 1`\n'
        '`كلمة محظورة 2`\n'
        '`عبارة محظورة`\n\n'
        'استخدم /cancel للإلغاء.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 العودة", callback_data='blacklist_menu')
        ]])
    )
    return WAITING_BLACKLIST_WORDS

# Process received blacklist words
def receive_blacklist_words(update, context):
    """Process received blacklisted words."""
    input_text = update.message.text.strip()
    
    if input_text == '/cancel':
        update.message.reply_text(
            '🚫 *تم الإلغاء*\n\n'
            'تم إلغاء العملية الحالية.',
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END
    
    # Process the blacklisted words
    words_added = 0
    
    # Load config for adding blacklisted words
    config = main.load_config()
    if 'blacklist' not in config:
        config['blacklist'] = []
    
    # Split by lines and process each one
    lines = input_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        
        # Check if word is already in the blacklist
        if line not in config['blacklist']:
            config['blacklist'].append(line)
            words_added += 1
    
    # Save the updated config
    success = main.save_config(config)
    
    if success and words_added > 0:
        # Format success message with keyboard
        blacklist = config.get('blacklist', [])
        keyboard = []
        
        # Add button to view blacklist
        keyboard.append([InlineKeyboardButton("📋 عرض القائمة السوداء", callback_data='view_blacklist')])
        
        # Add button to add more words
        keyboard.append([InlineKeyboardButton("➕ إضافة المزيد من الكلمات", callback_data='add_blacklist_words')])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            f'✅ *تم إضافة الكلمات المحظورة بنجاح!*\n\n'
            f'تم إضافة {words_added} كلمة/عبارة إلى القائمة السوداء.\n\n'
            f'الإجمالي: {len(blacklist)} كلمة/عبارة محظورة.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        # If no words were added
        if words_added == 0:
            update.message.reply_text(
                '⚠️ *تنبيه*\n\n'
                'لم يتم إضافة أي كلمات جديدة. قد تكون الكلمات موجودة بالفعل في القائمة أو أدخلت أسطرًا فارغة.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة للقائمة السوداء", callback_data='blacklist_menu')
                ]])
            )
        else:
            # If there was an error saving
            update.message.reply_text(
                '❌ *خطأ!*\n\n'
                'حدث خطأ أثناء حفظ الكلمات المحظورة. الرجاء المحاولة مرة أخرى.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة للقائمة السوداء", callback_data='blacklist_menu')
                ]])
            )
    
    return ConversationHandler.END

# Delete all blacklisted words
def delete_all_blacklist(update, context):
    """Delete all blacklisted words."""
    query = update.callback_query
    query.answer()
    
    # Load config
    config = main.load_config()
    
    # Store the count for the confirmation message
    count = len(config.get('blacklist', []))
    
    # Clear all blacklisted words
    config['blacklist'] = []
    
    # Save config
    success = main.save_config(config)
    
    if success:
        # Show success message
        query.edit_message_text(
            '✅ *تم حذف جميع الكلمات المحظورة بنجاح!*\n\n'
            f'تم حذف {count} كلمة/عبارة من القائمة السوداء.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة للقائمة السوداء", callback_data='blacklist_menu')
            ]])
        )
    else:
        # Show error message
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حذف الكلمات المحظورة. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة للقائمة السوداء", callback_data='blacklist_menu')
            ]])
        )
    return None