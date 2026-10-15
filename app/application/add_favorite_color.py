from app.domain.value_objects import HexCode
from app.domain.repositories import FavoriteColorRepository


class AddFavoriteColorUseCase:
    """Сценарий: добавить цвет в избранное."""

    def __init__(self, repo: FavoriteColorRepository):
        self._repo = repo

    async def execute(self, user_id: int, hex_str: str) -> bool:
        color = HexCode(hex_str)
        return await self._repo.add(user_id, color)