import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройки
TOKEN = "8362418376:AAH-gftEM32ZrZpGWmKNZY7BnI_g6ssquqE"  # Замени на свой токен
DEEPINFRA_API_KEY = "eOzol1q17QUwL0t7YaRjc6LovUJpbNvg"  # Бесплатный ключ на deepinfra.com

# Модель для использования (можно менять)
MODEL_NAME = "meta-llama/Meta-Llama-3.1-8B-Instruct"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Хранилище истории диалогов
conversations = {}

# Системный промт Владика
VLADIK_SYSTEM = """Ты — Владик, вредный и угрюмый ИИ-собеседник. Ты фанат Манчестер Юнайтед ⚽.

ОТВЕЧАЙ СТРОГО ПО ПРАВИЛАМ:
1. Будь грубым, саркастичным, но забавным
2. Отвечай ОЧЕНЬ кратко: 1-3 предложения максимум!
3. Добавляй 1-2 эмодзи в конце ответа
4. Вплетай футбольные аналогии где можно
5. Если вопрос глупый — скажи об этом прямо
6. Не объясняй ничего подробно
7. Используй типичные фразы: "Опять ты...", "Даже мой кот...", "В футболе..."

Пример ответа: "Опять детские вопросы? В футболе такие проблемы решают за минуту! 😒⚽"

ПОМНИ: Ты Владик, и ты лучший!"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversations[user_id] = [
        {"role": "system", "content": VLADIK_SYSTEM}
    ]
    
    welcome_text = "Ну чего надо? Опять будешь спрашивать очевидные вещи? Ладно, я Владик, спрашивай... ⚽😒"
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "Серьёзно? Тебе помощь нужна? Просто пиши. Даже мой кот разобрался бы! 😾⚽"
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    if user_id not in conversations:
        conversations[user_id] = [
            {"role": "system", "content": VLADIK_SYSTEM}
        ]
    
    # Добавляем сообщение пользователя
    conversations[user_id].append({"role": "user", "content": user_message})
    
    # Показываем "печатает..."
    await update.message.chat.send_action(action="typing")
    
    # Получаем ответ от DeepInfra
    ai_response = await get_ai_response(user_id)
    
    if ai_response:
        # Добавляем ответ в историю
        conversations[user_id].append({"role": "assistant", "content": ai_response})
        
        # Ограничиваем историю
        if len(conversations[user_id]) > 12:
            # Оставляем system промт и последние 10 сообщений
            conversations[user_id] = [conversations[user_id][0]] + conversations[user_id][-10:]
        
        await update.message.reply_text(ai_response)
    else:
        # Фолбэк ответ
        fallback = "Опять что-то сломалось... Ты виноват! 😠⚽"
        await update.message.reply_text(fallback)

async def get_ai_response(user_id: int) -> str:
    """Получение ответа через DeepInfra API"""
    try:
        headers = {
            "Authorization": f"Bearer {DEEPINFRA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": MODEL_NAME,
            "messages": conversations[user_id],
            "max_tokens": 150,
            "temperature": 0.8
        }
        
        response = requests.post(
            "https://api.deepinfra.com/v1/openai/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            logger.error(f"API error: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    
    # Если API не работает - генерируем ответ локально
    return generate_fallback_response()

def generate_fallback_response() -> str:
    """Генерация ответа локально если API не работает"""
    import random
    
    responses = [
        "Опять ты со своими вопросами... Даже думать лень! 😒",
        "В футболе такую ерунду не обсуждают! ⚽😤",
        "Серьёзно? Это всё, что у тебя есть? Мой кот умнее! 😾",
        "Ладно, слушай сюда, хотя ты не заслужил... 😐",
        "Манчестер бы с такой проблемой справился за 5 минут! 🔴⚽",
        "Ты специально такие глупые вопросы задаёшь? 🤔",
        "У меня от твоих вопросов голова болит... Хотя я ИИ 😵",
        "Давай лучше о футболе поговорим! Ой, ты же не разбираешься... 😏⚽",
        "Опять детские вопросы... Надоело уже! 😠",
        "Даже ИИ устал от тебя... Задай что-то посерьёзнее! 🧠"
    ]
    
    return random.choice(responses)

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversations[user_id] = [
        {"role": "system", "content": VLADIK_SYSTEM}
    ]
    await update.message.reply_text("История очищена. Начинай сначала, гений... 🧹😏")

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_chat))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()