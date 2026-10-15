from app.domain.repositories import FavoriteColorRepository
from app.application.dto import ColorDTO


class ListFavoriteColorsUseCase:
    """Сценарий: получить список избранных цветов."""

    def __init__(self, repo: FavoriteColorRepository):
        self._repo = repo

    async def execute(self, user_id: int) -> list[ColorDTO]:
        entities = await self._repo.list_all(user_id)
        return [
            ColorDTO(hex_code=e.hex_code.value, added_at=e.added_at)
            for e in entities
        ]