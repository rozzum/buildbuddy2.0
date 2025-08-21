"""
Simple Conversation Service for AI Assistant Bot
Natural conversation flow with AI assistant
"""

import logging
import random
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConversationService:
    """Handles natural conversation flow with users."""
    
    def __init__(self):
        """Initialize conversation service."""
        self.greeting_sent = set()  # Track users who got greeting
        
    async def handle_message(self, user_id: int, user_input: str, user_session: Dict[str, Any]) -> str:
        """Handle user message and return appropriate response."""
        
        # Check if this is first interaction
        is_first_time = user_id not in self.greeting_sent
        
        if is_first_time:
            self.greeting_sent.add(user_id)
            return await self._handle_first_interaction(user_input, user_session)
        
        # Continue conversation
        return await self._handle_ongoing_conversation(user_input, user_session)
    
    async def _handle_first_interaction(self, user_input: str, session: Dict[str, Any]) -> str:
        """Handle first user interaction."""
        
        # Detect language and respond accordingly
        if self._is_russian(user_input):
            greetings = [
                "Привет! Я ваш ИИ ассистент. Как я могу вам помочь?",
                "Здравствуйте! Я готов ответить на ваши вопросы. Что вас интересует?",
                "Привет! Я здесь, чтобы помочь. Расскажите, что вам нужно?",
                "Здравствуйте! Чем могу быть полезен сегодня?"
            ]
        else:
            greetings = [
                "Hello! I'm your AI assistant. How can I help you?",
                "Hi there! I'm ready to answer your questions. What would you like to know?",
                "Hello! I'm here to help. What do you need assistance with?",
                "Hi! How can I be of service today?"
            ]
        
        return random.choice(greetings)
    
    async def _handle_ongoing_conversation(self, user_input: str, session: Dict[str, Any]) -> str:
        """Handle ongoing conversation."""
        
        # Extract basic information from user input
        extracted_info = self._extract_basic_info(user_input)
        
        # Update session with extracted info
        for key, value in extracted_info.items():
            session[key] = value
            logger.info(f"Extracted {key}: {value}")
        
        # For ongoing conversation, let AI handle the response
        return "I understand. Let me process your request and provide a helpful response."
    
    def _extract_basic_info(self, user_input: str) -> Dict[str, Any]:
        """Extract basic information from user input."""
        extracted = {}
        
        # Detect language preference
        if self._is_russian(user_input):
            extracted['language'] = 'russian'
        else:
            extracted['language'] = 'english'
        
        # Extract any mentioned preferences or context
        user_input_lower = user_input.lower()
        
        # Simple keyword extraction
        if any(word in user_input_lower for word in ['фото', 'photo', 'изображение', 'image']):
            extracted['photo_interest'] = True
        
        if any(word in user_input_lower for word in ['тест', 'test', 'опрос', 'survey']):
            extracted['survey_interest'] = True
        
        return extracted
    
    def _is_russian(self, text: str) -> bool:
        """Check if text contains Russian characters."""
        russian_chars = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
        text_chars = set(text.lower())
        return bool(text_chars.intersection(russian_chars))
    
    def should_suggest_survey(self, user_session: Dict[str, Any]) -> bool:
        """Determine if we should suggest taking a survey."""
        # Suggest survey if user hasn't taken it and shows interest in personalized advice
        return not user_session.get('survey_completed', False) and user_session.get('survey_interest', False)
