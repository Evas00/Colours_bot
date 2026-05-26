# app/handlers/start_help.py
from telegram import Update
from telegram.ext import ContextTypes
from app.database.db_ops import Database
from .common import get_main_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    Database.add_user(user.id, user.username, user.first_name)
    context.user_data.clear()
    text = "🎨 <b>Color Bot</b>\n\nВыберите тематику:"
    await update.message.reply_text(
        text,
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )

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