# app/handlers/__init__.py
from telegram import Update
from telegram.ext import ContextTypes
from .start_help import start, show_help
from .theme_handlers import select_theme, adjust_colors, save_all_colors
from .favorites import (
    show_favorites_menu, show_my_colors,
    start_delete_color, delete_selected_color,
    start_update_color, update_selected_color,
    confirm_clear_favorites, clear_favorites,
    add_color_to_favorites
)
from .common import (
    get_main_keyboard, get_colors_keyboard, get_favorites_keyboard,
    get_confirm_keyboard, get_cancel_keyboard
)

class Handlers:
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await start(update, context)

    @staticmethod
    async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await show_help(update, context)

    @staticmethod
    async def select_theme(update: Update, context: ContextTypes.DEFAULT_TYPE, theme: str):
        await select_theme(update, context, theme)

    @staticmethod
    async def adjust_colors(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
        await adjust_colors(update, context, action)

    @staticmethod
    async def save_all_colors(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await save_all_colors(update, context)

    @staticmethod
    async def show_favorites_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await show_favorites_menu(update, context)

    @staticmethod
    async def show_my_colors(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await show_my_colors(update, context)

    @staticmethod
    async def start_delete_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await start_delete_color(update, context)

    @staticmethod
    async def delete_selected_color(update: Update, context: ContextTypes.DEFAULT_TYPE, color: str):
        await delete_selected_color(update, context, color)

    @staticmethod
    async def start_update_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await start_update_color(update, context)

    @staticmethod
    async def update_selected_color(update: Update, context: ContextTypes.DEFAULT_TYPE, new_hex: str):
        await update_selected_color(update, context, new_hex)

    @staticmethod
    async def confirm_clear_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await confirm_clear_favorites(update, context)

    @staticmethod
    async def clear_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await clear_favorites(update, context)

    @staticmethod
    async def add_color_to_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE, color: str):
        await add_color_to_favorites(update, context, color)

    # ==================== ГЛАВНЫЙ ОБРАБОТЧИК ТЕКСТА ====================
    @staticmethod
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        from app.database.db_ops import Database
        from config import Config

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
        elif text == "➖ Темнее":
            await Handlers.adjust_colors(update, context, "darker")
        elif text == "⭐ Добавить все":
            await Handlers.save_all_colors(update, context)
        elif text == "⭐ Избранное":
            await Handlers.show_favorites_menu(update, context)
        elif text == "📋 Мои цвета":
            await Handlers.show_my_colors(update, context)
        elif text == "✏️ Изменить цвет":
            await Handlers.start_update_color(update, context)
        elif text == "❌ Удалить цвет":
            await Handlers.start_delete_color(update, context)
        elif text == "🗑️ Очистить всё":
            await Handlers.confirm_clear_favorites(update, context)
        elif text == "✅ Да, очистить всё":
            await Handlers.clear_favorites(update, context)
        elif text == "❌ Нет, оставить":
            await Handlers.show_favorites_menu(update, context)
        elif text == "🏠 Главное меню":
            await Handlers.start(update, context)
        elif text == "❓ Помощь":
            await Handlers.show_help(update, context)
        elif text == "🏠 Отмена":
            await Handlers.show_favorites_menu(update, context)
            context.user_data.pop("awaiting_color_selection", None)
            context.user_data.pop("update_color_old", None)
            context.user_data.pop("awaiting_new_color", None)
        else:
            # Ожидание номера для удаления/изменения
            if "awaiting_color_selection" in context.user_data:
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
                                reply_markup=get_cancel_keyboard()
                            )
                            context.user_data["awaiting_new_color"] = True
                            context.user_data.pop("awaiting_color_selection", None)
                    else:
                        await update.message.reply_text("❌ Неверный номер. Попробуйте снова.")
                except ValueError:
                    await update.message.reply_text("❌ Пожалуйста, введите номер (цифру) из списка.")
                return

            # Ожидание нового HEX-кода
            if "awaiting_new_color" in context.user_data:
                if text.startswith("#") and len(text) == 7:
                    await Handlers.update_selected_color(update, context, text)
                else:
                    await update.message.reply_text("❌ Неверный формат HEX-цвета. Нужно #RRGGBB")
                return

            # Добавление цвета
            if text.startswith("#") and len(text) == 7:
                await Handlers.add_color_to_favorites(update, context, text)
                return

            await update.message.reply_text("Используйте кнопки меню или отправьте цвет в формате #FF5733")