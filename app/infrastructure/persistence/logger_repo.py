from app.domain.repositories import ActionLogger, PaletteRepository
from .models import Session, ActionLog, Palette, PaletteColor


class SqliteActionLogger(ActionLogger):
    """Реализация логгера через SQLite."""
    
    async def log(self, user_id: int, action_type: str, details: str) -> None:
        session = Session()
        try:
            log_entry = ActionLog(user_id=user_id, action_type=action_type, details=details)
            session.add(log_entry)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Ошибка логирования: {e}")
        finally:
            session.close()


class SqlitePaletteRepository(PaletteRepository):
    """Реализация репозитория палитр через SQLite."""
    
    async def save_palette(self, user_id: int, theme: str, colors: list[str]) -> bool:
        session = Session()
        try:
            palette = Palette(user_id=user_id, theme=theme)
            session.add(palette)
            session.flush()
            
            for hex_code in colors:
                session.add(PaletteColor(palette_id=palette.id, hex_code=hex_code))
                
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Ошибка сохранения палитры: {e}")
            return False
        finally:
            session.close()