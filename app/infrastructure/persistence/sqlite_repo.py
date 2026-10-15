from app.domain.repositories import FavoriteColorRepository
from app.domain.entities import FavoriteColor
from app.domain.value_objects import HexCode
from .models import Session, FavoriteColor as FavoriteColorModel


class SqliteFavoriteColorRepository(FavoriteColorRepository):
    """Реализация репозитория через SQLite."""

    async def add(self, user_id: int, color: HexCode) -> bool:
        session = Session()
        try:
            existing = session.query(FavoriteColorModel).filter_by(
                user_id=user_id, hex_code=color.value
            ).first()
            if existing:
                return False
            session.add(FavoriteColorModel(user_id=user_id, hex_code=color.value))
            session.commit()
            return True
        finally:
            session.close()

    async def remove(self, user_id: int, color: HexCode) -> bool:
        session = Session()
        try:
            deleted = session.query(FavoriteColorModel).filter_by(
                user_id=user_id, hex_code=color.value
            ).delete()
            session.commit()
            return deleted > 0
        finally:
            session.close()

    async def update(self, user_id: int, old: HexCode, new: HexCode) -> bool:
        session = Session()
        try:
            record = session.query(FavoriteColorModel).filter_by(
                user_id=user_id, hex_code=old.value
            ).first()
            if not record:
                return False
            record.hex_code = new.value
            session.commit()
            return True
        finally:
            session.close()

    async def list_all(self, user_id: int) -> list[FavoriteColor]:
        session = Session()
        try:
            rows = session.query(FavoriteColorModel).filter_by(
                user_id=user_id
            ).order_by(FavoriteColorModel.added_at.desc()).all()
            return [
                FavoriteColor(hex_code=HexCode(row.hex_code), added_at=row.added_at)
                for row in rows
            ]
        finally:
            session.close()

    async def clear(self, user_id: int) -> bool:
        session = Session()
        try:
            session.query(FavoriteColorModel).filter_by(user_id=user_id).delete()
            session.commit()
            return True
        finally:
            session.close()