from app.infrastructure.persistence.sqlite_repo import SqliteFavoriteColorRepository
from app.infrastructure.persistence.logger_repo import SqliteActionLogger, SqlitePaletteRepository
from app.infrastructure.color_api.colormind_provider import ColormindProvider

from app.application.add_favorite_color import AddFavoriteColorUseCase
from app.application.remove_favorite_color import RemoveFavoriteColorUseCase
from app.application.update_favorite_color import UpdateFavoriteColorUseCase
from app.application.list_favorite_colors import ListFavoriteColorsUseCase
from app.application.clear_favorite_colors import ClearFavoriteColorsUseCase
from app.application.generate_theme_palette import GenerateThemePaletteUseCase
from app.application.adjust_palette_brightness import AdjustPaletteBrightnessUseCase


class Container:
    """Собирает все зависимости вместе."""

    def __init__(self):
        # Реализации портов
        self.color_repo = SqliteFavoriteColorRepository()
        self.logger_repo = SqliteActionLogger()
        self.palette_repo = SqlitePaletteRepository()
        self.color_provider = ColormindProvider()

        # Сценарии (Use Cases)
        self.add_color = AddFavoriteColorUseCase(self.color_repo, self.logger_repo)
        self.remove_color = RemoveFavoriteColorUseCase(self.color_repo)
        self.update_color = UpdateFavoriteColorUseCase(self.color_repo)
        self.list_colors = ListFavoriteColorsUseCase(self.color_repo)
        self.clear_colors = ClearFavoriteColorsUseCase(self.color_repo)
        self.generate_palette = GenerateThemePaletteUseCase(
            self.color_provider, 
            self.palette_repo, 
            self.logger_repo
        )
        self.adjust_brightness = AdjustPaletteBrightnessUseCase()