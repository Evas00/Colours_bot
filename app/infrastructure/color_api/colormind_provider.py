import aiohttp
import json
from config import Config
from app.domain.color_provider import ColorProvider
from app.domain.value_objects import HexCode


class ColormindProvider(ColorProvider):
    """Реализация ColorProvider через внешние API."""

    _palettes_cache = None

    async def get_colors_by_theme(self, theme: str) -> list[HexCode]:
        raw = await self._get_raw_colors(theme)
        result: list[HexCode] = []
        for item in raw:
            try:
                result.append(HexCode(item))
            except Exception:
                continue
        return result

    async def _get_raw_colors(self, theme: str) -> list[str]:
        if theme not in Config.THEMES:
            return []

        all_colors: list[str] = []

        colors = await self._get_random_palette_from_colormind()
        if colors:
            all_colors = colors

        if not all_colors:
            palettes = await self._get_color_palettes()
            if palettes:
                palette_index = Config.THEMES.index(theme) % len(palettes)
                palette = palettes[palette_index]
                if isinstance(palette, list):
                    all_colors = [
                        c for c in palette[:5]
                        if isinstance(c, str) and c.startswith("#")
                    ]

        if not all_colors:
            all_colors = self._get_local_theme_colors(theme)

        unique: list[str] = []
        for color in all_colors:
            if color and color not in unique:
                unique.append(color)

        return unique[:5]

    async def _fetch_json(self, url: str, method: str = "GET", data: dict = None):
        try:
            async with aiohttp.ClientSession() as session:
                if method == "POST":
                    async with session.post(url, json=data, timeout=10) as response:
                        if response.status == 200:
                            try:
                                return await response.json()
                            except Exception:
                                text = await response.text()
                                try:
                                    return json.loads(text)
                                except Exception:
                                    return None
                else:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            try:
                                return await response.json()
                            except Exception:
                                text = await response.text()
                                try:
                                    return json.loads(text)
                                except Exception:
                                    return None
        except Exception as e:
            print(f"API Error {url}: {type(e).__name__}")
            return None

    async def _get_random_palette_from_colormind(self) -> list[str] | None:
        try:
            data = {"model": "default"}
            response = await self._fetch_json(
                Config.COLORMIND_API, method="POST", data=data
            )
            if response and "result" in response:
                colors = []
                for rgb in response["result"][:5]:
                    if len(rgb) == 3:
                        hex_color = f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
                        colors.append(hex_color)
                return colors
        except Exception as e:
            print(f"Colormind API error: {e}")
        return None

    async def _get_color_palettes(self):
        if ColormindProvider._palettes_cache is None:
            data = await self._fetch_json(Config.COLOR_PALETTES_API)
            if data and isinstance(data, list):
                ColormindProvider._palettes_cache = data
                return data
            return None
        return ColormindProvider._palettes_cache

    def _get_local_theme_colors(self, theme: str) -> list[str]:
        theme_palettes = {
            "education": ["#1E3A8A", "#3B82F6", "#10B981", "#6B7280", "#FFFFFF"],
            "bank_finance": ["#1E40AF", "#2563EB", "#059669", "#F59E0B", "#111827"],
            "games": ["#3B82F6", "#EF4444", "#F59E0B", "#8B5CF6", "#EC4899"],
            "health": ["#0EA5E9", "#10B981", "#FFFFFF", "#06B6D4", "#84CC16"],
            "food": ["#DC2626", "#EA580C", "#16A34A", "#A16207", "#B91C1C"],
            "technology": ["#1E40AF", "#1F2937", "#6B7280", "#8B5CF6", "#06B6D4"],
            "fashion": ["#EC4899", "#000000", "#FFFFFF", "#F59E0B", "#8B5CF6"],
            "nature": ["#15803D", "#A16207", "#0EA5E9", "#D97706", "#65A30D"],
        }
        return theme_palettes.get(theme, ["#3B82F6", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6"])