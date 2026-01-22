import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Работающие API
    COLORMIND_API = 'http://colormind.io/api/'
    COLOR_PALETTES_API = 'https://cdn.jsdelivr.net/gh/Jam3/nice-color-palettes@master/100.json'
    
    # Тематики (только названия для отображения)
    THEMES = ["education", "bank_finance", "games", "health", 
              "food", "technology", "fashion", "nature"]
    
    # Описания для пользователя
    THEME_DESCRIPTIONS = {
        "education": "🎓 Образование",
        "bank_finance": "🏦 Банк/Финансы", 
        "games": "🎮 Игры",
        "health": "🏥 Здоровье",
        "food": "🍕 Еда",
        "technology": "💻 Технологии",
        "fashion": "👗 Мода",
        "nature": "🌿 Природа"
    }
    
    DB_PATH = 'data/colors.db'