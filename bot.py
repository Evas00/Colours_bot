import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import Config
from handlers import Handlers

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Запуск бота"""
    if not Config.BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не найден")
        print("Создайте .env файл с BOT_TOKEN=ваш_токен")
        return
    
    # Создаем приложение
    app = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", Handlers.start))
    app.add_handler(CommandHandler("help", Handlers.help_cmd))
    # Убрали CommandHandler("status", Handlers.check_api_status)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, Handlers.handle_text))
    
    # Запускаем
    logger.info("Бот запущен - ТОЛЬКО API, без fallback!")
    app.run_polling()

if __name__ == "__main__":
    main()