from app.domain.value_objects import HexCode
from app.domain.repositories import FavoriteColorRepository


class RemoveFavoriteColorUseCase:
    """Сценарий: удалить цвет из избранного."""

    def __init__(self, repo: FavoriteColorRepository):
        self._repo = repo

    async def execute(self, user_id: int, hex_str: str) -> bool:
        color = HexCode(hex_str)
        return await self._repo.remove(user_id, color)