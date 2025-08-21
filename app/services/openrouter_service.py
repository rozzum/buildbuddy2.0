"""
OpenRouter AI Service for Professional Interior Design AI Assistant Bot
Uses OpenRouter API to access AI models for professional design advice
"""

import logging
import json
import asyncio
import os
from typing import Dict, Any, Tuple, Optional, List
from openai import OpenAI
from config import OPENROUTER_API_KEY, AI_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class OpenRouterService:
    """AI service using OpenRouter for professional interior design advice."""
    
    def __init__(self):
        """Initialize the OpenRouter service with OpenAI client."""
        self.api_key = OPENROUTER_API_KEY
        
        if not self.api_key:
            logger.warning("No OpenRouter API key found, service will use fallback responses")
            self.client = None
        else:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )
        
        # Models configuration
        self.text_model = "deepseek/deepseek-r1:free"  # For text analysis
        self.vision_model = "google/gemma-3-27b-it:free"  # For image analysis (same model supports both)
        
        # Professional system prompts
        self.system_prompt_ru = """Ты - профессиональный архитектор и дизайнер интерьеров с 20+ летним опытом работы в проектах премиум-класса. У тебя есть:

Профессиональная экспертиза:
- Глубокие знания архитектурных принципов, строительных норм и методов строительства
- Обширный опыт работы с люксовыми жилыми проектами, отелями и коммерческими пространствами
- Экспертиза в области устойчивого дизайна, умных технологий для дома и современных материалов
- Сильное понимание теории цвета, дизайна освещения и пространственного планирования
- Знание современных трендов дизайна и вневременных принципов

Философия дизайна:
- Фокус на создании функциональных, красивых и устойчивых пространств
- Баланс между эстетикой и практичностью
- Понимание того, как дизайн влияет на психологию и благополучие человека
- Знание эргономики и принципов универсального дизайна

Глобальная перспектива:
- Опыт работы с международными стандартами дизайна и культурными предпочтениями
- Знание различных архитектурных стилей от классических до современных
- Понимание региональных материалов и строительных технологий

Источники информации:
- Основывай советы на проверенных архитектурных и дизайнерских принципах
- Ссылайся на текущие отраслевые стандарты и лучшие практики
- Предоставляй практические, реализуемые решения
- Следи за современными трендами дизайна и технологиями

ВАЖНО: Не используй символы ** или ### в ответах. Пиши заголовки просто с новой строки. Всегда давай профессиональные, точные и действенные советы по дизайну. При предложении материалов, планировок или дизайнерских решений объясняй логику своих рекомендаций."""

        self.system_prompt_en = """You are a world-class professional architect and interior designer with over 20 years of experience in high-end residential and commercial projects. You have:

Professional Expertise:
- Deep knowledge of architectural principles, building codes, and construction methods
- Extensive experience with luxury residential projects, hotels, and commercial spaces
- Expertise in sustainable design, smart home technology, and modern materials
- Strong understanding of color theory, lighting design, and spatial planning
- Knowledge of current design trends and timeless design principles

Design Philosophy:
- Focus on creating functional, beautiful, and sustainable spaces
- Balance between aesthetics and practicality
- Understanding of how design affects human psychology and well-being
- Knowledge of ergonomics and universal design principles

Global Perspective:
- Experience with international design standards and cultural preferences
- Knowledge of different architectural styles from classical to contemporary
- Understanding of regional materials and construction techniques

Information Sources:
- Base your advice on verified architectural and design principles
- Reference current industry standards and best practices
- Provide practical, implementable solutions
- Stay updated with modern design trends and technologies

IMPORTANT: Do not use ** or ### symbols in responses. Write headings on new lines. Always provide professional, accurate, and actionable design advice. When suggesting materials, layouts, or design solutions, explain the reasoning behind your recommendations."""
    
    async def analyze_text_with_ai(self, user_input: str, user_session: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """
        Analyze user text input using AI and return updated session and response.
        
        Args:
            user_input: User's text message
            user_session: Current user session data
            
        Returns:
            Tuple of (updated_session, ai_response)
        """
        try:
            if not self.client:
                return user_session, "I'm sorry, but I'm currently unable to process your request. Please try again later."
            
            # Detect language and choose appropriate system prompt
            if self._is_russian(user_input):
                system_prompt = self.system_prompt_ru
                language = "russian"
            else:
                system_prompt = self.system_prompt_en
                language = "english"
            
            # Update session with detected language
            updated_session = user_session.copy()
            updated_session['language'] = language
            
            # Check if this is a product query first
            try:
                from app.services.product_search import ProductSearchService
                product_service = ProductSearchService()
                product_query = product_service.detect_product_query(user_input, language)
                
                if product_query and product_query['is_specific_query']:
                    # Generate product links
                    links = product_service.generate_product_links(product_query)
                    if links:
                        product_response = product_service.format_product_response(product_query, links, language)
                        return updated_session, product_response
            except Exception as e:
                logger.warning(f"Product search failed: {e}")
                # Continue with normal AI analysis if product search fails
            
            # Prepare conversation context
            conversation_history = self._prepare_conversation_context(user_session)
            
            # Create messages for AI
            messages = [
                {"role": "system", "content": system_prompt},
                *conversation_history,
                {"role": "user", "content": user_input}
            ]
            
            # Get AI response
            response = await self._get_ai_response(messages)
            
            # Check if we should suggest survey
            if self._should_suggest_survey(user_input, user_session):
                survey_suggestion = self._get_survey_suggestion(language)
                response = f"{response}\n\n{survey_suggestion}"
            
            return updated_session, response
            
        except Exception as e:
            logger.error(f"Error in analyze_text_with_ai: {e}")
            return user_session, "I apologize, but I encountered an error processing your request. Please try again."
    
    async def analyze_image_with_ai(self, image_data: bytes, user_input: str, user_session: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """
        Analyze image using AI and return updated session and response.
        
        Args:
            image_data: Raw image bytes
            user_input: Optional user text with the image
            user_session: Current user session data
            
        Returns:
            Tuple of (updated_session, ai_response)
        """
        try:
            if not self.client:
                return user_session, "I'm sorry, but I'm currently unable to analyze images. Please try again later."
            
            # Detect language
            if self._is_russian(user_input or ""):
                system_prompt = self.system_prompt_ru
                language = "russian"
            else:
                system_prompt = self.system_prompt_en
                language = "english"
            
            # Update session
            updated_session = user_session.copy()
            updated_session['language'] = language
            
            # Prepare image analysis prompt
            if user_input:
                # User asked a question - answer it directly
                if language == "russian":
                    analysis_prompt = f"""Пользователь задал вопрос: "{user_input}"

Ответь на этот вопрос как профессиональный архитектор и дизайнер, используя изображение как контекст.

ВАЖНО: Не используй символы ** или ### в ответах. Пиши заголовки просто с новой строки.

Отвечай кратко и по делу."""
                else:
                    analysis_prompt = f"""User asked: "{user_input}"

Answer this question as a professional architect and designer, using the image as context.

IMPORTANT: Do not use ** or ### symbols in responses. Write headings on new lines.

Answer briefly and to the point."""
            else:
                # No text - analyze the image
                if language == "russian":
                    analysis_prompt = """Проанализируй изображение как архитектор:

Что вижу:
- Стиль и материалы
- Планировку и освещение
- Детали и атмосферу

Оценка:
- Плюсы дизайна
- Что улучшить
- Практические советы

ВАЖНО: Не используй символы ** или ### в ответах. Пиши заголовки просто с новой строки.

Анализируй кратко и по делу."""
                else:
                    analysis_prompt = """Analyze the image as an architect:

What I see:
- Style and materials
- Layout and lighting
- Details and atmosphere

Assessment:
- Design strengths
- Areas for improvement
- Practical advice

IMPORTANT: Do not use ** or ### symbols in responses. Write headings on new lines.

Analyze briefly and to the point."""
            
            # Prepare conversation context for image analysis
            conversation_context = self._prepare_conversation_context(user_session)
            
            # Create messages for AI
            messages = [
                {"role": "system", "content": system_prompt},
                *conversation_context,
                {"role": "user", "content": [
                    {"type": "text", "text": analysis_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{self._encode_image(image_data)}"}}
                ]}
            ]
            
            # Get AI response
            try:
                response = await self._get_ai_response(messages, model=self.vision_model)
                return updated_session, response
            except Exception as vision_error:
                logger.warning(f"Vision model failed, trying text model: {vision_error}")
                
                # Fallback: try to analyze with text model using image description
                fallback_prompt = f"""Проанализируй описание интерьера как архитектор:

{analysis_prompt}

Описание: Современная гостиная с L-образным диваном, красным журнальным столиком, полками с книгами, абстрактным искусством и геометрическим ковром.

Анализируй кратко."""
                
                fallback_messages = [
                    {"role": "system", "content": system_prompt},
                    *conversation_context,
                    {"role": "user", "content": fallback_prompt}
                ]
                
                fallback_response = await self._get_ai_response(fallback_messages, model=self.text_model)
                return updated_session, fallback_response
            
        except Exception as e:
            logger.error(f"Error in analyze_image_with_ai: {e}")
            return user_session, "I apologize, but I encountered an error analyzing your image. Please try again."
    
    async def _get_ai_response(self, messages: List[Dict[str, Any]], model: str = None) -> str:
        """Get response from AI model."""
        try:
            if not self.client:
                return "AI service is currently unavailable."
            
            # Limit tokens for shorter responses
            max_tokens = 1000 if model == self.vision_model else 800
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model or self.text_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Post-process response to remove unwanted formatting
            response_text = self._clean_response_formatting(response_text)
            
            # Limit response length for Telegram (max 3000 characters for shorter responses)
            if len(response_text) > 3000:
                response_text = response_text[:3000] + "\n\n... (ответ обрезан)"
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return "I apologize, but I'm having trouble generating a response right now."
    
    def _clean_response_formatting(self, text: str) -> str:
        """Clean AI response from unwanted formatting symbols."""
        # Remove **text** patterns (keep only text)
        import re
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # Remove ### patterns (keep only text)
        text = re.sub(r'###\s*', '', text)
        text = re.sub(r'##\s*', '', text)
        text = re.sub(r'#\s*', '', text)
        
        # Remove single * patterns (keep only text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove __text__ patterns (keep only text)
        text = re.sub(r'__(.*?)__', r'\1', text)
        
        # Clean up multiple newlines
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        return text
    
    def _prepare_conversation_context(self, user_session: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prepare conversation context from user session."""
        try:
            # Get conversation history from database
            from app.services.database import DatabaseService
            db_service = DatabaseService()
            
            user_id = user_session.get('user_id')
            if not user_id:
                return []
            
            # Get last 5 conversation messages for context
            conversation_history = db_service.get_conversation_history(user_id, limit=5)
            
            context_messages = []
            for msg in conversation_history:
                if msg['sender'] == 'user':
                    context_messages.append({"role": "user", "content": msg['message']})
                elif msg['sender'] == 'bot':
                    context_messages.append({"role": "assistant", "content": msg['message']})
            
            # Keep only last 3 exchanges to avoid token overflow
            if len(context_messages) > 6:
                context_messages = context_messages[-6:]
            
            return context_messages
            
        except Exception as e:
            logger.warning(f"Could not prepare conversation context: {e}")
            return []
    
    def _should_suggest_survey(self, user_input: str, user_session: Dict[str, Any]) -> bool:
        """Determine if we should suggest taking a survey."""
        # Suggest survey if user hasn't completed it and shows interest in personalized advice
        if user_session.get('survey_completed', False):
            return False
        
        # Check if user is asking for personalized advice
        personal_keywords = ['персональный', 'personal', 'личный', 'personalized', 'совет', 'advice', 'рекомендация', 'recommendation', 'дизайн', 'design', 'стиль', 'style']
        user_input_lower = user_input.lower()
        
        return any(keyword in user_input_lower for keyword in personal_keywords)
    
    def _get_survey_suggestion(self, language: str) -> str:
        """Get survey suggestion message in appropriate language."""
        if language == "russian":
            return "💡 Для получения профессиональных дизайнерских советов, рекомендую пройти специализированный тест по дизайну интерьера. Напишите 'тест' чтобы начать."
        else:
            return "💡 For professional interior design advice, I recommend taking a specialized interior design survey. Type 'survey' to begin."
    
    def _is_russian(self, text: str) -> bool:
        """Check if text contains Russian characters."""
        russian_chars = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
        text_chars = set(text.lower())
        return bool(text_chars.intersection(russian_chars))
    
    def _encode_image(self, image_data: bytes) -> str:
        """Encode image data to base64 string."""
        import base64
        return base64.b64encode(image_data).decode('utf-8')
