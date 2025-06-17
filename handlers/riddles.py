from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter, state
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import riddles_menu, back_button
from data import user_data
from questions import question_bank
import logging

router = Router()
logger = logging.getLogger(__name__)


class RiddleState(StatesGroup):
    """Состояния для игры в загадки."""
    waiting_answer = State()

@router.callback_query(F.data == "riddles")
async def riddles_menu_callback(callback: CallbackQuery):
    """Показать меню загадок"""
    await callback.message.edit_text(
        "🧩 <b>Загадки</b>\n\nВыбери тип загадок:",
        reply_markup=riddles_menu()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("riddles:"))
async def riddle_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик загадок"""
    riddle_type = callback.data.split(":")[1]
    user_id = callback.from_user.id

    try:
        # Получаем загадку и сохраняем в состоянии
        riddle = question_bank.get_riddle(riddle_type)
        await state.set_state(RiddleState.waiting_answer)
        await state.update_data(riddle=riddle)

        riddle_text = f"""
🧩 <b>Загадка</b>

❓ <b>Загадка:</b>
{riddle['q']}

💰 <b>Очков за правильный ответ:</b> 3

<i>Напиши ответ сообщением:</i>
"""

        await callback.message.edit_text(riddle_text, reply_markup=back_button("riddles"))
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка при получении загадки: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке загадки. Попробуй еще раз.",
            reply_markup=back_button("riddles")
        )
        await callback.answer()

@router.message(StateFilter(RiddleState.waiting_answer), F.text)
async def handle_riddle_answer(message: Message, state: FSMContext):
    """Обработчик ответов на загадки"""
    user_id = message.from_user.id

    try:
        data = await state.get_data()
        riddle = data.get("riddle")
        if not riddle:
            await state.clear()
            return

        user_answer = message.text.lower().strip()

        # Проверяем ответ
        correct_answers = [ans.lower() for ans in riddle["a"]]
        is_correct = user_answer in correct_answers

        if is_correct:
            # Правильный ответ
            points = 3
            await user_data.update_score(user_id, points)
            await user_data.update_stat(user_id, "riddles_solved", 1)

            # Обновляем серию
            streak, streak_updated = await user_data.update_streak(user_id)

            streak_text = ""
            if streak_updated:
                streak_text = f"\n🔥 <b>Серия:</b> {streak}"

            response_text = f"""
✅ <b>Правильно!</b>

💰 <b>Получено очков:</b> +{points}
{streak_text}

💡 <b>Подсказка была:</b> {riddle.get('hint', 'Отличная работа!')}

Хочешь еще загадку?
"""
        else:
            # Неправильный ответ - даем подсказку
            hint_text = f"\n💡 <b>Подсказка:</b> {riddle.get('hint', 'Подумай еще!')}"

            response_text = f"""
❌ <b>Неправильно!</b>

{hint_text}

<i>Попробуй еще раз или выбери другую загадку.</i>
"""

            # Не удаляем загадку, даем возможность попробовать еще раз
            await message.answer(response_text)
            return

        # Очищаем состояние после правильного ответа
        await state.clear()
        await message.answer(response_text, reply_markup=riddles_menu())

    except Exception as e:
        logger.error(f"Ошибка при обработке ответа на загадку: {e}")
        await state.clear()
        await message.answer(
            "❌ Произошла ошибка при обработке ответа.",
            reply_markup=riddles_menu()
        )

@router.callback_query(F.data == "riddle_hint")
async def show_riddle_hint(callback: CallbackQuery):
    """Показать подсказку к загадке"""
    user_id = callback.from_user.id

    try:
        data = await state.get_data()
        riddle = data.get("riddle")
        if not riddle:
            await callback.answer("Сначала выбери загадку!")
            return
        hint = riddle.get('hint', 'Подсказки нет')
        await callback.answer(f"💡 Подсказка: {hint}", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка при показе подсказки: {e}")
        await state.clear()
        await callback.answer("Ошибка", show_alert=True)

@router.callback_query(F.data == "riddle_skip")
async def skip_riddle(callback: CallbackQuery):
    """Пропустить текущую загадку"""
    user_id = callback.from_user.id

    try:
        data = await state.get_data()
        riddle = data.get("riddle")
        if not riddle:
            await callback.answer("Сначала выбери загадку!")
            return

        correct_answer = riddle["a"][0]

        # Убираем очки за пропуск
        await user_data.update_score(user_id, -1)

        await state.clear()

        text = f"""
⏭️ <b>Загадка пропущена</b>

✅ <b>Правильный ответ:</b> {correct_answer}
💰 <b>Потеряно очков:</b> -1

💡 <b>Подсказка:</b> {riddle.get('hint', 'Изучай больше!')}

Попробуй другую загадку!
"""

        await callback.message.edit_text(text, reply_markup=riddles_menu())
    except Exception as e:
        logger.error(f"Ошибка при пропуске загадки: {e}")
        await state.clear()
        await callback.answer("Ошибка", show_alert=True)

    await callback.answer()