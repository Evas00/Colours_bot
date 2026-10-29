import pytest
from app.application.add_favorite_color import AddFavoriteColorUseCase
from app.domain.repositories import FavoriteColorRepository
from app.domain.entities import FavoriteColor

# Создаем фейковый репозиторий (имитация базы данных в памяти)
class FakeRepo(FavoriteColorRepository):
    def __init__(self):
        self.data = {}

    async def add(self, user_id, color):
        self.data[color.value] = FavoriteColor(hex_code=color)
        return True

    async def remove(self, user_id, color):
        return True

    async def update(self, user_id, old, new):
        return True

    async def list_all(self, user_id):
        return list(self.data.values())

    async def clear(self, user_id):
        return True

@pytest.mark.asyncio
async def test_add_color_use_case():
    """Проверяем, что сценарий добавления работает с фейковой базой."""
    repo = FakeRepo()
    use_case = AddFavoriteColorUseCase(repo)
    
    # Вызываем сценарий
    result = await use_case.execute(1, "#FF5733")
    
    # Проверяем результат
    assert result is True
    assert len(await repo.list_all(1)) == 1