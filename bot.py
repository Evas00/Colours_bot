# bot.py
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import Config
from app.handlers import Handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    if not Config.BOT_TOKEN:
        print("❌ Ошибка: не найден токен бота")
        print("Создайте файл .env и добавьте BOT_TOKEN=ваш_токен")
        return
    
    try:
        app = Application.builder().token(Config.BOT_TOKEN).build()
        
        app.add_handler(CommandHandler("start", Handlers.start))
        app.add_handler(CommandHandler("help", Handlers.show_help))
        app.add_handler(CommandHandler("favorites", Handlers.show_favorites_menu))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, Handlers.handle_text))
        
        print("✅ Бот запущен")
        print("🎨 Доступные тематики:")
        for theme, desc in Config.THEME_DESCRIPTIONS.items():
            print(f"  • {theme}: {desc}")
        print("\n🤖 Бот готов к работе...")
        
        app.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        if "timed out" in str(e).lower():
            print("\n💡 Совет: Попробуйте:")
            print("1. Проверить интернет-соединение")
            print("2. Запустить бота снова")
            print("3. Проверить токен бота в .env файле")

if __name__ == "__main__":
    main()