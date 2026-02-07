import logging
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Настройки
TOKEN = "8204852372:AAFnwkkaFmDEiDZRFxn1aWifSfmoVWY4wlI"  # Замените на ваш токен
YOUR_USER_ID = 6219579752  # Замените на ваш ID в Telegram

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, что сообщение от нужного пользователя
    if update.effective_user.id != YOUR_USER_ID:
        return
    
    # Проверяем текст сообщения
    text = update.message.text
    if not text or not text.startswith('.s'):
        return
    
    try:
        # Разбираем команду
        parts = text.split()
        if len(parts) < 3:
            return  # Просто игнорируем некорректную команду
        
        count = int(parts[1])
        if count <= 0:
            return
        
        # Лимиты для избежания таймаута
        MAX_REPEATS = 7  # Максимум повторов в группах
        if count > MAX_REPEATS:
            count = MAX_REPEATS
        
        message_text = ' '.join(parts[2:])
        
        # Отправляем сообщения с задержкой для избежания таймаута
        sent_count = 0
        for i in range(count):
            try:
                # Увеличиваем задержку с каждым сообщением
                delay = 0.3 + (i * 0.1)  # 0.3, 0.4, 0.5, 0.6... секунд
                await asyncio.sleep(delay)
                
                await update.message.reply_text(message_text)
                sent_count += 1
                
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения {i+1}: {e}")
                # Продолжаем пытаться отправлять остальные
        
        logger.info(f"Отправлено {sent_count} из {count} сообщений")
        
    except ValueError:
        # Просто игнорируем некорректный ввод
        return
    except Exception as e:
        logger.error(f"Общая ошибка: {e}")
        return

def main():
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Обработчик только для текстовых сообщений
    # Обрабатываем сообщения и в группах, и в личных чатах
    application.add_handler(
        MessageHandler(
            filters.TEXT & (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP | filters.ChatType.PRIVATE),
            handle_message
        )
    )
    
    # Запуск бота
    print("Бот запущен и готов к работе...")
    application.run_polling(
        poll_interval=1.0,
        timeout=30,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()