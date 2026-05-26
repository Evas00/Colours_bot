# app/handlers/common.py
from telegram import ReplyKeyboardMarkup

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

def get_main_keyboard():
    return ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)

def get_colors_keyboard():
    return ReplyKeyboardMarkup(COLORS_KEYBOARD, resize_keyboard=True)

def get_favorites_keyboard():
    return ReplyKeyboardMarkup(FAVORITES_KEYBOARD, resize_keyboard=True)

def get_confirm_keyboard():
    return ReplyKeyboardMarkup(CONFIRM_KEYBOARD, resize_keyboard=True)

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(CANCEL_KEYBOARD, resize_keyboard=True)