"""
نماذج قاعدة البيانات للتطبيق
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, BigInteger, ForeignKey
from db import Base

class User(Base):
    """نموذج المستخدم"""
    __tablename__ = 'tg_users'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

class BotSettings(Base):
    """نموذج إعدادات البوت"""
    __tablename__ = 'bot_settings'
    id = Column(Integer, primary_key=True)
    setting_key = Column(String(128), unique=True, nullable=False)
    setting_value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BotSettings {self.setting_key}>'

class BotStats(Base):
    """نموذج إحصائيات البوت"""
    __tablename__ = 'bot_stats'
    id = Column(Integer, primary_key=True)
    messages_forwarded = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_forwarded = Column(DateTime, nullable=True)
    errors = Column(Integer, default=0)
    
    def __repr__(self):
        return f'<BotStats {self.id}>'

class TextReplacement(Base):
    """نموذج استبدال النص"""
    __tablename__ = 'text_replacements'
    id = Column(Integer, primary_key=True)
    pattern = Column(String(255), nullable=False)
    replacement = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TextReplacement {self.pattern}>'

class Blacklist(Base):
    """نموذج القائمة السوداء"""
    __tablename__ = 'blacklist'
    id = Column(Integer, primary_key=True)
    word = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Blacklist {self.word}>'

class Whitelist(Base):
    """نموذج القائمة البيضاء"""
    __tablename__ = 'whitelist'
    id = Column(Integer, primary_key=True)
    word = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Whitelist {self.word}>'

class MessageHistory(Base):
    """نموذج سجل الرسائل"""
    __tablename__ = 'message_history'
    id = Column(Integer, primary_key=True)
    source_message_id = Column(BigInteger)
    target_message_id = Column(BigInteger)
    content_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MessageHistory {self.source_message_id} -> {self.target_message_id}>'