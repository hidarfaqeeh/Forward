
import os
import json
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler

# حالات المحادثة
WAITING_BOT_TOKEN = 1

logger = logging.getLogger(__name__)

def create_bot_menu(update, context):
    """عرض قائمة إنشاء بوت جديد"""
    keyboard = [
        [InlineKeyboardButton("➕ إنشاء بوت جديد", callback_data='start_bot_creation')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='admin_panel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.callback_query.edit_message_text(
        '🤖 *إنشاء بوت جديد*\n\n'
        'يمكنك إنشاء نسخة جديدة من هذا البوت.\n'
        'ستحتاج إلى توكن البوت الجديد من @BotFather.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

def start_bot_creation(update, context):
    """بدء عملية إنشاء بوت جديد"""
    query = update.callback_query
    query.answer()
    
    query.edit_message_text(
        '🤖 *إنشاء بوت جديد - الخطوة 1/1*\n\n'
        'الرجاء إرسال توكن البوت الجديد.\n'
        'يمكنك الحصول على التوكن من @BotFather.\n\n'
        'استخدم /cancel للإلغاء.',
        parse_mode=ParseMode.MARKDOWN
    )
    
    return WAITING_BOT_TOKEN

def receive_bot_token(update, context):
    """معالجة توكن البوت المستلم"""
    bot_token = update.message.text.strip()
    
    # إنشاء مجلد جديد للبوت
    bot_dir = f"new_bot_{update.effective_user.id}"
    os.makedirs(bot_dir, exist_ok=True)
    
    # نسخ الملفات الأساسية
    files_to_copy = [
        'main.py', 'bot_handler.py', 'command_handlers.py',
        'config.json', 'translations.py'
    ]
    
    for file in files_to_copy:
        try:
            with open(file, 'r') as source:
                content = source.read()
            
            # حفظ الملف في المجلد الجديد
            with open(f"{bot_dir}/{file}", 'w') as target:
                target.write(content)
        except Exception as e:
            logger.error(f"Error copying {file}: {str(e)}")
    
    # إنشاء ملف تهيئة جديد
    config = {
        "bot_token": bot_token,
        "source_channel": "",
        "target_channel": "",
        "admin_users": [update.effective_user.id],
        "forward_mode": "forward"
    }
    
    with open(f"{bot_dir}/config.json", 'w') as f:
        json.dump(config, f, indent=4)
    
    # إرسال رسالة النجاح
    update.message.reply_text(
        '✅ *تم إنشاء البوت بنجاح!*\n\n'
        'تم إنشاء نسخة جديدة من البوت.\n'
        'يمكنك الآن استخدام البوت الجديد وإعداده.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data='admin_panel')
        ]])
    )
    
    return ConversationHandler.END

def cancel_command(update, context):
    """إلغاء عملية إنشاء البوت"""
    update.message.reply_text(
        '❌ *تم الإلغاء*\n\n'
        'تم إلغاء عملية إنشاء البوت.',
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END
