"""
Module for handling text replacements in the Telegram bot.
This module contains all functions related to text replacement functionality.
"""

import logging
import main
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler

# Conversation states
WAITING_REPLACEMENT_PATTERN = 1
WAITING_REPLACEMENT_TEXT = 2

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Apply text replacements to a message
def apply_text_replacements(text, replacements):
    """Apply text replacements to a string."""
    if not text or not replacements:
        return text
    
    result = text
    for replacement in replacements:
        pattern = replacement.get('pattern', '')
        
        # Support both key names: 'replace_with' and 'replacement'
        replace_with = replacement.get('replace_with', '')
        if not replace_with:
            replace_with = replacement.get('replacement', '')
        
        if pattern and isinstance(result, str):
            result = result.replace(pattern, replace_with)
    
    return result

# Main menu for text replacements
def text_replacements_menu(update, context):
    """Show the text replacements main menu."""
    # Determine if this is called from a command or callback query
    if update.callback_query:
        query = update.callback_query
        query.answer()
        
        # Create a keyboard with options for replacement submenu
        keyboard = [
            [InlineKeyboardButton("➕ إضافة استبدال جديد", callback_data='add_replacement')],
            [InlineKeyboardButton("📋 عرض قائمة الاستبدالات", callback_data='view_replacements')],
            [InlineKeyboardButton("🗑 حذف كل الاستبدالات", callback_data='delete_all_replacements')],
            [InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            '📝 *قائمة الاستبدال*\n\n'
            'يمكنك إدارة الاستبدالات من هنا.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        # Called from a text command
        # Create a keyboard with options for replacement submenu
        keyboard = [
            [InlineKeyboardButton("➕ إضافة استبدال جديد", callback_data='add_replacement')],
            [InlineKeyboardButton("📋 عرض قائمة الاستبدالات", callback_data='view_replacements')],
            [InlineKeyboardButton("🗑 حذف كل الاستبدالات", callback_data='delete_all_replacements')],
            [InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            '📝 *قائمة الاستبدال*\n\n'
            'يمكنك إدارة الاستبدالات من هنا.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    return None

# View replacements list
def view_replacements(update, context):
    """Show the list of all current replacements."""
    query = update.callback_query
    query.answer()
    
    # Load current text replacements
    config = main.load_config()
    
    # Initialize text replacements if not exists
    if 'text_replacements' not in config:
        config['text_replacements'] = []
        main.save_config(config)
    
    # Create the text replacements menu
    text_replacements = config.get('text_replacements', [])
    
    # Create a list of current replacements
    replacements_text = ""
    for i, replacement in enumerate(text_replacements):
        pattern = replacement.get('pattern', '')
        replacement_text = replacement.get('replacement', '')
        if not replacement_text:
            replacement_text = replacement.get('replace_with', '')
        replacements_text += f"{i+1}. '{pattern}' ⟹ '{replacement_text}'\n"
    
    if not replacements_text:
        replacements_text = "لا يوجد استبدالات حالياً."
    
    # Create a keyboard with options
    keyboard = [
        [InlineKeyboardButton("➕ إضافة استبدال جديد", callback_data='add_replacement')],
        [InlineKeyboardButton("🗑 حذف كل الاستبدالات", callback_data='delete_all_replacements')],
        [InlineKeyboardButton("🔙 العودة لقائمة الاستبدال", callback_data='text_replacements')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        '📋 *قائمة الاستبدالات الحالية*\n\n'
        f"{replacements_text}\n\n"
        'يمكنك إضافة استبدالات جديدة أو حذف الموجودة.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    return None

# Add new replacement
def add_replacement(update, context):
    """Start the process of adding a new replacement."""
    query = update.callback_query
    query.answer()
    
    # Set the conversation state and ask for the pattern
    query.edit_message_text(
        '📝 *إضافة استبدالات جديدة*\n\n'
        'أرسل الاستبدالات بالصيغة التالية (كل سطر يمثل استبدالاً):\n'
        '`نص1 : نص1 بديل`\n'
        '`نص2 : نص2 بديل`\n'
        '`نص3 : نص3 بديل`\n\n'
        'يمكنك إضافة استبدال واحد فقط أو عدة استبدالات دفعة واحدة.\n\n'
        'استخدم /cancel للإلغاء.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 العودة", callback_data='text_replacements')
        ]])
    )
    return WAITING_REPLACEMENT_PATTERN

# Process received replacement pattern
def receive_replacement_pattern(update, context):
    """Process received replacement pattern."""
    input_text = update.message.text.strip()
    
    if input_text == '/cancel':
        update.message.reply_text(
            '🚫 *تم الإلغاء*\n\n'
            'تم إلغاء العملية الحالية.',
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END
    
    # Always use the "text : replacement" format
    replacements_added = 0
    error_lines = []
    
    # Load config for adding replacements
    config = main.load_config()
    if 'text_replacements' not in config:
        config['text_replacements'] = []
    
    # Check if multiple lines or single line
    lines = input_text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:  # Skip empty lines
            continue
            
        # If line doesn't have delimiter, assume it's a single replacement
        # and prompt for second part
        if ' : ' not in line and len(lines) == 1:
            # Store the pattern in user data
            context.user_data['replacement_pattern'] = input_text
            
            # Ask for the replacement text
            update.message.reply_text(
                '📝 *إضافة استبدال جديد - الخطوة 2/2*\n\n'
                'أرسل النص الذي تريد استبداله به بصيغة:\n'
                f'`{input_text} : النص البديل`\n\n'
                'استخدم /cancel للإلغاء.',
                parse_mode=ParseMode.MARKDOWN
            )
            return WAITING_REPLACEMENT_TEXT
            
        # Otherwise, try to parse as "text : replacement"
        if ' : ' in line:
            parts = line.split(' : ', 1)
            if len(parts) == 2:
                pattern = parts[0].strip()
                replacement = parts[1].strip()
                
                if pattern and replacement:
                    # Add this replacement
                    config['text_replacements'].append({
                        'pattern': pattern,
                        'replacement': replacement
                    })
                    replacements_added += 1
                else:
                    error_lines.append(i + 1)
            else:
                error_lines.append(i + 1)
        else:
            error_lines.append(i + 1)
    
    # If we processed something, save the config
    if replacements_added > 0:
        # Save the updated config
        success = main.save_config(config)
        
        if success:
            # Create success message
            if len(error_lines) > 0:
                error_msg = f"\n⚠️ لم يتم إضافة الاستبدالات في السطور التالية بسبب خطأ في الصيغة: {', '.join(map(str, error_lines))}"
            else:
                error_msg = ""
                
            # Format success message with keyboard
            replacements = config.get('text_replacements', [])
            keyboard = []
            
            # Add button to add new replacement
            keyboard.append([InlineKeyboardButton("➕ إضافة استبدال جديد", callback_data='add_replacement')])
            
            # List current replacements
            for i, replacement in enumerate(replacements):
                # Display pattern and replacement text (truncated if too long)
                pattern_text = replacement.get('pattern', '')
                replace_with_text = replacement.get('replace_with', '')
                if not replace_with_text:
                    replace_with_text = replacement.get('replacement', '')
                
                # Truncate if too long for display
                if len(pattern_text) > 15:
                    pattern_text = pattern_text[:15] + '...'
                if len(replace_with_text) > 15:
                    replace_with_text = replace_with_text[:15] + '...'
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"❌ {pattern_text} ➡️ {replace_with_text}",
                        callback_data=f'delete_replacement_{i}'
                    )
                ])
            
            # Add back button
            keyboard.append([InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            update.message.reply_text(
                f'✅ *تم إضافة الاستبدالات بنجاح!*\n\n'
                f'تم إضافة {replacements_added} استبدال(ات).{error_msg}\n\n'
                f'سيتم تطبيق هذه الاستبدالات على جميع الرسائل الجديدة.',
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Send a new message with the replacements menu
            update.message.reply_text(
                '📝 *قائمة الاستبدالات*\n\n'
                'يمكنك إدارة قائمة الاستبدالات من هنا:',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            return ConversationHandler.END
    
    # If we got here and there was an error or nothing added, show it
    if len(lines) > 1 or ' : ' in input_text:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'لم يتم إضافة أي استبدالات. تأكد من استخدام الصيغة الصحيحة:\n'
            '`نص : نص بديل`\n'
            'لكل سطر من الاستبدالات.',
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END

# Process received replacement text
def receive_replacement_text(update, context):
    """Process received replacement text."""
    replace_with = update.message.text.strip()
    
    if replace_with == '/cancel':
        update.message.reply_text(
            '🚫 *تم الإلغاء*\n\n'
            'تم إلغاء العملية الحالية.',
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END
    
    # Get the pattern from user data
    pattern = context.user_data.get('replacement_pattern', '')
    
    if not pattern:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الاستبدال. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END
    
    # Load config, add new replacement, and save
    config = main.load_config()
    if 'text_replacements' not in config:
        config['text_replacements'] = []
    
    # Add the new replacement
    config['text_replacements'].append({
        'pattern': pattern,
        'replacement': replace_with
    })
    
    success = main.save_config(config)
    
    if success:
        # Format success message
        # Create a keyboard with all current replacements
        replacements = config.get('text_replacements', [])
        keyboard = []
        
        # Add button to add new replacement
        keyboard.append([InlineKeyboardButton("➕ إضافة استبدال جديد", callback_data='add_replacement')])
        
        # List current replacements
        for i, replacement in enumerate(replacements):
            # Display pattern and replacement text (truncated if too long)
            pattern_text = replacement.get('pattern', '')
            replace_with_text = replacement.get('replace_with', '')
            if not replace_with_text:
                replace_with_text = replacement.get('replacement', '')
            
            # Truncate if too long for display
            if len(pattern_text) > 15:
                pattern_text = pattern_text[:15] + '...'
            if len(replace_with_text) > 15:
                replace_with_text = replace_with_text[:15] + '...'
            
            keyboard.append([
                InlineKeyboardButton(
                    f"❌ {pattern_text} ➡️ {replace_with_text}",
                    callback_data=f'delete_replacement_{i}'
                )
            ])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 العودة للوحة التحكم", callback_data='admin_panel')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            f'✅ *تم إضافة الاستبدال بنجاح!*\n\n'
            f'من: "{pattern}"\n'
            f'إلى: "{replace_with}"\n\n'
            f'سيتم تطبيق هذا الاستبدال على جميع الرسائل الجديدة.',
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Send a new message with the replacements menu
        update.message.reply_text(
            '📝 *قائمة الاستبدالات*\n\n'
            'يمكنك إدارة قائمة الاستبدالات من هنا:',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الاستبدال. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Clear user data
    if 'replacement_pattern' in context.user_data:
        del context.user_data['replacement_pattern']
    
    return ConversationHandler.END

# Delete all replacements
def delete_all_replacements(update, context):
    """Delete all text replacements."""
    query = update.callback_query
    query.answer()
    
    # Load config
    config = main.load_config()
    
    # Clear all replacements
    config['text_replacements'] = []
    
    # Save config
    success = main.save_config(config)
    
    if success:
        # Show success message
        query.edit_message_text(
            '✅ *تم حذف جميع الاستبدالات بنجاح!*\n\n'
            'تم حذف جميع قواعد استبدال النص من النظام.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة لإعدادات الاستبدال", callback_data='text_replacements')
            ]])
        )
    else:
        # Show error message
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حذف الاستبدالات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة لإعدادات الاستبدال", callback_data='text_replacements')
            ]])
        )
    return None

# Delete single replacement
def delete_replacement(update, context, replacement_id):
    """Delete a single replacement by ID."""
    query = update.callback_query
    query.answer()
    
    try:
        # Convert to integer index
        index = int(replacement_id)
        
        # Load config
        config = main.load_config()
        replacements = config.get('text_replacements', [])
        
        # Check if index is valid
        if 0 <= index < len(replacements):
            # Store the deleted replacement details for confirmation message
            deleted_pattern = replacements[index].get('pattern', '')
            deleted_replacement = replacements[index].get('replace_with', '')
            if not deleted_replacement:
                deleted_replacement = replacements[index].get('replacement', '')
            
            # Remove the replacement
            del replacements[index]
            config['text_replacements'] = replacements
            success = main.save_config(config)
            
            if success:
                # Return to the text replacements menu with success message
                # Create updated keyboard
                keyboard = []
                
                # Add button to add new replacement
                keyboard.append([InlineKeyboardButton("➕ إضافة استبدال جديد", callback_data='add_replacement')])
                
                # List current replacements (if any)
                if replacements:
                    for i, replacement in enumerate(replacements):
                        # Display pattern and replacement text (truncated if too long)
                        pattern = replacement.get('pattern', '')
                        replace_with = replacement.get('replace_with', '')
                        if not replace_with:
                            replace_with = replacement.get('replacement', '')
                        
                        # Truncate if too long for display
                        if len(pattern) > 15:
                            pattern = pattern[:15] + '...'
                        if len(replace_with) > 15:
                            replace_with = replace_with[:15] + '...'
                        
                        keyboard.append([
                            InlineKeyboardButton(
                                f"❌ {pattern} ➡️ {replace_with}",
                                callback_data=f'delete_replacement_{i}'
                            )
                        ])
                else:
                    # No replacements left
                    keyboard.append([InlineKeyboardButton("لا توجد استبدالات حالياً", callback_data='no_action')])
                
                # Add back button
                keyboard.append([InlineKeyboardButton("🔙 العودة لقائمة الاستبدال", callback_data='text_replacements')])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                query.edit_message_text(
                    f'✅ *تم حذف الاستبدال بنجاح!*\n\n'
                    f'تم حذف الاستبدال:\n'
                    f'من: `{deleted_pattern}`\n'
                    f'إلى: `{deleted_replacement}`\n\n'
                    f'📋 *قائمة الاستبدالات الحالية*',
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            else:
                # Show error message
                query.edit_message_text(
                    '❌ *خطأ!*\n\n'
                    'حدث خطأ أثناء حذف الاستبدال. الرجاء المحاولة مرة أخرى.',
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 العودة", callback_data='text_replacements')
                    ]])
                )
        else:
            # Invalid index
            query.edit_message_text(
                '❌ *خطأ!*\n\n'
                'الاستبدال المحدد غير موجود. ربما تم حذفه بالفعل.',
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data='text_replacements')
                ]])
            )
    except Exception as e:
        # Show error message
        query.edit_message_text(
            f'❌ *خطأ!*\n\n'
            f'حدث خطأ أثناء حذف الاستبدال: {str(e)}',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='text_replacements')
            ]])
        )
    return None