import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройки
TOKEN = "8204852372:AAFnwkkaFmDEiDZRFxn1aWifSfmoVWY4wlI"  
YOUR_USER_ID = 6219579752

# Включим логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, что сообщение от нужного пользователя
    if update.effective_user.id != YOUR_USER_ID:
        return
    
    # Проверяем текст сообщения
    text = update.message.text
    if text and text.startswith('.s'):
        try:
            # Разбираем команду
            parts = text.split()
            if len(parts) < 3:
                await update.message.reply_text("Использование: .s [число] [текст]")
                return
            
            count = int(parts[1])
            if count > 100:  # Ограничение от спама
                count = 100
            
            message_text = ' '.join(parts[2:])
            
            # Отправляем сообщения
            for _ in range(count):
                await update.message.reply_text(message_text)
                
        except ValueError:
            await update.message.reply_text("Ошибка: число должно быть целым")
        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == YOUR_USER_ID:
        await update.message.reply_text(
            "Привет! Я бот-помощник.\n"
            "Используй команду:\n"
            ".s [число] [текст]\n"
            "чтобы я повторил текст нужное количество раз."
        )

def main():
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()