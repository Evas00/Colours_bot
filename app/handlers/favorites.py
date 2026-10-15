from telegram import Update
from telegram.ext import ContextTypes
from .common import (
    get_favorites_keyboard, get_cancel_keyboard, get_confirm_keyboard,
    get_main_keyboard
)


async def show_favorites_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("awaiting_color_selection", None)
    context.user_data.pop("awaiting_new_color", None)
    context.user_data.pop("update_color_old", None)
    await update.message.reply_text(
        "⭐ <b>Избранное</b>\n\nВыберите действие:",
        reply_markup=get_favorites_keyboard(),
        parse_mode='HTML'
    )


async def show_my_colors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    container = context.bot_data["container"]
    colors = await container.list_colors.execute(user.id)

    if not colors:
        message = "⭐ У вас пока нет избранных цветов\n\nОтправьте цвет в формате #FF5733 или выберите тематику"
    else:
        message = f"⭐ <b>Ваши цвета ({len(colors)}):</b>\n\n"
        for i, color in enumerate(colors, 1):
            message += f"{i}. <code>{color.hex_code}</code>\n"

    await update.message.reply_text(message, parse_mode='HTML')


async def add_color_to_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE, color: str):
    user = update.effective_user
    container = context.bot_data["container"]
    try:
        ok = await container.add_color.execute(user.id, color)
    except Exception:
        await update.message.reply_text("❌ Неверный формат цвета")
        return

    if ok:
        await update.message.reply_text(f"✅ Цвет {color} добавлен в избранное!")
    else:
        await update.message.reply_text(f"ℹ️ Цвет {color} уже в избранном")


async def start_delete_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    container = context.bot_data["container"]
    colors = await container.list_colors.execute(user.id)

    if not colors:
        await update.message.reply_text("У вас нет сохранённых цветов.")
        return

    message = "Выберите номер цвета для удаления:\n\n"
    for i, color in enumerate(colors, 1):
        message += f"{i}. {color.hex_code}\n"
    message += "\nВведите номер (цифру):"

    await update.message.reply_text(message, reply_markup=get_cancel_keyboard())
    context.user_data["awaiting_color_selection"] = "delete"


async def delete_selected_color(update: Update, context: ContextTypes.DEFAULT_TYPE, color: str):
    user = update.effective_user
    container = context.bot_data["container"]

    ok = await container.remove_color.execute(user.id, color)
    if ok:
        await update.message.reply_text(f"✅ Цвет {color} удалён из избранного.")
    else:
        await update.message.reply_text(f"❌ Не удалось удалить {color}.")

    await show_favorites_menu(update, context)


async def start_update_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    container = context.bot_data["container"]
    colors = await container.list_colors.execute(user.id)

    if not colors:
        await update.message.reply_text("У вас нет сохранённых цветов.")
        return

    message = "Выберите номер цвета для изменения:\n\n"
    for i, color in enumerate(colors, 1):
        message += f"{i}. {color.hex_code}\n"
    message += "\nВведите номер (цифру):"

    await update.message.reply_text(message, reply_markup=get_cancel_keyboard())
    context.user_data["awaiting_color_selection"] = "update"


async def update_selected_color(update: Update, context: ContextTypes.DEFAULT_TYPE, new_hex: str):
    user = update.effective_user
    container = context.bot_data["container"]
    old_hex = context.user_data.get("update_color_old")

    if not old_hex:
        await update.message.reply_text("Ошибка: не выбран цвет для изменения.")
        await show_favorites_menu(update, context)
        return

    try:
        ok = await container.update_color.execute(user.id, old_hex, new_hex)
    except Exception:
        await update.message.reply_text("❌ Неверный формат цвета")
        return

    if ok:
        await update.message.reply_text(f"✅ Цвет {old_hex} изменён на {new_hex}.")
    else:
        await update.message.reply_text(f"❌ Не удалось изменить {old_hex} на {new_hex}.")

    context.user_data.pop("update_color_old", None)
    context.user_data.pop("awaiting_new_color", None)
    await show_favorites_menu(update, context)


async def confirm_clear_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    container = context.bot_data["container"]
    colors = await container.list_colors.execute(user.id)

    if not colors:
        await update.message.reply_text("ℹ️ Ваше избранное уже пустое")
        return

    await update.message.reply_text(
        f"⚠️ Вы уверены, что хотите очистить всё избранное?\n"
        f"Будет удалено {len(colors)} цветов.\n"
        f"Это действие нельзя отменить!",
        reply_markup=get_confirm_keyboard()
    )


async def clear_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    container = context.bot_data["container"]

    ok = await container.clear_colors.execute(user.id)
    if ok:
        await update.message.reply_text("✅ Все избранное очищено!")
    else:
        await update.message.reply_text("❌ Не удалось очистить избранное")

    from .start_help import start
    await start(update, context)