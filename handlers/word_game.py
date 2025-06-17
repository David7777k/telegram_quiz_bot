from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import word_game_menu, back_button
from data import user_data
from questions import question_bank
import logging
import random

router = Router()
logger = logging.getLogger(__name__)


class WordState(StatesGroup):
    """Состояния для игры 'Угадай слово'."""
    guessing = State()



def create_word_mask(word: str, guessed: set[str] = None) -> list[str]:
    """Возвращает список символов: либо букву, если она угадана, либо '_'."""
    guessed = guessed or set()
    return [letter if letter in guessed else "_" for letter in word]


def get_word_points(difficulty: str) -> int:
    return {"short": 5, "medium": 10, "long": 15, "hard": 20}.get(difficulty, 10)


def get_difficulty_name(difficulty: str) -> str:
    return {"short": "Легкий", "medium": "Средний", "long": "Длинный", "hard": "Сложный"}.get(difficulty, "Средний")


def get_word_hint(word: str, difficulty: str) -> str:
    """Возвращает подсказку для слова в зависимости от сложности."""
    hints = {
        # ... (ваш словарь подсказок) ...
        "кот": "🐱 Домашнее животное, которое мяукает",
        "пес": "🐕 Домашний друг, который лает",
        # добавьте остальные подсказки здесь
    }
    # Возвращаем подсказку или текст по умолчанию
    default = f"🔍 Подсказка недоступна для этого слова (сложность: {get_difficulty_name(difficulty)})"
    return hints.get(word, default)


def get_category_hint(word: str) -> str:
    """Возвращает категорию слова."""
    categories = {
        "кот": "Животные", "собака": "Животные", "слон": "Животные",
        "стол": "Мебель", "стул": "Мебель", "диван": "Мебель",
        "машина": "Транспорт", "самолет": "Транспорт", "велосипед": "Транспорт",
        "телефон": "Техника", "компьютер": "Техника", "холодильник": "Техника",
        "солнце": "Природа", "море": "Природа", "лес": "Природа",
        "дом": "Места", "школа": "Места", "магазин": "Места",
    }
    return categories.get(word, "Общие слова")


def show_letter_hint(word: str, guessed: set[str]) -> str:
    """Показывает подсказку с первой или последней буквой."""
    if not guessed:
        return f"🔤 Первая буква: <b>{word[0].upper()}</b>"
    elif len(guessed) >= 3:
        return f"🔤 Последняя буква: <b>{word[-1].upper()}</b>"
    return ""


@router.callback_query(F.data == "word")
async def word_menu_callback(callback: CallbackQuery):
    """Показать меню игры в слова."""
    logger.info("Opened word game menu")
    await callback.message.edit_text(
        "🔤 <b>Угадай слово</b>\n\nВыбери уровень сложности:",
        reply_markup=word_game_menu()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("word:"))
async def word_handler(callback: CallbackQuery, state: FSMContext):
    """Старт новой игры: выбираем слово, сохраняем состояние."""
    logger.info(f"word_handler triggered with {callback.data}")
    word_type = callback.data.split(":", 1)[1]
    user_id = callback.from_user.id

    difficulty = {
        "short": "short",
        "long": "long",
        "hard": "hard"
    }.get(word_type, random.choice(["short", "medium", "long"]))

    word = question_bank.get_word(difficulty).lower()
    points = get_word_points(difficulty)

    game = {
        "word": word,
        "guessed_letters": set(),
        "mask": create_word_mask(word),
        "attempts": 6,
        "difficulty": difficulty,
        "points": points,
        "hints_used": 0,
    }

    await state.set_state(WordState.guessing)
    await state.update_data(game=game)
    logger.info(f"Game started for user {user_id}: {word!r}")

    display_mask = " ".join(game["mask"])
    hint = get_word_hint(word, difficulty)
    category = get_category_hint(word)
    letter_hint = show_letter_hint(word, game["guessed_letters"])

    status = (
        f"🔤 <b>Угадай слово</b>\n\n"
        f"🎯 Слово: {display_mask}\n"
        f"📝 Подсказка: {hint}\n"
        f"📂 Категория: {category}\n"
        f"{letter_hint}\n"
        f"❤️ Попыток: {game['attempts']}\n"
        f"💰 Очков за угадывание: {points}\n\n"
        f"<i>Напиши букву или целое слово:</i>"
    )
    await callback.message.edit_text(status, reply_markup=back_button("word"))
    await callback.answer()


@router.message(StateFilter(WordState.guessing), F.text)
async def word_guess_handler(message: Message, state: FSMContext):
    """Обработка хода игрока, когда он в состоянии угадывания."""
    user_id = message.from_user.id
    guess = message.text.strip().lower()
    logger.info(f"User {user_id} guessed: {guess!r}")

    data = await state.get_data()
    game = data.get("game")
    if not game:
        await state.clear()
        return

    word = game["word"]
    guessed = game["guessed_letters"]
    attempts = game["attempts"]
    points = game["points"]

    response = ""

    if guess in ("подсказка", "?"):
        hints_used = game.get("hints_used", 0)
        if hints_used < 2:
            game["hints_used"] = hints_used + 1
            vowels = set("аеиоуыэюя")
            vowels_in_word = [v for v in word if v in vowels]
            if vowels_in_word:
                guessed.update(vowels_in_word)
                mask = create_word_mask(word, guessed)
                game["mask"] = mask
                game["guessed_letters"] = guessed
                response = f"💡 Подсказка: открыты все гласные буквы! (осталось {2 - game['hints_used']} подсказок)"
                await state.update_data(game=game)
            else:
                response = "💡 В этом слове нет гласных для подсказки"
        else:
            response = "⚠️ Подсказки закончились!"

    elif len(guess) > 1:
        if guess == word:
            bonus = points // 2 if game.get("hints_used", 0) == 0 else 0
            total = points + bonus
            bonus_text = f" (+{bonus} бонус!)" if bonus > 0 else ""
            response = f"🎉 Правильно! Было слово <b>{word}</b>. +{total} очков{bonus_text}."
            await user_data.update_score(user_id, total)
            await user_data.update_stat(user_id, "words_guessed", 1)
            await state.clear()
        else:
            attempts -= 1
            game["attempts"] = attempts
            if attempts <= 0:
                response = f"💥 Попытки закончились. Правильное слово: <b>{word}</b>."
                await state.clear()
            else:
                response = f"❌ Неверно, осталось {attempts} попыток."
                await state.update_data(game=game)

    else:
        letter = guess
        if letter in guessed:
            response = f"⚠️ Буква <b>{letter}</b> уже была."
        else:
            guessed.add(letter)
            if letter in word:
                mask = create_word_mask(word, guessed)
                game["mask"] = mask
                if "_" not in mask:
                    bonus = points // 2 if game.get("hints_used", 0) == 0 else 0
                    total = points + bonus
                    bonus_text = f" (+{bonus} бонус!)" if bonus > 0 else ""
                    response = f"🎉 Молодец! Слово <b>{word}</b> отгадано! +{total} очков{bonus_text}."
                    await user_data.update_score(user_id, total)
                    await user_data.update_stat(user_id, "words_guessed", 1)
                    await state.clear()
                else:
                    count = word.count(letter)
                    response = f"✅ Есть буква <b>{letter}</b>! (открыто {count} букв)"
                    game["guessed_letters"] = guessed
                    await state.update_data(game=game)
            else:
                attempts -= 1
                game["attempts"] = attempts
                game["guessed_letters"] = guessed
                if attempts <= 0:
                    response = f"💥 Попытки закончились. Правильное слово: <b>{word}</b>."
                    await state.clear()
                else:
                    response = f"❌ Нет буквы <b>{letter}</b>, осталось {attempts} попыток."
                    await state.update_data(game=game)

    if await state.get_state() == WordState.guessing:
        display_mask = " ".join(game["mask"])
        wrong = [l for l in game["guessed_letters"] if l not in word]
        display_wrong = ", ".join(sorted(wrong)) or "—"
        hint = get_word_hint(word, game["difficulty"])
        category = get_category_hint(word)
        letter_hint = show_letter_hint(word, game["guessed_letters"])
        guessed_count = len([c for c in word if c in game["guessed_letters"]])

        status = (
            f"🔤 <b>Угадай слово</b>\n\n"
            f"🎯 Слово: {display_mask}\n"
            f"📝 Подсказка: {hint}\n"
            f"📂 Категория: {category}\n"
            f"{letter_hint}\n"
            f"📊 Отгадано букв: {guessed_count}/{len(set(word))}\n"
            f"✅ Правильные: {', '.join(sorted([l for l in game['guessed_letters'] if l in word])) or '—'}\n"
            f"❌ Неправильные: {display_wrong}\n"
            f"❤️ Осталось попыток: {game['attempts']}\n"
            f"💡 Подсказок осталось: {2 - game.get('hints_used', 0)}\n\n"
            f"<i>Напиши букву, слово или 'подсказка':</i>\n"
        )
    else:
        status = ""

    await message.answer(status + response, reply_markup=back_button("word"))
    logger.info(f"Sent to {user_id}: {status + response}")
