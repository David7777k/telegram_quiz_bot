import json
import asyncio
import aiofiles
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class UserData:
    def __init__(self, path: str = 'user_data.json'):
        self.path = Path(path)
        self.data: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._achievements = {
            "first_answer": "🎯 Первый ответ",
            "streak_3": "🔥 Серия 3",
            "streak_7": "🔥🔥 Серия 7",
            "streak_30": "🔥🔥🔥 Серия 30",
            "score_100": "💯 100 очков",
            "score_500": "🏆 500 очков",
            "score_1000": "👑 1000 очков",
            "quiz_master": "🧠 Мастер викторин (50 правильных)",
            "riddle_solver": "🧩 Разгадчик загадок (20 загадок)",
            "word_champion": "📝 Чемпион слов (10 слов)",
            "daily_player": "📅 Ежедневный игрок (7 дней подряд)"
        }

    async def load(self):
        """Асинхронная загрузка данных"""
        try:
            if self.path.exists():
                async with aiofiles.open(self.path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    self.data = json.loads(content)
                    logger.info(f"Загружены данные для {len(self.data)} пользователей")
            else:
                self.data = {}
                logger.info("Создан новый файл данных")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            self.data = {}

    async def save(self):
        """Асинхронное сохранение данных"""
        async with self._lock:
            try:
                # Создаем резервную копию
                if self.path.exists():
                    backup_path = self.path.with_suffix('.bak')
                    self.path.rename(backup_path)

                async with aiofiles.open(self.path, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(self.data, indent=2, ensure_ascii=False))

                logger.debug("Данные сохранены")
            except Exception as e:
                logger.error(f"Ошибка сохранения данных: {e}")
                # Восстанавливаем из резервной копии
                backup_path = self.path.with_suffix('.bak')
                if backup_path.exists():
                    backup_path.rename(self.path)

    def ensure_user(self, user_id: int) -> Dict[str, Any]:
        """Создание пользователя если не существует"""
        uid = str(user_id)
        if uid not in self.data:
            self.data[uid] = {
                "score": 0,
                "answered": 0,
                "correct": 0,
                "games_played": 0,
                "riddles_solved": 0,
                "words_guessed": 0,
                "streak": 0,
                "last_day": "",
                "max_streak": 0,
                "achievements": [],
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "total_time_played": 0,
                "favorite_category": "",
                "level": 1
            }
        return self.data[uid]

    async def update_stat(self, user_id: int, field: str, amount: int):
        """Обновление статистики пользователя"""
        user = self.ensure_user(user_id)
        user[field] += amount
        user["last_activity"] = datetime.now().isoformat()

        # Проверка достижений
        await self._check_achievements(user_id)
        await self.save()

    async def update_score(self, user_id: int, delta: int):
        """Обновление очков пользователя"""
        await self.update_stat(user_id, "score", delta)

    async def add_achievement(self, user_id: int, achievement_key: str) -> bool:
        """Добавление достижения пользователю"""
        user = self.ensure_user(user_id)
        achievement_name = self._achievements.get(achievement_key, achievement_key)

        if achievement_name not in user["achievements"]:
            user["achievements"].append(achievement_name)
            await self.save()
            logger.info(f"Пользователь {user_id} получил достижение: {achievement_name}")
            return True
        return False

    async def update_streak(self, user_id: int) -> tuple[int, bool]:
        """Обновление серии ответов пользователя"""
        user = self.ensure_user(user_id)
        now = datetime.now().date()
        today = now.isoformat()
        last_day = user["last_day"]

        streak_updated = False

        if last_day != today:
            if last_day == (now - timedelta(days=1)).isoformat():
                # Продолжаем серию
                user["streak"] += 1
                streak_updated = True
            else:
                # Начинаем новую серию
                user["streak"] = 1
                streak_updated = True

            user["last_day"] = today
            user["max_streak"] = max(user["max_streak"], user["streak"])
            await self.save()

        return user["streak"], streak_updated

    async def _check_achievements(self, user_id: int):
        """Проверка и добавление достижений"""
        user = self.data[str(user_id)]

        # Достижения за очки
        if user["score"] >= 1000:
            await self.add_achievement(user_id, "score_1000")
        elif user["score"] >= 500:
            await self.add_achievement(user_id, "score_500")
        elif user["score"] >= 100:
            await self.add_achievement(user_id, "score_100")

        # Достижения за серии
        if user["streak"] >= 30:
            await self.add_achievement(user_id, "streak_30")
        elif user["streak"] >= 7:
            await self.add_achievement(user_id, "streak_7")
        elif user["streak"] >= 3:
            await self.add_achievement(user_id, "streak_3")

        # Достижения за активность
        if user["correct"] >= 50:
            await self.add_achievement(user_id, "quiz_master")
        elif user["answered"] >= 1:
            await self.add_achievement(user_id, "first_answer")

        if user["riddles_solved"] >= 20:
            await self.add_achievement(user_id, "riddle_solver")

        if user["words_guessed"] >= 10:
            await self.add_achievement(user_id, "word_champion")

    def get_info(self, user_id: int) -> Dict[str, Any]:
        """Получение информации о пользователе"""
        return self.ensure_user(user_id)

    def get_leaderboard(self, limit: int = 10) -> list:
        """Получение таблицы лидеров"""
        sorted_users = sorted(
            self.data.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        return sorted_users[:limit]

    async def get_stats_summary(self) -> Dict[str, Any]:
        """Получение общей статистики"""
        if not self.data:
            return {"total_users": 0}

        total_users = len(self.data)
        total_score = sum(user["score"] for user in self.data.values())
        total_answers = sum(user["answered"] for user in self.data.values())
        avg_score = total_score / total_users if total_users > 0 else 0

        return {
            "total_users": total_users,
            "total_score": total_score,
            "total_answers": total_answers,
            "average_score": round(avg_score, 2)
        }

# Глобальный экземпляр
user_data = UserData()

# Инициализация при импорте модуля
async def init_data():
    await user_data.load()

# Автоматическая инициализация
try:
    import asyncio
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(init_data())
    else:
        asyncio.run(init_data())
except RuntimeError:
    # Если цикл событий не запущен, инициализация произойдет позже
    pass