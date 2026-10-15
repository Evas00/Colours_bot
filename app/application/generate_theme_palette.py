from app.domain.color_provider import ColorProvider
from app.application.dto import PaletteDTO


class GenerateThemePaletteUseCase:
    """Сценарий: получить палитру по теме."""

    def __init__(self, provider: ColorProvider):
        self._provider = provider

    async def execute(self, theme: str) -> PaletteDTO:
        colors = await self._provider.get_colors_by_theme(theme)
        return PaletteDTO(
            colors=[c.value for c in colors],
            theme=theme,
        )