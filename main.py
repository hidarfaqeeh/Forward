"""
تطبيق الويب الرئيسي لإدارة بوت التلجرام
Main web application for managing the Telegram bot
"""

import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, session, redirect, url_for, render_template, request, flash, g
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from jinja_translations import init_template_translations, get_template_language

# تحميل متغيرات البيئة من ملف .env
# Load environment variables from .env file
load_dotenv()

# تكوين السجلات
# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إنشاء تطبيق Flask
# Create Flask application
app = Flask(__name__)
# تعيين مفتاح السر بشكل ثابت دون الاعتماد على متغيرات البيئة لضمان عمل الجلسات
# Set a fixed secret key to ensure session functionality
app.secret_key = "telegram_bot_secure_fixed_key_2025_05_08"

# تكوين قاعدة البيانات
# Configure database connection
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# تهيئة نظام الترجمة متعدد اللغات
# Initialize multilingual translation system
init_template_translations(app)

# تعيين متغير 'lang' افتراضي في الجلسة عند بدء الجلسة
# Set default language in session on first visit
@app.before_request
def before_request():
    if 'lang' not in session:
        session['lang'] = 'ar'  # افتراضي للغة العربية - Default to Arabic

# إعداد SQLAlchemy
db = SQLAlchemy(app)

# استيراد النماذج بعد إعداد قاعدة البيانات
class User(db.Model):
    """نموذج المستخدم"""
    __tablename__ = 'tg_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

class BotSettings(db.Model):
    """نموذج إعدادات البوت"""
    __tablename__ = 'bot_settings'
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(128), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BotSettings {self.setting_key}>'

class BotStats(db.Model):
    """نموذج إحصائيات البوت - Bot Statistics Model"""
    __tablename__ = 'bot_stats'
    id = db.Column(db.Integer, primary_key=True)
    messages_forwarded = db.Column(db.Integer, default=0)
    messages_received = db.Column(db.Integer, default=0)
    messages_filtered = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_forwarded = db.Column(db.DateTime, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    errors = db.Column(db.Integer, default=0)
    
    # فلترة - Filtering stats
    filtered_by_blacklist = db.Column(db.Integer, default=0)
    filtered_duplicates = db.Column(db.Integer, default=0)
    filtered_by_language = db.Column(db.Integer, default=0)
    filtered_links = db.Column(db.Integer, default=0)
    
    # أنواع الوسائط - Media types
    text_messages = db.Column(db.Integer, default=0)
    image_messages = db.Column(db.Integer, default=0)
    video_messages = db.Column(db.Integer, default=0)
    other_messages = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<BotStats {self.id}>'

class TextReplacement(db.Model):
    """نموذج استبدال النص"""
    __tablename__ = 'text_replacements'
    id = db.Column(db.Integer, primary_key=True)
    pattern = db.Column(db.String(255), nullable=False)
    replacement = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TextReplacement {self.pattern}>'

class Blacklist(db.Model):
    """نموذج القائمة السوداء"""
    __tablename__ = 'blacklist'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Blacklist {self.word}>'

class Whitelist(db.Model):
    """نموذج القائمة البيضاء"""
    __tablename__ = 'whitelist'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Whitelist {self.word}>'

class MessageHistory(db.Model):
    """نموذج سجل الرسائل"""
    __tablename__ = 'message_history'
    id = db.Column(db.Integer, primary_key=True)
    source_message_id = db.Column(db.BigInteger)
    target_message_id = db.Column(db.BigInteger)
    content_hash = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MessageHistory {self.source_message_id} -> {self.target_message_id}>'

# التحقق من مصادقة المستخدم
def has_admin_user():
    """التحقق مما إذا كان هناك مستخدم مشرف في قاعدة البيانات"""
    try:
        admin = User.query.filter_by(is_admin=True).first()
        return admin is not None
    except Exception as e:
        logger.error(f"Error checking admin user: {str(e)}")
        return False

# دالة لإنشاء مستخدم مشرف افتراضي
def create_admin_user():
    """إنشاء مستخدم مشرف افتراضي في قاعدة البيانات"""
    try:
        if has_admin_user():
            logger.info("Admin user already exists")
            return True
        
        try:
            admin = User()
            admin.username = 'admin'
            admin.password_hash = generate_password_hash('admin')
            admin.is_admin = True
            db.session.add(admin)
            db.session.commit()
            logger.info("Admin user created successfully")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating admin user: {str(e)}")
            return False
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        return False

# إنشاء جداول قاعدة البيانات
with app.app_context():
    try:
        db.create_all()
        logger.info("Database initialized successfully")
        
        # إنشاء مستخدم مشرف افتراضي إذا لم يكن موجودًا
        create_admin_user()
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")

# التحقق من مصادقة المستخدم
def is_authenticated():
    """التحقق مما إذا كان المستخدم الحالي مصادقًا"""
    return 'user_id' in session

# مطلوب تسجيل الدخول
def login_required(f):
    """وظيفة الزخرفة للتحقق من تسجيل دخول المستخدم"""
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# دالة للحصول على إعداد من قاعدة البيانات
def get_setting(key, default=None):
    """الحصول على إعداد من قاعدة البيانات"""
    setting = BotSettings.query.filter_by(setting_key=key).first()
    return setting.setting_value if setting else default

# دالة لحفظ إعداد في قاعدة البيانات
def save_setting(key, value):
    """حفظ إعداد في قاعدة البيانات"""
    setting = BotSettings.query.filter_by(setting_key=key).first()
    if setting:
        setting.setting_value = value
    else:
        setting = BotSettings()
        setting.setting_key = key
        setting.setting_value = value
        db.session.add(setting)
    db.session.commit()

# المسارات - Routes

@app.route('/change-language/<lang>')
def change_language(lang):
    """
    تغيير لغة الواجهة
    Change interface language
    """
    if lang in ['ar', 'en']:
        session['lang'] = lang
        
    # العودة إلى الصفحة السابقة، أو إلى الصفحة الرئيسية إذا لم تكن متوفرة
    # Return to previous page, or to home page if not available
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    """
    الصفحة الرئيسية
    Home page
    """
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/guest-features')
def guest_features():
    """
    صفحة عرض مميزات البوت للضيوف
    Guest features page
    """
    return render_template('guest_features.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        logger.info(f"Login attempt for username: {username}")
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('dashboard'))
        
        flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم"""
    try:
        logger.info("Dashboard accessed - loading configuration and stats")
        
        # الحصول على إحصائيات البوت
        stats = BotStats.query.first()
        if not stats:
            stats = BotStats()
            db.session.add(stats)
            db.session.commit()
        
        # الحصول على إعدادات البوت
        source_channel = get_setting('source_channel', 'غير محدد')
        target_channel = get_setting('target_channel', 'غير محدد')
        forward_mode = get_setting('forward_mode', 'copy')
        forwarding_active = get_setting('forwarding_active', 'true') == 'true'
        
        return render_template(
            'dashboard.html', 
            stats=stats, 
            source_channel=source_channel,
            target_channel=target_channel,
            forward_mode=forward_mode,
            forwarding_active=forwarding_active
        )
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """صفحة الإعدادات"""
    if request.method == 'POST':
        try:
            # ======== الإعدادات الأساسية ========
            # إعدادات القنوات والتوجيه
            source_channel = request.form.get('source_channel', '')
            target_channel = request.form.get('target_channel', '')
            forward_mode = request.form.get('forward_mode', 'copy')
            forwarding_active = 'forwarding_active' in request.form
            
            # حفظ الإعدادات الأساسية
            save_setting('source_channel', source_channel)
            save_setting('target_channel', target_channel)
            save_setting('forward_mode', forward_mode)
            save_setting('forwarding_active', 'true' if forwarding_active else 'false')
            
            # ======== إعدادات الفلاتر ========
            # فلتر اللغة
            language_filter_enabled = 'language_filter_enabled' in request.form
            language_code = request.form.get('language_code', 'ar')
            language_mode = request.form.get('language_mode', 'whitelist')
            
            # فلتر الكلمات
            blacklist_enabled = 'blacklist_enabled' in request.form
            blacklist_words = request.form.get('blacklist_words', '')
            
            # فلتر الميديا
            filter_photos = 'filter_photos' in request.form
            filter_videos = 'filter_videos' in request.form
            filter_animations = 'filter_animations' in request.form
            filter_documents = 'filter_documents' in request.form
            
            # فلتر الأزرار والروابط
            remove_buttons = 'remove_buttons' in request.form
            filter_forwarded = 'filter_forwarded' in request.form
            filter_inline_buttons = 'filter_inline_buttons' in request.form
            
            # حفظ إعدادات الفلاتر
            save_setting('language_filter_enabled', 'true' if language_filter_enabled else 'false')
            save_setting('language_code', language_code)
            save_setting('language_mode', language_mode)
            save_setting('blacklist_enabled', 'true' if blacklist_enabled else 'false')
            save_setting('blacklist_words', blacklist_words)
            save_setting('filter_photos', 'true' if filter_photos else 'false')
            save_setting('filter_videos', 'true' if filter_videos else 'false')
            save_setting('filter_animations', 'true' if filter_animations else 'false')
            save_setting('filter_documents', 'true' if filter_documents else 'false')
            save_setting('remove_buttons', 'true' if remove_buttons else 'false')
            save_setting('filter_forwarded', 'true' if filter_forwarded else 'false')
            save_setting('filter_inline_buttons', 'true' if filter_inline_buttons else 'false')
            
            # ======== إعدادات النصوص ========
            # استبدال النصوص
            text_replacement_enabled = 'text_replacement_enabled' in request.form
            
            # جمع استبدالات النصوص
            text_replacements = []
            for i in range(5):  # عدد الاستبدالات المسموح بها في النموذج
                pattern = request.form.get(f'text_replacement_pattern_{i}', '').strip()
                replacement = request.form.get(f'text_replacement_replacement_{i}', '').strip()
                if pattern:  # إضافة فقط إذا كان النمط غير فارغ
                    text_replacements.append({'pattern': pattern, 'replacement': replacement})
            
            # تنسيق النص
            text_formatting_enabled = 'text_formatting_enabled' in request.form
            capitalize_sentences = 'capitalize_sentences' in request.form
            remove_extra_spaces = 'remove_extra_spaces' in request.form
            fix_punctuation = 'fix_punctuation' in request.form
            
            # الترجمة التلقائية
            auto_translation = 'auto_translation' in request.form
            translation_source = request.form.get('translation_source', 'auto')
            translation_target = request.form.get('translation_target', 'ar')
            
            # حفظ إعدادات النصوص
            save_setting('text_replacement_enabled', 'true' if text_replacement_enabled else 'false')
            save_setting('text_replacements', json.dumps(text_replacements))
            save_setting('text_formatting_enabled', 'true' if text_formatting_enabled else 'false')
            save_setting('capitalize_sentences', 'true' if capitalize_sentences else 'false')
            save_setting('remove_extra_spaces', 'true' if remove_extra_spaces else 'false')
            save_setting('fix_punctuation', 'true' if fix_punctuation else 'false')
            save_setting('auto_translation', 'true' if auto_translation else 'false')
            save_setting('translation_source', translation_source)
            save_setting('translation_target', translation_target)
            
            # ======== إعدادات التحكم ========
            # تأخير الرسائل
            delay_enabled = 'delay_enabled' in request.form
            delay_seconds = request.form.get('delay_seconds', '0')
            
            # منع الرسائل المكررة
            duplicate_filter_enabled = 'duplicate_filter_enabled' in request.form
            duplicate_filter_time = request.form.get('duplicate_filter_time', '24')
            
            # الحد الأقصى للأحرف
            char_limit_enabled = 'char_limit_enabled' in request.form
            char_limit = request.form.get('char_limit', '4096')
            
            # ساعات العمل
            working_hours_enabled = 'working_hours_enabled' in request.form
            working_hours_start = request.form.get('working_hours_start', '08:00')
            working_hours_end = request.form.get('working_hours_end', '20:00')
            
            # حفظ إعدادات التحكم
            save_setting('delay_enabled', 'true' if delay_enabled else 'false')
            save_setting('delay_seconds', delay_seconds)
            save_setting('duplicate_filter_enabled', 'true' if duplicate_filter_enabled else 'false')
            save_setting('duplicate_filter_time', duplicate_filter_time)
            save_setting('char_limit_enabled', 'true' if char_limit_enabled else 'false')
            save_setting('char_limit', char_limit)
            save_setting('working_hours_enabled', 'true' if working_hours_enabled else 'false')
            save_setting('working_hours_start', working_hours_start)
            save_setting('working_hours_end', working_hours_end)
            
            flash('تم تحديث الإعدادات بنجاح', 'success')
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            flash(f'حدث خطأ أثناء حفظ الإعدادات: {str(e)}', 'danger')
        
        return redirect(url_for('settings'))
    
    try:
        # ======== الإعدادات الأساسية ========
        source_channel = get_setting('source_channel', '')
        target_channel = get_setting('target_channel', '')
        forward_mode = get_setting('forward_mode', 'copy')
        forwarding_active = get_setting('forwarding_active', 'true') == 'true'
        
        # ======== إعدادات الفلاتر ========
        # فلتر اللغة
        language_filter_enabled = get_setting('language_filter_enabled', 'false') == 'true'
        language_code = get_setting('language_code', 'ar')
        language_mode = get_setting('language_mode', 'whitelist')
        
        # فلتر الكلمات
        blacklist_enabled = get_setting('blacklist_enabled', 'false') == 'true'
        blacklist_words = get_setting('blacklist_words', '')
        
        # فلتر الميديا
        filter_photos = get_setting('filter_photos', 'false') == 'true'
        filter_videos = get_setting('filter_videos', 'false') == 'true'
        filter_animations = get_setting('filter_animations', 'false') == 'true'
        filter_documents = get_setting('filter_documents', 'false') == 'true'
        
        # فلتر الأزرار والروابط
        remove_buttons = get_setting('remove_buttons', 'false') == 'true'
        filter_forwarded = get_setting('filter_forwarded', 'false') == 'true'
        filter_inline_buttons = get_setting('filter_inline_buttons', 'false') == 'true'
        
        # ======== إعدادات النصوص ========
        # استبدال النصوص
        text_replacement_enabled = get_setting('text_replacement_enabled', 'false') == 'true'
        text_replacements_json = get_setting('text_replacements', '[]')
        try:
            text_replacements = json.loads(text_replacements_json)
        except:
            text_replacements = []
        
        # تنسيق النص
        text_formatting_enabled = get_setting('text_formatting_enabled', 'false') == 'true'
        capitalize_sentences = get_setting('capitalize_sentences', 'false') == 'true'
        remove_extra_spaces = get_setting('remove_extra_spaces', 'false') == 'true'
        fix_punctuation = get_setting('fix_punctuation', 'false') == 'true'
        
        # الترجمة التلقائية
        auto_translation = get_setting('auto_translation', 'false') == 'true'
        translation_source = get_setting('translation_source', 'auto')
        translation_target = get_setting('translation_target', 'ar')
        
        # ======== إعدادات التحكم ========
        # تأخير الرسائل
        delay_enabled = get_setting('delay_enabled', 'false') == 'true'
        delay_seconds = get_setting('delay_seconds', '0')
        
        # منع الرسائل المكررة
        duplicate_filter_enabled = get_setting('duplicate_filter_enabled', 'false') == 'true'
        duplicate_filter_time = get_setting('duplicate_filter_time', '24')
        
        # الحد الأقصى للأحرف
        char_limit_enabled = get_setting('char_limit_enabled', 'false') == 'true'
        char_limit = get_setting('char_limit', '4096')
        
        # ساعات العمل
        working_hours_enabled = get_setting('working_hours_enabled', 'false') == 'true'
        working_hours_start = get_setting('working_hours_start', '08:00')
        working_hours_end = get_setting('working_hours_end', '20:00')
        
        return render_template(
            'settings.html',
            source_channel=source_channel,
            target_channel=target_channel,
            forward_mode=forward_mode,
            forwarding_active=forwarding_active,
            language_filter_enabled=language_filter_enabled,
            language_code=language_code,
            language_mode=language_mode,
            blacklist_enabled=blacklist_enabled,
            blacklist_words=blacklist_words,
            filter_photos=filter_photos,
            filter_videos=filter_videos,
            filter_animations=filter_animations,
            filter_documents=filter_documents,
            remove_buttons=remove_buttons,
            filter_forwarded=filter_forwarded,
            filter_inline_buttons=filter_inline_buttons,
            text_replacement_enabled=text_replacement_enabled,
            text_replacements=text_replacements,
            text_formatting_enabled=text_formatting_enabled,
            capitalize_sentences=capitalize_sentences,
            remove_extra_spaces=remove_extra_spaces,
            fix_punctuation=fix_punctuation,
            auto_translation=auto_translation,
            translation_source=translation_source,
            translation_target=translation_target,
            delay_enabled=delay_enabled,
            delay_seconds=delay_seconds,
            duplicate_filter_enabled=duplicate_filter_enabled,
            duplicate_filter_time=duplicate_filter_time,
            char_limit_enabled=char_limit_enabled,
            char_limit=char_limit,
            working_hours_enabled=working_hours_enabled,
            working_hours_start=working_hours_start,
            working_hours_end=working_hours_end
        )
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        flash(f'حدث خطأ أثناء تحميل الإعدادات: {str(e)}', 'danger')
        return render_template('error.html', error=str(e))

@app.route('/admins', methods=['GET', 'POST'])
@login_required
def admins():
    """صفحة إدارة المشرفين"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # التحقق من وجود المدخلات المطلوبة
        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'danger')
            return redirect(url_for('admins'))
        
        # التحقق من وجود المستخدم
        user = User.query.filter_by(username=username).first()
        if user:
            flash('اسم المستخدم موجود بالفعل', 'danger')
            return redirect(url_for('admins'))
        
        # إنشاء مستخدم جديد
        new_admin = User()
        new_admin.username = username
        new_admin.password_hash = generate_password_hash(password)
        new_admin.is_admin = True
        db.session.add(new_admin)
        db.session.commit()
        
        flash('تمت إضافة المشرف بنجاح', 'success')
        return redirect(url_for('admins'))
    
    # عرض المشرفين الحاليين
    admin_users = User.query.filter_by(is_admin=True).all()
    return render_template('admins.html', admins=admin_users)

# تشغيل التطبيق عند استدعائه مباشرة
# Run the app when it's called directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)