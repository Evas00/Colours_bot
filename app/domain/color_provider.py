from abc import ABC, abstractmethod
from typing import List
from .value_objects import HexCode


class ColorProvider(ABC):
    """Порт: откуда брать цвета по теме."""
    
    @abstractmethod
    async def get_colors_by_theme(self, theme: str) -> List[HexCode]:
        """Получить список цветов для темы."""
        pass