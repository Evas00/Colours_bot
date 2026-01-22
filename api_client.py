import aiohttp
import random
import json
from config import Config

class ColorAPIClient:
    """Клиент для получения цветов из работающих API"""
    
    # Кэш для палитр
    _palettes_cache = None
    
    @staticmethod
    async def fetch_json(url: str, method: str = "GET", data: dict = None):
        """Получить JSON из URL"""
        try:
            async with aiohttp.ClientSession() as session:
                if method == "POST":
                    async with session.post(url, json=data, timeout=10) as response:
                        if response.status == 200:
                            try:
                                return await response.json()
                            except:
                                # Пробуем спарсить как JSON даже если content-type не правильный
                                text = await response.text()
                                try:
                                    return json.loads(text)
                                except:
                                    return {"error": "Invalid JSON", "text": text[:100]}
                else:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            try:
                                return await response.json()
                            except:
                                text = await response.text()
                                try:
                                    return json.loads(text)
                                except:
                                    return {"error": "Invalid JSON", "text": text[:100]}
        except Exception as e:
            print(f"API Error {url}: {type(e).__name__}")
            return None
    
    @staticmethod
    async def get_random_palette_from_colormind():
        """Получить случайную палитру из Colormind (работает!)"""
        try:
            data = {"model": "default"}
            response = await ColorAPIClient.fetch_json(
                Config.COLORMIND_API, 
                method="POST", 
                data=data
            )
            
            if response and 'result' in response:
                colors = []
                for rgb in response['result'][:5]:  # Берем первые 5 цветов
                    if len(rgb) == 3:
                        hex_color = f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
                        colors.append(hex_color)
                return colors
        except Exception as e:
            print(f"Colormind API error: {e}")
        
        return None
    
    @staticmethod
    async def get_color_palettes():
        """Получить цветовые палитры (работает!)"""
        if ColorAPIClient._palettes_cache is None:
            data = await ColorAPIClient.fetch_json(Config.COLOR_PALETTES_API)
            if data and isinstance(data, list):
                ColorAPIClient._palettes_cache = data
                return data
            return None
        return ColorAPIClient._palettes_cache
    
    @staticmethod
    async def get_colors_by_theme(theme: str):
        """Получить цвета по тематике"""
        if theme not in Config.THEMES:
            return None
        
        all_colors = []
        
        # Метод 1: Пробуем Colormind API (работает!)
        colors = await ColorAPIClient.get_random_palette_from_colormind()
        if colors:
            all_colors = colors
        
        # Метод 2: Если Colormind не работает, берем из палитр
        if not all_colors:
            palettes = await ColorAPIClient.get_color_palettes()
            if palettes:
                # Выбираем палитру в зависимости от темы
                palette_index = Config.THEMES.index(theme) % len(palettes)
                palette = palettes[palette_index]
                if isinstance(palette, list):
                    all_colors = [color for color in palette[:5] if isinstance(color, str) and color.startswith('#')]
        
        # Метод 3: Локальные цвета как последний вариант
        if not all_colors:
            all_colors = ColorAPIClient.get_local_theme_colors(theme)
        
        # Убираем дубликаты и возвращаем до 5 цветов
        unique_colors = []
        for color in all_colors:
            if color and color not in unique_colors:
                unique_colors.append(color)
        
        return unique_colors[:5]
    
    @staticmethod
    def get_local_theme_colors(theme: str):
        """Локальные цвета для тем"""
        theme_palettes = {
            "education": ["#1E3A8A", "#3B82F6", "#10B981", "#6B7280", "#FFFFFF"],
            "bank_finance": ["#1E40AF", "#2563EB", "#059669", "#F59E0B", "#111827"],
            "games": ["#3B82F6", "#EF4444", "#F59E0B", "#8B5CF6", "#EC4899"],
            "health": ["#0EA5E9", "#10B981", "#FFFFFF", "#06B6D4", "#84CC16"],
            "food": ["#DC2626", "#EA580C", "#16A34A", "#A16207", "#B91C1C"],
            "technology": ["#1E40AF", "#1F2937", "#6B7280", "#8B5CF6", "#06B6D4"],
            "fashion": ["#EC4899", "#000000", "#FFFFFF", "#F59E0B", "#8B5CF6"],
            "nature": ["#15803D", "#A16207", "#0EA5E9", "#D97706", "#65A30D"]
        }
        
        return theme_palettes.get(theme, ["#3B82F6", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6"])
    
    @staticmethod
    def adjust_colors(colors: list, action: str):
        """Изменить яркость цветов"""
        if not colors:
            return colors
        
        adjusted = []
        
        for hex_color in colors:
            if not hex_color or not hex_color.startswith('#'):
                adjusted.append(hex_color)
                continue
            
            try:
                # Конвертируем HEX в RGB
                hex_clean = hex_color.lstrip('#')
                r = int(hex_clean[0:2], 16)
                g = int(hex_clean[2:4], 16)
                b = int(hex_clean[4:6], 16)
                
                # Меняем яркость
                if action == "brighter":
                    r = min(255, int(r * 1.3))
                    g = min(255, int(g * 1.3))
                    b = min(255, int(b * 1.3))
                elif action == "darker":
                    r = max(0, int(r * 0.7))
                    g = max(0, int(g * 0.7))
                    b = max(0, int(b * 0.7))
                
                # Обратно в HEX
                new_hex = f"#{r:02X}{g:02X}{b:02X}"
                adjusted.append(new_hex)
            except:
                adjusted.append(hex_color)
        
        return adjusted