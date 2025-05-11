"""
Module for handling the whitelist functionality in the Telegram bot.
This module contains all functions related to whitelisted words and phrases.
"""

import logging
import main
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler

# Conversation states
WAITING_WHITELIST_WORDS = 1

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Whitelist check function
def contains_whitelisted_words(text, whitelist):
    """Check if a message contains any whitelisted words."""
    if not text or not whitelist:
        # No whitelist or no text means whitelist check passes
        return True
    
    # If whitelist exists, the message must contain at least one whitelisted word
    text_lower = text.lower()
    return any(word.lower() in text_lower for word in whitelist)

# Main menu for whitelist management
def toggle_whitelist_status(update, context):
    """Toggle the whitelist feature on/off."""
    # Determine if this is called from a command or callback query
    if update.callback_query:
        query = update.callback_query
        query.answer()
        
        # Load config
        config = main.load_config()
        
        # Toggle whitelist status
        current_status = config.get('whitelist_enabled', False)
        config['whitelist_enabled'] = not current_status
        
        # Save config
        success = main.save_config(config)
        
        if success:
            # Show success message
            new_status = config.get('whitelist_enabled', False)
            status_text = "مفعّلة ✅" if new_status else "معطّلة ❌"
            
            query.edit_message_text(
                f'✅ *تم تغيير حالة القائمة البيضاء بنجاح!*\n\n'
                f'حالة القائمة البيضاء الآن: {status_text}',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة للقائمة البيضاء", callback_data='whitelist_menu')
                ]])
            )
        else:
            # Show error message
            query.edit_message_text(
                '❌ *خطأ!*\n\n'
                'حدث خطأ أثناء تغيير حالة القائمة البيضاء. الرجاء المحاولة مرة أخرى.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة للقائمة البيضاء", callback_data='whitelist_menu')
                ]])
            )
    else:
        # Called from a text command
        # Load config
        config = main.load_config()
        
        # Toggle whitelist status
        current_status = config.get('whitelist_enabled', False)
        config['whitelist_enabled'] = not current_status
        
        # Save config
        success = main.save_config(config)
        
        if success:
            # Show success message
            new_status = config.get('whitelist_enabled', False)
            status_text = "مفعّلة ✅" if new_status else "معطّلة ❌"
            
            update.message.reply_text(
                f'✅ *تم تغيير حالة القائمة البيضاء بنجاح!*\n\n'
                f'حالة القائمة البيضاء الآن: {status_text}',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة للقائمة البيضاء", callback_data='whitelist_menu')
                ]])
            )
        else:
            # Show error message
            update.message.reply_text(
                '❌ *خطأ!*\n\n'
                'حدث خطأ أثناء تغيير حالة القائمة البيضاء. الرجاء المحاولة مرة أخرى.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة للقائمة البيضاء", callback_data='whitelist_menu')
                ]])
            )
    return None

def whitelist_menu(update, context):
    """Show the whitelist management menu."""
    # Determine if this is called from a command or callback query
    if update.callback_query:
        query = update.callback_query
        query.answer()
        
        # Load config to get current status
        config = main.load_config()
        is_enabled = config.get('whitelist_enabled', False)
        status_text = "مفعّلة ✅" if is_enabled else "معطّلة ❌"
        toggle_text = "تعطيل القائمة البيضاء ❌" if is_enabled else "تفعيل القائمة البيضاء ✅"
        
        # Create a keyboard with options for whitelist submenu
        keyboard = [
            [InlineKeyboardButton(f"حالة القائمة البيضاء: {status_text}", callback_data='no_action')],
            [InlineKeyboardButton(toggle_text, callback_data='toggle_whitelist_status')],
            [InlineKeyboardButton("➕ إضافة كلمات للقائمة البيضاء", callback_data='add_whitelist_words')],
            [InlineKeyboardButton("📋 عرض قائمة الكلمات البيضاء", callback_data='view_whitelist')],
            [InlineKeyboardButton("🗑 حذف كل الكلمات البيضاء", callback_data='delete_all_whitelist')],
            [InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            '✅ *القائمة البيضاء*\n\n'
            'يمكنك إدارة قائمة الكلمات البيضاء من هنا.\n'
            'سيتم توجيه الرسائل فقط إذا كانت تحتوي على كلمات من القائمة البيضاء.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        # Called from a text command
        # Load config to get current status
        config = main.load_config()
        is_enabled = config.get('whitelist_enabled', False)
        status_text = "مفعّلة ✅" if is_enabled else "معطّلة ❌"
        toggle_text = "تعطيل القائمة البيضاء ❌" if is_enabled else "تفعيل القائمة البيضاء ✅"
        
        # Create a keyboard with options for whitelist submenu
        keyboard = [
            [InlineKeyboardButton(f"حالة القائمة البيضاء: {status_text}", callback_data='no_action')],
            [InlineKeyboardButton(toggle_text, callback_data='toggle_whitelist_status')],
            [InlineKeyboardButton("➕ إضافة كلمات للقائمة البيضاء", callback_data='add_whitelist_words')],
            [InlineKeyboardButton("📋 عرض قائمة الكلمات البيضاء", callback_data='view_whitelist')],
            [InlineKeyboardButton("🗑 حذف كل الكلمات البيضاء", callback_data='delete_all_whitelist')],
            [InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            '✅ *القائمة البيضاء*\n\n'
            'يمكنك إدارة قائمة الكلمات البيضاء من هنا.\n'
            'سيتم توجيه الرسائل فقط إذا كانت تحتوي على كلمات من القائمة البيضاء.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    return None

# View whitelist
def view_whitelist(update, context):
    """Show the list of all whitelisted words."""
    query = update.callback_query
    query.answer()
    
    # Load current whitelist
    config = main.load_config()
    
    # Initialize whitelist if not exists
    if 'whitelist' not in config:
        config['whitelist'] = []
        main.save_config(config)
    
    # Create the whitelist display
    whitelist = config.get('whitelist', [])
    
    # Create a formatted list of whitelisted words
    whitelist_text = ""
    for i, word in enumerate(whitelist):
        whitelist_text += f"{i+1}. '{word}'\n"
    
    if not whitelist_text:
        whitelist_text = "لا توجد كلمات في القائمة البيضاء حالياً."
    
    # Create a keyboard with options
    keyboard = [
        [InlineKeyboardButton("➕ إضافة كلمات للقائمة البيضاء", callback_data='add_whitelist_words')],
        [InlineKeyboardButton("🗑 حذف كل الكلمات البيضاء", callback_data='delete_all_whitelist')],
        [InlineKeyboardButton("🔙 العودة للقائمة البيضاء", callback_data='whitelist_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        '📋 *قائمة الكلمات البيضاء*\n\n'
        f"{whitelist_text}\n\n"
        'سيتم توجيه الرسائل فقط إذا كانت تحتوي على أحد هذه الكلمات.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    return None

# Add whitelist words
def add_whitelist_words(update, context):
    """Start the process of adding whitelisted words."""
    query = update.callback_query
    query.answer()
    
    # Set the conversation state and ask for the whitelisted words
    query.edit_message_text(
        '✅ *إضافة كلمات للقائمة البيضاء*\n\n'
        'أرسل الكلمات التي تريد إضافتها إلى القائمة البيضاء.\n'
        'كل سطر يمثل كلمة أو عبارة.\n\n'
        'مثال:\n'
        '`كلمة مسموحة 1`\n'
        '`كلمة مسموحة 2`\n'
        '`عبارة مسموحة`\n\n'
        'استخدم /cancel للإلغاء.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 العودة", callback_data='whitelist_menu')
        ]])
    )
    return WAITING_WHITELIST_WORDS

# Process received whitelist words
def receive_whitelist_words(update, context):
    """Process received whitelisted words."""
    input_text = update.message.text.strip()
    
    if input_text == '/cancel':
        update.message.reply_text(
            '🚫 *تم الإلغاء*\n\n'
            'تم إلغاء العملية الحالية.',
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END
    
    # Process the whitelisted words
    words_added = 0
    
    # Load config for adding whitelisted words
    config = main.load_config()
    if 'whitelist' not in config:
        config['whitelist'] = []
    
    # Split by lines and process each one
    lines = input_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        
        # Check if word is already in the whitelist
        if line not in config['whitelist']:
            config['whitelist'].append(line)
            words_added += 1
    
    # Save the updated config
    success = main.save_config(config)
    
    if success and words_added > 0:
        # Format success message with keyboard
        whitelist = config.get('whitelist', [])
        keyboard = []
        
        # Add button to view whitelist
        keyboard.append([InlineKeyboardButton("📋 عرض القائمة البيضاء", callback_data='view_whitelist')])
        
        # Add button to add more words
        keyboard.append([InlineKeyboardButton("➕ إضافة المزيد من الكلمات", callback_data='add_whitelist_words')])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            f'✅ *تم إضافة الكلمات إلى القائمة البيضاء بنجاح!*\n\n'
            f'تم إضافة {words_added} كلمة/عبارة إلى القائمة البيضاء.\n\n'
            f'الإجمالي: {len(whitelist)} كلمة/عبارة في القائمة البيضاء.',
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
                    InlineKeyboardButton("🔙 العودة للقائمة البيضاء", callback_data='whitelist_menu')
                ]])
            )
        else:
            # If there was an error saving
            update.message.reply_text(
                '❌ *خطأ!*\n\n'
                'حدث خطأ أثناء حفظ الكلمات البيضاء. الرجاء المحاولة مرة أخرى.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة للقائمة البيضاء", callback_data='whitelist_menu')
                ]])
            )
    
    return ConversationHandler.END

# Delete all whitelisted words
def delete_all_whitelist(update, context):
    """Delete all whitelisted words."""
    query = update.callback_query
    query.answer()
    
    # Load config
    config = main.load_config()
    
    # Store the count for the confirmation message
    count = len(config.get('whitelist', []))
    
    # Clear all whitelisted words
    config['whitelist'] = []
    
    # Save config
    success = main.save_config(config)
    
    if success:
        # Show success message
        query.edit_message_text(
            '✅ *تم حذف جميع الكلمات من القائمة البيضاء بنجاح!*\n\n'
            f'تم حذف {count} كلمة/عبارة من القائمة البيضاء.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة للقائمة البيضاء", callback_data='whitelist_menu')
            ]])
        )
    else:
        # Show error message
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حذف الكلمات البيضاء. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة للقائمة البيضاء", callback_data='whitelist_menu')
            ]])
        )
    return None