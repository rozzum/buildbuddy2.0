"""
AI Processing Handler for AI Assistant Bot
Handles intelligent responses using OpenRouter AI
"""

import logging
import asyncio
from typing import Dict, List
from datetime import datetime, timedelta
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message, PhotoSize
from aiogram.fsm.context import FSMContext

from app.services.database import DatabaseService
from app.services.openrouter_service import OpenRouterService
from app.services.vision_service import VisionService

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("restart"))
async def restart_command(message: Message, state: FSMContext = None):
    """Handle /restart command with confirmation question."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Check if user has any data to reset
        user_session = db_service.get_user_session(user_id)
        has_data = any([
            user_session.get('name'),
            user_session.get('age'),
            user_session.get('interests'),
            user_session.get('preferences'),
            user_session.get('survey_completed', False)
        ])
        
        if not has_data:
            await message.answer("ℹ️ У вас пока нет сохраненных данных для сброса.")
            return
        
        # Set pending confirmation state
        db_service.update_user_field(user_id, 'pending_confirmation', 'restart')
        
        # Ask for confirmation
        confirmation_text = """🔄 **Сброс данных пользователя**

Вы уверены, что хотите сбросить все ваши данные и начать заново?

⚠️ **Это действие удалит:**
• Результаты теста предпочтений
• Сохраненные настройки
• Историю общения
• Все персональные данные

❌ **Данные нельзя будет восстановить!**

Для подтверждения напишите **"да"** или **"yes"**
Для отмены напишите **"нет"** или **"no"**"""
        
        await message.answer(confirmation_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in restart command: {e}")
        await message.answer("Произошла ошибка при выполнении команды restart.")

@router.message(lambda message: message.photo is None and message.text is not None and not message.text.startswith('/'))
async def handle_text_message(message: Message, state: FSMContext = None):
    """Handle all text messages with OpenRouter AI conversation flow."""
    try:
        # Skip if it's empty or None
        if not message.text or not message.text.strip():
            return
        
        user_id = message.from_user.id
        user_input = message.text.strip()
        
        # Initialize database service
        db_service = DatabaseService()
        user_session = db_service.get_user_session(user_id)
        
        # Check if user is in survey mode
        if user_session.get('in_survey_mode', False):
            logger.info(f"User {user_id} is in survey mode, skipping AI processing")
            return
        
        # Check for restart confirmation
        pending_confirmation = user_session.get('pending_confirmation')
        if pending_confirmation == 'restart':
            await handle_restart_confirmation(message, user_id, user_input, db_service)
            return
        
        # Use OpenRouter service for natural dialog
        openrouter_service = OpenRouterService()
        
        # Get AI response using OpenRouter
        updated_session, response = await openrouter_service.analyze_text_with_ai(user_input, user_session)
        
        # Update session with any extracted information
        if updated_session != user_session:
            for key, value in updated_session.items():
                if key not in ['user_id', 'created_at', 'updated_at'] and value != user_session.get(key):
                    if value is not None and value != "":
                        db_service.update_user_field(user_id, key, value)
                        logger.info(f"Updated field {key} = {value} for user {user_id}")
        
        # Store messages
        db_service.add_conversation_message(user_id, user_input, "user")
        db_service.add_conversation_message(user_id, response, "bot")
        
        # Send response
        await message.answer(response)
        
    except Exception as e:
        logger.error(f"Error in handle_text_message: {e}")
        await message.answer("Извините, произошла ошибка при обработке вашего сообщения. Попробуйте еще раз.")

async def handle_restart_confirmation(message: Message, user_id: int, user_input: str, db_service: DatabaseService):
    """Handle restart confirmation response."""
    try:
        user_input_lower = user_input.lower().strip()
        
        # Store user response in conversation history
        db_service.add_conversation_message(user_id, user_input, "user")
        
        if user_input_lower in ['да', 'yes', 'y', 'д']:
            # User confirmed restart - reset all data
            success = await reset_user_data(user_id, db_service)
            
            if success:
                restart_message = """✅ **Данные успешно сброшены!**

🔄 Теперь вы можете начать заново:
• Отправьте /start для начала работы
• Пройдите тест командой /test для персонализации
• Задавайте любые вопросы

Добро пожаловать в новое начало! 🚀"""
                
                db_service.add_conversation_message(user_id, restart_message, "bot")
                await message.answer(restart_message, parse_mode="Markdown")
                
                logger.info(f"User {user_id} confirmed restart - data reset successfully")
            else:
                error_message = "❌ Произошла ошибка при сбросе данных. Попробуйте еще раз."
                db_service.add_conversation_message(user_id, error_message, "bot")
                await message.answer(error_message)
                
        elif user_input_lower in ['нет', 'no', 'n', 'н']:
            # User cancelled restart
            cancel_message = """❌ **Сброс данных отменен**

✅ Ваши данные сохранены и остались без изменений.

Продолжайте использовать бота как обычно! 😊"""
            
            # Clear pending confirmation
            db_service.update_user_field(user_id, 'pending_confirmation', None)
            
            db_service.add_conversation_message(user_id, cancel_message, "bot")
            await message.answer(cancel_message, parse_mode="Markdown")
            
            logger.info(f"User {user_id} cancelled restart")
            
        else:
            # Invalid response - ask again
            invalid_message = """🤔 Не понял ваш ответ.

Для подтверждения сброса напишите **"да"** или **"yes"**
Для отмены напишите **"нет"** или **"no"**"""
            
            db_service.add_conversation_message(user_id, invalid_message, "bot")
            await message.answer(invalid_message, parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"Error handling restart confirmation: {e}")
        await message.answer("Произошла ошибка при обработке подтверждения. Попробуйте еще раз.")

async def reset_user_data(user_id: int, db_service: DatabaseService) -> bool:
    """Reset all user data and create fresh session."""
    try:
        # Get current users data
        from config import USER_DATA_FILE
        import json
        import os
        
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            user_id_str = str(user_id)
            
            # Create completely new session
            new_session = {
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'language': 'auto',
                'survey_completed': False,
                'preferences': {},
                'in_survey_mode': False,
                'start_option_chosen': None,
                'pending_confirmation': None
            }
            
            # Replace the entire session
            users_data[user_id_str] = new_session
            
            # Save updated data
            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Also clear conversation history
            try:
                from config import CONVERSATION_DATA_FILE
                
                if os.path.exists(CONVERSATION_DATA_FILE):
                    with open(CONVERSATION_DATA_FILE, 'r', encoding='utf-8') as f:
                        conversations_data = json.load(f)
                    
                    if user_id_str in conversations_data:
                        conversations_data[user_id_str] = []
                        
                        with open(CONVERSATION_DATA_FILE, 'w', encoding='utf-8') as f:
                            json.dump(conversations_data, f, indent=2, ensure_ascii=False, default=str)
                        
                        logger.info(f"Cleared conversation history for user {user_id}")
            except Exception as e:
                logger.warning(f"Could not clear conversation history: {e}")
            
            logger.info(f"Successfully reset all data for user {user_id}")
            return True
        else:
            logger.error(f"Users data file not found: {USER_DATA_FILE}")
            return False
        
    except Exception as e:
        logger.error(f"Error resetting user data: {e}")
        return False

@router.message(lambda message: message.photo is not None)
async def handle_photo_message(message: Message, state: FSMContext = None):
    """Handle photo messages with AI analysis."""
    try:
        user_id = message.from_user.id
        logger.info(f"Processing photo message from user {user_id}")
        
        # Get the largest photo (Telegram sends each photo as separate message)
        photo = max(message.photo, key=lambda p: p.file_size)
        logger.info(f"Photo info: file_id={photo.file_id}, size={photo.file_size}")
        
        # Initialize services early for media group check
        db_service = DatabaseService()
        vision_service = VisionService()
        openrouter_service = OpenRouterService()
        logger.info("Services initialized successfully")
        
        # Get user session
        user_session = db_service.get_user_session(user_id)
        
        # Check if this is a media group (multiple photos sent together)
        if hasattr(message, 'media_group_id') and message.media_group_id:
            # This is part of a media group - only process the first one
            # Check if we already processed this media group
            media_group_key = f"media_group_{message.media_group_id}"
            if user_session.get(media_group_key):
                logger.info(f"Media group {message.media_group_id} already processed, skipping")
                return
            
            # Mark this media group as processed
            db_service.update_user_field(user_id, media_group_key, True)
            
            # Send explanation for multiple photos
            if message.from_user.language_code == 'ru':
                response = """Множественные фотографии

Извините, но я могу анализировать только одну фотографию за раз.

Почему так:
• Для качественного анализа нужен фокус на одном интерьере
• Множественные фото могут создавать путаницу
• Я даю детальные рекомендации по каждому изображению

Что делать:
• Отправьте одну фотографию для анализа
• Или опишите, что именно вас интересует
• Я готов дать профессиональные советы по дизайну"""
            else:
                response = """Multiple Photos

Sorry, but I can analyze only one photo at a time.

Why:
• Quality analysis requires focus on one interior
• Multiple photos can create confusion
• I provide detailed recommendations for each image

What to do:
• Send one photo for analysis
• Or describe what interests you
• I'm ready to give professional design advice"""
            
            await message.answer(response, parse_mode="Markdown")
            logger.info(f"User {user_id} sent media group {message.media_group_id}, explained limitation")
            return
        
        # Download photo
        file_info = await message.bot.get_file(photo.file_id)
        photo_data = await message.bot.download_file(file_info.file_path)
        logger.info(f"Photo downloaded successfully, size: {len(photo_data.read())} bytes")
        
        # Reset file pointer and read photo data once
        photo_data.seek(0)
        photo_bytes = photo_data.read()
        logger.info(f"Photo data read: {len(photo_bytes)} bytes")
        
        # Check if user is in survey mode
        if user_session.get('in_survey_mode', False):
            logger.info(f"User {user_id} is in survey mode, skipping photo analysis")
            return
        
        # Basic image analysis
        try:
            image_analysis = await vision_service.analyze_image(photo_bytes)
            logger.info(f"Image analysis completed for user {user_id}: {image_analysis}")
        except Exception as e:
            logger.warning(f"Basic image analysis failed: {e}")
            image_analysis = {'description': 'Image uploaded'}
        
        # Get user's text input if any
        user_caption = message.caption or ""
        logger.info(f"User caption: '{user_caption}'")
        
        # Analyze with AI
        try:
            logger.info(f"Starting AI analysis for user {user_id}")
            updated_session, ai_response = await openrouter_service.analyze_image_with_ai(
                photo_bytes, user_caption, user_session
            )
            
            # Update session
            if updated_session != user_session:
                for key, value in updated_session.items():
                    if key not in ['user_id', 'created_at', 'updated_at'] and value != user_session.get(key):
                        if value is not None and value != "":
                            db_service.update_user_field(user_id, key, value)
            
            logger.info(f"AI analysis completed for user {user_id}, response length: {len(ai_response)}")
            
            # Ensure response fits Telegram limits
            if len(ai_response) > 3000:
                ai_response = ai_response[:3000] + "\n\n... (ответ обрезан)"
                logger.info(f"Response truncated to {len(ai_response)} characters for Telegram compatibility")
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            
            # Fallback: provide basic analysis based on image data
            try:
                basic_analysis = await vision_service.analyze_image(photo_bytes)
                logger.info(f"Basic image analysis: {basic_analysis}")
                
                # Create fallback response based on basic analysis
                if 'error' not in basic_analysis:
                    ai_response = f"""Анализ изображения (базовый)

Техническая информация:
• Формат: {basic_analysis.get('format', 'Неизвестно')}
• Размеры: {basic_analysis.get('width', '?')}x{basic_analysis.get('height', '?')} пикселей
• Цветовой режим: {basic_analysis.get('color_mode', 'Неизвестно')}

Рекомендации:
• Для профессионального анализа попробуйте отправить изображение еще раз
• Или опишите, что хотели бы узнать об этом интерьере
• Готов дать профессиональные советы по дизайну"""
                else:
                    ai_response = """Анализ изображения

Я получил ваше изображение, но возникла ошибка при анализе.

Что я могу проанализировать:
• Архитектурный стиль и период
• Цветовую палитру и материалы
• Планировочные решения
• Освещение и атмосферу
• Детали и декоративные элементы

Попробуйте отправить изображение еще раз или опишите, что хотели бы узнать об этом интерьере."""
                    
            except Exception as fallback_error:
                logger.error(f"Fallback analysis also failed: {fallback_error}")
                ai_response = """Анализ изображения

Я получил ваше изображение, но возникла ошибка при анализе.

Что я могу проанализировать:
• Архитектурный стиль и период
• Цветовую палитру и материалы
• Планировочные решения
• Освещение и атмосферу
• Детали и декоративные элементы

Попробуйте отправить изображение еще раз или опишите, что хотели бы узнать об этом интерьере."""
        
        # Store messages
        db_service.add_conversation_message(user_id, f"[Photo: {image_analysis.get('description', 'Image uploaded')}]", "user")
        db_service.add_conversation_message(user_id, ai_response, "bot")
        
        # Send response
        await message.answer(ai_response, parse_mode="Markdown")
        logger.info(f"Photo analysis response sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in handle_photo_message: {e}")
        await message.answer("Извините, произошла ошибка при анализе изображения. Попробуйте еще раз.")

@router.message(Command("help"))
async def help_command(message: Message):
    """Show help information."""
    help_text = """🏗️ **Помощь по использованию профессионального архитектора и дизайнера интерьеров**

**Основные команды:**
/start - Начать работу с ботом
/test - Пройти профессиональный тест по дизайну интерьера (русский)
/survey - Пройти профессиональный тест по дизайну интерьера (английский)
/restart - Сбросить все данные и начать заново
/help - Показать эту справку

**Что умеет профессиональный архитектор:**
📸 Анализировать фотографии интерьеров и архитектуры
💬 Отвечать на вопросы по дизайну на русском и английском
🎯 Давать персонализированные профессиональные советы
💾 Запоминать историю разговора и контекст
🏗️ Консультировать по планировке и материалам

**Профессиональная экспертиза:**
🎨 Архитектурные принципы и строительные нормы
🏠 Дизайн интерьеров премиум-класса
🌱 Устойчивый дизайн и умные технологии
💡 Теория цвета и дизайн освещения
📐 Пространственное планирование и эргономика

**Как использовать:**
1. Отправьте текст - получите профессиональный совет от архитектора
2. Отправьте фото интерьера - получите профессиональный анализ
3. Пройдите тест для персонализации дизайнерских советов
4. Используйте /restart для сброса данных

**Поддерживаемые языки:** Русский, Английский

**Источники информации:** Проверенные архитектурные принципы, отраслевые стандарты, современные тренды"""
    
    await message.answer(help_text, parse_mode="Markdown")

@router.message(Command("status"))
async def status_command(message: Message):
    """Show user status and design preferences."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        user_session = db_service.get_user_session(user_id)
        
        # Check survey completion
        survey_completed = user_session.get('survey_completed', False)
        
        if survey_completed:
            status_text = f"""📊 **Ваш профессиональный дизайнерский профиль**

✅ Профессиональный тест по дизайну интерьера пройден

🎨 **Стилевые предпочтения:**
• **Стиль:** {user_session.get('preferred_style', 'Не указано')}
• **Цвета:** {user_session.get('color_preference', 'Не указано')}
• **Материалы:** {user_session.get('material_preference', 'Не указано')}

🏠 **Пространственные решения:**
• **Тип пространства:** {user_session.get('space_type', 'Не указано')}
• **Приоритетные помещения:** {user_session.get('room_preference', 'Не указано')}
• **Планировка:** {user_session.get('layout_style', 'Не указано')}

⚙️ **Функциональность:**
• **Функции:** {user_session.get('functionality_preference', 'Не указано')}
• **Освещение:** {user_session.get('lighting_preference', 'Не указано')}
• **Хранение:** {user_session.get('storage_preference', 'Не указано')}

💰 **Проектные параметры:**
• **Бюджет:** {user_session.get('budget_range', 'Не указано')}
• **Время:** {user_session.get('timeline', 'Не указано')}
• **Приоритеты:** {user_session.get('project_priority', 'Не указано')}

🌟 **Образ жизни:**
• **Образ жизни:** {user_session.get('lifestyle', 'Не указано')}
• **Семейные потребности:** {user_session.get('family_needs', 'Не указано')}
• **Личные акценты:** {user_session.get('personal_touch', 'Не указано')}

💡 Теперь я могу давать вам профессиональные дизайнерские советы на основе ваших предпочтений!

🔄 Если хотите начать заново, используйте команду /restart"""
        else:
            status_text = """📊 **Ваш дизайнерский профиль**

❌ Профессиональный тест по дизайну интерьера не пройден

💡 Для получения профессиональных дизайнерских советов пройдите тест командой /test

🎨 **Тест включает 15 профессиональных вопросов:**
• Стилевые предпочтения (3 вопроса)
• Пространственные решения (3 вопроса)
• Функциональность (3 вопроса)
• Бюджет и время (3 вопроса)
• Образ жизни (3 вопроса)

🔄 Если хотите начать заново, используйте команду /restart"""
        
        await message.answer(status_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in status command: {e}")
        await message.answer("Произошла ошибка при получении статуса.")
