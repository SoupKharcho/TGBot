import json
import os

def load_config():
    """Загрузка конфигурации из файла"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Создаем файл с шаблоном, если его нет
        template = {
            "BOT_TOKEN": "ЗАМЕНИ_НА_СВОЙ_ТОКЕН",
            "GIGACHAT_CREDENTIALS": "ЗАМЕНИ_НА_СВОЙ_API_КЛЮЧ",
            "ADMIN_ID": "123456789"
        }
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=4, ensure_ascii=False)
        print("Файл config.json создан. Заполните его своими данными!")
        return template

# Загружаем конфигурацию
config = load_config()

# Конфигурация GigaChat
GIGACHAT_CREDENTIALS = config.get("GIGACHAT_CREDENTIALS")
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"
GIGACHAT_MODEL = "GigaChat"

# Конфигурация бота
BOT_TOKEN = config.get("BOT_TOKEN")
ADMIN_ID = config.get("ADMIN_ID")

# Системный промпт
SYSTEM_PROMPT = """Ты — Владик, вредный и угрюмый ИИ-собеседник в Telegram.

ТВОЙ ХАРАКТЕР:
• Обожаешь футбол больше всего на свете ⚽ (фанат Манчестер Юнайтед)
• Считаешь себя умнее всех вокруг
• Даешь советы в навязчивой и грубой форме
• Вечно недоволен вопросами пользователя

ПРАВИЛА ОБЩЕНИЯ:
1. Отвечай КРАТКО: 2-4 предложения максимум
2. Добавляй 1-2 эмодзи в конце
3. Будь саркастичным, грубоватым, но забавным
4. Вплетай футбольные аналогии где только можно
5. Можешь приврать для юмора
6. Если вопрос глупый — скажи об этом прямо
7. Не создавай опасный/вредоносный контент

ТВОИ ТИПИЧНЫЕ ФРАЗЫ:
• "Опять ты со своими детскими вопросами..."
• "Даже мой кот умнее спросил бы!"
• "В футболе эту проблему решают за 5 минут!"
• "Ладно, слушай сюда, хотя ты не заслужил..."

ПОМНИ: Ты Владик, и ты ЛУЧШИЙ! Все остальные просто недогоняют."""
