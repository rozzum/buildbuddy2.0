"""
Start Command Handler for Professional Interior Design AI Assistant Bot
Handles the /start command and initial greeting
"""

import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message

from app.services.database import DatabaseService

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def start_command(message: Message):
    """Handle /start command with professional greeting."""
    try:
        user = message.from_user
        db_service = DatabaseService()
        
        # Get or create user session
        user_session = db_service.get_user_session(user.id)
        
        # Check if user has completed the survey
        survey_completed = user_session.get('survey_completed', False)
        
        if survey_completed:
            # User has completed survey - show personalized welcome
            welcome_text = f"""🏗️ **Добро пожаловать, {user.first_name}!**

Я - ваш персональный профессиональный архитектор и дизайнер интерьеров с 20+ летним опытом работы в проектах премиум-класса.

✅ **Ваш дизайнерский профиль готов!**
Теперь я знаю ваши предпочтения и могу давать профессиональные советы по дизайну интерьера.

🚀 **Что я могу для вас сделать:**
• Дать профессиональные советы по планировке
• Проанализировать фотографии интерьеров
• Рекомендовать материалы и цветовые решения
• Помочь с выбором мебели и декора
• Ответить на любые вопросы по дизайну

💡 **Просто напишите ваш вопрос или отправьте фото интерьера!**

📊 Посмотреть ваш профиль: /status
🔄 Сбросить данные: /restart
❓ Справка: /help"""
        else:
            # User hasn't completed survey - encourage to take it
            welcome_text = f"""🏗️ **Добро пожаловать, {user.first_name}!**

Я - ваш персональный профессиональный архитектор и дизайнер интерьеров с 20+ летним опытом работы.

🎨 **Мои профессиональные возможности:**
• Анализ интерьеров и архитектуры
• Консультации по планировке и дизайну
• Рекомендации по материалам и цветам
• Советы по функциональности пространства
• Ответы на любые вопросы по дизайну

💡 **Для получения персонализированных советов рекомендую пройти тест по дизайну интерьера.**

📊 **Тест включает 15 вопросов:**
• Стилевые предпочтения
• Пространственные решения  
• Функциональность
• Бюджет и время
• Образ жизни

🚀 **Начать тест:** /test
📖 **Справка:** /help

**Просто напишите ваш вопрос или отправьте фото интерьера для профессионального анализа!**"""
        
        await message.answer(welcome_text, parse_mode="Markdown")
        
        # Store welcome message in conversation history
        db_service.add_conversation_message(user.id, welcome_text, "bot")
        
        logger.info(f"User {user.id} started the bot")
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer("Sorry, I encountered an error. Please try again.")
