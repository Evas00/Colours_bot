import os
from dotenv import load_dotenv

load_dotenv()   # Загружает переменные из .env файла в окружение ОС

# Класс для хранения конфигурации бота
class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    GITHUB_COLORS = 'https://cdn.jsdelivr.net/gh/ozh/github-colors@master/colors.json'
    COLOR_PALETTES = 'https://cdn.jsdelivr.net/gh/Jam3/nice-color-palettes@master/100.json'
    
    MAX_COLORS = 15
    MAX_PALETTES = 3

    DB_PATH = 'data/colors.db'