from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from api_client import ColorAPIClient
from database import Database
from config import Config

class Handlers:
    """Все обработчики бота"""
    
    # Главное меню - выбор тематики
    MAIN_KEYBOARD = [
        ["🎓 Образование", "🏦 Банк/Финансы"],
        ["🎮 Игры", "🏥 Здоровье"],
        ["🍕 Еда", "💻 Технологии"],
        ["👗 Мода", "🌿 Природа"],
        ["⭐ Избранное", "❓ Помощь"]
    ]
    
    # После выбора темы
    COLORS_KEYBOARD = [
        ["➕ Ярче", "➖ Темнее"],
        ["⭐ Добавить все", "🏠 Главное меню"]
    ]
    
    # Меню избранного
    FAVORITES_KEYBOARD = [
        ["📋 Мои цвета", "🗑️ Очистить"],
        ["🏠 Главное меню"]
    ]
    
    # Подтверждение очистки
    CONFIRM_KEYBOARD = [
        ["✅ Да, очистить всё", "❌ Нет, оставить"],
        ["🏠 Главное меню"]
    ]

    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало работы"""
        # Получение информации о пользователе
        user = update.effective_user
        Database.add_user(user.id, user.username, user.first_name)
        context.user_data.clear()
        
        text = """🎨 <b>Color Bot</b>

Выберите тематику, для которой нужны цвета:"""

        # Отправка текста
        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup(Handlers.MAIN_KEYBOARD, resize_keyboard=True),
            parse_mode='HTML'
        )

    @staticmethod
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text
        
        # Обработка выбора тематики
        theme_map = {
            "🎓 Образование": "education",
            "🏦 Банк/Финансы": "bank_finance",
            "🎮 Игры": "games", 
            "🏥 Здоровье": "health",
            "🍕 Еда": "food",
            "💻 Технологии": "technology",
            "👗 Мода": "fashion",
            "🌿 Природа": "nature"
        }
        
        if text in theme_map:
            await Handlers.select_theme(update, context, theme_map[text])
            return
        
        # Обработка действий с цветами
        if text == "➕ Ярче":
            await Handlers.adjust_colors(update, context, "brighter")
            return
        elif text == "➖ Темнее":
            await Handlers.adjust_colors(update, context, "darker")
            return
        elif text == "⭐ Добавить все":
            await Handlers.save_all_colors(update, context)
            return
        elif text == "⭐ Избранное":
            await Handlers.show_favorites_menu(update, context)
            return
        elif text == "📋 Мои цвета":
            await Handlers.show_my_colors(update, context)
            return
        elif text == "🗑️ Очистить":
            await Handlers.confirm_clear_favorites(update, context)
            return
        elif text == "✅ Да, очистить всё":
            await Handlers.clear_favorites(update, context)
            return
        elif text == "❌ Нет, оставить":
            await Handlers.show_favorites_menu(update, context)
            return
        elif text == "🏠 Главное меню":
            await Handlers.start(update, context)
            return
        elif text == "❓ Помощь":
            await Handlers.show_help(update, context)
            return
        
        # Обработка ввода цвета (например #FF5733)
        if text.startswith("#") and len(text) == 7:
            await Handlers.add_color_to_favorites(update, context, text)
            return
        
        await update.message.reply_text("Используйте кнопки меню или отправьте цвет в формате #FF5733")

    @staticmethod
    async def select_theme(update: Update, context: ContextTypes.DEFAULT_TYPE, theme: str):
        """Выбор тематики"""
        theme_desc = Config.THEME_DESCRIPTIONS.get(theme, theme)
        
        await update.message.reply_text(f"🔄 Получаю цвета для {theme_desc}...")
        
        # Получаем цвета из API
        colors = await ColorAPIClient.get_colors_by_theme(theme)
        
        if not colors:
            await update.message.reply_text(
                f"❌ Не удалось получить цвета для {theme_desc}\n"
                "Попробуйте позже.",
                reply_markup=ReplyKeyboardMarkup([["🏠 Главное меню"]], resize_keyboard=True)
            )
            return
        
        # Сохраняем в контексте
        context.user_data['current_theme'] = theme
        context.user_data['current_colors'] = colors
        context.user_data['theme_desc'] = theme_desc
        
        # Показываем цвета
        message = f"🎨 <b>Цвета для {theme_desc}:</b>\n\n"
        
        for i, color in enumerate(colors, 1):
            message += f"{i}. <code>{color}</code>\n"
        
        message += "\nВыберите действие:"
        
        await update.message.reply_text(
            message,
            reply_markup=ReplyKeyboardMarkup(Handlers.COLORS_KEYBOARD, resize_keyboard=True),
            parse_mode='HTML'
        )

    @staticmethod
    async def adjust_colors(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
        """Изменение яркости цветов"""
        if 'current_colors' not in context.user_data:
            await update.message.reply_text("Сначала выберите тематику!")
            return
        
        colors = context.user_data['current_colors']
        action_text = "ярче" if action == "brighter" else "темнее"
        
        await update.message.reply_text(f"🔄 Делаю цвета {action_text}...")
        
        # Изменяем цвета
        adjusted_colors = ColorAPIClient.adjust_colors(colors, action)
        
        # Обновляем в контексте
        context.user_data['current_colors'] = adjusted_colors
        
        # Показываем обновленные цвета
        theme_desc = context.user_data.get('theme_desc', 'темы')
        message = f"🎨 <b>Цвета для {theme_desc} ({action_text}):</b>\n\n"
        
        for i, color in enumerate(adjusted_colors, 1):
            message += f"{i}. <code>{color}</code>\n"
        
        message += "\nВыберите действие:"
        
        await update.message.reply_text(
            message,
            reply_markup=ReplyKeyboardMarkup(Handlers.COLORS_KEYBOARD, resize_keyboard=True),
            parse_mode='HTML'
        )

    @staticmethod
    async def save_all_colors(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сохранить все текущие цвета в избранное"""
        # Проверка наличия цветов в контексте пользователя
        if 'current_colors' not in context.user_data:
            await update.message.reply_text("Сначала выберите тематику!")
            return
        
        # Получение текущих цветов из контекста
        colors = context.user_data['current_colors']
        # Получение информации о пользователе
        user = update.effective_user
        
        saved = 0
        skipped = 0 
        # Счетчик пропущенных цветов (уже есть в избранном)
        
        for color in colors:
            if Database.add_favorite_color(user.id, color.upper()):
                saved += 1
            else:
                skipped += 1
        
        if saved > 0:
            await update.message.reply_text(f"✅ Сохранено {saved} цветов в избранное!")
        else:
            await update.message.reply_text("ℹ️ Все цвета уже были в избранном")

    @staticmethod
    async def add_color_to_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE, color: str):
        """Добавить один цвет в избранное"""
        user = update.effective_user
        
        if Database.add_favorite_color(user.id, color.upper()):
            await update.message.reply_text(f"✅ Цвет {color} добавлен в избранное!")
        else:
            await update.message.reply_text(f"ℹ️ Цвет {color} уже в избранном")

    @staticmethod
    async def show_favorites_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать меню избранного"""
        await update.message.reply_text(
            "⭐ <b>Избранное</b>\n\nВыберите действие:",
            reply_markup=ReplyKeyboardMarkup(Handlers.FAVORITES_KEYBOARD, resize_keyboard=True),
            parse_mode='HTML'
        )

    @staticmethod
    async def show_my_colors(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать избранные цвета"""
        user = update.effective_user
        favorite_colors = Database.get_user_favorite_colors(user.id)
        
        if not favorite_colors:
            message = "⭐ У вас пока нет избранных цветов\n\nОтправьте цвет в формате #FF5733 или выберите тематику"
        else:
            message = f"⭐ <b>Ваши цвета ({len(favorite_colors)}):</b>\n\n"
            for i, color in enumerate(favorite_colors, 1):
                message += f"{i}. <code>{color}</code>\n"
        
        await update.message.reply_text(message, parse_mode='HTML')

    @staticmethod
    async def confirm_clear_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение очистки избранного"""
        user = update.effective_user
        color_count, _ = Database.get_user_stats(user.id)
        
        if color_count == 0:
            await update.message.reply_text("ℹ️ Ваше избранное уже пустое")
            return
        
        await update.message.reply_text(
            f"⚠️ Вы уверены, что хотите очистить все избранное?\n"
            f"Будет удалено {color_count} цветов.\n"
            f"Это действие нельзя отменить!",
            reply_markup=ReplyKeyboardMarkup(Handlers.CONFIRM_KEYBOARD, resize_keyboard=True)
        )

    @staticmethod
    async def clear_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Очистить избранное"""
        user = update.effective_user
        
        if Database.clear_user_favorites(user.id):
            await update.message.reply_text("✅ Все избранное очищено!")
        else:
            await update.message.reply_text("❌ Не удалось очистить избранное")
        
        await Handlers.start(update, context)

    @staticmethod
    async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать справку"""
        help_text = """🎨 <b>Color Bot - помощь</b>

<b>Как использовать:</b>
1. Выберите тематику
2. Получите подобранные цвета
3. Настройте яркость при необходимости
4. Добавьте цвета в избранное

<b>Добавление цветов:</b>
Отправьте любой HEX-код в формате #FF5733

<b>Избранное:</b>
Хранит ваши любимые цвета"""
        
        await update.message.reply_text(help_text, parse_mode='HTML')