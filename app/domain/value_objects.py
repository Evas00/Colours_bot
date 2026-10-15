import re


class DomainError(Exception):
    """Базовая ошибка предметной области."""
    pass


class InvalidHexError(DomainError):
    """Ошибка: невалидный HEX-цвет."""
    pass


class HexCode:
    """Value Object: валидный HEX-цвет вида #RRGGBB."""
    
    # Регулярка проверяет: решётка + 6 символов от 0 до F
    _PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")
    
    def __init__(self, value: str):
        # Приводим к верхнему регистру (#ff5733 -> #FF5733)
        normalized = value.strip().upper()
        
        # Проверяем формат — если не подходит, ошибка
        if not self._PATTERN.match(normalized):
            raise InvalidHexError(f"Невалидный HEX-цвет: {value}")
        
        self._value = normalized
    
    @property
    def value(self) -> str:
        """Возвращает строку цвета."""
        return self._value
    
    def __eq__(self, other):
        return isinstance(other, HexCode) and self._value == other._value
    
    def __str__(self):
        return self._value