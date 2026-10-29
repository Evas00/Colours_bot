import pytest
from app.domain.value_objects import HexCode, InvalidHexError

def test_valid_hex():
    """Проверяем, что валидный HEX создается и нормализуется."""
    color = HexCode("#ff5733")
    assert color.value == "#FF5733"

def test_invalid_hex():
    """Проверяем, что невалидный HEX выбрасывает ошибку."""
    with pytest.raises(InvalidHexError):
        HexCode("#ABC")

def test_hex_comparison():
    """Проверяем, что цвета сравниваются по значению."""
    assert HexCode("#FF5733") == HexCode("#ff5733")
    assert HexCode("#FF5733") != HexCode("#000000")