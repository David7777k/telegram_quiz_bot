from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards import games_menu, rps_keyboard, back_button, main_menu
from data import user_data
import logging
import random

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data == "games")
async def games_menu_callback(callback: CallbackQuery):
    """Показать меню игр"""
    await callback.message.edit_text(
        "🎲 <b>Игры</b>\n\nВыбери игру:",
        reply_markup=games_menu()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("game:"))
async def game_handler(callback: CallbackQuery):
    """Обработчик игр"""
    game_type = callback.data.split(":")[1]
    user_id = callback.from_user.id

    try:
        if game_type == "dice":
            await play_dice(callback, user_id)
        elif game_type == "coin":
            await play_coin(callback, user_id)
        elif game_type == "roulette":
            await play_roulette(callback, user_id)
        elif game_type == "number":
            await play_number_guess(callback, user_id)
        elif game_type == "rps":
            await show_rps_menu(callback)
        elif game_type == "double_dice":
            await play_double_dice(callback, user_id)
        else:
            await callback.message.edit_text(
                "❌ Неизвестная игра",
                reply_markup=games_menu()
            )
    except Exception as e:
        logger.error(f"Ошибка в игре {game_type}: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка в игре. Попробуй еще раз.",
            reply_markup=games_menu()
        )

    await callback.answer()

async def play_dice(callback: CallbackQuery, user_id: int):
    """Игра в кубик"""
    user_roll = random.randint(1, 6)
    bot_roll = random.randint(1, 6)

    if user_roll > bot_roll:
        result = "🎉 Ты выиграл!"
        points = 3
        await user_data.update_score(user_id, points)
    elif user_roll < bot_roll:
        result = "😔 Ты проиграл!"
        points = -1
        await user_data.update_score(user_id, points)
    else:
        result = "🤝 Ничья!"
        points = 1
        await user_data.update_score(user_id, points)

    await user_data.update_stat(user_id, "games_played", 1)

    text = f"""
🎲 <b>Игра в кубик</b>

🎯 <b>Твой результат:</b> {user_roll}
🤖 <b>Результат бота:</b> {bot_roll}

{result}
💰 <b>Очков:</b> {'+' if points > 0 else ''}{points}
"""

    await callback.message.edit_text(text, reply_markup=games_menu())

async def play_coin(callback: CallbackQuery, user_id: int):
    """Игра в монетку"""
    user_choice = random.choice(["Орёл", "Решка"])
    result = random.choice(["Орёл", "Решка"])

    if user_choice == result:
        outcome = "🎉 Угадал!"
        points = 2
        await user_data.update_score(user_id, points)
    else:
        outcome = "😔 Не угадал!"
        points = -1
        await user_data.update_score(user_id, points)

    await user_data.update_stat(user_id, "games_played", 1)

    text = f"""
🪙 <b>Игра в монетку</b>

🎯 <b>Твой выбор:</b> {user_choice}
🎲 <b>Результат:</b> {result}

{outcome}
💰 <b>Очков:</b> {'+' if points > 0 else ''}{points}
"""

    await callback.message.edit_text(text, reply_markup=games_menu())

async def play_roulette(callback: CallbackQuery, user_id: int):
    """Игра в рулетку"""
    user_number = random.randint(0, 36)
    winning_number = random.randint(0, 36)

    if user_number == winning_number:
        result = "🎉 ДЖЕКПОТ! Точное попадание!"
        points = 10
    elif abs(user_number - winning_number) <= 2:
        result = "🎊 Близко! Хороший результат!"
        points = 5
    elif abs(user_number - winning_number) <= 5:
        result = "👍 Неплохо!"
        points = 2
    else:
        result = "😔 Не повезло!"
        points = -1

    await user_data.update_score(user_id, points)
    await user_data.update_stat(user_id, "games_played", 1)

    text = f"""
🎰 <b>Рулетка</b>

🎯 <b>Твое число:</b> {user_number}
🎲 <b>Выпавшее число:</b> {winning_number}

{result}
💰 <b>Очков:</b> {'+' if points > 0 else ''}{points}
"""

    await callback.message.edit_text(text, reply_markup=games_menu())

async def play_number_guess(callback: CallbackQuery, user_id: int):
    """Игра угадай число"""
    secret_number = random.randint(1, 10)
    user_guess = random.randint(1, 10)

    if user_guess == secret_number:
        result = "🎉 Угадал! Отличная интуиция!"
        points = 5
    elif abs(user_guess - secret_number) == 1:
        result = "🔥 Очень близко!"
        points = 2
    else:
        result = "😔 Не угадал!"
        points = -1

    await user_data.update_score(user_id, points)
    await user_data.update_stat(user_id, "games_played", 1)

    text = f"""
🎯 <b>Угадай число (1-10)</b>

🤔 <b>Твоя догадка:</b> {user_guess}
🎲 <b>Загаданное число:</b> {secret_number}

{result}
💰 <b>Очков:</b> {'+' if points > 0 else ''}{points}
"""

    await callback.message.edit_text(text, reply_markup=games_menu())

async def play_double_dice(callback: CallbackQuery, user_id: int):
    """Игра в два кубика"""
    user_dice1 = random.randint(1, 6)
    user_dice2 = random.randint(1, 6)
    bot_dice1 = random.randint(1, 6)
    bot_dice2 = random.randint(1, 6)

    user_sum = user_dice1 + user_dice2
    bot_sum = bot_dice1 + bot_dice2

    if user_sum > bot_sum:
        result = "🎉 Ты выиграл!"
        points = 4
    elif user_sum < bot_sum:
        result = "😔 Ты проиграл!"
        points = -1
    else:
        result = "🤝 Ничья!"
        points = 1

    # Бонус за дубль
    if user_dice1 == user_dice2:
        points += 2
        result += "\n🎊 Бонус за дубль: +2"

    await user_data.update_score(user_id, points)
    await user_data.update_stat(user_id, "games_played", 1)

    text = f"""
🎲🎲 <b>Два кубика</b>

🎯 <b>Твои кубики:</b> {user_dice1} + {user_dice2} = {user_sum}
🤖 <b>Кубики бота:</b> {bot_dice1} + {bot_dice2} = {bot_sum}

{result}
💰 <b>Очков:</b> {'+' if points > 0 else ''}{points}
"""

    await callback.message.edit_text(text, reply_markup=games_menu())

async def show_rps_menu(callback: CallbackQuery):
    """Показать меню камень-ножницы-бумага"""
    await callback.message.edit_text(
        "🎮 <b>Камень-Ножницы-Бумага</b>\n\nВыбери свой ход:",
        reply_markup=rps_keyboard()
    )

@router.callback_query(F.data.startswith("rps:"))
async def rps_game(callback: CallbackQuery):
    """Игра камень-ножницы-бумага"""
    user_choice = callback.data.split(":")[1]
    user_id = callback.from_user.id

    choices = ["rock", "scissors", "paper"]
    bot_choice = random.choice(choices)

    choice_emoji = {
        "rock": "🗿 Камень",
        "scissors": "✂️ Ножницы",
        "paper": "📄 Бумага"
    }

    # Определяем победителя
    if user_choice == bot_choice:
        result = "🤝 Ничья!"
        points = 0
    elif (user_choice == "rock" and bot_choice == "scissors") or \
            (user_choice == "scissors" and bot_choice == "paper") or \
            (user_choice == "paper" and bot_choice == "rock"):
        result = "🎉 Ты выиграл!"
        points = 3
    else:
        result = "😔 Ты проиграл!"
        points = -1

    await user_data.update_score(user_id, points)
    await user_data.update_stat(user_id, "games_played", 1)

    text = f"""
🎮 <b>Камень-Ножницы-Бумага</b>

🎯 <b>Твой выбор:</b> {choice_emoji[user_choice]}
🤖 <b>Выбор бота:</b> {choice_emoji[bot_choice]}

{result}
💰 <b>Очков:</b> {'+' if points > 0 else ''}{points}
"""

    await callback.message.edit_text(text, reply_markup=games_menu())
    await callback.answer()