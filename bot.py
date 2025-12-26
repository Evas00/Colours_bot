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
        print("❌ Ошибка не найден токен бота")
        return
    try:
        # Создаем приложение с увеличенным таймаутом
        app = Application.builder()\
            .token(Config.BOT_TOKEN)\
            .connect_timeout(10)\
            .read_timeout(10)\
            .write_timeout(10)\
            .pool_timeout(10)\
            .build()
        
        # добавляем команды и регистрируем обработчики
        app.add_handler(CommandHandler("start", Handlers.start))
        app.add_handler(CommandHandler("colors", Handlers.show_colors))
        app.add_handler(CommandHandler("palettes", Handlers.show_palettes))
        app.add_handler(CommandHandler("random", Handlers.show_random))
        app.add_handler(CommandHandler("favorites", Handlers.show_favorites))
        app.add_handler(CommandHandler("stats", Handlers.show_stats))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, Handlers.handle_text))
        
        # Запускаем
        print("Бот запущен")
        
        app.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка при запуске: {type(e).__name__}")
        print(f"Подробно: {e}")
        
        if "timed out" in str(e).lower():
            print("\n💡 Совет: Попробуй:")
            print("1. Запустить бота снова")
            print("2. Проверить интернет-соединение")
            print("3. Подождать 5 минут и повторить")

if __name__ == "__main__":
    main()