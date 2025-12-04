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
            ["💡 Случайная палитра", "🔄 Проверить API"]
        ]
        
        text = """🎨 *Добро пожаловать в Color Bot!*
        
*Реальные данные из API:*
• GitHub Colors API - цвета языков программирования
• Nice Color Palettes API - готовые палитры
        
_Если API недоступны - бот покажет ошибку_
        
Используйте кнопки ниже:"""
        
        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка /help"""
        text = """📚 *Color Bot - ТОЛЬКО реальные API*
        
*Источники:*
1. GitHub Colors API
   - Цвета языков программирования
   - Пример: Python - синий, JavaScript - желтый
   
2. Nice Color Palettes API
   - Готовые цветовые палитры
   - 5 цветов в каждой
        
*Бот не имеет резервных данных*
Если API не работают - вы увидите сообщение об ошибке"""
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    @staticmethod
    async def check_api_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Проверить статус API"""
        await update.message.reply_text("🔍 Проверяю доступность API...")
        
        github_status = await ColorAPIClient.get_github_colors()
        palettes_status = await ColorAPIClient.get_color_palettes()
        
        text = "*Статус API:*\n\n"
        
        if github_status:
            text += "✅ GitHub Colors API - работает\n"
            text += f"   Доступно цветов: {len(github_status)}\n"
        else:
            text += "❌ GitHub Colors API - недоступен\n"
        
        text += "\n"
        
        if palettes_status:
            text += "✅ Nice Color Palettes API - работает\n"
            text += f"   Доступно палитр: {len(palettes_status)}\n"
        else:
            text += "❌ Nice Color Palettes API - недоступен\n"
        
        text += "\n_Попробуйте позже, если API недоступны_"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    @staticmethod
    async def show_trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать трендовые цвета - ТОЛЬКО из API"""
        await update.message.reply_text("🔄 Получаю цвета из GitHub API...")
        
        colors = await ColorAPIClient.get_github_colors()
        
        if not colors:
            await update.message.reply_text(
                "❌ GitHub Colors API временно недоступен\n\n"
                "Попробуйте позже или нажмите '🔄 Проверить API'"
            )
            return
        
        message = "🎨 *Топ цвета из GitHub API:*\n\n"
        for i in range(0, len(colors), 5):
            batch = colors[i:i+5]
            message += " ".join([f"🟥{c}" for c in batch]) + "\n"
            message += f"`{' '.join(batch)}`\n\n"
        
        message += "_Источник: GitHub Colors API_"
        await update.message.reply_text(message, parse_mode='Markdown')
    
    @staticmethod
    async def show_palettes(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать популярные палитры - ТОЛЬКО из API"""
        await update.message.reply_text("🔄 Загружаю палитры из Nice Color Palettes API...")
        
        palettes = await ColorAPIClient.get_color_palettes()
        
        if not palettes:
            await update.message.reply_text(
                "❌ Nice Color Palettes API временно недоступен\n\n"
                "Попробуйте позже или нажмите '🔄 Проверить API'"
            )
            return
        
        message = "🔥 *Популярные палитры из API:*\n\n"
        for i, palette in enumerate(palettes, 1):
            message += f"*Палитра #{i}*\n"
            message += " ".join([f"🟥{c}" for c in palette]) + "\n"
            message += f"`{' '.join(palette)}`\n\n"
        
        message += "_Источник: Nice Color Palettes API_"
        await update.message.reply_text(message, parse_mode='Markdown')
    
    @staticmethod
    async def show_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать случайную палитру - ТОЛЬКО из API"""
        await update.message.reply_text("🎲 Ищу случайную палитру в API...")
        
        palette = await ColorAPIClient.get_random_palette()
        
        if not palette:
            await update.message.reply_text(
                "❌ Все API временно недоступны\n\n"
                "Не удалось получить данные ни из одного источника.\n"
                "Проверьте статус API или попробуйте позже."
            )
            return
        
        message = "💡 *Случайная палитра из API:*\n\n"
        message += " ".join([f"🟥{c}" for c in palette]) + "\n\n"
        message += f"`{' '.join(palette)}`\n\n"
        message += "_Собрано из доступных API_"
        
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
        elif text == "🔄 Проверить API":
            await Handlers.check_api_status(update, context)
        else:
            await update.message.reply_text(
                "Используйте кнопки или команды\n"
                "Напишите /help для справки"
            )