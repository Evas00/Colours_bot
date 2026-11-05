from app.domain.color_provider import ColorProvider
from app.domain.repositories import PaletteRepository, ActionLogger
from app.application.dto import PaletteDTO


class GenerateThemePaletteUseCase:
    """Сценарий: получить палитру по теме и сохранить её."""

    def __init__(self, provider: ColorProvider, palette_repo: PaletteRepository, logger: ActionLogger):
        self._provider = provider
        self._palette_repo = palette_repo
        self._logger = logger

    async def execute(self, user_id: int, theme: str) -> PaletteDTO:
        colors = await self._provider.get_colors_by_theme(theme)
        color_values = [c.value for c in colors]
        
        if colors:
            await self._palette_repo.save_palette(user_id, theme, color_values)
            await self._logger.log(user_id, "generate_palette", f"Палитра для темы {theme}")
            
        return PaletteDTO(colors=color_values, theme=theme)