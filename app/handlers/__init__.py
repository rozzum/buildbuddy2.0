"""
Handlers package for AI Assistant Bot
"""

from .start import router as start_router
from .questions import router as questions_router
from .ai_processing import router as ai_processing_router

__all__ = ['start_router', 'questions_router', 'ai_processing_router']
