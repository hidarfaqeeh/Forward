"""
إعداد قاعدة البيانات للتطبيق
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# التحقق من وجود الرابط لقاعدة البيانات
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set")

# إنشاء رابط لقاعدة البيانات
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)

# إنشاء الجلسة
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(session_factory)

# إنشاء القاعدة الأساسية للنماذج
Base = declarative_base()

# دالة لتهيئة قاعدة البيانات
def init_db():
    """إنشاء جداول قاعدة البيانات"""
    try:
        from models import User, BotSettings, BotStats, TextReplacement, Blacklist, Whitelist, MessageHistory
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False

# دالة للحصول على جلسة قاعدة البيانات
def get_db():
    """الحصول على جلسة قاعدة بيانات"""
    db = Session()
    try:
        return db
    finally:
        db.close()
        
# دالة للتحقق مما إذا كان هناك مستخدم مشرف
def has_admin_user():
    """التحقق مما إذا كان هناك مستخدم مشرف في قاعدة البيانات"""
    try:
        from models import User
        db = get_db()
        admin = db.query(User).filter(User.is_admin == True).first() 
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
        
        from models import User
        from werkzeug.security import generate_password_hash
        
        db = get_db()
        try:
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin'),
                is_admin=True
            )
            db.add(admin)
            db.commit()
            logger.info("Admin user created successfully")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating admin user: {str(e)}")
            return False
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        return False