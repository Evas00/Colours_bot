from app.domain.value_objects import HexCode


class AdjustPaletteBrightnessUseCase:
    """Сценарий: изменить яркость цветов."""

    def execute(self, colors: list[str], action: str) -> list[str]:
        result: list[str] = []
        for raw in colors:
            try:
                color = HexCode(raw)
            except Exception:
                result.append(raw)
                continue
            result.append(self._adjust(color, action).value)
        return result

    def _adjust(self, color: HexCode, action: str) -> HexCode:
        value = color.value.lstrip("#")
        r = int(value[0:2], 16)
        g = int(value[2:4], 16)
        b = int(value[4:6], 16)

        if action == "brighter":
            r = min(255, int(r * 1.3))
            g = min(255, int(g * 1.3))
            b = min(255, int(b * 1.3))
        elif action == "darker":
            r = max(0, int(r * 0.7))
            g = max(0, int(g * 0.7))
            b = max(0, int(b * 0.7))

        return HexCode(f"#{r:02X}{g:02X}{b:02X}")