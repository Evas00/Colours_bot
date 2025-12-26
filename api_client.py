import aiohttp
import random
from config import Config

class ColorAPIClient:
    """Клиент для получения цветов"""
    
    @staticmethod
    async def fetch_json(url: str):
        """Получить JSON из URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        return await response.json()
        except:
            return None
    
    @staticmethod
    async def get_github_colors():
        """Получить цвета GitHub"""
        # Получаем данные из API
        data = await ColorAPIClient.fetch_json(Config.GITHUB_COLORS)
        if not data:
            return None
            
        colors = []
        # data.items() возвращает пары (ключ, значение)
        for lang, info in data.items():
            if info and 'color' in info and info['color']:
                color = info['color'].strip()   # Убираем пробелы
                if color.startswith('#') and len(color) == 7:
                    colors.append(color)
            if len(colors) >= Config.MAX_COLORS:
                break
        return colors
    
    @staticmethod
    async def get_palettes():
        """Получить цветовые палитры"""
        data = await ColorAPIClient.fetch_json(Config.COLOR_PALETTES)
        # Проверяем, что данные получены и это список
        if not data or not isinstance(data, list):
            return None
            
        palettes = []
        for palette in data[:Config.MAX_PALETTES]:
            if isinstance(palette, list) and len(palette) >= 5:
                valid_colors = [c for c in palette[:5] if isinstance(c, str) and c.startswith('#')]
                if len(valid_colors) == 5:
                    palettes.append(valid_colors)
        return palettes
    
    @staticmethod
    async def get_random_palette():
        """Получить случайную палитру"""
        # Сначала пробуем получить палитры
        palettes = await ColorAPIClient.get_palettes()
        if palettes:
            return random.choice(palettes)
        
        # Если нет палитр, пробуем получить цвета и собрать из них палитру
        colors = await ColorAPIClient.get_github_colors()
        if colors and len(colors) >= 5:
            return random.sample(colors, 5)
        
        return None