from app.domain.value_objects import HexCode
from app.domain.repositories import FavoriteColorRepository


class UpdateFavoriteColorUseCase:
    """Сценарий: заменить один цвет на другой."""

    def __init__(self, repo: FavoriteColorRepository):
        self._repo = repo

    async def execute(self, user_id: int, old_hex: str, new_hex: str) -> bool:
        old_color = HexCode(old_hex)
        new_color = HexCode(new_hex)
        return await self._repo.update(user_id, old_color, new_color)