"""
ملف إعدادات التطبيق ويحتوي على تكوين قاعدة البيانات والمتغيرات العامة
"""

import os
import secrets
from datetime import timedelta

# إعدادات قاعدة البيانات
DATABASE_URL = os.environ.get("DATABASE_URL")

# إعدادات عامة
SECRET_KEY = os.environ.get("SESSION_SECRET", "telegram_bot_security_key_fixed_2025")
SESSION_LIFETIME = timedelta(days=1)
DEBUG = True

# إعدادات التطبيق
PORT = 5000
HOST = '0.0.0.0'