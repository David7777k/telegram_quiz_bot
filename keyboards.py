from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Tuple, Optional

class KeyboardBuilder:
    """Класс для создания клавиатур"""

    @staticmethod
    def make_keyboard(layout: List[List[Tuple[str, str]]], **kwargs) -> InlineKeyboardMarkup:
        """Создание клавиатуры из макета"""
        builder = InlineKeyboardBuilder()

        for row in layout:
            buttons = []
            for text, callback_data in row:
                buttons.append(InlineKeyboardButton(text=text, callback_data=callback_data))
            builder.row(*buttons)

        return builder.as_markup(**kwargs)

    @staticmethod
    def make_inline_keyboard(buttons: List[List[dict]], **kwargs) -> InlineKeyboardMarkup:
        """Создание клавиатуры из словарей"""
        builder = InlineKeyboardBuilder()

        for row in buttons:
            row_buttons = []
            for btn in row:
                if 'url' in btn:
                    button = InlineKeyboardButton(text=btn['text'], url=btn['url'])
                else:
                    button = InlineKeyboardButton(text=btn['text'], callback_data=btn['callback_data'])
                row_buttons.append(button)
            builder.row(*row_buttons)

        return builder.as_markup(**kwargs)

# Основное меню
def main_menu() -> InlineKeyboardMarkup:
    return KeyboardBuilder.make_keyboard([
        [("🧠 Викторина", "quiz"), ("🎲 Игры", "games")],
        [("🧩 Загадки", "riddles"), ("🔤 Угадай слово", "word")],
        [("📊 Статистика", "stats"), ("🏆 Достижения", "achievements")],
        [("👥 Рейтинг", "leaderboard"), ("ℹ️ Помощь", "help")]
    ])

# Меню викторины
def quiz_menu() -> InlineKeyboardMarkup:
    return KeyboardBuilder.make_keyboard([
        [("🟢 Легкие вопросы", "quiz:easy"), ("🟡 Средние вопросы", "quiz:medium")],
        [("🔴 Сложные вопросы", "quiz:hard"), ("🎯 Случайный вопрос", "quiz:random")],
        [("🏃‍♂️ Быстрая викторина", "quiz:speed"), ("🎪 Смешанная викторина", "quiz:mixed")],
        [("⬅️ Назад", "back_to_main")]
    ])

# Меню игр
def games_menu() -> InlineKeyboardMarkup:
    return KeyboardBuilder.make_keyboard([
        [("🎲 Кубик", "game:dice"), ("🪙 Монета", "game:coin")],
        [("🎰 Рулетка", "game:roulette"), ("🎯 Угадай число", "game:number")],
        [("🎮 Камень-ножницы-бумага", "game:rps"), ("🎲 Два кубика", "game:double_dice")],
        [("⬅️ Назад", "back_to_main")]
    ])

# Меню загадок
def riddles_menu() -> InlineKeyboardMarkup:
    return KeyboardBuilder.make_keyboard([
        [("🧩 Простые загадки", "riddles:easy"), ("🤔 Сложные загадки", "riddles:hard")],
        [("🎭 Загадки-шутки", "riddles:funny"), ("🔍 Логические загадки", "riddles:logic")],
        [("⬅️ Назад", "back_to_main")]
    ])

# Меню слов
def word_game_menu() -> InlineKeyboardMarkup:
    return KeyboardBuilder.make_keyboard([
        [("🔤 Короткие слова", "word:short"), ("📝 Длинные слова", "word:long")],
        [("🎯 Случайное слово", "word:random"), ("🏆 Топ слова", "word:hard")],
        [("⬅️ Назад", "back_to_main")]
    ])

# Меню настроек
def settings_menu() -> InlineKeyboardMarkup:
    return KeyboardBuilder.make_keyboard([
        [("🔊 Звуки", "settings:sounds"), ("🌙 Ночной режим", "settings:night")],
        [("📊 Сбросить статистику", "settings:reset"), ("🗃️ Экспорт данных", "settings:export")],
        [("⬅️ Назад", "back_to_main")]
    ])

# Кнопки подтверждения
def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    return KeyboardBuilder.make_keyboard([
        [("✅ Да", f"confirm:{action}"), ("❌ Нет", f"cancel:{action}")],
        [("⬅️ Назад", "back_to_main")]
    ])

# Навигация по страницам
def pagination_keyboard(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Кнопки навигации
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"{prefix}:page:{current_page-1}"))

    nav_buttons.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="noop"))

    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"{prefix}:page:{current_page+1}"))

    if nav_buttons:
        builder.row(*nav_buttons)

    # Кнопка "Назад"
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))

    return builder.as_markup()

# Клавиатура для игры в камень-ножницы-бумага
def rps_keyboard() -> InlineKeyboardMarkup:
    return KeyboardBuilder.make_keyboard([
        [("🗿 Камень", "rps:rock"), ("✂️ Ножницы", "rps:scissors"), ("📄 Бумага", "rps:paper")],
        [("⬅️ Назад", "games")]
    ])

# Клавиатура выбора сложности
def difficulty_keyboard(game_type: str) -> InlineKeyboardMarkup:
    return KeyboardBuilder.make_keyboard([
        [("🟢 Легко", f"{game_type}:easy"), ("🟡 Средне", f"{game_type}:medium")],
        [("🔴 Сложно", f"{game_type}:hard")],
        [("⬅️ Назад", "back_to_main")]
    ])

# Клавиатура для статистики
def stats_keyboard() -> InlineKeyboardMarkup:
    return KeyboardBuilder.make_keyboard([
        [("📈 Подробная статистика", "stats:detailed"), ("🏆 Мои достижения", "achievements")],
        [("👥 Сравнить с другими", "stats:compare"), ("📊 Графики", "stats:charts")],
        [("⬅️ Назад", "back_to_main")]
    ])

# Клавиатура помощи
def help_keyboard() -> InlineKeyboardMarkup:
    return KeyboardBuilder.make_keyboard([
        [("❓ Как играть", "help:how_to_play"), ("🎯 Система очков", "help:scoring")],
        [("🏆 Достижения", "help:achievements"), ("⚙️ Команды", "help:commands")],
        [("📞 Поддержка", "help:support"), ("ℹ️ О боте", "help:about")],
        [("⬅️ Назад", "back_to_main")]
    ])

# Вспомогательные функции
def back_button(callback_data: str = "back_to_main") -> InlineKeyboardMarkup:
    """Простая кнопка назад"""
    return KeyboardBuilder.make_keyboard([
        [("⬅️ Назад", callback_data)]
    ])

def yes_no_keyboard(yes_callback: str, no_callback: str) -> InlineKeyboardMarkup:
    """Клавиатура Да/Нет"""
    return KeyboardBuilder.make_keyboard([
        [("✅ Да", yes_callback), ("❌ Нет", no_callback)]
    ])

def menu_with_back(items: List[Tuple[str, str]], back_callback: str = "back_to_main") -> InlineKeyboardMarkup:
    """Создание меню с кнопкой назад"""
    layout = []

    # Группируем кнопки по 2 в ряд
    for i in range(0, len(items), 2):
        row = items[i:i+2]
        layout.append(row)

    # Добавляем кнопку назад
    layout.append([("⬅️ Назад", back_callback)])

    return KeyboardBuilder.make_keyboard(layout)

# Клавиатура с URL кнопками
def url_keyboard(buttons: List[Tuple[str, str]]) -> InlineKeyboardMarkup:
    """Создание клавиатуры с URL кнопками"""
    keyboard_buttons = []
    for text, url in buttons:
        keyboard_buttons.append([{'text': text, 'url': url}])

    return KeyboardBuilder.make_inline_keyboard(keyboard_buttons)