"""
ملف إعدادات التطبيق ويحتوي على تكوين قاعدة البيانات والمتغيرات العامة
"""

import os
import secrets
from datetime import timedelta

# إعدادات قاعدة البيانات
DATABASE_URL = os.environ.get("postgresql://_7833b8445553a4d6:_21dc1465df194c7bb8ec33ee1ae369@primary.mp31--vnbw5fmyn97t.addon.code.run:5432/_bd56d473bd07?sslmode=require")

# إعدادات عامة
SECRET_KEY = os.environ.get("SESSION_SECRET", "telegram_bot_security_key_fixed_2025")
SESSION_LIFETIME = timedelta(days=1)
DEBUG = True

# إعدادات التطبيق
PORT = 5000
HOST = '0.0.0.0'
