from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import BaseFilter  # +++
from keyboards import quiz_menu, back_button
from data import user_data
from questions import question_bank, Difficulty, Category, check_answer
import logging
import random

router = Router()
logger = logging.getLogger(__name__)

# Временное хранение текущих вопросов для пользователей
user_questions = {}

# --------------------------------------------------------------------------- #
#                              ДОБАВЛЕН ФИЛЬТР                                #
# --------------------------------------------------------------------------- #
class HasActiveQuiz(BaseFilter):
    """Фильтр: у пользователя есть активный вопрос викторины"""
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in user_questions
# --------------------------------------------------------------------------- #

@router.callback_query(F.data == "quiz")
async def quiz_menu_callback(callback: CallbackQuery):
    """Показать меню викторины"""
    await callback.message.edit_text(
        "🧠 <b>Викторина</b>\n\nВыбери уровень сложности:",
        reply_markup=quiz_menu()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("quiz:"))
async def quiz_handler(callback: CallbackQuery):
    """Обработчик викторины"""
    quiz_type = callback.data.split(":")[1]
    user_id = callback.from_user.id

    # Определяем параметры вопроса
    category = None
    difficulty = None

    if quiz_type == "easy":
        difficulty = Difficulty.EASY
    elif quiz_type == "medium":
        difficulty = Difficulty.MEDIUM
    elif quiz_type == "hard":
        difficulty = Difficulty.HARD
    elif quiz_type == "random":
        difficulty = random.choice([Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])
    elif quiz_type == "speed":
        # Быстрая викторина - только легкие вопросы
        difficulty = Difficulty.EASY
    elif quiz_type == "mixed":
        # Смешанная викторина - случайная категория и сложность
        category = random.choice(list(Category))
        difficulty = random.choice([Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])

    try:
        # Получаем вопрос
        question = question_bank.get_question(category, difficulty)
        user_questions[user_id] = question

        # Определяем очки за вопрос
        points = get_question_points(question["difficulty"])

        question_text = f"""
🧠 <b>Викторина</b>

📝 <b>Вопрос:</b>
{question['q']}

🎯 <b>Сложность:</b> {get_difficulty_name(question['difficulty'])}
💰 <b>Очков за правильный ответ:</b> {points}

<i>Напиши ответ сообщением:</i>
"""

        await callback.message.edit_text(question_text, reply_markup=back_button("quiz"))
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при получении вопроса: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке вопроса. Попробуй еще раз.",
            reply_markup=back_button("quiz")
        )
        await callback.answer()

# --------------------------------------------------------------------------- #
#            ОБНОВЛЁН ДЕКОРАТОР: ДОБАВЛЕН ФИЛЬТР HasActiveQuiz                #
# --------------------------------------------------------------------------- #
@router.message(HasActiveQuiz(), F.text)
async def handle_quiz_answer(message: Message):
    """Обработчик ответов на вопросы викторины"""
    user_id = message.from_user.id

    # Проверка более не нужна – фильтр гарантирует наличие вопроса
    question = user_questions[user_id]
    user_answer = message.text.strip()

    try:
        # Проверяем ответ
        is_correct = check_answer(question, user_answer)
        points = get_question_points(question["difficulty"])

        if is_correct:
            # Правильный ответ
            await user_data.update_stat(user_id, "answered", 1)
            await user_data.update_stat(user_id, "correct", 1)
            await user_data.update_score(user_id, points)

            # Обновляем серию
            streak, streak_updated = await user_data.update_streak(user_id)

            streak_text = ""
            if streak_updated:
                streak_text = f"\n🔥 <b>Серия:</b> {streak}"

            response_text = f"""
✅ <b>Правильно!</b>

💰 <b>Получено очков:</b> +{points}
{streak_text}

📚 <b>Объяснение:</b>
{question.get('explanation', 'Молодец!')}

Хочешь продолжить?
"""
        else:
            # Неправильный ответ
            await user_data.update_stat(user_id, "answered", 1)
            await user_data.update_score(user_id, -1)

            # Сбрасываем серию
            user_info = user_data.get_info(user_id)
            user_info["streak"] = 0
            await user_data.save()

            correct_answer = question["a"][0]
            response_text = f"""
❌ <b>Неправильно!</b>

💰 <b>Потеряно очков:</b> -1
🔥 <b>Серия сброшена</b>

✅ <b>Правильный ответ:</b> {correct_answer}

📚 <b>Объяснение:</b>
{question.get('explanation', 'Изучай больше!')}

Не расстраивайся, попробуй еще раз!
"""

        # Удаляем вопрос из памяти
        del user_questions[user_id]

        await message.answer(response_text, reply_markup=quiz_menu())

    except Exception as e:
        logger.error(f"Ошибка при обработке ответа: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке ответа.",
            reply_markup=quiz_menu()
        )

def get_question_points(difficulty: Difficulty) -> int:
    """Получить количество очков за вопрос"""
    if difficulty == Difficulty.EASY:
        return 2
    elif difficulty == Difficulty.MEDIUM:
        return 4
    elif difficulty == Difficulty.HARD:
        return 6
    return 2

def get_difficulty_name(difficulty: Difficulty) -> str:
    """Получить название сложности"""
    if difficulty == Difficulty.EASY:
        return "🟢 Легкий"
    elif difficulty == Difficulty.MEDIUM:
        return "🟡 Средний"
    elif difficulty == Difficulty.HARD:
        return "🔴 Сложный"
    return "🟢 Легкий"