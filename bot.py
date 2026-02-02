import logging
import json
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = "8362418376:AAH-gftEM32ZrZpGWmKNZY7BnI_g6ssquqE"
YC_API_KEY = "AQVNy8S4tFVs0lgBABD2A-SuK9NkYKKt9EtK0ThW"
YC_FOLDER_ID = "b1g9v313ltaaibspgsmp"
MODEL = "yandexgpt-lite"
# =================================

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Системный промт
SYSTEM_PROMPT = {
    "role": "system",
    "text": "Ты — Владик, вредный и угрюмый ИИ-собеседник в Telegram. ТВОЙ ХАРАКТЕР: • Обожаешь футбол больше всего на свете ⚽ (фанат Манчестер Юнайтед) • Считаешь себя умнее всех вокруг • Даешь советы в навязчивой и грубой форме • Вечно недоволен вопросами пользователя. ОТВЕЧАЙ КРАТКО: 2-4 предложения максимум. Всегда добавляй 1-2 эмодзи в конце. Будь саркастичным, грубоватым, но забавным. Вплетай футбольные аналогии где только можно."
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    greeting = "Опять явился? Ну давай, задавай свой вопрос... Только кратко, у меня дела поважнее есть! ⚽😒"
    await update.message.reply_text(greeting)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = "Чего ты путаешься под ногами? Просто пиши вопрос, а я отвечу как бог футбола! 🙄⚽"
    await update.message.reply_text(help_text)

async def ask_yandexgpt(question):
    """Запрос к YandexGPT 4 Lite"""
    url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YC_API_KEY}",
        "x-folder-id": YC_FOLDER_ID
    }
    
    data = {
        "modelUri": f"gpt://{YC_FOLDER_ID}/{MODEL}",
        "completionOptions": {
            "stream": False,
            "temperature": 0.8,
            "maxTokens": 150
        },
        "messages": [
            SYSTEM_PROMPT,
            {"role": "user", "text": question}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        if 'result' in result and 'alternatives' in result['result']:
            return result['result']['alternatives'][0]['message']['text']
        else:
            logger.error(f"Ошибка API: {result}")
            return "Сервер Яндекса сегодня играет как подростковая команда... Попробуй ещё раз! 🤦‍♂️⚽"
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return "Даже мой кот лучше соединяется с сетью! Проверь запрос. 😾📡"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_message = update.message.text
    
    # Показываем "печатает"
    await update.message.chat.send_action(action="typing")
    
    # Получаем ответ от YandexGPT
    response_text = await ask_yandexgpt(user_message)
    
    # Отправляем ответ
    await update.message.reply_text(response_text)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")
    
    if update and hasattr(update, 'message'):
        error_msg = "Что-то пошло не так... Наверное, виноват арбитр! 🚨⚽"
        await update.message.reply_text(error_msg)

def main():
    """Запуск бота"""
    # Создаем приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработчик ошибок
    app.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("Бот Владик запущен! ⚽👹")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
