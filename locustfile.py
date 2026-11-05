import random
import asyncio
from locust import HttpUser, task, between
from app.container import Container
from app.infrastructure.persistence.models import Session, User as DBUser

class ColorsBotUser(HttpUser):
    # Ставим минимальную паузу, чтобы нагрузка шла быстрее
    wait_time = between(0.01, 0.1)

    def on_start(self):
        # Инициализируем контейнер
        self.container = Container()
        
        # Получаем случайного пользователя из нашей огромной базы (2 ГБ)
        session = Session()
        try:
            user = session.query(DBUser).order_by(DBUser.id.desc()).first()
            self.user_id = user.id if user else 1
        finally:
            session.close()

    def _run_async(self, coro):
        """Вспомогательная функция для запуска асинхронного кода."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    @task(8) # Сценарий S1 (Чтение) - 80%
    def read_colors(self):
        with self.client.get("/read", catch_response=True) as response:
            self._run_async(self.container.list_colors.execute(self.user_id))
            response.success()
        
    @task(2) # Сценарий S2 (Запись) - 20%
    def write_color(self):
        hex_code = f"#{random.randint(0, 0xFFFFFF):06x}"
        with self.client.post("/write", catch_response=True) as response:
            self._run_async(self.container.add_color.execute(self.user_id, hex_code))
            response.success()