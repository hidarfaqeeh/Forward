"""
وحدة برمجية للترجمات متعددة اللغات للتطبيق
Module for multilingual translations for the application
"""

# قواميس الترجمة للغات المدعومة
# Translation dictionaries for supported languages

TRANSLATIONS = {
    'ar': {  # Arabic translations
        # العناصر العامة - Common elements
        'app_name': 'بوت توجيه تلجرام المتطور',
        'developer_name': 'عدي الغولي',
        'developer_channel': 'قناة المطور',
        'copyright': 'جميع الحقوق محفوظة',
        'login': 'تسجيل الدخول',
        'logout': 'تسجيل الخروج',
        'home': 'الرئيسية',
        'features': 'المميزات',
        'settings': 'الإعدادات',
        'admins': 'المشرفون',
        'dashboard': 'لوحة التحكم',
        'save': 'حفظ',
        'cancel': 'إلغاء',
        'delete': 'حذف',
        'edit': 'تعديل',
        'add': 'إضافة',
        
        # صفحة الرئيسية - Home page
        'welcome_title': 'مرحباً بك في بوت توجيه تلجرام المتطور',
        'welcome_subtitle': 'أداة متطورة لإدارة وتوجيه الرسائل بين قنوات تلجرام',
        'get_started': 'البدء الآن',
        'learn_more': 'تعرف على المزيد',
        
        # صفحة تسجيل الدخول - Login page
        'login_title': 'تسجيل الدخول',
        'username': 'اسم المستخدم',
        'password': 'كلمة المرور',
        'remember_me': 'تذكرني',
        'login_button': 'دخول',
        'login_error': 'اسم المستخدم أو كلمة المرور غير صحيحة',
        
        # صفحة لوحة التحكم - Dashboard
        'dashboard_welcome': 'مرحباً،',
        'forwarding_active': 'التوجيه نشط',
        'forwarding_inactive': 'التوجيه متوقف',
        'last_update': 'آخر تحديث:',
        'not_forwarded_yet': 'لم يتم التوجيه بعد',
        'stop_forwarding': 'إيقاف التوجيه',
        'start_forwarding': 'تشغيل التوجيه',
        'refresh': 'تحديث',
        'bot_performance': 'أداء البوت',
        'today': 'اليوم',
        'week': 'الأسبوع',
        'month': 'الشهر',
        'forwarded_messages': 'رسائل تم توجيهها',
        'today_increase': 'اليوم',
        'start_date': 'تاريخ بدء التشغيل',
        'operation_days': 'يوم من التشغيل',
        'last_forwarding': 'آخر توجيه',
        'hours_ago': 'منذ',
        'hour': 'ساعة',
        'errors': 'أخطاء',
        'this_week_increase': 'هذا الأسبوع',
        
        # إحصائيات - Statistics
        'statistics_title': 'الإحصائيات التفصيلية',
        'last_updated': 'آخر تحديث:',
        'message_stats': 'إحصائيات الرسائل',
        'total_received': 'إجمالي الرسائل المستلمة:',
        'total_forwarded': 'إجمالي الرسائل الموجهة:',
        'rejected_messages': 'الرسائل المرفوضة:',
        'forwarding_success_rate': 'معدل نجاح التوجيه:',
        'filter_reasons': 'أسباب الفلترة',
        'blacklisted_words': 'كلمات محظورة:',
        'duplicate_messages': 'رسائل مكررة:',
        'unsupported_language': 'لغة غير مدعومة:',
        'blocked_links': 'روابط محظورة:',
        'media_types': 'أنواع الوسائط',
        'texts': 'نصوص:',
        'images': 'صور:',
        'videos': 'فيديوهات:',
        'files_others': 'ملفات وأخرى:',
        'time_stats': 'إحصائيات الوقت',
        'uptime': 'فترة التشغيل:',
        'day': 'يوم',
        'daily_average': 'معدل الرسائل اليومي:',
        'peak_time': 'وقت ذروة النشاط:',
        'response_time': 'معدل الاستجابة:',
        'second': 'ثانية',
        
        # القنوات والإعدادات - Channels and settings
        'channels_forwarding_settings': 'القنوات وإعدادات التوجيه',
        'source_channel': 'القناة المصدر',
        'target_channel': 'القناة الهدف',
        'config_details': 'تفاصيل التكوين',
        'forwarding_mode': 'وضع التوجيه:',
        'copy_mode': 'نسخ',
        'forward_mode': 'توجيه',
        'forwarding_status': 'حالة التوجيه:',
        'active': 'نشط',
        'inactive': 'متوقف',
        'active_filters': 'فلاتر نشطة:',
        'filters': 'فلاتر',
        'time_period': 'الفترة الزمنية:',
        
        # الإشعارات والتحديثات - Notifications and updates
        'latest_updates': 'أحدث التحديثات',
        'forwarded_success': 'تم توجيه رسائل بنجاح',
        'ago': 'منذ',
        'hours': 'ساعات',
        'hour': 'ساعة',
        'filters_updated': 'تم تحديث إعدادات الفلاتر',
        'forwarding_error': 'تم تسجيل خطأ في التوجيه',
        'day': 'يوم',
        'view_all_updates': 'عرض جميع التحديثات',
        
        # الفلاتر النشطة - Active filters
        'active_filters_title': 'الفلاتر النشطة',
        'edit_filters': 'تعديل الفلاتر',
        'filter_type': 'نوع الفلتر',
        'status': 'الحالة',
        'details': 'التفاصيل',
        'language_filter': 'فلتر اللغة',
        'arabic_only': 'اللغة العربية فقط',
        'words_filter': 'فلتر الكلمات',
        'blacklisted_words_count': 'كلمات محظورة',
        'media_filter': 'فلتر الوسائط',
        'inactive': 'غير نشط',
        'links_filter': 'فلتر الروابط',
        'remove_buttons_links': 'إزالة الأزرار والروابط',
        'duplication_filter': 'منع التكرار',
        'remember_duration': 'التذكر لمدة',
        'hours': 'ساعة',
        
        # المهام السريعة - Quick tasks
        'quick_tasks': 'المهام السريعة',
        'perform_task': 'تنفيذ',
        'clear_cache': 'مسح الذاكرة المؤقتة',
        'test_connection': 'اختبار الاتصال',
        'restart_bot': 'إعادة تشغيل البوت',
        'backup_settings': 'نسخ احتياطي للإعدادات',
        
        # صفحة المميزات - Features page
        'features_title': 'مميزات بوت تلجرام المتطور',
        'features_subtitle': 'استكشف الإمكانيات المتقدمة للبوت واكتشف كيف يمكن أن يساعدك في إدارة قنواتك بكفاءة أكبر',
        'all_features': 'جميع المميزات في مكان واحد',
        'features_intro': 'استعرض جميع الميزات الرائعة التي يقدمها البوت لإدارة قنوات تلجرام الخاصة بك',
        
        # ميزة التوجيه الذكي - Smart forwarding feature
        'main_feature': 'الميزة الرئيسية',
        'smart_message_forwarding': 'التوجيه الذكي للرسائل',
        'forwarding_description': 'قم بتوجيه الرسائل بين قنوات تلجرام المختلفة بشكل ذكي مع خيارات متعددة للتحكم في طريقة العرض والتوجيه.',
        'copy_mode_feature': 'وضع النسخ',
        'copy_mode_desc': 'نسخ الرسائل بشكل كامل دون ظهور مصدر الرسالة الأصلي.',
        'forward_mode_feature': 'وضع التوجيه',
        'forward_mode_desc': 'إعادة توجيه الرسائل مع الإشارة إلى مصدرها الأصلي.',
        'forwarding_speed': 'سرعة التوجيه',
        'forwarding_speed_desc': 'التوجيه الفوري للرسائل بمجرد وصولها إلى القناة المصدر.',
        'media_support': 'دعم جميع أنواع الوسائط',
        'media_support_desc': 'توجيه النصوص، الصور، الفيديوهات، الملفات وغيرها.',
        
        # ميزة فلترة المحتوى - Content filtering feature
        'smart_filtering': 'تصفية ذكية',
        'content_filtering': 'فلترة محتوى الرسائل',
        'filtering_description': 'تحكم بشكل كامل في المحتوى الذي يتم توجيهه من خلال مجموعة متنوعة من الفلاتر الذكية التي تضمن جودة المحتوى.',
        'language_filter_feature': 'فلتر اللغة',
        'language_filter_desc': 'تصفية الرسائل حسب اللغة المستخدمة مع دعم القائمة البيضاء والسوداء.',
        'blacklist_feature': 'منع الكلمات المحظورة',
        'blacklist_desc': 'إنشاء قائمة بالكلمات المحظورة لمنع توجيه الرسائل التي تحتوي عليها.',
        'media_filter_feature': 'فلتر الوسائط',
        'media_filter_desc': 'تحديد أنواع الوسائط المسموح بها (صور، فيديوهات، ملفات، روابط).',
        'duplicate_filter_feature': 'منع الرسائل المكررة',
        'duplicate_filter_desc': 'التعرف التلقائي على الرسائل المكررة ومنع توجيهها مرة أخرى.',
        
        # ميزة تخصيص النصوص - Text customization feature
        'content_customization': 'تخصيص محتوى',
        'text_links_customization': 'تخصيص النصوص والروابط',
        'customization_description': 'قم بتعديل محتوى الرسائل قبل توجيهها، واستبدل النصوص والروابط بشكل تلقائي لضمان التحكم الكامل في المحتوى.',
        'text_replacement_feature': 'استبدال النصوص',
        'text_replacement_desc': 'استبدال كلمات أو عبارات محددة بنصوص أخرى قبل التوجيه.',
        'link_cleaner_feature': 'تنظيف الروابط',
        'link_cleaner_desc': 'إزالة أو تعديل الروابط بشكل تلقائي لمنع تسرب قنوات خارجية.',
        'custom_templates_feature': 'نماذج مخصصة',
        'custom_templates_desc': 'إضافة محتوى ثابت أو نماذج نصية يتم دمجها مع الرسائل الموجهة.',
        'button_management_feature': 'إدارة الأزرار التفاعلية',
        'button_management_desc': 'التحكم في الأزرار التفاعلية مع إمكانية إزالتها أو تعديلها.',
        
        # ميزة أدوات التحكم - Control tools feature
        'advanced_management': 'إدارة متقدمة',
        'control_scheduling_tools': 'أدوات التحكم والجدولة',
        'control_description': 'سيطر على عملية التوجيه بشكل كامل من خلال مجموعة متكاملة من أدوات التحكم، الجدولة، والتأخير.',
        'quick_toggle_feature': 'التفعيل/التعطيل السريع',
        'quick_toggle_desc': 'تفعيل أو تعطيل التوجيه بشكل فوري عند الحاجة.',
        'delay_feature': 'التأخير بين الرسائل',
        'delay_desc': 'ضبط فترة زمنية بين توجيه كل رسالة لتجنب الإغراق.',
        'work_hours_feature': 'جدولة أوقات العمل',
        'work_hours_desc': 'تحديد الأوقات التي يعمل فيها البوت وتوجيه الرسائل.',
        'scheduled_posting_feature': 'النشر المجدول',
        'scheduled_posting_desc': 'إعداد رسائل مجدولة ليتم نشرها في أوقات محددة مسبقاً.',
        
        # ميزة الترجمة التلقائية - Automatic translation feature
        'smart_translation': 'ترجمة ذكية',
        'automatic_translation': 'الترجمة التلقائية',
        'translation_description': 'قم بترجمة محتوى الرسائل بشكل تلقائي إلى اللغة المطلوبة قبل توجيهها، مما يتيح لك الوصول إلى جمهور أوسع.',
        'multi_language_feature': 'دعم لغات متعددة',
        'multi_language_desc': 'ترجمة المحتوى بين العديد من اللغات العالمية.',
        'auto_detection_feature': 'كشف اللغة التلقائي',
        'auto_detection_desc': 'التعرف التلقائي على لغة النص الأصلي قبل الترجمة.',
        'custom_settings_feature': 'إعدادات مخصصة',
        'custom_settings_desc': 'تخصيص إعدادات الترجمة حسب احتياجاتك ومتطلبات قناتك.',
        'format_preservation_feature': 'الحفاظ على التنسيق',
        'format_preservation_desc': 'الحفاظ على تنسيق النص وتخطيطه بعد الترجمة.',
        
        # ميزة الإحصائيات والتقارير - Statistics and reports feature
        'data_analysis': 'تحليل البيانات',
        'statistics_reports': 'الإحصائيات والتقارير',
        'stats_description': 'احصل على رؤية شاملة لأداء البوت من خلال إحصائيات دقيقة وتقارير تفصيلية حول نشاط الرسائل والتوجيه.',
        'realtime_dashboard_feature': 'لوحة معلومات مباشرة',
        'realtime_dashboard_desc': 'عرض الإحصائيات في الوقت الفعلي على لوحة معلومات سهلة الاستخدام.',
        'activity_log_feature': 'سجل النشاط',
        'activity_log_desc': 'تتبع جميع العمليات واستعراض سجل نشاط البوت بشكل تفصيلي.',
        'analytical_reports_feature': 'تقارير تحليلية',
        'analytical_reports_desc': 'تحليل أداء البوت مع تقارير دورية مفصلة عن النشاط.',
        'notifications_alerts_feature': 'إشعارات وتنبيهات',
        'notifications_alerts_desc': 'تلقي إشعارات حول أداء البوت والأحداث المهمة.',
        
        # ميزات إضافية - Additional features
        'additional_features': 'ميزات إضافية',
        'access_control_feature': 'تحكم كامل بالوصول',
        'access_control_desc': 'إدارة المشرفين والصلاحيات بشكل مرن مع تأمين عالي للبوت.',
        'advanced_commands_feature': 'أوامر متقدمة',
        'advanced_commands_desc': 'واجهة أوامر سهلة للتحكم بالبوت مباشرة من تطبيق تلجرام.',
        'scalability_feature': 'قابلية التوسع',
        'scalability_desc': 'بنية مرنة تسمح بإضافة ميزات جديدة وتكامل مع خدمات أخرى.',
        'back_to_top': 'العودة للأعلى',
        
        # الإعدادات - Settings
        'bot_settings': 'إعدادات البوت',
        'general_settings': 'الإعدادات العامة',
        'bot_token': 'توكن البوت',
        'change': 'تغيير',
        'channel_settings': 'إعدادات القنوات',
        'source_channel': 'القناة المصدر',
        'target_channel': 'القناة الهدف',
        'forwarding_settings': 'إعدادات التوجيه',
        'forwarding_mode': 'وضع التوجيه',
        'copy': 'نسخ',
        'forward': 'توجيه',
        'auto_start': 'تشغيل تلقائي',
        'advanced_settings': 'إعدادات متقدمة',
        'save_settings': 'حفظ الإعدادات',
        
        # المشرفين - Admins
        'manage_admins': 'إدارة المشرفين',
        'current_admins': 'المشرفون الحاليون',
        'admin_name': 'اسم المشرف',
        'admin_id': 'معرف المشرف',
        'actions': 'إجراءات',
        'remove': 'إزالة',
        'add_new_admin': 'إضافة مشرف جديد',
        'admin_user_id': 'معرف المستخدم',
        'add_admin': 'إضافة مشرف',
        
        # رسائل الحالة - Status messages
        'settings_saved': 'تم حفظ الإعدادات بنجاح',
        'admin_added': 'تمت إضافة المشرف بنجاح',
        'admin_removed': 'تمت إزالة المشرف بنجاح',
        'bot_started': 'تم تشغيل البوت بنجاح',
        'bot_stopped': 'تم إيقاف البوت بنجاح',
        'error_occurred': 'حدث خطأ',
    },
    
    'en': {  # English translations
        # Common elements
        'app_name': 'Advanced Telegram Forwarding Bot',
        'developer_name': 'Oday Al-Gholi',
        'developer_channel': 'Developer Channel',
        'copyright': 'All Rights Reserved',
        'login': 'Login',
        'logout': 'Logout',
        'home': 'Home',
        'features': 'Features',
        'settings': 'Settings',
        'admins': 'Admins',
        'dashboard': 'Dashboard',
        'save': 'Save',
        'cancel': 'Cancel',
        'delete': 'Delete',
        'edit': 'Edit',
        'add': 'Add',
        
        # Home page
        'welcome_title': 'Welcome to Advanced Telegram Forwarding Bot',
        'welcome_subtitle': 'An advanced tool for managing and forwarding messages between Telegram channels',
        'get_started': 'Get Started',
        'learn_more': 'Learn More',
        
        # Login page
        'login_title': 'Login',
        'username': 'Username',
        'password': 'Password',
        'remember_me': 'Remember Me',
        'login_button': 'Login',
        'login_error': 'Username or password is incorrect',
        
        # Dashboard
        'dashboard_welcome': 'Welcome,',
        'forwarding_active': 'Forwarding Active',
        'forwarding_inactive': 'Forwarding Inactive',
        'last_update': 'Last update:',
        'not_forwarded_yet': 'Not forwarded yet',
        'stop_forwarding': 'Stop Forwarding',
        'start_forwarding': 'Start Forwarding',
        'refresh': 'Refresh',
        'bot_performance': 'Bot Performance',
        'today': 'Today',
        'week': 'Week',
        'month': 'Month',
        'forwarded_messages': 'Forwarded Messages',
        'today_increase': 'Today',
        'start_date': 'Start Date',
        'operation_days': 'days of operation',
        'last_forwarding': 'Last Forwarding',
        'hours_ago': 'ago',
        'hour': 'hour',
        'errors': 'Errors',
        'this_week_increase': 'This week',
        
        # Statistics
        'statistics_title': 'Detailed Statistics',
        'last_updated': 'Last updated:',
        'message_stats': 'Message Statistics',
        'total_received': 'Total Messages Received:',
        'total_forwarded': 'Total Messages Forwarded:',
        'rejected_messages': 'Rejected Messages:',
        'forwarding_success_rate': 'Forwarding Success Rate:',
        'filter_reasons': 'Filter Reasons',
        'blacklisted_words': 'Blacklisted Words:',
        'duplicate_messages': 'Duplicate Messages:',
        'unsupported_language': 'Unsupported Language:',
        'blocked_links': 'Blocked Links:',
        'media_types': 'Media Types',
        'texts': 'Texts:',
        'images': 'Images:',
        'videos': 'Videos:',
        'files_others': 'Files & Others:',
        'time_stats': 'Time Statistics',
        'uptime': 'Uptime:',
        'day': 'day',
        'daily_average': 'Daily Average:',
        'peak_time': 'Peak Activity Time:',
        'response_time': 'Response Time:',
        'second': 'second',
        
        # Channels and settings
        'channels_forwarding_settings': 'Channels & Forwarding Settings',
        'source_channel': 'Source Channel',
        'target_channel': 'Target Channel',
        'config_details': 'Configuration Details',
        'forwarding_mode': 'Forwarding Mode:',
        'copy_mode': 'Copy',
        'forward_mode': 'Forward',
        'forwarding_status': 'Forwarding Status:',
        'active': 'Active',
        'inactive': 'Inactive',
        'active_filters': 'Active Filters:',
        'filters': 'filters',
        'time_period': 'Time Period:',
        
        # Notifications and updates
        'latest_updates': 'Latest Updates',
        'forwarded_success': 'Successfully forwarded messages',
        'ago': 'ago',
        'hours': 'hours',
        'hour': 'hour',
        'filters_updated': 'Filter settings updated',
        'forwarding_error': 'Forwarding error recorded',
        'day': 'day',
        'view_all_updates': 'View All Updates',
        
        # Active filters
        'active_filters_title': 'Active Filters',
        'edit_filters': 'Edit Filters',
        'filter_type': 'Filter Type',
        'status': 'Status',
        'details': 'Details',
        'language_filter': 'Language Filter',
        'arabic_only': 'Arabic only',
        'words_filter': 'Words Filter',
        'blacklisted_words_count': 'blacklisted words',
        'media_filter': 'Media Filter',
        'inactive': 'Inactive',
        'links_filter': 'Links Filter',
        'remove_buttons_links': 'Remove buttons and links',
        'duplication_filter': 'Duplication Filter',
        'remember_duration': 'Remember for',
        'hours': 'hours',
        
        # Quick tasks
        'quick_tasks': 'Quick Tasks',
        'perform_task': 'Perform',
        'clear_cache': 'Clear Cache',
        'test_connection': 'Test Connection',
        'restart_bot': 'Restart Bot',
        'backup_settings': 'Backup Settings',
        
        # Features page
        'features_title': 'Advanced Telegram Bot Features',
        'features_subtitle': 'Explore the advanced capabilities of the bot and discover how it can help you manage your channels more efficiently',
        'all_features': 'All Features in One Place',
        'features_intro': 'Explore all the amazing features offered by the bot to manage your Telegram channels',
        
        # Smart forwarding feature
        'main_feature': 'Main Feature',
        'smart_message_forwarding': 'Smart Message Forwarding',
        'forwarding_description': 'Forward messages between different Telegram channels intelligently with multiple options to control display and forwarding methods.',
        'copy_mode_feature': 'Copy Mode',
        'copy_mode_desc': 'Copy messages completely without showing the original message source.',
        'forward_mode_feature': 'Forwarding Mode',
        'forward_mode_desc': 'Forward messages with reference to their original source.',
        'forwarding_speed': 'Forwarding Speed',
        'forwarding_speed_desc': 'Instant forwarding of messages as soon as they arrive at the source channel.',
        'media_support': 'All Media Types Support',
        'media_support_desc': 'Forward texts, images, videos, files, and more.',
        
        # Content filtering feature
        'smart_filtering': 'Smart Filtering',
        'content_filtering': 'Message Content Filtering',
        'filtering_description': 'Full control over forwarded content through a variety of smart filters ensuring content quality.',
        'language_filter_feature': 'Language Filter',
        'language_filter_desc': 'Filter messages based on language with whitelist and blacklist support.',
        'blacklist_feature': 'Blacklisted Words',
        'blacklist_desc': 'Create a list of blacklisted words to prevent forwarding messages containing them.',
        'media_filter_feature': 'Media Filter',
        'media_filter_desc': 'Specify allowed media types (images, videos, files, links).',
        'duplicate_filter_feature': 'Duplicate Message Prevention',
        'duplicate_filter_desc': 'Automatically identify duplicate messages and prevent re-forwarding them.',
        
        # Text customization feature
        'content_customization': 'Content Customization',
        'text_links_customization': 'Text and Links Customization',
        'customization_description': 'Modify message content before forwarding, automatically replace text and links to ensure full control over content.',
        'text_replacement_feature': 'Text Replacement',
        'text_replacement_desc': 'Replace specific words or phrases with other text before forwarding.',
        'link_cleaner_feature': 'Link Cleaning',
        'link_cleaner_desc': 'Automatically remove or modify links to prevent external channel leakage.',
        'custom_templates_feature': 'Custom Templates',
        'custom_templates_desc': 'Add fixed content or text templates to be merged with forwarded messages.',
        'button_management_feature': 'Interactive Button Management',
        'button_management_desc': 'Control interactive buttons with the ability to remove or modify them.',
        
        # Control tools feature
        'advanced_management': 'Advanced Management',
        'control_scheduling_tools': 'Control and Scheduling Tools',
        'control_description': 'Control the forwarding process completely through an integrated set of control, scheduling, and delay tools.',
        'quick_toggle_feature': 'Quick Enable/Disable',
        'quick_toggle_desc': 'Enable or disable forwarding instantly when needed.',
        'delay_feature': 'Message Delay',
        'delay_desc': 'Set a time period between forwarding each message to avoid flooding.',
        'work_hours_feature': 'Working Hours Schedule',
        'work_hours_desc': 'Specify times when the bot works and forwards messages.',
        'scheduled_posting_feature': 'Scheduled Posting',
        'scheduled_posting_desc': 'Set up scheduled messages to be posted at predetermined times.',
        
        # Automatic translation feature
        'smart_translation': 'Smart Translation',
        'automatic_translation': 'Automatic Translation',
        'translation_description': 'Automatically translate message content to the desired language before forwarding, allowing you to reach a wider audience.',
        'multi_language_feature': 'Multiple Languages Support',
        'multi_language_desc': 'Translate content between many world languages.',
        'auto_detection_feature': 'Automatic Language Detection',
        'auto_detection_desc': 'Automatically detect the original text language before translation.',
        'custom_settings_feature': 'Custom Settings',
        'custom_settings_desc': 'Customize translation settings according to your needs and channel requirements.',
        'format_preservation_feature': 'Format Preservation',
        'format_preservation_desc': 'Maintain text formatting and layout after translation.',
        
        # Statistics and reports feature
        'data_analysis': 'Data Analysis',
        'statistics_reports': 'Statistics and Reports',
        'stats_description': 'Get a comprehensive view of bot performance through accurate statistics and detailed reports on message and forwarding activity.',
        'realtime_dashboard_feature': 'Real-time Dashboard',
        'realtime_dashboard_desc': 'Display real-time statistics on an easy-to-use dashboard.',
        'activity_log_feature': 'Activity Log',
        'activity_log_desc': 'Track all operations and view detailed bot activity logs.',
        'analytical_reports_feature': 'Analytical Reports',
        'analytical_reports_desc': 'Analyze bot performance with detailed periodic reports on activity.',
        'notifications_alerts_feature': 'Notifications and Alerts',
        'notifications_alerts_desc': 'Receive notifications about bot performance and important events.',
        
        # Additional features
        'additional_features': 'Additional Features',
        'access_control_feature': 'Complete Access Control',
        'access_control_desc': 'Flexible management of administrators and permissions with high bot security.',
        'advanced_commands_feature': 'Advanced Commands',
        'advanced_commands_desc': 'Easy command interface to control the bot directly from Telegram app.',
        'scalability_feature': 'Scalability',
        'scalability_desc': 'Flexible architecture allows adding new features and integration with other services.',
        'back_to_top': 'Back to Top',
        
        # Settings
        'bot_settings': 'Bot Settings',
        'general_settings': 'General Settings',
        'bot_token': 'Bot Token',
        'change': 'Change',
        'channel_settings': 'Channel Settings',
        'source_channel': 'Source Channel',
        'target_channel': 'Target Channel',
        'forwarding_settings': 'Forwarding Settings',
        'forwarding_mode': 'Forwarding Mode',
        'copy': 'Copy',
        'forward': 'Forward',
        'auto_start': 'Auto Start',
        'advanced_settings': 'Advanced Settings',
        'save_settings': 'Save Settings',
        
        # Admins
        'manage_admins': 'Manage Administrators',
        'current_admins': 'Current Administrators',
        'admin_name': 'Admin Name',
        'admin_id': 'Admin ID',
        'actions': 'Actions',
        'remove': 'Remove',
        'add_new_admin': 'Add New Administrator',
        'admin_user_id': 'User ID',
        'add_admin': 'Add Admin',
        
        # Status messages
        'settings_saved': 'Settings saved successfully',
        'admin_added': 'Administrator added successfully',
        'admin_removed': 'Administrator removed successfully',
        'bot_started': 'Bot started successfully',
        'bot_stopped': 'Bot stopped successfully',
        'error_occurred': 'An error occurred',
    }
}

def get_text(key, lang='ar'):
    """
    Get translated text for a specific key in the specified language.
    
    Args:
        key (str): The translation key to look up
        lang (str): The language code ('ar' for Arabic, 'en' for English)
        
    Returns:
        str: The translated text, or the key itself if translation not found
    """
    # Validate inputs
    if not isinstance(key, str):
        key = str(key)
    
    # Ensure lang is a valid language code
    if not isinstance(lang, str) or lang not in TRANSLATIONS:
        lang = 'ar'  # Default to Arabic if language not supported or invalid
        
    return TRANSLATIONS[lang].get(key, key)