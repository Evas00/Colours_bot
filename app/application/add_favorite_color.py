from app.domain.value_objects import HexCode
from app.domain.repositories import FavoriteColorRepository, ActionLogger


class AddFavoriteColorUseCase:
    """Сценарий: добавить цвет в избранное."""

    def __init__(self, repo: FavoriteColorRepository, logger: ActionLogger):
        self._repo = repo
        self._logger = logger

    async def execute(self, user_id: int, hex_str: str) -> bool:
        color = HexCode(hex_str)
        success = await self._repo.add(user_id, color)
        
        if success:
            await self._logger.log(user_id, "add_color", f"Добавлен цвет {color.value}")
            
        return success