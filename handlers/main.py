from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from keyboards import main_menu, help_keyboard, stats_keyboard, pagination_keyboard
from data import user_data
import logging
from datetime import datetime

router = Router()
logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def start_command(message: Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    # Регистрируем пользователя
    user_info = user_data.get_info(user_id)

    welcome_text = f"""
🎉 <b>Добро пожаловать в Quiz Bot, {username}!</b>

🧠 <b>Викторина</b> - проверь свои знания
🎲 <b>Игры</b> - развлекись с мини-играми  
🧩 <b>Загадки</b> - разгадай головоломки
🔤 <b>Угадай слово</b> - классическая игра
📊 <b>Статистика</b> - отслеживай прогресс
🏆 <b>Достижения</b> - собирай награды

💡 <i>Отвечай правильно, зарабатывай очки и открывай достижения!</i>
"""

    await message.answer(welcome_text, reply_markup=main_menu())
    logger.info(f"Пользователь {user_id} ({username}) запустил бота")

@router.message(Command("help"))
async def help_command(message: Message):
    """Обработчик команды /help"""
    help_text = """
📖 <b>Помощь по боту</b>

<b>Основные команды:</b>
/start - Запуск бота
/help - Эта справка
/stats - Моя статистика
/top - Рейтинг игроков

<b>Как играть:</b>
• Выбирай категории и отвечай на вопросы
• За правильные ответы получай очки
• Поддерживай серию правильных ответов
• Собирай достижения
• Сравнивай результаты с другими игроками

<b>Система очков:</b>
• Легкие вопросы: 2 очка
• Средние вопросы: 4 очка  
• Сложные вопросы: 6 очков
• Загадки: 3 очка
• Слова: 5 очков
• За неправильный ответ: -1 очко

<b>Достижения:</b>
Выполняй различные задания и получай особые награды!
"""

    await message.answer(help_text, reply_markup=help_keyboard())

@router.message(Command("stats"))
async def stats_command(message: Message):
    """Обработчик команды /stats"""
    await show_user_stats(message, message.from_user.id)

@router.message(Command("top"))
async def top_command(message: Message):
    """Обработчик команды /top"""
    await show_leaderboard(message)

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.edit_text(
        "🏠 <b>Главное меню</b>\n\nВыбери, что хочешь делать:",
        reply_markup=main_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "stats")
async def stats_callback(callback: CallbackQuery):
    """Показать статистику пользователя"""
    await show_user_stats(callback.message, callback.from_user.id, edit=True)
    await callback.answer()

@router.callback_query(F.data == "stats:detailed")
async def detailed_stats(callback: CallbackQuery):
    """Подробная статистика пользователя"""
    user_info = user_data.get_info(callback.from_user.id)

    # Вычисляем дополнительные метрики
    accuracy = 0
    if user_info["answered"] > 0:
        accuracy = (user_info["correct"] / user_info["answered"]) * 100

    avg_score_per_game = 0
    if user_info["games_played"] > 0:
        avg_score_per_game = user_info["score"] / user_info["games_played"]

    # Определяем уровень игрока
    level = calculate_user_level(user_info["score"])

    created_date = datetime.fromisoformat(user_info["created_at"]).strftime("%d.%m.%Y")

    detailed_text = f"""
📊 <b>Подробная статистика</b>

👤 <b>Общая информация:</b>
🎯 Уровень: {level}
📅 Дата регистрации: {created_date}
🏆 Общий счет: {user_info['score']}

🎲 <b>Игровая активность:</b>
❓ Всего ответов: {user_info['answered']}
✅ Правильных: {user_info['correct']}
❌ Неправильных: {user_info['answered'] - user_info['correct']}
📈 Точность: {accuracy:.1f}%

🎮 <b>По категориям:</b>
🧠 Викторины: {user_info.get('quiz_answered', 0)}
🧩 Загадки: {user_info['riddles_solved']}
🔤 Слова: {user_info['words_guessed']}
🎲 Игры: {user_info['games_played']}

🔥 <b>Серии:</b>
⚡ Текущая серия: {user_info['streak']}
🏆 Лучшая серия: {user_info['max_streak']}

📊 <b>Средние показатели:</b>
💰 Очков за игру: {avg_score_per_game:.1f}
🎯 Достижений: {len(user_info['achievements'])}
"""

    await callback.message.edit_text(detailed_text, reply_markup=stats_keyboard())
    await callback.answer()

@router.callback_query(F.data == "achievements")
async def show_achievements(callback: CallbackQuery):
    """Показать достижения пользователя"""
    user_info = user_data.get_info(callback.from_user.id)
    achievements = user_info["achievements"]

    if not achievements:
        text = """
🏆 <b>Достижения</b>

😔 У тебя пока нет достижений.

<b>Доступные достижения:</b>
🎯 Первый ответ - ответь на первый вопрос
🔥 Серия 3 - ответь правильно 3 раза подряд
🔥🔥 Серия 7 - ответь правильно 7 раз подряд
🔥🔥🔥 Серия 30 - ответь правильно 30 раз подряд
💯 100 очков - набери 100 очков
🏆 500 очков - набери 500 очков
👑 1000 очков - набери 1000 очков
🧠 Мастер викторин - ответь правильно на 50 вопросов
🧩 Разгадчик загадок - реши 20 загадок
📝 Чемпион слов - угадай 10 слов

Играй больше, чтобы получить их!
"""
    else:
        text = f"""
🏆 <b>Твои достижения ({len(achievements)})</b>

"""
        for i, achievement in enumerate(achievements, 1):
            text += f"{i}. {achievement}\n"

        text += f"\n🎯 <b>Прогресс:</b> {len(achievements)}/11 достижений"

    await callback.message.edit_text(text, reply_markup=main_menu())
    await callback.answer()

@router.callback_query(F.data == "leaderboard")
async def show_leaderboard_callback(callback: CallbackQuery):
    """Показать рейтинг игроков"""
    await show_leaderboard(callback.message, edit=True)
    await callback.answer()

@router.callback_query(F.data.startswith("leaderboard:page:"))
async def leaderboard_page(callback: CallbackQuery):
    """Показать страницу рейтинга"""
    page = int(callback.data.split(":")[-1])
    await show_leaderboard(callback.message, page=page, edit=True)
    await callback.answer()

@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    """Показать помощь"""
    help_text = """
❓ <b>Помощь</b>

<b>Как пользоваться ботом:</b>
1. Выбери раздел в главном меню
2. Отвечай на вопросы, набирай очки
3. Следи за своей статистикой
4. Собирай достижения

<b>Система очков:</b>
• Легкие вопросы: +2 очка
• Средние вопросы: +4 очка  
• Сложные вопросы: +6 очков
• Загадки: +3 очка
• Угаданные слова: +5 очков
• Неправильный ответ: -1 очко

<b>Советы:</b>
• Играй каждый день для поддержания серии
• Изучай объяснения к вопросам
• Попробуй все категории для разнообразия
"""

    await callback.message.edit_text(help_text, reply_markup=help_keyboard())
    await callback.answer()

async def show_user_stats(message: Message, user_id: int, edit: bool = False):
    """Показать статистику пользователя"""
    user_info = user_data.get_info(user_id)

    # Вычисляем точность
    accuracy = 0
    if user_info["answered"] > 0:
        accuracy = (user_info["correct"] / user_info["answered"]) * 100

    # Определяем уровень
    level = calculate_user_level(user_info["score"])

    stats_text = f"""
📊 <b>Твоя статистика</b>

🎯 <b>Уровень:</b> {level}
🏆 <b>Очки:</b> {user_info['score']}
❓ <b>Всего ответов:</b> {user_info['answered']}
✅ <b>Правильных:</b> {user_info['correct']}
📈 <b>Точность:</b> {accuracy:.1f}%

🔥 <b>Текущая серия:</b> {user_info['streak']}
🏆 <b>Лучшая серия:</b> {user_info['max_streak']}

🎮 <b>Активность:</b>
🧩 Загадок решено: {user_info['riddles_solved']}
🔤 Слов угадано: {user_info['words_guessed']}
🎲 Игр сыграно: {user_info['games_played']}

🏅 <b>Достижений:</b> {len(user_info['achievements'])}
"""

    if edit:
        await message.edit_text(stats_text, reply_markup=stats_keyboard())
    else:
        await message.answer(stats_text, reply_markup=stats_keyboard())

async def show_leaderboard(message: Message, page: int = 1, edit: bool = False):
    """Показать рейтинг игроков"""
    leaderboard = user_data.get_leaderboard(50)  # Получаем топ-50

    if not leaderboard:
        text = "📊 <b>Рейтинг игроков</b>\n\n😔 Рейтинг пуст. Будь первым!"
        keyboard = main_menu()
    else:
        # Пагинация
        items_per_page = 10
        total_pages = (len(leaderboard) - 1) // items_per_page + 1
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page

        current_page_leaders = leaderboard[start_idx:end_idx]

        text = f"📊 <b>Рейтинг игроков</b>\n<i>Страница {page}/{total_pages}</i>\n\n"

        for i, (user_id, user_info) in enumerate(current_page_leaders, start_idx + 1):
            # Определяем медаль для топ-3
            medal = ""
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"

            # Показываем только первые 8 символов user_id для анонимности
            user_display = f"User{str(user_id)[:4]}***"
            accuracy = 0
            if user_info["answered"] > 0:
                accuracy = (user_info["correct"] / user_info["answered"]) * 100

            text += f"{medal}<b>{i}.</b> {user_display}\n"
            text += f"   🏆 {user_info['score']} очков | 📈 {accuracy:.0f}% | 🔥 {user_info['max_streak']}\n\n"

        keyboard = pagination_keyboard(page, total_pages, "leaderboard")

    if edit:
        await message.edit_text(text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)

def calculate_user_level(score: int) -> int:
    """Вычислить уровень пользователя на основе очков"""
    if score < 50:
        return 1
    elif score < 150:
        return 2
    elif score < 300:
        return 3
    elif score < 500:
        return 4
    elif score < 800:
        return 5
    elif score < 1200:
        return 6
    elif score < 1700:
        return 7
    elif score < 2300:
        return 8
    elif score < 3000:
        return 9
    else:
        return 10

@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    """Заглушка для неактивных кнопок"""
    await callback.answer()