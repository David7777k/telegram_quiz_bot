import asyncio
import logging
import os
import sys                       # ➊ добавили
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers import main_router, quiz_router, games_router, riddles_router, word_router

# ➋ Гарантируем UTF-8 в stdout / stderr (Windows)
if os.name == "nt":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        # Fallback для очень старых интерпретаторов
        import codecs
        import msvcrt
        msvcrt.setmode(sys.stdout.fileno(), os.O_TEXT)
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "replace")
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "replace")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),   # ➌ указываем кодировку
        logging.StreamHandler()                             # использует перенастроенный stdout
    ]
)
logger = logging.getLogger(__name__)

def get_token():
    """Получение токена из переменной окружения или .env файла"""
    token = os.getenv('BOT_TOKEN')
    if not token:
        try:
            env_path = Path('.env')
            if env_path.exists():
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('BOT_TOKEN='):
                            token = line.strip().split('=', 1)[1]
                            break
        except Exception as e:
            logger.error(f"Ошибка чтения .env файла: {e}")

    if not token:
        raise ValueError("BOT_TOKEN не найден! Установите переменную окружения или создайте .env файл")

    return token

async def on_startup():
    """Функция выполняется при запуске бота"""
    logger.info("Бот запускается...")

async def on_shutdown():
    """Функция выполняется при остановке бота"""
    logger.info("Бот останавливается...")

async def main():
    try:
        token = get_token()

        # Создание бота с настройками по умолчанию
        bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

        # Создание диспетчера
        dp = Dispatcher()

        # Подключение обработчиков событий
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        # Подключение роутеров
        dp.include_router(main_router)
        dp.include_router(quiz_router)
        dp.include_router(games_router)
        dp.include_router(riddles_router)
        dp.include_router(word_router)

        # Запуск бота
        logger.info("Начинаю polling...")
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")