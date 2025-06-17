import random
from typing import List, Dict, Any
from enum import Enum

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

class Category(Enum):
    MATH = "math"
    SCIENCE = "science"
    HISTORY = "history"
    GEOGRAPHY = "geography"
    CULTURE = "culture"
    SPORTS = "sports"
    TECHNOLOGY = "technology"
    NATURE = "nature"

class QuestionBank:
    def __init__(self):
        self.questions = {
            Category.MATH: [
                {"q": "2 + 2 × 2 = ?", "a": ["6"], "difficulty": Difficulty.EASY, "explanation": "Сначала умножение: 2 × 2 = 4, потом сложение: 2 + 4 = 6"},
                {"q": "Корень из 81?", "a": ["9"], "difficulty": Difficulty.EASY, "explanation": "9² = 81, поэтому √81 = 9"},
                {"q": "5! (факториал 5)?", "a": ["120"], "difficulty": Difficulty.MEDIUM, "explanation": "5! = 5 × 4 × 3 × 2 × 1 = 120"},
                {"q": "Чему равен sin(90°)?", "a": ["1"], "difficulty": Difficulty.MEDIUM, "explanation": "Синус 90 градусов равен 1"},
                {"q": "Производная от x²?", "a": ["2x", "2*x"], "difficulty": Difficulty.HARD, "explanation": "d/dx(x²) = 2x"},
                {"q": "Интеграл от 2x dx?", "a": ["x²+c", "x^2+c"], "difficulty": Difficulty.HARD, "explanation": "∫2x dx = x² + C"},
            ],
            Category.SCIENCE: [
                {"q": "Символ кислорода в таблице Менделеева?", "a": ["o", "O"], "difficulty": Difficulty.EASY, "explanation": "Кислород обозначается символом O"},
                {"q": "Сколько планет в Солнечной системе?", "a": ["8"], "difficulty": Difficulty.EASY, "explanation": "После исключения Плутона осталось 8 планет"},
                {"q": "Скорость света в вакууме (км/с)?", "a": ["300000", "300 000"], "difficulty": Difficulty.MEDIUM, "explanation": "Скорость света ≈ 300,000 км/с"},
                {"q": "Формула воды?", "a": ["h2o", "H2O"], "difficulty": Difficulty.EASY, "explanation": "Молекула воды состоит из 2 атомов водорода и 1 атома кислорода"},
                {"q": "Кто открыл пенициллин?", "a": ["флеминг", "александр флеминг"], "difficulty": Difficulty.MEDIUM, "explanation": "Александр Флеминг открыл пенициллин в 1928 году"},
            ],
            Category.GEOGRAPHY: [
                {"q": "Столица Франции?", "a": ["париж"], "difficulty": Difficulty.EASY, "explanation": "Париж - столица и крупнейший город Франции"},
                {"q": "Самая длинная река в мире?", "a": ["нил"], "difficulty": Difficulty.MEDIUM, "explanation": "Река Нил в Африке - самая длинная река в мире (6650 км)"},
                {"q": "На каком континенте находится Египет?", "a": ["африка"], "difficulty": Difficulty.EASY, "explanation": "Египет расположен в северо-восточной части Африки"},
                {"q": "Самый большой океан?", "a": ["тихий", "тихий океан"], "difficulty": Difficulty.EASY, "explanation": "Тихий океан - самый большой океан на Земле"},
                {"q": "Столица Австралии?", "a": ["канберра"], "difficulty": Difficulty.MEDIUM, "explanation": "Канберра - столица Австралии, а не Сидней как многие думают"},
            ],
            Category.HISTORY: [
                {"q": "В каком году началась Вторая мировая война?", "a": ["1939"], "difficulty": Difficulty.MEDIUM, "explanation": "Вторая мировая война началась 1 сентября 1939 года"},
                {"q": "Кто был первым президентом США?", "a": ["вашингтон", "джордж вашингтон"], "difficulty": Difficulty.MEDIUM, "explanation": "Джордж Вашингтон был первым президентом США (1789-1797)"},
                {"q": "В каком году пал Берлинский берлинская стена?", "a": ["1989"], "difficulty": Difficulty.HARD, "explanation": "Берлинская стена была разрушена 9 ноября 1989 года"},
                {"q": "Кто написал 'Войну и мир'?", "a": ["толстой", "лев толстой"], "difficulty": Difficulty.MEDIUM, "explanation": "Лев Николаевич Толстой написал роман 'Война и мир'"},
            ],
            Category.CULTURE: [
                {"q": "Кто написал 'Гамлета'?", "a": ["шекспир", "уильям шекспир"], "difficulty": Difficulty.MEDIUM, "explanation": "Уильям Шекспир написал трагедию 'Гамлет'"},
                {"q": "Сколько струн у классической гитары?", "a": ["6"], "difficulty": Difficulty.EASY, "explanation": "У классической гитары 6 струн"},
                {"q": "Автор 'Мона Лизы'?", "a": ["да винчи", "леонардо да винчи"], "difficulty": Difficulty.EASY, "explanation": "Леонардо да Винчи написал знаменитую 'Мона Лизу'"},
            ],
            Category.SPORTS: [
                {"q": "Сколько игроков в футбольной команде на поле?", "a": ["11"], "difficulty": Difficulty.EASY, "explanation": "В футболе на поле одновременно играет 11 игроков от каждой команды"},
                {"q": "В каком виде спорта используют шайбу?", "a": ["хоккей"], "difficulty": Difficulty.EASY, "explanation": "В хоккее с шайбой используется резиновая шайба"},
                {"q": "Каждые сколько лет проводятся Олимпийские игры?", "a": ["4", "четыре"], "difficulty": Difficulty.EASY, "explanation": "Летние и зимние Олимпийские игры проводятся каждые 4 года"},
                {"q": "Максимальное количество очков в боулинге?", "a": ["300"], "difficulty": Difficulty.HARD, "explanation": "300 очков - максимум в боулинге (12 страйков подряд)"},
            ],
            Category.TECHNOLOGY: [
                {"q": "Что означает WWW?", "a": ["world wide web"], "difficulty": Difficulty.MEDIUM, "explanation": "WWW расшифровывается как World Wide Web"},
                {"q": "Кто основал Microsoft?", "a": ["билл гейтс", "гейтс"], "difficulty": Difficulty.MEDIUM, "explanation": "Билл Гейтс и Пол Аллен основали Microsoft в 1975 году"},
                {"q": "В каком году был создан Google?", "a": ["1998"], "difficulty": Difficulty.HARD, "explanation": "Google был основан в 1998 году Ларри Пейджем и Сергеем Брином"},
                {"q": "Что означает CPU?", "a": ["central processing unit", "центральный процессор"], "difficulty": Difficulty.MEDIUM, "explanation": "CPU - Central Processing Unit, центральный процессор"},
            ],
            Category.NATURE: [
                {"q": "Самое большое животное в мире?", "a": ["синий кит", "кит"], "difficulty": Difficulty.EASY, "explanation": "Синий кит - самое большое животное на планете"},
                {"q": "Сколько камер в сердце у человека?", "a": ["4", "четыре"], "difficulty": Difficulty.MEDIUM, "explanation": "Сердце человека имеет 4 камеры: 2 предсердия и 2 желудочка"},
                {"q": "Какой газ выделяют растения?", "a": ["кислород"], "difficulty": Difficulty.EASY, "explanation": "При фотосинтезе растения выделяют кислород"},
                {"q": "Сколько костей у взрослого человека?", "a": ["206"], "difficulty": Difficulty.HARD, "explanation": "У взрослого человека 206 костей"},
            ]
        }

        self.riddles = {
            "easy": [
                {"q": "Зимой и летом одним цветом", "a": ["елка", "ель", "сосна"], "hint": "Хвойное дерево"},
                {"q": "Без рук, без ног, а рисовать умеет", "a": ["мороз"], "hint": "Зимнее явление"},
                {"q": "Висит груша, нельзя скушать", "a": ["лампочка"], "hint": "Источник света"},
                {"q": "Что можно увидеть с закрытыми глазами?", "a": ["сон", "сны"], "hint": "То, что снится ночью"},
                {"q": "Не лает, не кусает, а в дом не пускает", "a": ["замок"], "hint": "Механизм для закрывания двери"},
            ],
            "hard": [
                {"q": "Я не живой, но расту. У меня нет легких, но мне нужен воздух. У меня нет рта, но вода меня убивает", "a": ["огонь"], "hint": "Стихия"},
                {"q": "Чем больше из неё берёшь, тем больше она становится", "a": ["яма"], "hint": "Углубление в земле"},
                {"q": "У меня есть города, но нет домов. У меня есть горы, но нет деревьев. У меня есть вода, но нет рыбы", "a": ["карта"], "hint": "Изображение местности"},
                {"q": "Что становится влажнее, чем больше сохнет?", "a": ["полотенце"], "hint": "Предмет для вытирания"},
            ],
            "funny": [
                {"q": "Что такое: глаза боятся, а руки делают?", "a": ["работа"], "hint": "То, чем занимаются на службе"},
                {"q": "Кто ходит сидя?", "a": ["шахматист"], "hint": "Игрок в настольную игру"},
                {"q": "Что можно приготовить, но нельзя съесть?", "a": ["уроки"], "hint": "Домашнее задание"},
            ],
            "logic": [
                {"q": "У отца Мэри есть 5 дочерей: Чача, Чече, Чичи, Чочо. Как зовут пятую дочь?", "a": ["мэри"], "hint": "Перечитай условие внимательно"},
                {"q": "Что тяжелее: килограмм пуха или килограмм железа?", "a": ["одинаково", "равны"], "hint": "Обрати внимание на единицы измерения"},
                {"q": "Сколько месяцев в году имеют 28 дней?", "a": ["12", "все"], "hint": "Подумай логически"},
            ]
        }

        self.words = {
            "short": ["кот", "дом", "лес", "сад", "мир", "дар", "сон", "лед", "огонь", "море"],
            "medium": ["собака", "дерево", "солнце", "радуга", "звезда", "облако", "цветок", "бабочка"],
            "long": ["компьютер", "телефон", "автомобиль", "холодильник", "телевизор", "пианино", "библиотека"],
            "hard": ["программирование", "администрирование", "дифференциал", "криптография", "археология"]
        }

    def get_question(self, category: Category = None, difficulty: Difficulty = None) -> Dict[str, Any]:
        """Получить случайный вопрос"""
        if category:
            questions = self.questions.get(category, [])
        else:
            # Собираем все вопросы из всех категорий
            questions = []
            for cat_questions in self.questions.values():
                questions.extend(cat_questions)

        if difficulty:
            questions = [q for q in questions if q["difficulty"] == difficulty]

        if not questions:
            # Если нет вопросов с заданными параметрами, берем любой
            questions = []
            for cat_questions in self.questions.values():
                questions.extend(cat_questions)

        question = random.choice(questions)
        question["category"] = self._find_category(question)
        return question

    def get_riddle(self, difficulty: str = None) -> Dict[str, Any]:
        """Получить загадку"""
        if difficulty and difficulty in self.riddles:
            riddles = self.riddles[difficulty]
        else:
            # Берем из всех категорий
            riddles = []
            for cat_riddles in self.riddles.values():
                riddles.extend(cat_riddles)

        return random.choice(riddles)

    def get_word(self, difficulty: str = None) -> str:
        """Получить слово для угадывания"""
        if difficulty and difficulty in self.words:
            words = self.words[difficulty]
        else:
            # Берем из всех категорий
            words = []
            for cat_words in self.words.values():
                words.extend(cat_words)

        return random.choice(words)

    def _find_category(self, question: Dict[str, Any]) -> Category:
        """Найти категорию вопроса"""
        for category, questions in self.questions.items():
            if question in questions:
                return category
        return Category.CULTURE  # По умолчанию

    def get_categories(self) -> List[Category]:
        """Получить список всех категорий"""
        return list(self.questions.keys())

    def get_questions_by_category(self, category: Category) -> List[Dict[str, Any]]:
        """Получить все вопросы определенной категории"""
        return self.questions.get(category, [])

    def check_answer(self, question: Dict[str, Any], user_answer: str) -> bool:
        """Проверить ответ пользователя"""
        user_answer = user_answer.lower().strip()
        correct_answers = [ans.lower() for ans in question["a"]]
        return user_answer in correct_answers

    def get_difficulty_multiplier(self, difficulty: Difficulty) -> int:
        """Получить множитель очков за сложность"""
        multipliers = {
            Difficulty.EASY: 1,
            Difficulty.MEDIUM: 2,
            Difficulty.HARD: 3
        }
        return multipliers.get(difficulty, 1)

    def get_stats(self) -> Dict[str, int]:
        """Получить статистику по базе вопросов"""
        stats = {
            "total_questions": 0,
            "categories": len(self.questions),
            "easy_questions": 0,
            "medium_questions": 0,
            "hard_questions": 0,
            "total_riddles": sum(len(riddles) for riddles in self.riddles.values()),
            "total_words": sum(len(words) for words in self.words.values())
        }

        for questions in self.questions.values():
            stats["total_questions"] += len(questions)
            for q in questions:
                if q["difficulty"] == Difficulty.EASY:
                    stats["easy_questions"] += 1
                elif q["difficulty"] == Difficulty.MEDIUM:
                    stats["medium_questions"] += 1
                elif q["difficulty"] == Difficulty.HARD:
                    stats["hard_questions"] += 1

        return stats

# Глобальный экземпляр банка вопросов
question_bank = QuestionBank()

# Удобные функции для быстрого доступа
def get_random_question(category: Category = None, difficulty: Difficulty = None):
    return question_bank.get_question(category, difficulty)

def get_random_riddle(difficulty: str = None):
    return question_bank.get_riddle(difficulty)

def get_random_word(difficulty: str = None):
    return question_bank.get_word(difficulty)

def check_answer(question: Dict[str, Any], user_answer: str) -> bool:
    return question_bank.check_answer(question, user_answer)

# Для обратной совместимости
questions = []
for cat_questions in question_bank.questions.values():
    for q in cat_questions:
        questions.append({
            "q": q["q"],
            "a": q["a"][0],  # Берем первый вариант ответа
            "difficulty": q["difficulty"].value
        })

riddles = []
for cat_riddles in question_bank.riddles.values():
    for r in cat_riddles:
        riddles.append({
            "q": r["q"],
            "a": r["a"][0]  # Берем первый вариант ответа
        })

words = []
for cat_words in question_bank.words.values():
    words.extend(cat_words)