import logging
import json
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext
)
from gigachat_api import GigaChatAPI
from config import BOT_TOKEN, ADMIN_ID, GIGACHAT_CREDENTIALS, config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация GigaChat
gigachat = None

def check_config():
    """Проверка конфигурации"""
    # Импортируем переменные из config
    from config import BOT_TOKEN, GIGACHAT_CREDENTIALS
    
    if BOT_TOKEN == "ЗАМЕНИ_НА_СВОЙ_ТОКЕН" or not BOT_TOKEN:
        logger.error("❌ НЕ ЗАПОЛНЕН BOT_TOKEN в config.json!")
        return False
    
    if GIGACHAT_CREDENTIALS == "ЗАМЕНИ_НА_СВОЙ_API_КЛЮЧ" or not GIGACHAT_CREDENTIALS:
        logger.error("❌ НЕ ЗАПОЛНЕН GIGACHAT_CREDENTIALS в config.json!")
        return False
    
    logger.info("✅ Конфигурация проверена успешно")
    logger.info(f"Bot Token: {BOT_TOKEN[:10]}...")
    logger.info(f"GigaChat Creds: {GIGACHAT_CREDENTIALS[:10]}...")
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = (
        "Ну привет, опять ты... 😒\n"
        "Я Владик, самый умный (и самый вредный) бот в этом чате! ⚽\n\n"
        "• Задавай вопросы — буду отвечать и грубить\n"
        "• /help — если совсем тупой (скорее всего)\n"
        "• /football — получи порцию мудрости про футбол\n\n"
        "И запомни: Месси — переоценен, Роналду — король! 👑"
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = (
        "Слушай сюда, балбес: 🤨\n\n"
        "• Просто пиши мне — буду грубить и давать советы\n"
        "• /start — если забыл, кто я\n"
        "• /football — мое экспертное мнение ⚽\n"
        "• /stats — статистика (только для админа)\n\n"
        "И не задавай глупых вопросов, ладно?"
    )
    await update.message.reply_text(help_text)

async def football_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Случайный футбольный факт"""
    import random
    
    facts = [
        "Так, слушай: 4-4-2 это классика для гениев, а 5-3-2 для трусов. Твоя команда наверняка играет вторым способом! 😏",
        "Месси? Талантливый карлик. Роналду? Машина для голов. Я? Гений тактики. Ты? Зритель с чипсами. 🍟⚽",
        "Если бы я тренировал 'Спартак', они бы уже 10 раз выиграли Лигу Чемпионов. Но нет, берут каких-то дилетантов... 🤦‍♂️",
        "Офсайд — это не правило, а искусство! Но тебе этого не понять... 🎨",
        "Английский футбол — беготня с мячом. Итальянская серия A — шахматы. Российская Премьер-лига... лучше промолчу. 🇷🇺"
    ]
    
    await update.message.reply_text(random.choice(facts))

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика для админа"""
    user_id = update.effective_user.id
    
    if str(user_id) == ADMIN_ID:
        try:
            with open('bot.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            stats_text = (
                f"📊 Статистика для админа:\n"
                f"• Лог файл: {len(lines)} строк\n"
                f"• ID пользователя: {user_id}\n"
                f"• Бот запущен и работает\n"
            )
            await update.message.reply_text(stats_text)
        except:
            await update.message.reply_text("Лог файл не найден... Опять что-то сломалось! 🔧")
    else:
        await update.message.reply_text("Ты кто такой, чтобы смотреть статистику? Иди отсюда! 🚫")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    global gigachat
    
    user_id = update.effective_user.id
    username = update.effective_user.username or "без username"
    user_message = update.message.text
    
    logger.info(f"👤 Пользователь @{username} ({user_id}): {user_message[:50]}...")
    
    # Проверяем инициализацию GigaChat
    if gigachat is None:
        try:
            gigachat = GigaChatAPI()
            logger.info("✅ GigaChat инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации GigaChat: {e}")
            await update.message.reply_text("Что-то пошло не так при запуске... Опять эти техники! 🔧")
            return
    
    # Показываем статус "печатает"
    await update.message.chat.send_action(action="typing")
    
    try:
        # Получаем ответ от GigaChat
        response = gigachat.get_response(user_message)
        
        # Логируем ответ
        logger.info(f"🤖 Владик ответил: {response[:50]}...")
        
        # Отправляем ответ
        await update.message.reply_text(response)
        
    except Exception as e:
        error_msg = "Ой, что-то пошло не так... Наверное, виноват ты! Попробуй еще раз. 🔧"
        logger.error(f"❌ Ошибка: {e}")
        await update.message.reply_text(error_msg)

async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка всего остального"""
    responses = [
        "Что это такое? Я только текст понимаю... Ну ты и даешь! 📎",
        "Картинки? Голосовые? Ой, отстань со своими fancy штуками! 📸",
        "Вижу что-то непонятное... Лучше напиши словами, ладно? ✍️"
    ]
    import random
    await update.message.reply_text(random.choice(responses))

async def error_handler(update: Update, context: CallbackContext):
    """Обработчик ошибок"""
    logger.error(f"💥 Ошибка в обновлении {update}: {context.error}")
    
    if update and update.message:
        try:
            await update.message.reply_text(
                "Упс... У меня в голове что-то замкнуло от твоего вопроса! "
                "Попробуй спросить по-другому. ⚡"
            )
        except:
            pass

def main():
    """Запуск бота"""
    print("=" * 50)
    print("🤖 Запуск бота Владика...")
    print("=" * 50)
    
    # Проверяем конфигурацию
    if not check_config():
        print("❌ ЗАПОЛНИТЕ config.json ПЕРЕД ЗАПУСКОМ!")
        print("Используйте шаблон из сообщения выше")
        return
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("football", football_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработчик всего остального (стикеры, фото и т.д.)
    application.add_handler(MessageHandler(filters.ALL, handle_other))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    print("✅ Бот запущен! Ожидание сообщений...")
    print(f"🤖 Имя бота: Владик")
    print(f"⚽ Любимая тема: футбол и грубости")
    print("=" * 50)
    
    # Запуск бота
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()
