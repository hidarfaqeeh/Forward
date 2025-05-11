
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import json
import logging
import os
import secrets
from datetime import datetime, timedelta
from utils import load_config, save_config, get_bot_stats
from functools import wraps

# تكوين التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(16))
app.permanent_session_lifetime = timedelta(days=1)

# تحقق من مستخدم مصرح له
def is_authenticated():
    return session.get('authenticated', False)

# دالة تغليف للتحقق من المصادقة
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# نستخدم get_bot_stats المعرفة في utils.py

# الصفحة الرئيسية
@app.route('/')
def index():
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# صفحة تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        config = load_config()
        username = request.form.get('username')
        password = request.form.get('password')
        admin_id = request.form.get('admin_id')
        
        # التحقق من صحة بيانات المستخدم 
        is_valid_user = False
        
        # التحقق من اسم المستخدم وكلمة المرور الافتراضية أو المخصصة
        if username == config.get('web_username', 'admin') and password == config.get('web_password', 'admin'):
            is_valid_user = True
        
        # إذا أدخل المستخدم معرف تلجرام، تحقق من أنه مشرف
        if admin_id and admin_id.isdigit():
            admin_users = config.get('admin_users', [])
            if int(admin_id) in admin_users:
                is_valid_user = True
        
        if is_valid_user:
            session['authenticated'] = True
            session.permanent = True
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('بيانات الدخول غير صحيحة، تأكد من أنك مشرف في البوت', 'danger')
    
    return render_template('login.html')

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('index'))

# لوحة القيادة الرئيسية
@app.route('/dashboard')
@login_required
def dashboard():
    config = load_config()
    stats = get_bot_stats()
    logger.info("Dashboard accessed - loading configuration and stats")
    
    # تنسيق البيانات للعرض
    admin_users = config.get('admin_users', [])
    admin_count = len(admin_users)
    
    # تحديد حالة البوت (نشط أو غير نشط)
    forwarding_enabled = config.get('forwarding_enabled', True)
    
    return render_template(
        'dashboard.html',
        config=config,
        stats=stats,
        admin_count=admin_count,
        bot_active=forwarding_enabled
    )

# صفحة إعدادات البوت
@app.route('/settings')
@login_required
def settings():
    config = load_config()
    return render_template('settings.html', config=config)

# تحديث إعدادات البوت
@app.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    config = load_config()
    
    # تحديث إعدادات عامة
    if 'source_channel' in request.form:
        config['source_channel'] = request.form.get('source_channel')
    if 'target_channel' in request.form:
        config['target_channel'] = request.form.get('target_channel')
    if 'forward_mode' in request.form:
        config['forward_mode'] = request.form.get('forward_mode')
    
    # تحديث الحالة
    if 'forwarding_enabled' in request.form:
        config['forwarding_enabled'] = request.form.get('forwarding_enabled') == 'on'
    
    # تحديث الكلمات المحظورة والمسموح بها
    if 'blacklist' in request.form:
        blacklist = request.form.get('blacklist').split('\n')
        config['blacklist'] = [word.strip() for word in blacklist if word.strip()]
    
    if 'whitelist' in request.form:
        whitelist = request.form.get('whitelist').split('\n')
        config['whitelist'] = [word.strip() for word in whitelist if word.strip()]
    
    # حفظ التغييرات
    success = save_config(config)
    if success:
        flash('تم تحديث الإعدادات بنجاح', 'success')
    else:
        flash('حدث خطأ أثناء حفظ الإعدادات', 'danger')
    
    return redirect(url_for('settings'))

# صفحة المشرفين
@app.route('/admins')
@login_required
def admins():
    config = load_config()
    admin_users = config.get('admin_users', [])
    developer_id = config.get('developer_id', '')
    return render_template('admins.html', admin_users=admin_users, developer_id=developer_id)

# إضافة مشرف جديد
@app.route('/admins/add', methods=['POST'])
@login_required
def add_admin():
    admin_id = request.form.get('admin_id', '').strip()
    try:
        admin_id = int(admin_id)
        config = load_config()
        admin_users = config.get('admin_users', [])
        
        if admin_id not in admin_users:
            admin_users.append(admin_id)
            config['admin_users'] = admin_users
            success = save_config(config)
            
            if success:
                flash(f'تمت إضافة المشرف {admin_id} بنجاح', 'success')
            else:
                flash('حدث خطأ أثناء حفظ الإعدادات', 'danger')
        else:
            flash('المشرف موجود بالفعل', 'warning')
            
    except ValueError:
        flash('يجب أن يكون معرف المشرف رقمًا صحيحًا', 'danger')
    
    return redirect(url_for('admins'))

# إزالة مشرف
@app.route('/admins/remove/<int:admin_id>')
@login_required
def remove_admin(admin_id):
    config = load_config()
    admin_users = config.get('admin_users', [])
    
    if admin_id in admin_users:
        admin_users.remove(admin_id)
        config['admin_users'] = admin_users
        success = save_config(config)
        
        if success:
            flash(f'تمت إزالة المشرف {admin_id} بنجاح', 'success')
        else:
            flash('حدث خطأ أثناء حفظ الإعدادات', 'danger')
    else:
        flash('المشرف غير موجود', 'warning')
    
    return redirect(url_for('admins'))

# صفحة تخصيص الرسائل
@app.route('/message_customization')
@login_required
def message_customization():
    config = load_config()
    header_enabled = config.get('header_enabled', False)
    header_text = config.get('header_text', '')
    footer_enabled = config.get('footer_enabled', False)
    footer_text = config.get('footer_text', '')
    button_enabled = config.get('inline_button_enabled', False)
    button_text = config.get('inline_button_text', '')
    button_url = config.get('inline_button_url', '')
    
    return render_template(
        'message_customization.html',
        header_enabled=header_enabled,
        header_text=header_text,
        footer_enabled=footer_enabled,
        footer_text=footer_text,
        button_enabled=button_enabled,
        button_text=button_text,
        button_url=button_url
    )

# تحديث تخصيص الرسائل
@app.route('/message_customization/update', methods=['POST'])
@login_required
def update_message_customization():
    config = load_config()
    
    # تحديث رأس الرسالة
    config['header_enabled'] = 'header_enabled' in request.form
    config['header_text'] = request.form.get('header_text', '')
    
    # تحديث تذييل الرسالة
    config['footer_enabled'] = 'footer_enabled' in request.form
    config['footer_text'] = request.form.get('footer_text', '')
    
    # تحديث زر الرسالة
    config['inline_button_enabled'] = 'button_enabled' in request.form
    config['inline_button_text'] = request.form.get('button_text', '')
    config['inline_button_url'] = request.form.get('button_url', '')
    
    # حفظ التغييرات
    success = save_config(config)
    if success:
        flash('تم تحديث تخصيص الرسائل بنجاح', 'success')
    else:
        flash('حدث خطأ أثناء حفظ الإعدادات', 'danger')
    
    return redirect(url_for('message_customization'))

# صفحة الاستبدالات النصية
@app.route('/text_replacements')
@login_required
def text_replacements():
    config = load_config()
    replacements = config.get('text_replacements', [])
    return render_template('text_replacements.html', replacements=replacements)

# إضافة استبدال نصي جديد
@app.route('/text_replacements/add', methods=['POST'])
@login_required
def add_text_replacement():
    pattern = request.form.get('pattern', '').strip()
    replacement = request.form.get('replacement', '').strip()
    
    if pattern and replacement:
        config = load_config()
        replacements = config.get('text_replacements', [])
        
        # إضافة الاستبدال الجديد
        replacements.append({
            'pattern': pattern,
            'replacement': replacement
        })
        
        config['text_replacements'] = replacements
        success = save_config(config)
        
        if success:
            flash('تمت إضافة الاستبدال النصي بنجاح', 'success')
        else:
            flash('حدث خطأ أثناء حفظ الإعدادات', 'danger')
    else:
        flash('يجب تعبئة كلا الحقلين', 'warning')
    
    return redirect(url_for('text_replacements'))

# حذف استبدال نصي
@app.route('/text_replacements/remove/<int:index>')
@login_required
def remove_text_replacement(index):
    config = load_config()
    replacements = config.get('text_replacements', [])
    
    if 0 <= index < len(replacements):
        del replacements[index]
        config['text_replacements'] = replacements
        success = save_config(config)
        
        if success:
            flash('تم حذف الاستبدال النصي بنجاح', 'success')
        else:
            flash('حدث خطأ أثناء حفظ الإعدادات', 'danger')
    else:
        flash('الاستبدال النصي غير موجود', 'warning')
    
    return redirect(url_for('text_replacements'))

# تشغيل الموقع
if __name__ == '__main__':
    logger.info("Starting web dashboard on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
