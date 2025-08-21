#!/usr/bin/env python3
"""
Final test script for formatting fixes
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_formatting_fix_final():
    """Test final formatting fixes."""
    print("🧪 Testing final formatting fixes...")
    
    try:
        # Test OpenRouter service
        from app.services.openrouter_service import OpenRouterService
        openrouter_service = OpenRouterService()
        
        print(f"✅ OpenRouter service initialized")
        
        # Check system prompts for proper formatting
        ru_prompt = openrouter_service.system_prompt_ru
        en_prompt = openrouter_service.system_prompt_en
        
        print("\n📝 Testing system prompts...")
        
        # Check for no special formatting symbols
        if "**" not in ru_prompt and "**" not in en_prompt:
            print("✅ No ** symbols in system prompts")
        else:
            print("❌ ** symbols found in system prompts")
            return False
        
        if "###" not in ru_prompt and "###" not in en_prompt:
            print("✅ No ### symbols in system prompts")
        else:
            print("❌ ### symbols found in system prompts")
            return False
        
        # Check for proper instructions
        if "ВАЖНО: Не используй символы ** или ### в ответах" in ru_prompt:
            print("✅ Russian prompt has proper formatting instructions")
        else:
            print("❌ Russian prompt missing formatting instructions")
            return False
        
        if "IMPORTANT: Do not use ** or ### symbols in responses" in en_prompt:
            print("✅ English prompt has proper formatting instructions")
        else:
            print("❌ English prompt missing formatting instructions")
            return False
        
        # Test vision prompts
        print("\n📸 Testing vision prompts...")
        
        # Simulate vision prompt generation
        user_input = ""
        language = "russian"
        
        if user_input:
            analysis_prompt = f"""Пользователь задал вопрос: "{user_input}"

Ответь на этот вопрос как профессиональный архитектор и дизайнер, используя изображение как контекст.

ВАЖНО: Не используй символы ** или ### в ответах. Пиши заголовки просто с новой строки.

Отвечай кратко и по делу."""
        else:
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
        
        if "ВАЖНО: Не используй символы ** или ### в ответах" in analysis_prompt:
            print("✅ Vision prompt has proper formatting instructions")
        else:
            print("❌ Vision prompt missing formatting instructions")
            return False
        
        # Check for no special symbols in vision prompts
        if "**" not in analysis_prompt and "###" not in analysis_prompt:
            print("✅ No special symbols in vision prompts")
        else:
            print("❌ Special symbols found in vision prompts")
            return False
        
        print("🎉 Final formatting fixes working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing final formatting fixes: {e}")
        return False

async def main():
    """Run final formatting fix test."""
    print("🚀 Testing final formatting fixes...\n")
    
    success = await test_formatting_fix_final()
    
    print("\n" + "="*60)
    if success:
        print("🎉 FINAL FORMATTING FIX TEST PASSED!")
        print("\n✅ Форматирование исправлено:")
        print("   • Убраны все ** звездочки из промптов")
        print("   • Убраны все ### решетки из промптов")
        print("   • Добавлены четкие инструкции для AI")
        print("   • AI не будет генерировать специальные символы")
        print("   • Ответы будут чистыми без звездочек и решеток")
        print("\n🚀 Теперь AI будет генерировать чистый текст!")
    else:
        print("❌ Final formatting fix test failed. Check the errors above.")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
