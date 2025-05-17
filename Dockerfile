Process terminated with exit code 0# استخدم صورة بايثون خفيفة
FROM python:3.11-slim

# إعداد بيئة العمل
WORKDIR /app

# تثبيت أدوات النظام المطلوبة (gcc مفيد لبعض الحزم)
RUN apt-get update && apt-get install -y gcc && apt-get clean

# نسخ ملفات المشروع
COPY . .

# تثبيت التبعيات (يفضل استخدام requirements.txt إذا كان موجوداً)
RUN pip install --upgrade pip \
    && if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# إذا كنت تستخدم poetry بدلاً من requirements.txt فعّل السطر التالي:
# RUN pip install poetry && poetry install --no-dev

# تعيين متغيرات البيئة (اختياري)
ENV PYTHONUNBUFFERED=1

# الأمر الافتراضي لتشغيل المشروع (عدله حسب الملف الرئيسي)
CMD ["python", "main.py"]
