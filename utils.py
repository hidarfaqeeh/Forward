"""
وحدة برمجية للوظائف المشتركة بين مختلف أجزاء التطبيق
"""

import json
import logging
import os
import sys

# تكوين السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def load_config():
    """تحميل إعدادات البوت من ملف config.json"""
    try:
        if not os.path.exists('config.json'):
            logger.error("Config file not found")
            return create_default_config()
            
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            if not isinstance(config, dict):
                logger.error("Invalid config format")
                return create_default_config()
                
            # التحقق من وجود المفاتيح الأساسية
            required_keys = ['bot_token', 'admin_users', 'source_channel', 'target_channel']
            for key in required_keys:
                if key not in config:
                    logger.warning(f"Missing required key in config: {key}")
                    config[key] = "" if key == 'bot_token' else []
            return config
    except FileNotFoundError:
        logger.error("Config file not found")
        return {}
    except json.JSONDecodeError:
        logger.error("Invalid JSON in config file")
        return {}
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        return {}

def save_config(config):
    """حفظ الإعدادات إلى ملف config.json"""
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"خطأ في حفظ الإعدادات: {str(e)}")
        return False

def get_bot_stats():
    """جلب إحصائيات البوت"""
    # استخدام البيانات الافتراضية إذا لم يتم العثور على الإحصائيات
    from datetime import datetime
    config = load_config()

    # محاولة جلب بيانات الإحصائيات من ملف مؤقت إذا كان موجودًا
    try:
        with open('stats.json', 'r') as f:
            stats = json.load(f)
            # تحويل تنسيق التواريخ من السلاسل النصية إلى كائنات datetime
            if stats.get('started_at'):
                stats['started_at'] = datetime.fromisoformat(stats['started_at'].replace('Z', '+00:00'))
            if stats.get('last_forwarded'):
                stats['last_forwarded'] = datetime.fromisoformat(stats['last_forwarded'].replace('Z', '+00:00'))
            return stats
    except (FileNotFoundError, json.JSONDecodeError):
        # إنشاء بيانات إحصائيات متكاملة تشمل جميع المعلومات اللازمة للوحة التحكم المطورة
        default_stats = {
            # إحصائيات أساسية
            'messages_forwarded': 0,
            'messages_received': 0,
            'messages_filtered': 0,
            'started_at': datetime.now(),
            'last_forwarded': None,
            'last_updated': datetime.now(),
            'errors': 0,
            'source_channel': config.get('source_channel', 'غير محدد'),
            'target_channel': config.get('target_channel', 'غير محدد'),
            
            # إحصائيات متقدمة للفلاتر
            'filtered_by_blacklist': 0,
            'filtered_duplicates': 0,
            'filtered_by_language': 0,
            'filtered_links': 0,
            
            # إحصائيات أنواع الوسائط
            'text_messages': 0,
            'image_messages': 0,
            'video_messages': 0,
            'other_messages': 0,
            
            # إحصائيات الوقت والأداء
            'uptime': 1,  # أيام التشغيل
            'daily_average': 0,  # متوسط الرسائل اليومي
            'peak_time': '14:00',  # وقت ذروة النشاط
            'response_time': 0.3  # متوسط وقت الاستجابة بالثواني
        }
        return default_stats