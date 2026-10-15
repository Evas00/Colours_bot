from dataclasses import dataclass
from datetime import datetime


@dataclass
class ColorDTO:
    """Цвет для передачи наружу."""
    hex_code: str
    added_at: datetime


@dataclass
class PaletteDTO:
    """Палитра для передачи наружу."""
    colors: list[str]
    theme: str | None = None