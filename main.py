#!/usr/bin/env python3
"""
AI Assistant Bot - Telegram Bot with Photo Analysis and Text Processing
Main entry point for the bot application using aiogram
"""

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, LOG_LEVEL

# Import handlers from the new structure
from app.handlers.start import router as start_router
from app.handlers.questions import router as questions_router
from app.handlers.ai_processing import router as ai_processing_router

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL),
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create bot and dispatcher
bot = Bot(
    token=BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

async def main():
    """Start the bot."""
    try:
        logger.info("Starting AI Assistant Bot...")
        
        # Include all routers in priority order
        # Commands and specific handlers first
        dp.include_router(start_router)
        
        # Questions handler BEFORE AI processing (states have priority!)
        dp.include_router(questions_router)
        
        # AI processing handler after questions
        dp.include_router(ai_processing_router)
        
        logger.info("All handlers registered successfully")
        
        # Start polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.critical(f"Bot startup failed: {e}")
        sys.exit(1)
    finally:
        logger.info("AI Assistant Bot stopped.")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
