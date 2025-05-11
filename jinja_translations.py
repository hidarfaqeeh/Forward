"""
Module for integrating Jinja2 templates with multilingual support
وحدة برمجية لدمج قوالب جينجا2 مع دعم تعدد اللغات
"""

from flask import request, session
from translations import get_text

def get_template_language():
    """
    Get the current user's preferred language, 
    either from the session or from the request parameters.
    
    Returns:
        str: Language code ('ar' or 'en')
    """
    # Get language from query parameter if present
    lang_param = request.args.get('lang', '')
    if lang_param in ['ar', 'en']:
        # Set it in session for future requests
        session['lang'] = lang_param
        return lang_param
    
    # Get language from session if present
    if 'lang' in session and session['lang'] in ['ar', 'en']:
        return session['lang']
    
    # Default to Arabic
    return 'ar'

def init_template_translations(app):
    """
    Initialize Jinja2 environment with translation function.
    
    Args:
        app: Flask application instance
    """
    @app.context_processor
    def inject_translations():
        """
        Add translation-related functions and variables to Jinja2 templates.
        
        Returns:
            dict: Dictionary with translation functions and variables
        """
        def t(key):
            """
            Get translated text for a key in the current language.
            
            Args:
                key (str): The translation key
                
            Returns:
                str: Translated text for the current language
            """
            lang = get_template_language()
            return get_text(key, lang)
        
        # Return functions and variables to be available in templates
        return {
            't': t,
            'current_lang': get_template_language(),
            'other_lang': 'en' if get_template_language() == 'ar' else 'ar',
            'is_rtl': get_template_language() == 'ar',
        }