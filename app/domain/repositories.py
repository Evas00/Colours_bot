from abc import ABC, abstractmethod
from typing import List
from .entities import FavoriteColor
from .value_objects import HexCode


class FavoriteColorRepository(ABC):
    """Порт: как хранить любимые цвета. Реализация — снаружи."""
    
    @abstractmethod
    async def add(self, user_id: int, color: HexCode) -> bool:
        """Добавить цвет. True — если добавили, False — если уже есть."""
        pass
    
    @abstractmethod
    async def remove(self, user_id: int, color: HexCode) -> bool:
        """Удалить цвет. True — если удалили, False — если не было."""
        pass
    
    @abstractmethod
    async def update(self, user_id: int, old: HexCode, new: HexCode) -> bool:
        """Заменить цвет. True — если заменили."""
        pass
    
    @abstractmethod
    async def list_all(self, user_id: int) -> List[FavoriteColor]:
        """Получить все цвета пользователя."""
        pass
    
    @abstractmethod
    async def clear(self, user_id: int) -> bool:
        """Удалить все цвета пользователя."""
        pass