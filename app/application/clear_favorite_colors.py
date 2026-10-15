from app.domain.repositories import FavoriteColorRepository


class ClearFavoriteColorsUseCase:
    """Сценарий: удалить все избранные цвета."""

    def __init__(self, repo: FavoriteColorRepository):
        self._repo = repo

    async def execute(self, user_id: int) -> bool:
        return await self._repo.clear(user_id)