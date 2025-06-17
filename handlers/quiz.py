from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from keyboards import quiz_menu, back_button, difficulty_keyboard
from questions import question_bank, Difficulty, Category, check_answer
from data import user_data
import logging
import asyncio
import random

router = Router()
logger = logging.getLogger(__name__)

# Словарь для хранения активных викторин пользователей
active_quizzes = {}

@router.callback_query(F.data == "quiz")
async def quiz_menu_handler(callback: CallbackQuery):
    """Показать меню викторины"""
    await callback.message.edit_text(
        "🧠 <b>Викторина</b>\n\nВыбери тип вопросов:",
        reply_markup=quiz_menu()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("quiz:"))
async def quiz_handler(callback: CallbackQuery):
    """Обработчик различных типов викторин"""
    quiz_type = callback.data.split(":")[1]
    user_id = callback.from_user.id

    if quiz_type == "easy":
        await start_quiz(callback, Difficulty.EASY)
    elif quiz_type == "medium":
        await start_quiz(callback, Difficulty.MEDIUM)
    elif quiz_type == "hard":
        await start_quiz(callback, Difficulty.HARD)
    elif quiz_type == "random":
        difficulty = random.choice(list(Difficulty))
        await start_quiz(callback, difficulty)
    elif quiz_type == "speed":
        await start_speed_quiz(callback)
    elif quiz_type == "mixed":
        await start_mixed_quiz(callback)

    await callback.answer()

async def start_quiz(callback: CallbackQuery, difficulty: Difficulty):
    """Начать обычную викторину"""
    user_id = callback.from_user.id

    # Получаем случайный вопрос заданной сложности
    question_data = question_bank.get_question(difficulty=difficulty)

    if not question_data:
        await callback.message.edit_text(
            "😔 К сожалению, вопросы этой сложности временно недоступны.",
            reply_markup=back_button("quiz")
        )
        return

    # Сохраняем состояние викторины
    active_quizzes[user_id] = {
        "question": question_data,
        "start_time": asyncio.get_event_loop().time(),
        "type": "normal",
        "difficulty": difficulty
    }

    difficulty_emoji = {
        Difficulty.EASY: "🟢",
        Difficulty.MEDIUM: "🟡",
        Difficulty.HARD: "🔴"
    }

    difficulty_points = {
        Difficulty.EASY: 2,
        Difficulty.MEDIUM: 4,
        Difficulty.HARD: 6
    }

    quiz_text = f"""
🧠 <b>Викторина</b>
{difficulty_emoji[difficulty]} <b>Сложность:</b> {difficulty.name.title()}
💰 <b>За правильный ответ:</b> {difficulty_points[difficulty]} очков

❓ <b>Вопрос:</b>
{question_data['q']}

✍️ <i>Напишите ваш ответ...</i>
"""

    await callback.message.edit_text(quiz_text, reply_markup=back_button("quiz"))

async def start_speed_quiz(callback: CallbackQuery):
    """Начать быструю викторину (5 вопросов за 60 секунд)"""
    user_id = callback.from_user.id

    questions = []
    for _ in range(5):
        q = question_bank.get_question()
        questions.append(q)

    active_quizzes[user_id] = {
        "questions": questions,
        "current_question": 0,
        "correct_answers": 0,
        "start_time": asyncio.get_event_loop().time(),
        "type": "speed",
        "time_limit": 60
    }

    await show_speed_question(callback.message, user_id)

async def start_mixed_quiz(callback: CallbackQuery):
    """Начать смешанную викторину (разные категории)"""
    user_id = callback.from_user.id

    questions = []
    categories = list(Category)

    for _ in range(10):
        category = random.choice(categories)
        difficulty = random.choice(list(Difficulty))
        q = question_bank.get_question(category=category, difficulty=difficulty)
        questions.append(q)

    active_quizzes[user_id] = {
        "questions": questions,
        "current_question": 0,
        "correct_answers": 0,
        "start_time": asyncio.get_event_loop().time(),
        "type": "mixed"
    }

    await show_mixed_question(callback.message, user_id)

async def show_speed_question(message: Message, user_id: int):
    """Показать вопрос в быстрой викторине"""
    quiz = active_quizzes.get(user_id)
    if not quiz:
        return

    current_q = quiz["current_question"]
    total_q = len(quiz["questions"])
    question = quiz["questions"][current_q]

    elapsed_time = asyncio.get_event_loop().time() - quiz["start_time"]
    remaining_time = max(0, quiz["time_limit"] - elapsed_time)

    if remaining_time <= 0:
        await finish_speed_quiz(message, user_id)
        return

    quiz_text = f"""
⚡ <b>Быстрая викторина</b>
📊 <b>Прогресс:</b> {current_q + 1}/{total_q}
⏰ <b>Осталось времени:</b> {int(remaining_time)} сек
✅ <b>Правильных ответов:</b> {quiz["correct_answers"]}

❓ <b>Вопрос:</b>
{question['q']}

✍️ <i>Быстрее отвечайте!</i>
"""

    await message.edit_text(quiz_text, reply_markup=back_button("quiz"))

async def show_mixed_question(message: Message, user_id: int):
    """Показать вопрос в смешанной викторине"""
    quiz = active_quizzes.get(user_id)
    if not quiz:
        return

    current_q = quiz["current_question"]
    total_q = len(quiz["questions"])
    question = quiz["questions"][current_q]

    difficulty_emoji = {
        Difficulty.EASY: "🟢",
        Difficulty.MEDIUM: "🟡",
        Difficulty.HARD: "🔴"
    }

    quiz_text = f"""
🎪 <b>Смешанная викторина</b>
📊 <b>Прогресс:</b> {current_q + 1}/{total_q}
{difficulty_emoji[question['difficulty']]} <b>Сложность:</b> {question['difficulty'].name.title()}
📂 <b>Категория:</b> {question['category'].value.title()}
✅ <b>Правильных ответов:</b> {quiz["correct_answers"]}

❓ <b>Вопрос:</b>
{question['q']}

✍️ <i>Напишите ваш ответ...</i>
"""

    await message.edit_text(quiz_text, reply_markup=back_button("quiz"))

@router.message()
async def process_quiz_answer(message: Message):
    """Обработка ответов на вопросы викторины"""
    user_id = message.from_user.id

    if user_id not in active_quizzes:
        return

    quiz = active_quizzes[user_id]
    user_answer = message.text.strip()

    if quiz["type"] == "normal":
        await process_normal_answer(message, user_id, user_answer)
    elif quiz["type"] == "speed":
        await process_speed_answer(message, user_id, user_answer)
    elif quiz["type"] == "mixed":
        await process_mixed_answer(message, user_id, user_answer)

async def process_normal_answer(message: Message, user_id: int, user_answer: str):
    """Обработка ответа в обычной викторине"""
    quiz = active_quizzes[user_id]
    question = quiz["question"]
    difficulty = quiz["difficulty"]

    is_correct = check_answer(question, user_answer)

    # Подсчет очков
    points_map = {
        Difficulty.EASY: 2,
        Difficulty.MEDIUM: 4,
        Difficulty.HARD: 6
    }

    if is_correct:
        points = points_map[difficulty]
        await user_data.update_score(user_id, points)
        await user_data.update_stat(user_id, "correct", 1)
        await user_data.update_streak(user_id)

        result_text = f"""
✅ <b>Правильно!</b>
💰 +{points} очков

💡 <b>Объяснение:</b>
{question.get('explanation', 'Отличная работа!')}
"""
    else:
        await user_data.update_score(user_id, -1)
        correct_answer = question['a'][0]

        result_text = f"""
❌ <b>Неправильно!</b>
💰 -1 очко

✅ <b>Правильный ответ:</b> {correct_answer}

💡 <b>Объяснение:</b>
{question.get('explanation', 'Не расстраивайтесь, в следующий раз получится!')}
"""

    await user_data.update_stat(user_id, "answered", 1)

    # Удаляем викторину из активных
    del active_quizzes[user_id]

    await message.answer(result_text, reply_markup=quiz_menu())

async def process_speed_answer(message: Message, user_id: int, user_answer: str):
    """Обработка ответа в быстрой викторине"""
    quiz = active_quizzes[user_id]

    # Проверяем время
    elapsed_time = asyncio.get_event_loop().time() - quiz["start_time"]
    if elapsed_time > quiz["time_limit"]:
        await finish_speed_quiz(message, user_id)
        return

    question = quiz["questions"][quiz["current_question"]]
    is_correct = check_answer(question, user_answer)

    if is_correct:
        quiz["correct_answers"] += 1
        await user_data.update_score(user_id, 3)
        await user_data.update_stat(user_id, "correct", 1)
    else:
        await user_data.update_score(user_id, -1)

    await user_data.update_stat(user_id, "answered", 1)

    # Переходим к следующему вопросу
    quiz["current_question"] += 1

    if quiz["current_question"] >= len(quiz["questions"]):
        await finish_speed_quiz(message, user_id)
    else:
        await show_speed_question(message, user_id)

async def process_mixed_answer(message: Message, user_id: int, user_answer: str):
    """Обработка ответа в смешанной викторине"""
    quiz = active_quizzes[user_id]
    question = quiz["questions"][quiz["current_question"]]

    is_correct = check_answer(question, user_answer)

    # Подсчет очков в зависимости от сложности
    points_map = {
        Difficulty.EASY: 2,
        Difficulty.MEDIUM: 4,
        Difficulty.HARD: 6
    }

    if is_correct:
        points = points_map[question['difficulty']]
        quiz["correct_answers"] += 1
        await user_data.update_score(user_id, points)
        await user_data.update_stat(user_id, "correct", 1)
    else:
        await user_data.update_score(user_id, -1)

    await user_data.update_stat(user_id, "answered", 1)

    # Переходим к следующему вопросу
    quiz["current_question"] += 1

    if quiz["current_question"] >= len(quiz["questions"]):
        await finish_mixed_quiz(message, user_id)
    else:
        await show_mixed_question(message, user_id)

async def finish_speed_quiz(message: Message, user_id: int):
    """Завершение быстрой викторины"""
    quiz = active_quizzes.get(user_id)
    if not quiz:
        return

    correct = quiz["correct_answers"]
    total = len(quiz["questions"])
    accuracy = (correct / total) * 100 if total > 0 else 0

    result_text = f"""
⚡ <b>Быстрая викторина завершена!</b>

📊 <b>Результаты:</b>
✅ Правильных ответов: {correct}/{total}
📈 Точность: {accuracy:.1f}%
⏱️ Время: 60 секунд

🏆 <b>Отличная работа!</b>
"""

    await user_data.update_stat(user_id, "games_played", 1)
    del active_quizzes[user_id]

    await message.answer(result_text, reply_markup=quiz_menu())

async def finish_mixed_quiz(message: Message, user_id: int):
    """Завершение смешанной викторины"""
    quiz = active_quizzes.get(user_id)
    if not quiz:
        return

    correct = quiz["correct_answers"]
    total = len(quiz["questions"])
    accuracy = (correct / total) * 100 if total > 0 else 0

    result_text = f"""
🎪 <b>Смешанная викторина завершена!</b>

📊 <b>Результаты:</b>
✅ Правильных ответов: {correct}/{total}
📈 Точность: {accuracy:.1f}%

🏆 <b>Поздравляем!</b>
"""

    await user_data.update_stat(user_id, "games_played", 1)
    del active_quizzes[user_id]

    await message.answer(result_text, reply_markup=quiz_menu())
