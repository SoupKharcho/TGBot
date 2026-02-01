import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_keyboard():
    return ReplyKeyboardMarkup([
        ['7', '8', '9', '/', 'C'],
        ['4', '5', '6', '*', '⌫'],
        ['1', '2', '3', '-'],
        ['0', '.', '+', '=']
    ], resize_keyboard=True)

async def start(update, context):
    await update.message.reply_text(
        "Калькулятор готов! Используйте кнопки или введите выражение.",
        reply_markup=get_keyboard()
    )

async def handle_calc(update, context):
    text = update.message.text
    
    if text == 'C':
        await update.message.reply_text("0", reply_markup=get_keyboard())
        return
    
    if text == '=':
        # Получаем предыдущее сообщение как выражение
        await update.message.reply_text("Введите выражение и нажмите =", reply_markup=get_keyboard())
        return
    
    # Простое вычисление
    try:
        if text in '0123456789+-*/.⌫':
            await update.message.reply_text(text, reply_markup=get_keyboard())
        else:
            result = eval(text)
            await update.message.reply_text(f"{text} = {result}", reply_markup=get_keyboard())
    except:
        await update.message.reply_text("Ошибка!", reply_markup=get_keyboard())

def main():
    TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        logger.error("Токен не найден!")
        return
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_calc))
    
    logger.info("Бот запускается...")
    app.run_polling()

if __name__ == '__main__':
    main()
