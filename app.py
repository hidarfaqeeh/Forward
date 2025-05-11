"""
تطبيق الويب الرئيسي لإدارة بوت التلجرام
"""

import logging
from flask import Flask
from config import SECRET_KEY, SESSION_LIFETIME, DEBUG, HOST, PORT

# تكوين السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إنشاء تطبيق Flask
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = SESSION_LIFETIME
app.config['SESSION_TYPE'] = 'filesystem'
app.config['DEBUG'] = DEBUG

# تهيئة قاعدة البيانات
from db import init_db, create_admin_user

# أستورد المسارات بعد تكوين التطبيق
import routes

# عند تشغيل التطبيق مباشرة
if __name__ == '__main__':
    # تهيئة قاعدة البيانات
    init_db()
    
    try:
        # إنشاء مستخدم المسؤول الافتراضي إذا لم يكن موجودًا
        create_admin_user()
        logger.info("Database and admin user initialized successfully")
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
    
    # تشغيل التطبيق
    app.run(host=HOST, port=PORT, debug=DEBUG)