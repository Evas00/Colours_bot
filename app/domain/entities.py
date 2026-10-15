from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional #либо значение указанного типа, либо None
from .value_objects import HexCode


@dataclass
class FavoriteColor:
    """Сущность: избранный цвет пользователя."""
    hex_code: HexCode
    added_at: datetime = field(default_factory=datetime.now)


@dataclass
class User:
    """Сущность: пользователь бота."""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    joined_at: datetime = field(default_factory=datetime.now)