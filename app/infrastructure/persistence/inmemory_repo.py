from app.domain.repositories import FavoriteColorRepository
from app.domain.entities import FavoriteColor
from app.domain.value_objects import HexCode


class InMemoryFavoriteColorRepository(FavoriteColorRepository):
    """Реализация репозитория в памяти."""

    def __init__(self):
        self._storage: dict[int, dict[str, FavoriteColor]] = {}

    async def add(self, user_id: int, color: HexCode) -> bool:
        user_bucket = self._storage.setdefault(user_id, {})
        if color.value in user_bucket:
            return False
        user_bucket[color.value] = FavoriteColor(hex_code=color)
        return True

    async def remove(self, user_id: int, color: HexCode) -> bool:
        user_bucket = self._storage.get(user_id, {})
        if color.value not in user_bucket:
            return False
        del user_bucket[color.value]
        return True

    async def update(self, user_id: int, old: HexCode, new: HexCode) -> bool:
        user_bucket = self._storage.get(user_id, {})
        if old.value not in user_bucket:
            return False
        entity = user_bucket.pop(old.value)
        entity.hex_code = new
        user_bucket[new.value] = entity
        return True

    async def list_all(self, user_id: int) -> list[FavoriteColor]:
        user_bucket = self._storage.get(user_id, {})
        return list(user_bucket.values())

    async def clear(self, user_id: int) -> bool:
        self._storage[user_id] = {}
        return True