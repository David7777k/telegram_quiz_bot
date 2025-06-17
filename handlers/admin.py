import os
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from data import user_data

# Получаем список админов из переменных окружения
admin_ids_str = os.getenv("ADMIN_IDS", "")
if admin_ids_str.strip():
    ADMIN_IDS = set(map(int, admin_ids_str.split(',')))
else:
    # По умолчанию ваш Telegram ID
    ADMIN_IDS = {1009310689}

router = Router()
logger = logging.getLogger(__name__)

# FSM состояния для админских действий
class AdminStates(StatesGroup):
    waiting_user_id_grant = State()
    waiting_points_grant = State()
    waiting_user_id_reset = State()
    waiting_user_id_fullaccess = State()

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        is_admin = message.from_user.id in ADMIN_IDS
        logger.info(f"Проверка админ-прав для пользователя {message.from_user.id}: {is_admin}")
        return is_admin

def get_admin_menu():
    """Создает главное админское меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 Выдать очки", callback_data="admin_grant_points"),
            InlineKeyboardButton(text="🔄 Сбросить данные", callback_data="admin_reset_user")
        ],
        [
            InlineKeyboardButton(text="🔑 Полный доступ", callback_data="admin_full_access"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_user_list"),
            InlineKeyboardButton(text="🔧 Системная информация", callback_data="admin_system_info")
        ],
        [
            InlineKeyboardButton(text="❌ Закрыть меню", callback_data="admin_close")
        ]
    ])
    return keyboard

def get_back_menu():
    """Кнопка возврата в главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="admin_menu")]
    ])

def get_confirmation_menu(action_data: str):
    """Меню подтверждения действия"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_{action_data}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="admin_menu")
        ]
    ])

# Отладочный хэндлер для проверки
@router.message(IsAdmin(), F.text == '/test_admin')
async def test_admin(message: Message):
    """Тестовая админ-команда"""
    await message.answer(f"✅ Админ-права работают! Ваш ID: {message.from_user.id}")

@router.message(IsAdmin(), F.text.in_(['/admin', '/panel']))
async def admin_panel(message: Message):
    """Главная команда админ-панели"""
    admin_text = """
🔧 <b>АДМИН-ПАНЕЛЬ</b> 🔧

Добро пожаловать в панель администратора!
Выберите необходимое действие:

💰 <b>Выдать очки</b> - начислить очки пользователю
🔄 <b>Сбросить данные</b> - обнулить статистику пользователя
🔑 <b>Полный доступ</b> - предоставить админские права
📊 <b>Статистика</b> - общая статистика бота
👥 <b>Список пользователей</b> - активные пользователи
🔧 <b>Системная информация</b> - техническая информация

<i>Используйте кнопки ниже для навигации</i>
    """

    await message.answer(
        admin_text,
        reply_markup=get_admin_menu(),
        parse_mode='HTML'
    )

@router.callback_query(F.data == "admin_menu")
async def show_admin_menu(callback: CallbackQuery):
    """Показать главное админское меню"""
    admin_text = """
🔧 <b>АДМИН-ПАНЕЛЬ</b> 🔧

Добро пожаловать в панель администратора!
Выберите необходимое действие:

💰 <b>Выдать очки</b> - начислить очки пользователю
🔄 <b>Сбросить данные</b> - обнулить статистику пользователя
🔑 <b>Полный доступ</b> - предоставить админские права
📊 <b>Статистика</b> - общая статистика бота
👥 <b>Список пользователей</b> - активные пользователи
🔧 <b>Системная информация</b> - техническая информация

<i>Используйте кнопки ниже для навигации</i>
    """

    await callback.message.edit_text(
        admin_text,
        reply_markup=get_admin_menu(),
        parse_mode='HTML'
    )

@router.callback_query(F.data == "admin_grant_points")
async def start_grant_points(callback: CallbackQuery, state: FSMContext):
    """Начать процесс выдачи очков"""
    await state.set_state(AdminStates.waiting_user_id_grant)

    text = """
💰 <b>ВЫДАЧА ОЧКОВ</b>

Введите ID пользователя, которому хотите начислить очки:

<i>Пример: 123456789</i>

❗️ Для отмены отправьте /cancel
    """

    await callback.message.edit_text(
        text,
        reply_markup=get_back_menu(),
        parse_mode='HTML'
    )

@router.message(AdminStates.waiting_user_id_grant, IsAdmin())
async def process_user_id_grant(message: Message, state: FSMContext):
    """Обработать ID пользователя для выдачи очков"""
    if message.text == '/cancel':
        await state.clear()
        return await admin_panel(message)

    try:
        user_id = int(message.text.strip())
        await state.update_data(user_id=user_id)
        await state.set_state(AdminStates.waiting_points_grant)

        text = f"""
💰 <b>ВЫДАЧА ОЧКОВ</b>

Пользователь: <code>{user_id}</code>

Введите количество очков для начисления:

<i>Пример: 100</i>
<i>Для отрицательных значений: -50</i>

❗️ Для отмены отправьте /cancel
        """

        await message.answer(text, parse_mode='HTML')

    except ValueError:
        await message.answer(
            "❌ Неверный формат ID пользователя!\n"
            "Введите числовой ID пользователя:"
        )

@router.message(AdminStates.waiting_points_grant, IsAdmin())
async def process_points_grant(message: Message, state: FSMContext):
    """Обработать количество очков для выдачи"""
    if message.text == '/cancel':
        await state.clear()
        return await admin_panel(message)

    try:
        points = int(message.text.strip())
        data = await state.get_data()
        user_id = data['user_id']

        # Подтверждение действия
        text = f"""
💰 <b>ПОДТВЕРЖДЕНИЕ ВЫДАЧИ ОЧКОВ</b>

Пользователь: <code>{user_id}</code>
Очки: <b>{points:+}</b>

Подтвердите действие:
        """

        await state.update_data(points=points)
        await message.answer(
            text,
            reply_markup=get_confirmation_menu(f"grant_{user_id}_{points}"),
            parse_mode='HTML'
        )

    except ValueError:
        await message.answer(
            "❌ Неверный формат количества очков!\n"
            "Введите число (может быть отрицательным):"
        )

@router.callback_query(F.data.startswith("confirm_grant_"))
async def confirm_grant_points(callback: CallbackQuery, state: FSMContext):
    """Подтвердить выдачу очков"""
    try:
        data = await state.get_data()
        user_id = data['user_id']
        points = data['points']

        # Получаем текущие очки пользователя
        user_info = user_data.ensure_user(user_id)
        old_score = user_info.get('score', 0)

        await user_data.update_score(user_id, points)
        new_score = old_score + points

        success_text = f"""
✅ <b>ОЧКИ УСПЕШНО НАЧИСЛЕНЫ</b>

Пользователь: <code>{user_id}</code>
Начислено: <b>{points:+}</b> очков
Было: <b>{old_score}</b> очков
Стало: <b>{new_score}</b> очков

Операция выполнена успешно!
        """

        await callback.message.edit_text(
            success_text,
            reply_markup=get_back_menu(),
            parse_mode='HTML'
        )

        await state.clear()
        logger.info(f"Админ {callback.from_user.id} начислил {points} очков пользователю {user_id}")

    except Exception as e:
        logger.error(f'Ошибка выдачи очков: {e}')
        await callback.message.edit_text(
            "❌ <b>ОШИБКА</b>\n\nНе удалось начислить очки. Попробуйте позже.",
            reply_markup=get_back_menu(),
            parse_mode='HTML'
        )
        await state.clear()

@router.callback_query(F.data == "admin_reset_user")
async def start_reset_user(callback: CallbackQuery, state: FSMContext):
    """Начать процесс сброса данных пользователя"""
    await state.set_state(AdminStates.waiting_user_id_reset)

    text = """
🔄 <b>СБРОС ДАННЫХ ПОЛЬЗОВАТЕЛЯ</b>

Введите ID пользователя, данные которого хотите сбросить:

<i>Пример: 123456789</i>

⚠️ <b>ВНИМАНИЕ!</b> Эта операция сбросит:
• Очки (score)
• Отвеченные вопросы (answered)
• Правильные ответы (correct)
• Игры (games_played)
• Загадки (riddles_solved)
• Угаданные слова (words_guessed)
• Текущую серию (streak)
• Максимальную серию (max_streak)
• Достижения (achievements)

❗️ Для отмены отправьте /cancel
    """

    await callback.message.edit_text(
        text,
        reply_markup=get_back_menu(),
        parse_mode='HTML'
    )

@router.message(AdminStates.waiting_user_id_reset, IsAdmin())
async def process_reset_user(message: Message, state: FSMContext):
    """Обработать сброс данных пользователя"""
    if message.text == '/cancel':
        await state.clear()
        return await admin_panel(message)

    try:
        user_id = int(message.text.strip())

        # Проверяем, существует ли пользователь
        user_info = user_data.ensure_user(user_id)

        text = f"""
🔄 <b>ПОДТВЕРЖДЕНИЕ СБРОСА ДАННЫХ</b>

Пользователь: <code>{user_id}</code>
Текущие очки: <b>{user_info.get('score', 0)}</b>
Игр сыграно: <b>{user_info.get('games_played', 0)}</b>

⚠️ <b>ВСЕ ДАННЫЕ БУДУТ УДАЛЕНЫ!</b>

Подтвердите действие:
        """

        await state.update_data(user_id=user_id)
        await message.answer(
            text,
            reply_markup=get_confirmation_menu(f"reset_{user_id}"),
            parse_mode='HTML'
        )

    except ValueError:
        await message.answer(
            "❌ Неверный формат ID пользователя!\n"
            "Введите числовой ID пользователя:"
        )

@router.callback_query(F.data.startswith("confirm_reset_"))
async def confirm_reset_user(callback: CallbackQuery, state: FSMContext):
    """Подтвердить сброс данных пользователя"""
    try:
        data = await state.get_data()
        user_id = data['user_id']

        user_info = user_data.ensure_user(user_id)

        # Сохраняем старые данные для отчета
        old_data = {
            'score': user_info.get('score', 0),
            'games_played': user_info.get('games_played', 0),
            'achievements_count': len(user_info.get('achievements', []))
        }

        # Обнуляем ключевые поля
        reset_fields = ['score', 'answered', 'correct', 'games_played',
                        'riddles_solved', 'words_guessed', 'streak', 'max_streak']

        for field in reset_fields:
            user_info[field] = 0
        user_info['achievements'] = []

        await user_data.save()

        success_text = f"""
✅ <b>ДАННЫЕ УСПЕШНО СБРОШЕНЫ</b>

Пользователь: <code>{user_id}</code>

<b>Сброшенные данные:</b>
• Очки: <s>{old_data['score']}</s> → 0
• Игры: <s>{old_data['games_played']}</s> → 0
• Достижения: <s>{old_data['achievements_count']}</s> → 0

Все статистики обнулены!
        """

        await callback.message.edit_text(
            success_text,
            reply_markup=get_back_menu(),
            parse_mode='HTML'
        )

        await state.clear()
        logger.info(f"Админ {callback.from_user.id} сбросил данные пользователя {user_id}")

    except Exception as e:
        logger.error(f'Ошибка сброса данных: {e}')
        await callback.message.edit_text(
            "❌ <b>ОШИБКА</b>\n\nНе удалось сбросить данные. Попробуйте позже.",
            reply_markup=get_back_menu(),
            parse_mode='HTML'
        )
        await state.clear()

@router.callback_query(F.data == "admin_full_access")
async def start_full_access(callback: CallbackQuery, state: FSMContext):
    """Начать процесс выдачи полного доступа"""
    await state.set_state(AdminStates.waiting_user_id_fullaccess)

    text = """
🔑 <b>ПРЕДОСТАВЛЕНИЕ ПОЛНОГО ДОСТУПА</b>

Введите ID пользователя, которому хотите предоставить админские права:

<i>Пример: 123456789</i>

⚠️ <b>ВНИМАНИЕ!</b> Пользователь получит:
• Доступ к админ-панели
• Возможность управлять другими пользователями
• Полные права в системе

❗️ Для отмены отправьте /cancel
    """

    await callback.message.edit_text(
        text,
        reply_markup=get_back_menu(),
        parse_mode='HTML'
    )

@router.message(AdminStates.waiting_user_id_fullaccess, IsAdmin())
async def process_full_access(message: Message, state: FSMContext):
    """Обработать выдачу полного доступа"""
    if message.text == '/cancel':
        await state.clear()
        return await admin_panel(message)

    try:
        user_id = int(message.text.strip())

        user_info = user_data.ensure_user(user_id)
        is_already_admin = user_info.get('is_admin', False)

        text = f"""
🔑 <b>ПОДТВЕРЖДЕНИЕ ВЫДАЧИ ПРАВ</b>

Пользователь: <code>{user_id}</code>
Текущий статус: {'Уже админ' if is_already_admin else 'Обычный пользователь'}

{'⚠️ Пользователь уже имеет админские права!' if is_already_admin else '🔓 Пользователь получит полный доступ!'}

Подтвердите действие:
        """

        await state.update_data(user_id=user_id, is_already_admin=is_already_admin)
        await message.answer(
            text,
            reply_markup=get_confirmation_menu(f"fullaccess_{user_id}"),
            parse_mode='HTML'
        )

    except ValueError:
        await message.answer(
            "❌ Неверный формат ID пользователя!\n"
            "Введите числовой ID пользователя:"
        )

@router.callback_query(F.data.startswith("confirm_fullaccess_"))
async def confirm_full_access(callback: CallbackQuery, state: FSMContext):
    """Подтвердить выдачу полного доступа"""
    try:
        data = await state.get_data()
        user_id = data['user_id']
        was_admin = data['is_already_admin']

        user_info = user_data.ensure_user(user_id)
        user_info['is_admin'] = True

        # Добавляем в список админов
        ADMIN_IDS.add(user_id)

        await user_data.save()

        status_text = "подтверждены" if was_admin else "предоставлены"

        success_text = f"""
✅ <b>ПРАВА УСПЕШНО {status_text.upper()}</b>

Пользователь: <code>{user_id}</code>
Новый статус: <b>Администратор</b>

🔑 Пользователь теперь имеет полный доступ к системе!
        """

        await callback.message.edit_text(
            success_text,
            reply_markup=get_back_menu(),
            parse_mode='HTML'
        )

        await state.clear()
        logger.info(f"Админ {callback.from_user.id} предоставил полный доступ пользователю {user_id}")

    except Exception as e:
        logger.error(f'Ошибка выдачи полного доступа: {e}')
        await callback.message.edit_text(
            "❌ <b>ОШИБКА</b>\n\nНе удалось предоставить полный доступ. Попробуйте позже.",
            reply_markup=get_back_menu(),
            parse_mode='HTML'
        )
        await state.clear()

@router.callback_query(F.data == "admin_stats")
async def show_admin_stats(callback: CallbackQuery):
    """Показать общую статистику бота"""
    try:
        # Собираем статистику
        all_users = user_data.data.get('users', {})
        total_users = len(all_users)
        total_games = sum(user.get('games_played', 0) for user in all_users.values())
        total_score = sum(user.get('score', 0) for user in all_users.values())
        active_users = len([u for u in all_users.values() if u.get('games_played', 0) > 0])
        admin_users = len([u for u in all_users.values() if u.get('is_admin', False)])

        # Топ пользователи по очкам
        top_users = sorted(all_users.items(), key=lambda x: x[1].get('score', 0), reverse=True)[:5]

        top_list = ""
        for i, (uid, data) in enumerate(top_users, 1):
            score = data.get('score', 0)
            games = data.get('games_played', 0)
            top_list += f"{i}. ID: <code>{uid}</code> | {score} очков | {games} игр\n"

        stats_text = f"""
📊 <b>СТАТИСТИКА БОТА</b>

<b>Общая информация:</b>
👥 Всего пользователей: <b>{total_users}</b>
🎮 Активных пользователей: <b>{active_users}</b>
🔑 Администраторов: <b>{admin_users}</b>

<b>Игровая статистика:</b>
🎯 Всего игр: <b>{total_games}</b>
💰 Общий счет: <b>{total_score}</b>
📈 Среднее очков на игрока: <b>{total_score // max(active_users, 1)}</b>

<b>ТОП-5 игроков:</b>
{top_list}

<i>Обновлено: сейчас</i>
        """

        await callback.message.edit_text(
            stats_text,
            reply_markup=get_back_menu(),
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f'Ошибка получения статистики: {e}')
        await callback.message.edit_text(
            "❌ <b>ОШИБКА</b>\n\nНе удалось получить статистику.",
            reply_markup=get_back_menu(),
            parse_mode='HTML'
        )

@router.callback_query(F.data == "admin_user_list")
async def show_user_list(callback: CallbackQuery):
    """Показать список активных пользователей"""
    try:
        all_users = user_data.data.get('users', {})
        active_users = [(uid, data) for uid, data in all_users.items()
                        if data.get('games_played', 0) > 0]

        # Сортируем по активности
        active_users.sort(key=lambda x: x[1].get('score', 0), reverse=True)

        if not active_users:
            text = "👥 <b>СПИСОК ПОЛЬЗОВАТЕЛЕЙ</b>\n\n📭 Активных пользователей нет"
        else:
            text = f"👥 <b>СПИСОК АКТИВНЫХ ПОЛЬЗОВАТЕЛЕЙ</b>\n\nВсего: <b>{len(active_users)}</b>\n\n"

            for i, (uid, data) in enumerate(active_users[:20], 1):  # Показываем только первые 20
                score = data.get('score', 0)
                games = data.get('games_played', 0)
                admin_badge = " 🔑" if data.get('is_admin', False) else ""
                text += f"{i}. <code>{uid}</code>{admin_badge} | {score} очков | {games} игр\n"

            if len(active_users) > 20:
                text += f"\n<i>... и еще {len(active_users) - 20} пользователей</i>"

        await callback.message.edit_text(
            text,
            reply_markup=get_back_menu(),
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f'Ошибка получения списка пользователей: {e}')
        await callback.message.edit_text(
            "❌ <b>ОШИБКА</b>\n\nНе удалось получить список пользователей.",
            reply_markup=get_back_menu(),
            parse_mode='HTML'
        )

@router.callback_query(F.data == "admin_system_info")
async def show_system_info(callback: CallbackQuery):
    """Показать системную информацию"""
    try:
        import sys
        import psutil
        import platform
        from datetime import datetime

        # Системная информация
        python_version = sys.version.split()[0]
        platform_info = platform.platform()

        # Память (если доступно)
        try:
            memory = psutil.virtual_memory()
            memory_info = f"💾 Память: {memory.percent}% ({memory.used // 1024 // 1024} MB)"
        except:
            memory_info = "💾 Память: недоступно"

        # Время работы
        start_time = datetime.now().strftime("%H:%M:%S")

        # Размер данных
        try:
            data_size = len(str(user_data.data))
            data_info = f"📦 Размер данных: ~{data_size // 1024} KB"
        except:
            data_info = "📦 Размер данных: недоступно"

        system_text = f"""
🔧 <b>СИСТЕМНАЯ ИНФОРМАЦИЯ</b>

<b>Платформа:</b>
🖥 Система: <code>{platform_info}</code>
🐍 Python: <code>{python_version}</code>

<b>Ресурсы:</b>
{memory_info}
{data_info}

<b>Статус:</b>
✅ Бот работает
🕐 Проверка: {start_time}

<b>Администраторы:</b>
{', '.join(f'<code>{admin_id}</code>' for admin_id in ADMIN_IDS)}

<i>Обновлено: сейчас</i>
        """

        await callback.message.edit_text(
            system_text,
            reply_markup=get_back_menu(),
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f'Ошибка получения системной информации: {e}')
        await callback.message.edit_text(
            "❌ <b>ОШИБКА</b>\n\nНе удалось получить системную информацию.",
            reply_markup=get_back_menu(),
            parse_mode='HTML'
        )

@router.callback_query(F.data == "admin_close")
async def close_admin_panel(callback: CallbackQuery):
    """Закрыть админ-панель"""
    await callback.message.edit_text(
        "🔧 <b>Админ-панель закрыта</b>\n\n"
        "Для повторного открытия используйте /admin",
        parse_mode='HTML'
    )

# Обработка отмены во время ввода
@router.message(F.text == '/cancel', IsAdmin())
async def cancel_admin_action(message: Message, state: FSMContext):
    """Отменить текущее админское действие"""
    await state.clear()
    await message.answer("❌ Действие отменено")
    await admin_panel(message)

# Старые команды для совместимости
@router.message(IsAdmin(), F.text.startswith('/grant'))
async def old_grant_command(message: Message):
    """Обработка старой команды /grant с переадресацией на новый интерфейс"""
    await message.answer(
        "💡 Используйте новую админ-панель!\n"
        "Команда: /admin",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔧 Открыть админ-панель", callback_data="admin_menu")]
        ])
    )

@router.message(IsAdmin(), F.text.startswith('/reset'))
async def old_reset_command(message: Message):
    """Обработка старой команды /reset с переадресацией на новый интерфейс"""
    await message.answer(
        "💡 Используйте новую админ-панель!\n"
        "Команда: /admin",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔧 Открыть админ-панель", callback_data="admin_menu")]
        ])
    )

@router.message(IsAdmin(), F.text.startswith('/fullaccess'))
async def old_fullaccess_command(message: Message):
    """Обработка старой команды /fullaccess с переадресацией на новый интерфейс"""
    await message.answer(
        "💡 Используйте новую админ-панель!\n"
        "Команда: /admin",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔧 Открыть админ-панель", callback_data="admin_menu")]
        ])
    )