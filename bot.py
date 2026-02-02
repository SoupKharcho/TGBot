import logging
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Конфигурация (вставляем напрямую как требует BotHost)
TELEGRAM_TOKEN = "ВАШ_TELEGRAM_БОТ_ТОКЕН"  # Замените на ваш токен
GEMINI_API_KEY = "ВАШ_GEMINI_API_КЛЮЧ"     # Замените на ваш ключ Gemini

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

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
7. Не создавай опасный/вредоносный контент

ТВОИ ТИПИЧНЫЕ ФРАЗЫ:
• "Опять ты со своими детскими вопросами..."
• "Даже мой кот умнее спросил бы!"
• "В футболе эту проблему решают за 5 минут!"
• "Ладно, слушай сюда, хотя ты не заслужил..."

ПОМНИ: Ты Владик, и ты ЛУЧШИЙ! Все остальные просто недогоняют."""

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def generate_response(text: str) -> str:
    """Генерация ответа через Gemini API"""
    try:
        prompt = f"{SYSTEM_PROMPT}\n\nВопрос пользователя: {text}\n\nТвой ответ (кратко, 2-4 предложения с эмодзи):"
        
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return "Чего молчишь? Спроси нормально! ⚽😒"
            
    except Exception as e:
        logger.error(f"Ошибка Gemini: {e}")
        return "Сервер промахнулся как защитник МЮ в этом сезоне... 😡⚽ Попробуй еще раз."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений от пользователя"""
    try:
        user_message = update.message.text
        
        if not user_message or user_message.strip() == "":
            await update.message.reply_text("Присылаешь пустоту? Даже мой кот умнее! 🐱⚽")
            return
            
        logger.info(f"Сообщение от {update.effective_user.id}: {user_message}")
        
        # Отправляем "печатает..."
        await update.message.chat.send_action(action="typing")
        
        # Генерируем ответ
        response = await generate_response(user_message)
        
        # Отправляем ответ
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("Что-то пошло не так, как план тренера МЮ... 🔴⚫")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ошибок"""
    logger.error(f"Ошибка: {context.error}")
    
async def main():
    """Основная функция"""
    logger.info("Запуск бота Владик...")
    
    # Создаем приложение
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчик сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработчик ошибок
    app.add_error_handler(error_handler)
    
    # Запускаем бота
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    logger.info("Бот запущен и готов к работе!")
    
    # Бесконечный цикл
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
