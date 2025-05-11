"""
وحدة برمجية لمسارات تطبيق الويب
"""

from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from functools import wraps

from main import app, db, logger
from models import User, BotSettings, BotStats, TextReplacement, Blacklist, Whitelist, MessageHistory
from utils import load_config, save_config, get_bot_stats

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

# الصفحة الرئيسية
@app.route('/')
def index():
    try:
        if is_authenticated():
            return redirect(url_for('dashboard'))
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Index error: {str(e)}")
        return "حدث خطأ في النظام. الرجاء المحاولة مرة أخرى."

# صفحة تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            config = load_config()
            username = request.form.get('username')
            password = request.form.get('password')
            admin_id = request.form.get('admin_id')
            
            logger.info(f"Login attempt for username: {username}")

            # التحقق من تسجيل الدخول باستخدام اسم المستخدم وكلمة المرور
            if username and password:
                user = User.query.filter_by(username=username).first()
                
                if user and check_password_hash(user.password_hash, password):
                    session.permanent = True
                    session['authenticated'] = True
                    session['user_id'] = user.id
                    session['is_admin'] = user.is_admin
                    flash('تم تسجيل الدخول بنجاح!', 'success')
                    return redirect(url_for('dashboard'))

            # التحقق من تسجيل الدخول باستخدام معرف التلجرام
            if admin_id:
                try:
                    admin_id = admin_id.strip()
                    admin_users = config.get('admin_users', [])
                    if not admin_id.isdigit():
                        flash('معرف التلجرام يجب أن يكون رقماً', 'danger')
                    elif int(admin_id) in admin_users:
                        session.permanent = True
                        session['authenticated'] = True
                        session['admin_id'] = int(admin_id)
                        flash('تم تسجيل الدخول بنجاح!', 'success')
                        return redirect(url_for('dashboard'))
                    else:
                        flash(f'معرف التلجرام {admin_id} غير مسجل كمشرف', 'danger')
                except ValueError:
                    flash('خطأ في معالجة معرف التلجرام', 'danger')
                except Exception as e:
                    logger.error(f"Telegram login error: {str(e)}")
                    flash('حدث خطأ أثناء التحقق من معرف التلجرام', 'danger')

            flash('بيانات الدخول غير صحيحة', 'danger')
        
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return render_template('login.html', error="حدث خطأ في النظام. الرجاء المحاولة مرة أخرى")

# تسجيل الخروج
@app.route('/logout')
def logout():
    try:
        session.clear()
        flash('تم تسجيل الخروج بنجاح', 'success')
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
    return redirect(url_for('index'))

# لوحة القيادة الرئيسية
@app.route('/dashboard')
@login_required
def dashboard():
    try:
        config = load_config()
        if not config:
            flash('حدث خطأ في تحميل الإعدادات', 'danger')
            return redirect(url_for('login'))

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
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        flash('حدث خطأ في تحميل لوحة التحكم', 'danger')
        return redirect(url_for('login'))

# صفحة إعدادات البوت
@app.route('/settings')
@login_required
def settings():
    try:
        config = load_config()
        return render_template('settings.html', config=config)
    except Exception as e:
        logger.error(f"Settings page error: {str(e)}")
        flash('حدث خطأ في تحميل صفحة الإعدادات', 'danger')
        return redirect(url_for('dashboard'))

# تحديث إعدادات البوت
@app.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    try:
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
        blacklist_text = request.form.get('blacklist', '')
        if blacklist_text:
            blacklist = blacklist_text.split('\n')
            config['blacklist'] = [word.strip() for word in blacklist if word.strip()]

        whitelist_text = request.form.get('whitelist', '')
        if whitelist_text:
            whitelist = whitelist_text.split('\n')
            config['whitelist'] = [word.strip() for word in whitelist if word.strip()]

        # حفظ التغييرات
        success = save_config(config)
        if success:
            flash('تم تحديث الإعدادات بنجاح', 'success')
        else:
            flash('حدث خطأ أثناء حفظ الإعدادات', 'danger')
    except Exception as e:
        logger.error(f"Update settings error: {str(e)}")
        flash('حدث خطأ أثناء تحديث الإعدادات', 'danger')

    return redirect(url_for('settings'))

# صفحة المشرفين
@app.route('/admins')
@login_required
def admins():
    try:
        config = load_config()
        admin_users = config.get('admin_users', [])
        developer_id = config.get('developer_id', '')
        return render_template('admins.html', admin_users=admin_users, developer_id=developer_id)
    except Exception as e:
        logger.error(f"Admins page error: {str(e)}")
        flash('حدث خطأ في تحميل صفحة المشرفين', 'danger')
        return redirect(url_for('dashboard'))

# إضافة مشرف جديد
@app.route('/admins/add', methods=['POST'])
@login_required
def add_admin():
    try:
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
    except Exception as e:
        logger.error(f"Add admin error: {str(e)}")
        flash('حدث خطأ أثناء إضافة المشرف', 'danger')

    return redirect(url_for('admins'))

# إزالة مشرف
@app.route('/admins/remove/<int:admin_id>')
@login_required
def remove_admin(admin_id):
    try:
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
    except Exception as e:
        logger.error(f"Remove admin error: {str(e)}")
        flash('حدث خطأ أثناء إزالة المشرف', 'danger')

    return redirect(url_for('admins'))

# صفحة تخصيص الرسائل
@app.route('/message_customization')
@login_required
def message_customization():
    try:
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
    except Exception as e:
        logger.error(f"Message customization page error: {str(e)}")
        flash('حدث خطأ في تحميل صفحة تخصيص الرسائل', 'danger')
        return redirect(url_for('dashboard'))

# تحديث تخصيص الرسائل
@app.route('/message_customization/update', methods=['POST'])
@login_required
def update_message_customization():
    try:
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
    except Exception as e:
        logger.error(f"Update message customization error: {str(e)}")
        flash('حدث خطأ أثناء تحديث تخصيص الرسائل', 'danger')

    return redirect(url_for('message_customization'))

# صفحة الاستبدالات النصية
@app.route('/text_replacements')
@login_required
def text_replacements():
    try:
        config = load_config()
        replacements = config.get('text_replacements', [])
        return render_template('text_replacements.html', replacements=replacements)
    except Exception as e:
        logger.error(f"Text replacements page error: {str(e)}")
        flash('حدث خطأ في تحميل صفحة الاستبدالات النصية', 'danger')
        return redirect(url_for('dashboard'))

# إضافة استبدال نصي جديد
@app.route('/text_replacements/add', methods=['POST'])
@login_required
def add_text_replacement():
    try:
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
    except Exception as e:
        logger.error(f"Add text replacement error: {str(e)}")
        flash('حدث خطأ أثناء إضافة الاستبدال النصي', 'danger')

    return redirect(url_for('text_replacements'))

# حذف استبدال نصي
@app.route('/text_replacements/remove/<int:index>')
@login_required
def remove_text_replacement(index):
    try:
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
    except Exception as e:
        logger.error(f"Remove text replacement error: {str(e)}")
        flash('حدث خطأ أثناء حذف الاستبدال النصي', 'danger')

    return redirect(url_for('text_replacements'))

# معالج الأخطاء
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="الصفحة غير موجودة", code=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return render_template('error.html', error="خطأ في الخادم", code=500), 500