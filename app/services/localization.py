"""
Localization Service for AI Assistant Bot
Handles language detection and localization
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Language detection patterns
RUSSIAN_CHARS = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
ENGLISH_CHARS = set('abcdefghijklmnopqrstuvwxyz')

def get_user_locale(user_id: int) -> str:
    """
    Get user's preferred language.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Language code: 'ru' for Russian, 'en' for English
    """
    # For now, return 'en' as default
    # This can be enhanced to store user preferences
    return 'en'

def detect_language(text: str) -> str:
    """
    Detect language from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Language code: 'ru' for Russian, 'en' for English
    """
    if not text:
        return 'en'
    
    text_lower = text.lower()
    russian_count = sum(1 for char in text_lower if char in RUSSIAN_CHARS)
    english_count = sum(1 for char in text_lower if char in ENGLISH_CHARS)
    
    if russian_count > english_count:
        return 'ru'
    else:
        return 'en'

def t(key: str, locale: str = 'en', **kwargs) -> str:
    """
    Get localized text.
    
    Args:
        key: Translation key
        locale: Language code
        **kwargs: Format parameters
        
    Returns:
        Localized text
    """
    translations = {
        'welcome': {
            'en': 'Welcome! I\'m your AI assistant. How can I help you?',
            'ru': 'Добро пожаловать! Я ваш ИИ ассистент. Как я могу вам помочь?'
        },
        'photo_analyzed': {
            'en': 'Photo analyzed!',
            'ru': 'Фото проанализировано!'
        },
        'survey_suggestion': {
            'en': 'For more personalized advice, I recommend taking a short survey. Type "survey" to begin.',
            'ru': 'Для получения более персонализированных советов, рекомендую пройти короткий тест. Напишите "тест" чтобы начать.'
        },
        'error_processing': {
            'en': 'I apologize, but I encountered an error processing your request. Please try again.',
            'ru': 'Извините, но произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова.'
        }
    }
    
    if key in translations and locale in translations[key]:
        text = translations[key][locale]
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                logger.warning(f"Missing format parameters for key: {key}")
        return text
    
    # Return key if translation not found
    return key
