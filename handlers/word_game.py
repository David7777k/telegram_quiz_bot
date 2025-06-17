from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards import word_game_menu, back_button
from data import user_data
from questions import question_bank
import logging
import random

router = Router()
logger = logging.getLogger(__name__)

# Временное хранение текущих слов для пользователей
user_words = {}


def create_word_mask(word: str, guessed: set[str] = None) -> str:
    guessed = guessed or set()
    return "".join(letter if letter in guessed else "_" for letter in word)


def get_word_points(difficulty: str) -> int:
    # Пример: начисляем больше очков за сложные слова
    return {"short": 5, "medium": 10, "long": 15, "hard": 20}.get(difficulty, 10)


def get_difficulty_name(difficulty: str) -> str:
    return {"short": "Легкий", "medium": "Средний", "long": "Длинный", "hard": "Сложный"}.get(difficulty, "Средний")


@router.callback_query(F.data == "word")
async def word_menu_callback(callback: CallbackQuery):
    """Показать меню игры в слова"""
    await callback.message.edit_text(
        "🔤 <b>Угадай слово</b>\n\nВыбери уровень сложности:",
        reply_markup=word_game_menu()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("word:"))
async def word_handler(callback: CallbackQuery):
    """Обработчик старта игры в слова"""
    word_type = callback.data.split(":")[1]
    user_id = callback.from_user.id

    # Определяем сложность
    difficulty = {
        "short": "short",
        "long": "long",
        "hard": "hard"
    }.get(word_type, random.choice(["short", "medium", "long"]))

    word = question_bank.get_word(difficulty).lower()
    masked = create_word_mask(word)
    points = get_word_points(difficulty)

    user_words[user_id] = {
        "word": word,
        "masked": masked,
        "guessed_letters": set(),
        "attempts": 6,
        "difficulty": difficulty,
        "points": points
    }

    text = (
        f"🔤 <b>Угадай слово</b>\n\n"
        f"🎯 <b>Слово:</b> {masked}\n"
        f"📏 <b>Длина:</b> {len(word)} букв\n"
        f"🎚️ <b>Сложность:</b> {get_difficulty_name(difficulty)}\n"
        f"💰 <b>Очков за угадывание:</b> {points}\n"
        f"❤️ <b>Попыток осталось:</b> 6\n\n"
        f"<i>Напиши букву или целое слово:</i>"
    )

    await callback.message.edit_text(text, reply_markup=back_button("word"))
    await callback.answer()


@router.message(F.text)
async def handle_word_guess(message: Message):
    """Обработчик угадывания слов"""
    user_id = message.from_user.id
    guess = message.text.strip().lower()

    # Проверяем, есть ли активная игра
    if user_id not in user_words:
        return  # Нет активной игры

    game = user_words[user_id]
    word = game["word"]
    guessed = game["guessed_letters"]
    attempts = game["attempts"]
    points = game["points"]

    response = ""

    # Полное слово
    if len(guess) > 1:
        if guess == word:
            response = f"🎉 Поздравляю! Ты угадал слово <b>{word}</b> и заработал <b>{points}</b> очков."
            user_data.add_points(user_id, points)
            del user_words[user_id]
        else:
            game["attempts"] -= 1
            if game["attempts"] <= 0:
                response = f"💥 Ты исчерпал все попытки. Правильное слово: <b>{word}</b>."
                del user_words[user_id]
            else:
                response = (
                    f"❌ Неверно. Осталось попыток: <b>{game['attempts']}</b>\n"
                    f"Слово: {game['masked']}"
                )

    # Буква
    else:
        letter = guess
        if letter in guessed:
            response = f"⚠️ Буква <b>{letter}</b> уже была. Попробуй другую."
        elif letter in word:
            guessed.add(letter)
            new_mask = create_word_mask(word, guessed)
            game["masked"] = new_mask
            if "_" not in new_mask:
                response = f"🎉 Отлично! Ты открыл все буквы: <b>{word}</b>. Получено <b>{points}</b> очков."
                user_data.add_points(user_id, points)
                del user_words[user_id]
            else:
                response = (
                    f"✅ Есть такая буква!\n"
                    f"Слово: {new_mask}\n"
                    f"Попыток осталось: <b>{attempts}</b>"
                )
        else:
            game["attempts"] -= 1
            if game["attempts"] <= 0:
                response = f"💥 Ты исчерпал все попытки. Правильное слово: <b>{word}</b>."
                del user_words[user_id]
            else:
                response = (
                    f"❌ Буквы <b>{letter}</b> нет. Осталось попыток: <b>{game['attempts']}</b>\n"
                    f"Слово: {game['masked']}"
                )

    await message.answer(response, reply_markup=back_button("word"))
