from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from .common import get_colors_keyboard, get_main_keyboard


async def select_theme(update: Update, context: ContextTypes.DEFAULT_TYPE, theme: str):
    container = context.bot_data["container"]
    theme_desc = Config.THEME_DESCRIPTIONS.get(theme, theme)

    await update.message.reply_text(f"🔄 Получаю цвета для {theme_desc}...")

    palette = await container.generate_palette.execute(theme)

    if not palette.colors:
        await update.message.reply_text(
            f"❌ Не удалось получить цвета для {theme_desc}\nПопробуйте позже.",
            reply_markup=get_main_keyboard()
        )
        return

    context.user_data['current_theme'] = theme
    context.user_data['current_colors'] = palette.colors
    context.user_data['theme_desc'] = theme_desc

    message = f"🎨 <b>Цвета для {theme_desc}:</b>\n\n"
    for i, color in enumerate(palette.colors, 1):
        message += f"{i}. <code>{color}</code>\n"
    message += "\nВыберите действие:"

    await update.message.reply_text(
        message,
        reply_markup=get_colors_keyboard(),
        parse_mode='HTML'
    )


async def adjust_colors(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
    if 'current_colors' not in context.user_data:
        await update.message.reply_text("Сначала выберите тематику!")
        return

    container = context.bot_data["container"]
    colors = context.user_data['current_colors']
    action_text = "ярче" if action == "brighter" else "темнее"

    await update.message.reply_text(f"🔄 Делаю цвета {action_text}...")

    adjusted = container.adjust_brightness.execute(colors, action)
    context.user_data['current_colors'] = adjusted

    theme_desc = context.user_data.get('theme_desc', 'темы')
    message = f"🎨 <b>Цвета для {theme_desc} ({action_text}):</b>\n\n"
    for i, color in enumerate(adjusted, 1):
        message += f"{i}. <code>{color}</code>\n"
    message += "\nВыберите действие:"

    await update.message.reply_text(
        message,
        reply_markup=get_colors_keyboard(),
        parse_mode='HTML'
    )


async def save_all_colors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'current_colors' not in context.user_data:
        await update.message.reply_text("Сначала выберите тематику!")
        return

    container = context.bot_data["container"]
    colors = context.user_data['current_colors']
    user = update.effective_user

    saved = 0
    for color in colors:
        try:
            if await container.add_color.execute(user.id, color):
                saved += 1
        except Exception:
            continue

    if saved > 0:
        await update.message.reply_text(f"✅ Сохранено {saved} цветов в избранное!")
    else:
        await update.message.reply_text("ℹ️ Все цвета уже были в избранном")