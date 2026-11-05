from abc import ABC, abstractmethod
from typing import List
from .entities import FavoriteColor
from .value_objects import HexCode


class FavoriteColorRepository(ABC):
    """Порт: как хранить любимые цвета."""
    
    @abstractmethod
    async def add(self, user_id: int, color: HexCode) -> bool:
        pass
    
    @abstractmethod
    async def remove(self, user_id: int, color: HexCode) -> bool:
        pass
    
    @abstractmethod
    async def update(self, user_id: int, old: HexCode, new: HexCode) -> bool:
        pass
    
    @abstractmethod
    async def list_all(self, user_id: int) -> List[FavoriteColor]:
        pass
    
    @abstractmethod
    async def clear(self, user_id: int) -> bool:
        pass


class ActionLogger(ABC):
    """Порт: для записи действий пользователя (для генерации нагрузки)."""
    
    @abstractmethod
    async def log(self, user_id: int, action_type: str, details: str) -> None:
        pass


class PaletteRepository(ABC):
    """Порт: для сохранения сгенерированных палитр."""
    
    @abstractmethod
    async def save_palette(self, user_id: int, theme: str, colors: list[str]) -> bool:
        pass