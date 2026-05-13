from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from api_client import ColorAPIClient
from database import Database
from config import Config

class Handlers:
    MAIN_KEYBOARD = [
        ["🎓 Образование", "🏦 Банк/Финансы"],
        ["🎮 Игры", "🏥 Здоровье"],
        ["🍕 Еда", "💻 Технологии"],
        ["👗 Мода", "🌿 Природа"],
        ["⭐ Избранное", "❓ Помощь"]
    ]
    
    COLORS_KEYBOARD = [
        ["➕ Ярче", "➖ Темнее"],
        ["⭐ Добавить все", "🏠 Главное меню"]
    ]
    
    FAVORITES_KEYBOARD = [
        ["📋 Мои цвета", "✏️ Изменить цвет"],
        ["❌ Удалить цвет", "🗑️ Очистить всё"],
        ["🏠 Главное меню"]
    ]
    
    CONFIRM_KEYBOARD = [
        ["✅ Да, очистить всё", "❌ Нет, оставить"],
        ["🏠 Главное меню"]
    ]
    
    CANCEL_KEYBOARD = [["🏠 Отмена"]]

    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        Database.add_user(user.id, user.username, user.first_name)
        context.user_data.clear()
        text = "🎨 <b>Color Bot</b>\n\nВыберите тематику:"
        await update.message.reply_text(
            text,
            reply_markup=ReplyKeyboardMarkup(Handlers.MAIN_KEYBOARD, resize_keyboard=True),
            parse_mode='HTML'
        )

    @staticmethod
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        
        theme_map = {
            "🎓 Образование": "education", "🏦 Банк/Финансы": "bank_finance",
            "🎮 Игры": "games", "🏥 Здоровье": "health",
            "🍕 Еда": "food", "💻 Технологии": "technology",
            "👗 Мода": "fashion", "🌿 Природа": "nature"
        }
        
        if text in theme_map:
            await Handlers.select_theme(update, context, theme_map[text])
            return
        
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
        elif text == "✏️ Изменить цвет":
            await Handlers.start_update_color(update, context)
            return
        elif text == "❌ Удалить цвет":
            await Handlers.start_delete_color(update, context)
            return
        elif text == "🗑️ Очистить всё":
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
        elif text == "🏠 Отмена":
            await Handlers.show_favorites_menu(update, context)
            context.user_data.pop("awaiting_color_selection", None)
            context.user_data.pop("update_color_old", None)
            context.user_data.pop("awaiting_new_color", None)
            return
        
        # Логика выбора цвета по номеру
        if "awaiting_color_selection" in context.user_data:
            # Если пользователь ввел HEX вместо номера – предупредить
            if text.startswith("#") and len(text) == 7:
                await update.message.reply_text(
                    "⚠️ Сейчас нужно ввести НОМЕР цвета из списка (цифру), а не сам цвет.\n"
                    "Пожалуйста, введите номер 1, 2, 3... или нажмите «Отмена»."
                )
                return
            
            try:
                index = int(text) - 1
                action = context.user_data["awaiting_color_selection"]
                user = update.effective_user
                colors = Database.get_user_favorite_colors(user.id)
                
                if 0 <= index < len(colors):
                    selected_color = colors[index]
                    if action == "delete":
                        await Handlers.delete_selected_color(update, context, selected_color)
                    elif action == "update":
                        context.user_data["update_color_old"] = selected_color
                        await update.message.reply_text(
                            f"Выбран цвет {selected_color}\nВведите новый HEX-код (например #FF5733):",
                            reply_markup=ReplyKeyboardMarkup(Handlers.CANCEL_KEYBOARD, resize_keyboard=True)
                        )
                        context.user_data["awaiting_new_color"] = True
                        context.user_data.pop("awaiting_color_selection", None)
                else:
                    await update.message.reply_text("❌ Неверный номер. Попробуйте снова.")
            except ValueError:
                await update.message.reply_text("❌ Пожалуйста, введите номер (цифру) из списка.")
            return
        
        # Логика ожидания нового HEX-кода
        if "awaiting_new_color" in context.user_data:
            if text.startswith("#") and len(text) == 7:
                await Handlers.update_selected_color(update, context, text)
            else:
                await update.message.reply_text("❌ Неверный формат HEX-цвета. Нужно #RRGGBB")
            return
        
        # Добавление нового цвета
        if text.startswith("#") and len(text) == 7:
            await Handlers.add_color_to_favorites(update, context, text)
            return
        
        # Если ничего не подошло
        await update.message.reply_text("Используйте кнопки меню или отправьте цвет в формате #FF5733")

    @staticmethod
    async def select_theme(update: Update, context: ContextTypes.DEFAULT_TYPE, theme: str):
        theme_desc = Config.THEME_DESCRIPTIONS.get(theme, theme)
        await update.message.reply_text(f"🔄 Получаю цвета для {theme_desc}...")
        colors = await ColorAPIClient.get_colors_by_theme(theme)
        if not colors:
            await update.message.reply_text(
                f"❌ Не удалось получить цвета для {theme_desc}\nПопробуйте позже.",
                reply_markup=ReplyKeyboardMarkup([["🏠 Главное меню"]], resize_keyboard=True)
            )
            return
        context.user_data['current_theme'] = theme
        context.user_data['current_colors'] = colors
        context.user_data['theme_desc'] = theme_desc
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
        if 'current_colors' not in context.user_data:
            await update.message.reply_text("Сначала выберите тематику!")
            return
        colors = context.user_data['current_colors']
        action_text = "ярче" if action == "brighter" else "темнее"
        await update.message.reply_text(f"🔄 Делаю цвета {action_text}...")
        adjusted_colors = ColorAPIClient.adjust_colors(colors, action)
        context.user_data['current_colors'] = adjusted_colors
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
        if 'current_colors' not in context.user_data:
            await update.message.reply_text("Сначала выберите тематику!")
            return
        colors = context.user_data['current_colors']
        user = update.effective_user
        saved = 0
        for color in colors:
            if Database.add_favorite_color(user.id, color.upper()):
                saved += 1
        if saved > 0:
            await update.message.reply_text(f"✅ Сохранено {saved} цветов в избранное!")
        else:
            await update.message.reply_text("ℹ️ Все цвета уже были в избранном")

    @staticmethod
    async def add_color_to_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE, color: str):
        user = update.effective_user
        if Database.add_favorite_color(user.id, color.upper()):
            await update.message.reply_text(f"✅ Цвет {color} добавлен в избранное!")
        else:
            await update.message.reply_text(f"ℹ️ Цвет {color} уже в избранном")

    @staticmethod
    async def show_favorites_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.pop("awaiting_color_selection", None)
        context.user_data.pop("awaiting_new_color", None)
        context.user_data.pop("update_color_old", None)
        await update.message.reply_text(
            "⭐ <b>Избранное</b>\n\nВыберите действие:",
            reply_markup=ReplyKeyboardMarkup(Handlers.FAVORITES_KEYBOARD, resize_keyboard=True),
            parse_mode='HTML'
        )

    @staticmethod
    async def show_my_colors(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    async def start_delete_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        colors = Database.get_user_favorite_colors(user.id)
        if not colors:
            await update.message.reply_text("У вас нет сохранённых цветов.")
            return
        message = "Выберите номер цвета для удаления:\n\n"
        for i, color in enumerate(colors, 1):
            message += f"{i}. {color}\n"
        message += "\nВведите номер (цифру):"
        await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup(Handlers.CANCEL_KEYBOARD, resize_keyboard=True))
        context.user_data["awaiting_color_selection"] = "delete"

    @staticmethod
    async def delete_selected_color(update: Update, context: ContextTypes.DEFAULT_TYPE, color: str):
        user = update.effective_user
        if Database.delete_favorite_color(user.id, color):
            await update.message.reply_text(f"✅ Цвет {color} удалён из избранного.")
        else:
            await update.message.reply_text(f"❌ Не удалось удалить {color}.")
        await Handlers.show_favorites_menu(update, context)

    @staticmethod
    async def start_update_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        colors = Database.get_user_favorite_colors(user.id)
        if not colors:
            await update.message.reply_text("У вас нет сохранённых цветов.")
            return
        message = "Выберите номер цвета для изменения:\n\n"
        for i, color in enumerate(colors, 1):
            message += f"{i}. {color}\n"
        message += "\nВведите номер (цифру):"
        await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup(Handlers.CANCEL_KEYBOARD, resize_keyboard=True))
        context.user_data["awaiting_color_selection"] = "update"

    @staticmethod
    async def update_selected_color(update: Update, context: ContextTypes.DEFAULT_TYPE, new_hex: str):
        user = update.effective_user
        old_hex = context.user_data.get("update_color_old")
        if not old_hex:
            await update.message.reply_text("Ошибка: не выбран цвет для изменения.")
            await Handlers.show_favorites_menu(update, context)
            return
        if Database.update_favorite_color(user.id, old_hex, new_hex):
            await update.message.reply_text(f"✅ Цвет {old_hex} изменён на {new_hex}.")
        else:
            await update.message.reply_text(f"❌ Не удалось изменить {old_hex} на {new_hex}.")
        context.user_data.pop("update_color_old", None)
        context.user_data.pop("awaiting_new_color", None)
        await Handlers.show_favorites_menu(update, context)

    @staticmethod
    async def confirm_clear_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        color_count, _ = Database.get_user_stats(user.id)
        if color_count == 0:
            await update.message.reply_text("ℹ️ Ваше избранное уже пустое")
            return
        await update.message.reply_text(
            f"⚠️ Вы уверены, что хотите очистить всё избранное?\nБудет удалено {color_count} цветов.\nЭто действие нельзя отменить!",
            reply_markup=ReplyKeyboardMarkup(Handlers.CONFIRM_KEYBOARD, resize_keyboard=True)
        )

    @staticmethod
    async def clear_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if Database.clear_user_favorites(user.id):
            await update.message.reply_text("✅ Все избранное очищено!")
        else:
            await update.message.reply_text("❌ Не удалось очистить избранное")
        await Handlers.start(update, context)

    @staticmethod
    async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """🎨 <b>Color Bot - помощь</b>

<b>Как использовать:</b>
1. Выберите тематику
2. Получите подобранные цвета
3. Настройте яркость при необходимости
4. Добавьте цвета в избранное

<b>Добавление цветов:</b>
Отправьте любой HEX-код в формате #FF5733

<b>Избранное:</b>
• 📋 Мои цвета – посмотреть список
• ✏️ Изменить цвет – заменить существующий
• ❌ Удалить цвет – удалить один цвет
• 🗑️ Очистить всё – удалить все цвета"""
        await update.message.reply_text(help_text, parse_mode='HTML')