"""
Professional Interior Design Survey Handler for AI Assistant Bot
Handles specialized interior design survey with professional questions
"""

import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.database import DatabaseService

logger = logging.getLogger(__name__)
router = Router()

# Professional interior design survey states
class DesignSurveyStates(StatesGroup):
    # Style preferences
    waiting_style_choice = State()
    waiting_color_preference = State()
    waiting_material_preference = State()
    
    # Space and layout preferences
    waiting_space_type = State()
    waiting_room_preference = State()
    waiting_layout_style = State()
    
    # Functional preferences
    waiting_functionality = State()
    waiting_lighting_preference = State()
    waiting_storage_preference = State()
    
    # Budget and timeline
    waiting_budget_range = State()
    waiting_timeline = State()
    waiting_priority = State()
    
    # Lifestyle and personal preferences
    waiting_lifestyle = State()
    waiting_family_needs = State()
    waiting_personal_touch = State()

# Design style options with descriptions
DESIGN_STYLES = {
    'modern': {
        'name': 'Современный (Modern)',
        'description': 'Чистые линии, минимализм, функциональность',
        'keywords': ['минимализм', 'функциональность', 'технологии', 'открытое пространство']
    },
    'classic': {
        'name': 'Классический (Classic)',
        'description': 'Элегантность, традиции, роскошь',
        'keywords': ['элегантность', 'традиции', 'роскошь', 'симметрия']
    },
    'scandinavian': {
        'name': 'Скандинавский (Scandinavian)',
        'description': 'Светлость, натуральные материалы, уют',
        'keywords': ['светлость', 'натуральность', 'уют', 'простота']
    },
    'industrial': {
        'name': 'Индустриальный (Industrial)',
        'description': 'Открытые коммуникации, металл, бетон',
        'keywords': ['открытость', 'металл', 'бетон', 'лофт']
    },
    'rustic': {
        'name': 'Рустик (Rustic)',
        'description': 'Натуральность, теплота, деревенский шарм',
        'keywords': ['натуральность', 'теплота', 'деревенский', 'дерево']
    },
    'contemporary': {
        'name': 'Современный эклектичный (Contemporary)',
        'description': 'Смешение стилей, индивидуальность, тренды',
        'keywords': ['эклектика', 'индивидуальность', 'тренды', 'креативность']
    }
}

@router.message(Command("test"))
async def start_design_survey(message: Message, state: FSMContext):
    """Start the professional interior design survey."""
    try:
        user = message.from_user
        db_service = DatabaseService()
        
        # Clear any existing state
        await state.clear()
        
        # Set survey mode flag in database
        db_service.update_user_field(user.id, 'in_survey_mode', True)
        
        # Show survey introduction
        intro_text = """🎨 ** ТЕСТ ПО ДИЗАЙНУ ИНТЕРЬЕРА**

⏱ **Время:** 10-15 минут

🚀 **Начинаем с выбора стиля!**"""
        
        await message.answer(intro_text, parse_mode="Markdown")
        await ask_style_preference(message, state)
        
    except Exception as e:
        logger.error(f"Error starting design survey: {e}")
        await message.answer("Произошла ошибка при запуске теста. Попробуйте /start")

async def ask_style_preference(message: Message, state: FSMContext):
    """Ask for design style preference with visual examples."""
    try:
        # Create inline keyboard with style options
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏗️ Современный", callback_data="style_modern")],
            [InlineKeyboardButton(text="👑 Классический", callback_data="style_classic")],
            [InlineKeyboardButton(text="🌲 Скандинавский", callback_data="style_scandinavian")],
            [InlineKeyboardButton(text="⚙️ Индустриальный", callback_data="style_industrial")],
            [InlineKeyboardButton(text="🪵 Рустик", callback_data="style_rustic")],
            [InlineKeyboardButton(text="🎭 Современный эклектичный", callback_data="style_contemporary")]
        ])
        
        style_text = """🎨 **ВОПРОС 1: Выберите ваш любимый стиль дизайна**

Каждый стиль имеет свои уникальные характеристики:

🏗️ **Современный (Modern)**
• Чистые линии и минимализм
• Функциональность превыше всего
• Открытые пространства
• Современные технологии

👑 **Классический (Classic)**
• Элегантность и традиции
• Роскошные материалы
• Симметричные композиции
• Вневременная красота

🌲 **Скандинавский (Scandinavian)**
• Светлость и простота
• Натуральные материалы
• Уютная атмосфера
• Функциональный дизайн

⚙️ **Индустриальный (Industrial)**
• Открытые коммуникации
• Металл и бетон
• Лофт-эстетика
• Урбанистический стиль

🪵 **Рустик (Rustic)**
• Натуральность и теплота
• Деревенский шарм
• Текстурированные материалы
• Уютная атмосфера

🎭 **Современный эклектичный (Contemporary)**
• Смешение стилей
• Индивидуальность
• Современные тренды
• Креативность

Выберите стиль, который больше всего отражает ваши предпочтения:"""
        
        await message.answer(style_text, parse_mode="Markdown", reply_markup=keyboard)
        await state.set_state(DesignSurveyStates.waiting_style_choice)
        
    except Exception as e:
        logger.error(f"Error asking style preference: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.callback_query(lambda c: c.data.startswith('style_'))
async def handle_style_choice(callback_query: types.CallbackQuery, state: FSMContext):
    """Handle style choice selection."""
    try:
        user_id = callback_query.from_user.id
        db_service = DatabaseService()
        
        # Extract style from callback data
        style = callback_query.data.replace('style_', '')
        
        # Store style choice
        db_service.update_user_field(user_id, 'preferred_style', style)
        db_service.update_user_field(user_id, 'style_description', DESIGN_STYLES[style]['description'])
        
        # Store in conversation history
        db_service.add_conversation_message(user_id, f"Выбран стиль: {DESIGN_STYLES[style]['name']}", "user")
        
        # Confirm choice and move to next question
        confirm_text = f"""✅ **Стиль выбран: {DESIGN_STYLES[style]['name']}**

{DESIGN_STYLES[style]['description']}

Переходим к следующему вопросу..."""
        
        await callback_query.message.edit_text(confirm_text, parse_mode="Markdown")
        
        # Move to color preference question
        await ask_color_preference(callback_query.message, state)
        
    except Exception as e:
        logger.error(f"Error handling style choice: {e}")
        await callback_query.answer("Произошла ошибка. Попробуйте еще раз.")

async def ask_color_preference(message: Message, state: FSMContext):
    """Ask for color preference."""
    try:
        color_text = """🎨 **ВОПРОС 2: Цветовая палитра**

Какие цвета вызывают у вас положительные эмоции?

**Основные палитры:**

🌞 **Теплые тона**
• Бежевый, кремовый, песочный
• Терракотовый, коричневый
• Желтый, оранжевый
• Создают уютную, гостеприимную атмосферу

❄️ **Холодные тона**
• Белый, серый, голубой
• Синий, фиолетовый
• Зеленый, мятный
• Дарят спокойствие и свежесть

🌈 **Яркие акценты**
• Красный, розовый, малиновый
• Зеленый, бирюзовый
• Желтый, оранжевый
• Добавляют энергии и индивидуальности

🎭 **Монохромные**
• Оттенки одного цвета
• Черно-белая гамма
• Элегантность и минимализм

**Напишите, какие цвета вам нравятся больше всего, или выберите палитру из списка выше.**"""
        
        await message.answer(color_text, parse_mode="Markdown")
        await state.set_state(DesignSurveyStates.waiting_color_preference)
        
    except Exception as e:
        logger.error(f"Error asking color preference: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.message(DesignSurveyStates.waiting_color_preference)
async def handle_color_preference(message: Message, state: FSMContext):
    """Handle color preference response."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Store color preference
        db_service.update_user_field(user_id, 'color_preference', message.text)
        
        # Store in conversation history
        db_service.add_conversation_message(user_id, message.text, "user")
        
        await ask_material_preference(message, state)
        
    except Exception as e:
        logger.error(f"Error handling color preference: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

async def ask_material_preference(message: Message, state: FSMContext):
    """Ask for material preference."""
    try:
        material_text = """🏗️ **ВОПРОС 3: Материалы и текстуры**

Какие материалы вызывают у вас приятные тактильные ощущения?

**Основные категории материалов:**

🌳 **Натуральные материалы**
• Дерево (дуб, ясень, сосна)
• Камень (мрамор, гранит, известняк)
• Натуральные ткани (лен, хлопок, шерсть)
• Кожа и замша

🔧 **Современные материалы**
• Металл (сталь, алюминий, латунь)
• Стекло и зеркала
• Бетон и керамика
• Искусственные ткани

💎 **Роскошные материалы**
• Мрамор и гранит
• Драгоценные породы дерева
• Шелк и бархат
• Хрусталь и фарфор

**Напишите, какие материалы вам нравятся, или выберите категорию из списка выше.**"""
        
        await message.answer(material_text, parse_mode="Markdown")
        await state.set_state(DesignSurveyStates.waiting_material_preference)
        
    except Exception as e:
        logger.error(f"Error asking material preference: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.message(DesignSurveyStates.waiting_material_preference)
async def handle_material_preference(message: Message, state: FSMContext):
    """Handle material preference response."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Store material preference
        db_service.update_user_field(user_id, 'material_preference', message.text)
        
        # Store in conversation history
        db_service.add_conversation_message(user_id, message.text, "user")
        
        await ask_space_type(message, state)
        
    except Exception as e:
        logger.error(f"Error handling material preference: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

async def ask_space_type(message: Message, state: FSMContext):
    """Ask for space type preference."""
    try:
        space_text = """🏠 **ВОПРОС 4: Тип пространства**

Какой тип жилого пространства вы планируете обустраивать?

**Жилые пространства:**
🏡 **Частный дом**
• Больше возможностей для планировки
• Связь с природой
• Индивидуальность

🏢 **Квартира**
• Компактность и функциональность
• Городская среда
• Социальная инфраструктура

🏰 **Пентхаус/Лофт**
• Высота и панорамные виды
• Открытые пространства
• Премиум-статус

**Напишите, какой тип жилого пространства вас интересует, или выберите из списка выше.**"""
        
        await message.answer(space_text, parse_mode="Markdown")
        await state.set_state(DesignSurveyStates.waiting_space_type)
        
    except Exception as e:
        logger.error(f"Error asking space type: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.message(DesignSurveyStates.waiting_space_type)
async def handle_space_type(message: Message, state: FSMContext):
    """Handle space type response."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Store space type
        db_service.update_user_field(user_id, 'space_type', message.text)
        
        # Store in conversation history
        db_service.add_conversation_message(user_id, message.text, "user")
        
        await ask_room_preference(message, state)
        
    except Exception as e:
        logger.error(f"Error handling space type: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

async def ask_room_preference(message: Message, state: FSMContext):
    """Ask for room preference."""
    try:
        room_text = """🚪 **ВОПРОС 5: Приоритетные помещения**

Какие помещения для вас наиболее важны?

**Основные помещения:**
🛋️ **Гостиная**
• Центр семейной жизни
• Прием гостей
• Отдых и развлечения

🍽️ **Кухня**
• Приготовление пищи
• Семейные завтраки
• Социальное пространство

🛏️ **Спальня**
• Отдых и восстановление
• Личное пространство
• Уют и комфорт

🛁 **Ванная комната**
• Утренние процедуры
• Расслабление
• Функциональность

🏠 **Прихожая**
• Первое впечатление
• Хранение вещей
• Переход между зонами

**Напишите, какие помещения для вас приоритетны, или выберите из списка выше.**"""
        
        await message.answer(room_text, parse_mode="Markdown")
        await state.set_state(DesignSurveyStates.waiting_room_preference)
        
    except Exception as e:
        logger.error(f"Error asking room preference: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.message(DesignSurveyStates.waiting_room_preference)
async def handle_room_preference(message: Message, state: FSMContext):
    """Handle room preference response."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Store room preference
        db_service.update_user_field(user_id, 'room_preference', message.text)
        
        # Store in conversation history
        db_service.add_conversation_message(user_id, message.text, "user")
        
        await ask_layout_style(message, state)
        
    except Exception as e:
        logger.error(f"Error handling room preference: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

async def ask_layout_style(message: Message, state: FSMContext):
    """Ask for layout style preference."""
    try:
        layout_text = """📐 **ВОПРОС 6: Стиль планировки**

Какой стиль планировки вам больше нравится?

**Типы планировок:**

🏠 **Открытая планировка (Open Plan)**
• Минимум перегородок
• Светлые пространства
• Социальное взаимодействие
• Современный подход

🚪 **Зонированная планировка (Zoned)**
• Четкое разделение функций
• Приватность помещений
• Традиционный подход
• Структурированность

🔄 **Гибкая планировка (Flexible)**
• Трансформируемые пространства
• Многофункциональность
• Адаптивность
• Инновационность

**Напишите, какой стиль планировки вам больше подходит, или выберите из списка выше.**"""
        
        await message.answer(layout_text, parse_mode="Markdown")
        await state.set_state(DesignSurveyStates.waiting_layout_style)
        
    except Exception as e:
        logger.error(f"Error asking layout style: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.message(DesignSurveyStates.waiting_layout_style)
async def handle_layout_style(message: Message, state: FSMContext):
    """Handle layout style response."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Store layout style
        db_service.update_user_field(user_id, 'layout_style', message.text)
        
        # Store in conversation history
        db_service.add_conversation_message(user_id, message.text, "user")
        
        await ask_functionality(message, state)
        
    except Exception as e:
        logger.error(f"Error handling layout style: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

async def ask_functionality(message: Message, state: FSMContext):
    """Ask for functionality preferences."""
    try:
        functionality_text = """⚙️ **ВОПРОС 7: Функциональные потребности**

Какие функции для вас наиболее важны?

**Основные функции:**

💻 **Технологичность**
• Умный дом
• Автоматизация
• Медиа-системы
• Энергоэффективность

📚 **Хранение**
• Встроенные шкафы
• Системы хранения
• Организация вещей
• Многофункциональная мебель

🌱 **Экологичность**
• Натуральные материалы
• Энергосбережение
• Переработка
• Устойчивое развитие

**Напишите, какие функции для вас приоритетны, или выберите из списка выше.**"""
        
        await message.answer(functionality_text, parse_mode="Markdown")
        await state.set_state(DesignSurveyStates.waiting_functionality)
        
    except Exception as e:
        logger.error(f"Error asking functionality: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.message(DesignSurveyStates.waiting_functionality)
async def handle_functionality(message: Message, state: FSMContext):
    """Handle functionality response."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Store functionality preference
        db_service.update_user_field(user_id, 'functionality_preference', message.text)
        
        # Store in conversation history
        db_service.add_conversation_message(user_id, message.text, "user")
        
        await ask_lighting_preference(message, state)
        
    except Exception as e:
        logger.error(f"Error handling functionality: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

async def ask_lighting_preference(message: Message, state: FSMContext):
    """Ask for lighting preference."""
    try:
        lighting_text = """💡 **ВОПРОС 8: Предпочтения в освещении**

Какой тип освещения вам больше нравится?

**Типы освещения:**

☀️ **Естественное освещение**
• Большие окна
• Световые колодцы
• Зеркальные поверхности
• Светлые тона

💡 **Искусственное освещение**
• Точечные светильники
• Подсветка
• Настенные бра
• Декоративные лампы

🌅 **Комбинированное освещение**
• Естественный + искусственный свет
• Автоматическое управление
• Разные сценарии освещения
• Адаптивность

**Напишите, какой тип освещения вам больше подходит, или выберите из списка выше.**"""
        
        await message.answer(lighting_text, parse_mode="Markdown")
        await state.set_state(DesignSurveyStates.waiting_lighting_preference)
        
    except Exception as e:
        logger.error(f"Error asking lighting preference: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.message(DesignSurveyStates.waiting_lighting_preference)
async def handle_lighting_preference(message: Message, state: FSMContext):
    """Handle lighting preference response."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Store lighting preference
        db_service.update_user_field(user_id, 'lighting_preference', message.text)
        
        # Store in conversation history
        db_service.add_conversation_message(user_id, message.text, "user")
        
        await ask_storage_preference(message, state)
        
    except Exception as e:
        logger.error(f"Error handling lighting preference: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

async def ask_storage_preference(message: Message, state: FSMContext):
    """Ask for storage preference."""
    try:
        storage_text = """🗄️ **ВОПРОС 9: Системы хранения**

Какие системы хранения вам нужны?

**Типы хранения:**

📦 **Встроенные системы**
• Встроенные шкафы
• Ниши и полки
• Многофункциональная мебель
• Скрытое хранение

🎨 **Декоративные системы**
• Открытые полки
• Стеллажи
• Корзины и коробки
• Видимые системы хранения

🔒 **Функциональные системы**
• Гардеробные комнаты
• Кладовые
• Технические помещения
• Специализированное хранение

**Напишите, какие системы хранения вам нужны, или выберите из списка выше.**"""
        
        await message.answer(storage_text, parse_mode="Markdown")
        await state.set_state(DesignSurveyStates.waiting_storage_preference)
        
    except Exception as e:
        logger.error(f"Error asking storage preference: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.message(DesignSurveyStates.waiting_storage_preference)
async def handle_storage_preference(message: Message, state: FSMContext):
    """Handle storage preference response."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Store storage preference
        db_service.update_user_field(user_id, 'storage_preference', message.text)
        
        # Store in conversation history
        db_service.add_conversation_message(user_id, message.text, "user")
        
        await ask_budget_range(message, state)
        
    except Exception as e:
        logger.error(f"Error handling storage preference: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

async def ask_budget_range(message: Message, state: FSMContext):
    """Ask for budget range."""
    try:
        budget_text = """💰 **ВОПРОС 10: Бюджетный диапазон**

Какой бюджет вы планируете на проект?

**Бюджетные категории:**

💸 **Экономный (до $50,000)**
• Базовые материалы
• Простые решения
• DIY элементы
• Функциональность

💵 **Средний ($50,000 - $150,000)**
• Качественные материалы
• Профессиональные решения
• Дизайнерская мебель
• Баланс цены и качества

💎 **Премиум ($150,000+)**
• Люксовые материалы
• Индивидуальные решения
• Дизайнерская мебель
• Максимальное качество

**Напишите ваш бюджетный диапазон или выберите категорию из списка выше.**"""
        
        await message.answer(budget_text, parse_mode="Markdown")
        await state.set_state(DesignSurveyStates.waiting_budget_range)
        
    except Exception as e:
        logger.error(f"Error asking budget range: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.message(DesignSurveyStates.waiting_budget_range)
async def handle_budget_range(message: Message, state: FSMContext):
    """Handle budget range response."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Store budget range
        db_service.update_user_field(user_id, 'budget_range', message.text)
        
        # Store in conversation history
        db_service.add_conversation_message(user_id, message.text, "user")
        
        await ask_timeline(message, state)
        
    except Exception as e:
        logger.error(f"Error handling budget range: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

async def ask_timeline(message: Message, state: FSMContext):
    """Ask for project timeline."""
    try:
        timeline_text = """⏰ **ВОПРОС 11: Временные рамки**

Какие временные рамки у вашего проекта?

**Временные категории:**

🚀 **Срочно (1-3 месяца)**
• Быстрые решения
• Готовые элементы
• Минимальные изменения
• Оперативность

📅 **Средний срок (3-6 месяцев)**
• Планирование и подготовка
• Качественные материалы
• Профессиональный подход
• Баланс времени и качества

🕐 **Нет спешки (6+ месяцев)**
• Детальное планирование
• Индивидуальные решения
• Люксовые материалы
• Максимальное качество

**Напишите ваши временные рамки или выберите категорию из списка выше.**"""
        
        await message.answer(timeline_text, parse_mode="Markdown")
        await state.set_state(DesignSurveyStates.waiting_timeline)
        
    except Exception as e:
        logger.error(f"Error asking timeline: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.message(DesignSurveyStates.waiting_timeline)
async def handle_timeline(message: Message, state: FSMContext):
    """Handle timeline response."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Store timeline
        db_service.update_user_field(user_id, 'timeline', message.text)
        
        # Store in conversation history
        db_service.add_conversation_message(user_id, message.text, "user")
        
        await ask_priority(message, state)
        
    except Exception as e:
        logger.error(f"Error handling timeline: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

async def ask_priority(message: Message, state: FSMContext):
    """Ask for project priorities."""
    try:
        priority_text = """🎯 **ВОПРОС 12: Приоритеты проекта**

Что для вас важнее всего в проекте?

**Приоритетные аспекты:**

🏠 **Функциональность**
• Удобство использования
• Практичность
• Эргономика
• Эффективность

🎨 **Эстетика**
• Красота и стиль
• Визуальная привлекательность
• Гармония и баланс
• Индивидуальность

💰 **Экономия**
• Оптимизация бюджета
• Долговечность
• Энергоэффективность
• Разумные траты

**Напишите, что для вас важнее всего, или выберите из списка выше.**"""
        
        await message.answer(priority_text, parse_mode="Markdown")
        await state.set_state(DesignSurveyStates.waiting_priority)
        
    except Exception as e:
        logger.error(f"Error asking priority: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.message(DesignSurveyStates.waiting_priority)
async def handle_priority(message: Message, state: FSMContext):
    """Handle priority response."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Store priority
        db_service.update_user_field(user_id, 'project_priority', message.text)
        
        # Store in conversation history
        db_service.add_conversation_message(user_id, message.text, "user")
        
        await ask_lifestyle(message, state)
        
    except Exception as e:
        logger.error(f"Error handling priority: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

async def ask_lifestyle(message: Message, state: FSMContext):
    """Ask for lifestyle preferences."""
    try:
        lifestyle_text = """🌟 **ВОПРОС 13: Образ жизни**

Какой у вас образ жизни?

**Типы образа жизни:**

🏠 **Домашний**
• Много времени дома
• Семейные ценности
• Уют и комфорт
• Приватность

🌍 **Активный**
• Путешествия и спорт
• Социальная активность
• Динамичность
• Открытость

💼 **Деловой**
• Работа из дома
• Встречи и переговоры
• Профессиональная среда
• Функциональность

**Напишите, какой у вас образ жизни, или выберите из списка выше.**"""
        
        await message.answer(lifestyle_text, parse_mode="Markdown")
        await state.set_state(DesignSurveyStates.waiting_lifestyle)
        
    except Exception as e:
        logger.error(f"Error asking lifestyle: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.message(DesignSurveyStates.waiting_lifestyle)
async def handle_lifestyle(message: Message, state: FSMContext):
    """Handle lifestyle response."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Store lifestyle
        db_service.update_user_field(user_id, 'lifestyle', message.text)
        
        # Store in conversation history
        db_service.add_conversation_message(user_id, message.text, "user")
        
        await ask_family_needs(message, state)
        
    except Exception as e:
        logger.error(f"Error handling lifestyle: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

async def ask_family_needs(message: Message, state: FSMContext):
    """Ask for family needs."""
    try:
        family_text = """👨‍👩‍👧‍👦 **ВОПРОС 14: Семейные потребности**

Какие у вас семейные потребности?

**Семейные ситуации:**

👤 **Один человек**
• Личное пространство
• Индивидуальность
• Функциональность
• Минимализм

👫 **Пара**
• Романтическая атмосфера
• Совместное время
• Личное пространство
• Гостеприимство

👨‍👩‍👧‍👦 **Семья с детьми**
• Безопасность
• Игровые зоны
• Практичность
• Долговечность

👴 **Мультипоколенная семья**
• Доступность
• Комфорт для всех возрастов
• Функциональность
• Универсальность

**Напишите ваши семейные потребности или выберите из списка выше.**"""
        
        await message.answer(family_text, parse_mode="Markdown")
        await state.set_state(DesignSurveyStates.waiting_family_needs)
        
    except Exception as e:
        logger.error(f"Error asking family needs: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.message(DesignSurveyStates.waiting_family_needs)
async def handle_family_needs(message: Message, state: FSMContext):
    """Handle family needs response."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Store family needs
        db_service.update_user_field(user_id, 'family_needs', message.text)
        
        # Store in conversation history
        db_service.add_conversation_message(user_id, message.text, "user")
        
        await ask_personal_touch(message, state)
        
    except Exception as e:
        logger.error(f"Error handling family needs: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

async def ask_personal_touch(message: Message, state: FSMContext):
    """Ask for personal touch preferences."""
    try:
        personal_text = """🎭 **ВОПРОС 15: Личные акценты**

Что сделает пространство по-настоящему вашим?

**Личные элементы:**

🎨 **Хобби и увлечения**
• Творческие зоны
• Коллекции
• Специализированное оборудование
• Индивидуальные решения

🌍 **Культурные корни**
• Национальные мотивы
• Традиционные элементы
• Культурные символы
• Семейные реликвии

💝 **Эмоциональные связи**
• Любимые цвета
• Значимые предметы
• Воспоминания
• Личные истории

**Напишите, что сделает пространство по-настоящему вашим, или выберите из списка выше.**"""
        
        await message.answer(personal_text, parse_mode="Markdown")
        await state.set_state(DesignSurveyStates.waiting_personal_touch)
        
    except Exception as e:
        logger.error(f"Error asking personal touch: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.message(DesignSurveyStates.waiting_personal_touch)
async def handle_personal_touch(message: Message, state: FSMContext):
    """Handle personal touch response and complete survey."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Store personal touch
        db_service.update_user_field(user_id, 'personal_touch', message.text)
        db_service.update_user_field(user_id, 'survey_completed', True)
        db_service.update_user_field(user_id, 'in_survey_mode', False)
        
        # Store in conversation history
        db_service.add_conversation_message(user_id, message.text, "user")
        
        # Complete survey
        await complete_design_survey(message, state)
        
    except Exception as e:
        logger.error(f"Error handling personal touch: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

async def complete_design_survey(message: Message, state: FSMContext):
    """Complete the design survey and show professional summary."""
    try:
        user_id = message.from_user.id
        db_service = DatabaseService()
        
        # Get user session to show summary
        user_session = db_service.get_user_session(user_id)
        
        # Create professional summary
        summary = f"""🎉 **ПРОФЕССИОНАЛЬНЫЙ ТЕСТ ПО ДИЗАЙНУ ИНТЕРЬЕРА ЗАВЕРШЕН!**

✅ Спасибо за прохождение теста! Теперь я знаю ваши предпочтения как профессиональный архитектор и дизайнер интерьеров.

📊 **Ваш дизайн-профиль:**

🎨 **Стиль:** {user_session.get('preferred_style', 'Не указано')}
🎨 **Цвета:** {user_session.get('color_preference', 'Не указано')}
🏗️ **Материалы:** {user_session.get('material_preference', 'Не указано')}
🏠 **Тип пространства:** {user_session.get('space_type', 'Не указано')}
🚪 **Помещения:** {user_session.get('room_preference', 'Не указано')}
📐 **Планировка:** {user_session.get('layout_style', 'Не указано')}
⚙️ **Функциональность:** {user_session.get('functionality_preference', 'Не указано')}
💡 **Освещение:** {user_session.get('lighting_preference', 'Не указано')}
🗄️ **Хранение:** {user_session.get('storage_preference', 'Не указано')}
💰 **Бюджет:** {user_session.get('budget_range', 'Не указано')}
⏰ **Время:** {user_session.get('timeline', 'Не указано')}
🎯 **Приоритеты:** {user_session.get('project_priority', 'Не указано')}
🌟 **Образ жизни:** {user_session.get('lifestyle', 'Не указано')}
👨‍👩‍👧‍👦 **Семья:** {user_session.get('family_needs', 'Не указано')}
🎭 **Личные акценты:** {user_session.get('personal_touch', 'Не указано')}

💡 **Теперь я могу давать вам профессиональные дизайнерские советы на основе ваших предпочтений!**

🚀 Можете задавать любые вопросы по дизайну, планировке, материалам или отправлять фотографии для профессионального анализа."""
        
        # Store completion message in conversation history
        db_service.add_conversation_message(user_id, summary, "bot")
        
        await message.answer(summary, parse_mode="Markdown")
        
        # Clear state
        await state.clear()
        
        logger.info(f"User {user_id} completed the professional design survey")
        
    except Exception as e:
        logger.error(f"Error completing design survey: {e}")
        await message.answer("Произошла ошибка при завершении теста.")

@router.message(Command("survey"))
async def start_survey_english(message: Message, state: FSMContext):
    """Start survey in English."""
    try:
        user = message.from_user
        db_service = DatabaseService()
        
        # Clear any existing state
        await state.clear()
        
        # Set survey mode flag in database
        db_service.update_user_field(user.id, 'in_survey_mode', True)
        
        # Show survey introduction in English
        intro_text = """🎨 **PROFESSIONAL INTERIOR DESIGN SURVEY**

Hello! I'm a professional architect and interior designer with 20+ years of experience.

🔍 **What we'll discover:**
• Your style and color preferences
• Functional space requirements
• Budget and timeline constraints
• Lifestyle and family needs

📊 **15 professional questions:**
1-3: Style preferences
4-6: Spatial solutions
7-9: Functionality
10-12: Budget and time
13-15: Lifestyle

⏱ **Time:** 10-15 minutes

🚀 **Let's start with style selection!**"""
        
        await message.answer(intro_text, parse_mode="Markdown")
        await ask_style_preference(message, state)
        
    except Exception as e:
        logger.error(f"Error starting English survey: {e}")
        await message.answer("An error occurred while starting the survey. Try /start")