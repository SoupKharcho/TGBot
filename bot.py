import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройки
TOKEN = "YOUR_BOT_TOKEN_HERE"  # Замени на свой токен
CHARACTER_ID = ""  # Оставь пустым для случайного персонажа или укажи ID персонажа c.ai
API_URL = "https://api.c.ai/v1/chat"
API_KEY = "YOUR_CAI_API_KEY_HERE"  # Замени на свой API ключ c.ai

# Системный промт
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

ПОМНИ: Ты Владик, и ты ЛУЧШИЙ!"""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Хранилище истории диалогов
conversations = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    conversations[user_id] = []
    
    welcome_text = (
        "Ну чего надо? Опять будешь спрашивать очевидные вещи? "
        "Ладно, я Владик, задавай свой вопрос... ⚽😒"
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = (
        "Серьёзно? Тебе нужна помощь, чтобы общаться со мной? "
        "Просто пиши как обычный человек. Даже мой кот разобрался бы! 😾⚽"
    )
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка всех текстовых сообщений"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    if user_id not in conversations:
        conversations[user_id] = []
    
    # Добавляем сообщение пользователя в историю
    conversations[user_id].append({"role": "user", "content": user_message})
    
    # Отправляем "печатает..."
    await update.message.chat.send_action(action="typing")
    
    # Получаем ответ от c.ai API
    ai_response = await get_cai_response(user_message, user_id)
    
    # Добавляем ответ в историю и отправляем
    if ai_response:
        conversations[user_id].append({"role": "assistant", "content": ai_response})
        # Ограничиваем историю последними 10 сообщениями
        if len(conversations[user_id]) > 10:
            conversations[user_id] = conversations[user_id][-10:]
        
        await update.message.reply_text(ai_response)
    else:
        error_text = "Опять что-то сломалось... Ты точно нормальный вопрос задал? 🔧😠"
        await update.message.reply_text(error_text)

async def get_cai_response(message: str, user_id: int) -> str:
    """Получение ответа от Character.ai API"""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Формируем данные для запроса
        data = {
            "message": {
                "content": message,
                "role": "user"
            },
            "character_id": CHARACTER_ID if CHARACTER_ID else None,
            "stream": False
        }
        
        # Добавляем системный промт
        if not CHARACTER_ID:
            data["prompt"] = SYSTEM_PROMPT
        
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "reply" in result:
                return result["reply"]
            elif "content" in result:
                return result["content"]
        else:
            logger.error(f"API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
    
    # Фолбэк ответы если API не работает
    fallback_responses = [
        "Сервера опять глючат, как твоя игра в футбол! ⚽😤",
        "Даже ИИ устал от твоих вопросов... Задай что-то посерьёзнее! 🧠",
        "Мне скучно, поговорим о Манчестер Юнайтед? О нет, тебе это не интересно... 😒⚽",
        "Опять ты со своими детскими вопросами... Ладно, слушай сюда! 🤨",
        "Даже мой кот умнее спросил бы! Мяу... то есть, задавай нормально! 😾"
    ]
    
    import random
    return random.choice(fallback_responses)

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистка истории диалога (/clear)"""
    user_id = update.effective_user.id
    if user_id in conversations:
        conversations[user_id] = []
        await update.message.reply_text("История очищена. Можешь начинать снова, хотя вряд ли станешь умнее... 🧹😏")
    else:
        await update.message.reply_text("У нас и так нет истории. Ты что, забыл? 🤔⚽")

def main():
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_chat))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
