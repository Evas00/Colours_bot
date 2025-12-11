from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from api_client import ColorAPIClient

class Handlers:
    """Все обработчики бота"""
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка /start"""
        keyboard = [
            ["🎨 Трендовые цвета", "🔥 Популярные палитры"],
            ["💡 Случайная палитра"]
        ]
        
        text = """🎨 *Добро пожаловать в Color Bot!*"""
        
        # Отправляем приветственное сообщение с клавиатурой
        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def show_trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать трендовые цвета - ТОЛЬКО из API"""
        await update.message.reply_text("🔄 Получаю цвета...")
        
        colors = await ColorAPIClient.get_github_colors()
        
        if not colors:
            await update.message.reply_text(
                "❌ Временно недоступно\n\n"
                "Попробуйте позже"
            )
            return
        
        message = "🎨 *Топ цвета:*\n\n"
        for i in range(0, len(colors), 5):
            batch = colors[i:i+5]
            message += " ".join([f"🟥{c}" for c in batch]) + "\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    @staticmethod
    async def show_palettes(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать популярные палитры - ТОЛЬКО из API"""
        await update.message.reply_text("🔄 Загружаю палитры...")
        
        palettes = await ColorAPIClient.get_color_palettes()
        
        if not palettes:
            await update.message.reply_text(
                "❌ Временно недоступно\n\n"
                "Попробуйте позже"
            )
            return
        
        message = "🔥 *Популярные палитры:*\n\n"
        for i, palette in enumerate(palettes, 1):
            message += f"*Палитра #{i}*\n"
            message += " ".join([f"🟥{c}" for c in palette]) + "\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    @staticmethod
    async def show_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать случайную палитру - ТОЛЬКО из API"""
        await update.message.reply_text("🎲 Ищу случайную палитру...")
        
        palette = await ColorAPIClient.get_random_palette()
        
        if not palette:
            await update.message.reply_text(
                "❌ Не удалось получить данные ни из одного источника\n\n"
                "Попробуйте позже."
            )
            return
        
        message = "💡 *Случайная палитра:*\n\n"
        message += " ".join([f"🟥{c}" for c in palette]) + "\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    @staticmethod
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text
        
        if text == "🎨 Трендовые цвета":
            await Handlers.show_trending(update, context)
        elif text == "🔥 Популярные палитры":
            await Handlers.show_palettes(update, context)
        elif text == "💡 Случайная палитра":
            await Handlers.show_random(update, context)
        else:
            await update.message.reply_text(
                "Используйте кнопки или команды"
            )