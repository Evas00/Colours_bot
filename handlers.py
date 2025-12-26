from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from api_client import ColorAPIClient
from database import Database
from datetime import datetime

class Handlers:
    """Все обработчики бота"""
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка /start"""
        user = update.effective_user
        db_user = Database.add_user(user.id, user.username, user.first_name)

        keyboard = [
            ["🎨 Трендовые цвета", "🔥 Популярные палитры"],
            ["💡 Случайная палитра", "⭐ Избранное"],
            ["📊 Статистика"]
        ]
        
        text = """🎨 <b>Добро пожаловать в Color Bot!</b>"""
        
        # Отправляем приветственное сообщение с клавиатурой
        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
            parse_mode='HTML'
        )
    
    @staticmethod
    async def show_colors(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показываем трендовые цвета"""
        await update.message.reply_text("🔄 Получаю цвета...")
        
        user = update.effective_user
        Database.log_action(user.id, 'get_colors')

        colors = await ColorAPIClient.get_github_colors()
        
        if not colors:
            await update.message.reply_text(
                "❌ Временно недоступно\n\n"
                "Попробуйте позже"
            )
            return

        for i in range(0, len(colors), 5):
            batch = colors[i:i+5]
            message = "🎨 <b>Трендовые цвета:</b>\n\n"
            for color in batch:
                # Цветной квадрат + HEX код
                message += f'<code>{color}</code>\n'
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    @staticmethod
    async def show_palettes(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показываем популярные палитры"""
        await update.message.reply_text("🔄 Загружаю палитры...")
        
        user = update.effective_user
        Database.log_action(user.id, 'get_palettes')

        palettes = await ColorAPIClient.get_palettes()
        
        if not palettes:
            await update.message.reply_text(
                "❌ Временно недоступно\n\n"
                "Попробуйте позже"
            )
            return
        
        message = "🔥 <b>Популярные палитры:</b>\n\n"
        for i, palette in enumerate(palettes, 1):
            message += f"<b>Палитра #{i}</b>\n"
            for color in palette:
                message += f'<code>{color}</code>\n'
            message += "\n"
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    @staticmethod
    async def show_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показываем случайную палитру"""
        await update.message.reply_text("🎲 Ищу случайную палитру...")
        
        palette = await ColorAPIClient.get_random_palette()
        
        if not palette:
            await update.message.reply_text(
                "❌ Не удалось получить данные ни из одного источника\n\n"
                "Попробуйте позже."
            )
            return
        
        message = "💡 <b>Случайная палитра:</b>\n\n"
        for color in palette:
            message += f'<code>{color}</code>\n'
        
        await update.message.reply_text(message, parse_mode='HTML')

    @staticmethod
    async def show_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показываем избранные цвета"""
        user = update.effective_user
        
        favorite_colors = Database.get_user_favorites(user.id)
            
        if not favorite_colors:
            message = "⭐ <b>У тебя пока нет избранных цветов</b>\n\n"
            message += "Чтобы добавить цвет:\n"
            message += "1. Нажми 🎨 Трендовые цвета\n"
            message += "2. Отправь мне HEX-код цвета"
        else:
            message = f"⭐ <b>Твои избранные цвета</b> ({len(favorite_colors)}):\n\n"
            for color_hex in favorite_colors:
                message += f'<code>{color_hex}</code>\n'
                
            message += f"\n<b>Всего цветов:</b> {len(favorite_colors)}"
            
        await update.message.reply_text(message, parse_mode='HTML')
    
    @staticmethod
    async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показываем статистику"""
        user = update.effective_user
        
        fav_count, history_count = Database.get_user_stats(user.id)
        
        message = f"📊 <b>Статистика для {user.first_name}</b>\n\n"
        message += f"• ⭐ Избранных цветов: {fav_count}\n"
        message += f"• 📝 Действий в истории: {history_count}\n"
        message += f"• 🗓️ Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    @staticmethod
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text
        
        if text == "🎨 Трендовые цвета":
            await Handlers.show_colors(update, context)
        elif text == "🔥 Популярные палитры":
            await Handlers.show_palettes(update, context)
        elif text == "💡 Случайная палитра":
            await Handlers.show_random(update, context)
        elif text == "⭐ Избранное":
            await Handlers.show_favorites(update, context)
        elif text == "📊 Статистика":
            await Handlers.show_stats(update, context)
        elif text.startswith("#") and len(text) == 7:
            # Если отправили цвет
            user = update.effective_user
            if Database.add_favorite(user.id, text.upper()):
                await update.message.reply_text(f"✅ Цвет {text} добавлен в избранное!")
            else:
                await update.message.reply_text(f"ℹ️ Цвет {text} уже в избранном!")
        else:
            await update.message.reply_text(
                "Используй кнопки меню или отправь мне цвет в формате #FF5733"
            )