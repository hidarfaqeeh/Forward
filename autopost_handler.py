"""
Module for handling scheduled posts (autopost) functionality in the Telegram bot.
This module contains all functions related to scheduling posts to be automatically sent at specific times.
"""

import json
import logging
import time
from datetime import datetime, timedelta
import threading
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler
import main

# Configure logging
logger = logging.getLogger(__name__)

# Conversation states
WAITING_POST_TEXT = 1
WAITING_POST_INTERVAL = 2

# Store scheduled posts
scheduled_posts = []
scheduler_thread = None
is_scheduler_running = False

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

def save_posts():
    """Save scheduled posts to config file"""
    config = load_config()
    config["scheduled_posts"] = scheduled_posts
    return save_config(config)

def load_posts():
    """Load scheduled posts from config file"""
    global scheduled_posts
    config = load_config()
    posts = config.get("scheduled_posts", [])
    scheduled_posts = posts
    return scheduled_posts

def autopost_menu(update, context):
    """Show the autopost menu."""
    config = load_config()
    
    # Get current status
    autopost_enabled = config.get("autopost_enabled", False)
    status = "✅ مفعّل" if autopost_enabled else "❌ معطّل"
    
    # Load posts if not already loaded
    if not scheduled_posts:
        load_posts()
    
    # Create keyboard with options
    keyboard = [
        [InlineKeyboardButton(
            f"حالة النشر التلقائي: {status}", 
            callback_data='toggle_autopost'
        )],
        [InlineKeyboardButton(
            "➕ إضافة منشور مجدول", 
            callback_data='add_scheduled_post'
        )],
        [InlineKeyboardButton(
            "📋 عرض المنشورات المجدولة", 
            callback_data='view_scheduled_posts'
        )],
        [InlineKeyboardButton(
            "🗑️ حذف جميع المنشورات المجدولة", 
            callback_data='delete_all_scheduled_posts'
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
            '⏱ *النشر التلقائي المجدول*\n\n'
            'يمكنك إعداد منشورات ليتم نشرها بشكل تلقائي ودوري.\n\n'
            f'الحالة الحالية: *{status}*\n'
            f'عدد المنشورات المجدولة: *{len(scheduled_posts)}*',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    # For direct commands
    else:
        update.message.reply_text(
            '⏱ *النشر التلقائي المجدول*\n\n'
            'يمكنك إعداد منشورات ليتم نشرها بشكل تلقائي ودوري.\n\n'
            f'الحالة الحالية: *{status}*\n'
            f'عدد المنشورات المجدولة: *{len(scheduled_posts)}*',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

def toggle_autopost_status(update, context):
    """Toggle the autopost feature on/off."""
    query = update.callback_query
    query.answer()
    
    # Load config
    config = load_config()
    
    # Toggle setting
    current_status = config.get("autopost_enabled", False)
    config["autopost_enabled"] = not current_status
    
    # Save config
    success = save_config(config)
    
    if success:
        # If toggling on, make sure scheduler is running
        if not current_status:  # Turning on
            start_scheduler(context.bot)
        
        # Show the menu again with updated status
        autopost_menu(update, context)
    else:
        # Show error
        query.edit_message_text(
            '❌ *خطأ!*\n\n'
            'حدث خطأ أثناء حفظ الإعدادات. الرجاء المحاولة مرة أخرى.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='autopost_menu')
            ]])
        )

def add_scheduled_post(update, context):
    """Start the process of adding a scheduled post."""
    query = update.callback_query
    query.answer()
    
    query.edit_message_text(
        '➕ *إضافة منشور مجدول جديد*\n\n'
        'الرجاء إرسال نص المنشور الذي تريد جدولته للنشر التلقائي.\n\n'
        'استخدم /cancel للإلغاء.',
        parse_mode=ParseMode.MARKDOWN
    )
    
    return WAITING_POST_TEXT

def receive_post_text(update, context):
    """Process received post text."""
    # Save the received text in context
    context.user_data['scheduled_post_text'] = update.message.text
    
    update.message.reply_text(
        '⏱ *تحديد فترة التكرار*\n\n'
        'الرجاء إرسال فترة التكرار بالدقائق (رقم فقط).\n'
        'مثال: `60` لتكرار المنشور كل ساعة.\n\n'
        'استخدم /cancel للإلغاء.',
        parse_mode=ParseMode.MARKDOWN
    )
    
    return WAITING_POST_INTERVAL

def receive_post_interval(update, context):
    """Process received post interval."""
    try:
        # Get interval from message
        interval_minutes = int(update.message.text.strip())
        
        if interval_minutes < 1:
            update.message.reply_text(
                '❌ *خطأ!*\n\n'
                'يجب أن تكون فترة التكرار رقماً موجباً.\n'
                'الرجاء إدخال فترة التكرار بالدقائق (رقم فقط).',
                parse_mode=ParseMode.MARKDOWN
            )
            return WAITING_POST_INTERVAL
        
        # Get the post text from context
        post_text = context.user_data.get('scheduled_post_text', '')
        
        # Add to scheduled posts
        post = {
            'text': post_text,
            'interval_minutes': interval_minutes,
            'last_sent': None,
            'id': int(time.time())  # Use timestamp as unique ID
        }
        
        global scheduled_posts
        scheduled_posts.append(post)
        
        # Save posts to config
        save_posts()
        
        # Start scheduler if not already running
        config = load_config()
        if config.get("autopost_enabled", False):
            start_scheduler(context.bot)
        
        # Show success message
        keyboard = [
            [InlineKeyboardButton("🔙 العودة إلى قائمة النشر التلقائي", callback_data='autopost_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            '✅ *تمت الإضافة بنجاح!*\n\n'
            'تم إضافة المنشور المجدول بنجاح.\n\n'
            f'النص: "{post_text[:50]}{"..." if len(post_text) > 50 else ""}"\n'
            f'فترة التكرار: كل {interval_minutes} دقيقة',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
        # Clear the context
        if 'scheduled_post_text' in context.user_data:
            del context.user_data['scheduled_post_text']
        
        return ConversationHandler.END
        
    except ValueError:
        update.message.reply_text(
            '❌ *خطأ!*\n\n'
            'يجب أن تكون فترة التكرار رقماً.\n'
            'الرجاء إدخال فترة التكرار بالدقائق (رقم فقط).',
            parse_mode=ParseMode.MARKDOWN
        )
        return WAITING_POST_INTERVAL

def view_scheduled_posts(update, context):
    """Show the list of scheduled posts."""
    query = update.callback_query
    query.answer()
    
    # Load posts if not already loaded
    if not scheduled_posts:
        load_posts()
    
    if not scheduled_posts:
        # No posts
        query.edit_message_text(
            '📋 *المنشورات المجدولة*\n\n'
            'لا توجد منشورات مجدولة حالياً.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='autopost_menu')
            ]])
        )
        return
    
    # Create message with all posts
    message = '📋 *المنشورات المجدولة*\n\n'
    
    for i, post in enumerate(scheduled_posts, 1):
        # Get post details
        text = post['text']
        interval = post['interval_minutes']
        last_sent = post['last_sent']
        
        # Format last sent time
        if last_sent:
            last_sent_str = datetime.fromtimestamp(last_sent).strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_sent_str = "لم يتم النشر بعد"
        
        # Add to message (with text truncation for long posts)
        message += f'*{i}. النشر كل {interval} دقيقة*\n'
        message += f'النص: "{text[:30]}{"..." if len(text) > 30 else ""}"\n'
        message += f'آخر نشر: {last_sent_str}\n\n'
    
    # Create keyboard with options
    keyboard = [
        [InlineKeyboardButton("🗑️ حذف منشور", callback_data='delete_post_menu')],
        [InlineKeyboardButton("🔙 العودة", callback_data='autopost_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

def delete_post_menu(update, context):
    """Show menu to delete a specific post."""
    query = update.callback_query
    query.answer()
    
    # Load posts if not already loaded
    if not scheduled_posts:
        load_posts()
    
    if not scheduled_posts:
        # No posts
        query.edit_message_text(
            '🗑️ *حذف منشور مجدول*\n\n'
            'لا توجد منشورات مجدولة للحذف.',
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data='autopost_menu')
            ]])
        )
        return
    
    # Create keyboard with all posts
    keyboard = []
    
    for i, post in enumerate(scheduled_posts, 1):
        # Get post text (truncated)
        text = post['text']
        short_text = f"{text[:20]}..." if len(text) > 20 else text
        
        # Add button for this post
        keyboard.append([
            InlineKeyboardButton(
                f"{i}. {short_text}",
                callback_data=f'delete_post_{post["id"]}'
            )
        ])
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton("🔙 العودة", callback_data='view_scheduled_posts')
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        '🗑️ *حذف منشور مجدول*\n\n'
        'اختر المنشور الذي تريد حذفه:',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

def delete_post(update, context):
    """Delete a specific scheduled post."""
    query = update.callback_query
    query.answer()
    
    # Get post ID from callback data
    post_id = int(query.data.split('_')[-1])
    
    # Find and remove the post
    global scheduled_posts
    for i, post in enumerate(scheduled_posts):
        if post["id"] == post_id:
            del scheduled_posts[i]
            break
    
    # Save updated posts list
    save_posts()
    
    # Show success message
    query.edit_message_text(
        '✅ *تم الحذف بنجاح!*\n\n'
        'تم حذف المنشور المجدول بنجاح.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 العودة", callback_data='view_scheduled_posts')
        ]])
    )

def delete_all_scheduled_posts(update, context):
    """Delete all scheduled posts."""
    query = update.callback_query
    query.answer()
    
    # Create confirmation keyboard
    keyboard = [
        [
            InlineKeyboardButton("✅ نعم، حذف الكل", callback_data='confirm_delete_all_posts'),
            InlineKeyboardButton("❌ لا، إلغاء", callback_data='autopost_menu')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text(
        '⚠️ *تأكيد حذف جميع المنشورات*\n\n'
        'هل أنت متأكد من رغبتك في حذف جميع المنشورات المجدولة؟\n'
        'هذا الإجراء لا يمكن التراجع عنه.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

def confirm_delete_all_posts(update, context):
    """Confirm and delete all scheduled posts."""
    query = update.callback_query
    query.answer()
    
    # Clear all posts
    global scheduled_posts
    scheduled_posts = []
    
    # Save empty list
    save_posts()
    
    # Show success message
    query.edit_message_text(
        '✅ *تم الحذف بنجاح!*\n\n'
        'تم حذف جميع المنشورات المجدولة بنجاح.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 العودة", callback_data='autopost_menu')
        ]])
    )

def start_scheduler(bot):
    """Start the scheduler thread if it's not already running."""
    global scheduler_thread, is_scheduler_running
    
    if scheduler_thread is None or not scheduler_thread.is_alive():
        is_scheduler_running = True
        scheduler_thread = threading.Thread(target=scheduler_loop, args=(bot,))
        scheduler_thread.daemon = True
        scheduler_thread.start()
        logger.info("Autopost scheduler started")

def stop_scheduler():
    """Stop the scheduler thread."""
    global is_scheduler_running
    is_scheduler_running = False
    logger.info("Autopost scheduler stopped")

def scheduler_loop(bot):
    """The main scheduler loop that runs in a separate thread."""
    while is_scheduler_running:
        try:
            # Check if autopost is enabled
            config = load_config()
            if not config.get("autopost_enabled", False):
                # Feature is disabled, exit the loop
                logger.info("Autopost is disabled, stopping scheduler")
                break
            
            # Get target channel
            target_channel = config.get("target_channel")
            if not target_channel:
                # No target channel configured, wait and try again
                time.sleep(60)
                continue
            
            # Load posts if needed
            if not scheduled_posts:
                load_posts()
            
            # Check each post to see if it's time to send
            current_time = time.time()
            for post in scheduled_posts:
                interval_seconds = post["interval_minutes"] * 60
                last_sent = post.get("last_sent")
                
                # Check if post should be sent (never sent or interval has passed)
                if last_sent is None or (current_time - last_sent) >= interval_seconds:
                    try:
                        # Send the post
                        bot.send_message(
                            chat_id=target_channel,
                            text=post["text"],
                            parse_mode=ParseMode.HTML
                        )
                        logger.info(f"Sent scheduled post: {post['text'][:30]}...")
                        
                        # Update last sent time
                        post["last_sent"] = current_time
                        save_posts()
                    except Exception as e:
                        logger.error(f"Error sending scheduled post: {str(e)}")
            
            # Wait before checking again (30 seconds to avoid excessive checking)
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"Error in scheduler loop: {str(e)}")
            time.sleep(60)  # Wait longer on error
    
    logger.info("Scheduler loop exited")