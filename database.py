from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os

os.makedirs('data', exist_ok=True)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String(50))
    first_name = Column(String(50))
    joined_at = Column(DateTime, default=datetime.now)
    favorite_colors = relationship("FavoriteColor", back_populates="user", cascade="all, delete-orphan")
    favorite_palettes = relationship("FavoritePalette", back_populates="user", cascade="all, delete-orphan")

class FavoriteColor(Base):
    __tablename__ = 'favorite_colors'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    hex_code = Column(String(7))
    added_at = Column(DateTime, default=datetime.now)
    user = relationship("User", back_populates="favorite_colors")

class FavoritePalette(Base):
    __tablename__ = 'favorite_palettes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    palette_name = Column(String(100))
    colors = Column(String(500))
    added_at = Column(DateTime, default=datetime.now)
    user = relationship("User", back_populates="favorite_palettes")

engine = create_engine('sqlite:///data/colors.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class Database:
    @staticmethod
    def get_session():
        return Session()
    
    @staticmethod
    def add_user(telegram_id, username, first_name):
        session = Session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                user = User(telegram_id=telegram_id, username=username, first_name=first_name)
                session.add(user)
                session.commit()
            return user
        except Exception as e:
            session.rollback()
            print(f"Ошибка при добавлении пользователя: {e}")
            return None
        finally:
            session.close()
    
    @staticmethod
    def add_favorite_color(user_id, color_hex):
        session = Session()
        try:
            existing = session.query(FavoriteColor).filter_by(user_id=user_id, hex_code=color_hex.upper()).first()
            if not existing:
                favorite = FavoriteColor(user_id=user_id, hex_code=color_hex.upper())
                session.add(favorite)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Ошибка при добавлении цвета: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def get_user_favorite_colors(user_id):
        session = Session()
        try:
            favorites = session.query(FavoriteColor).filter_by(user_id=user_id).order_by(FavoriteColor.added_at.desc()).all()
            return [fav.hex_code for fav in favorites]
        finally:
            session.close()
    
    @staticmethod
    def delete_favorite_color(user_id, hex_code):
        session = Session()
        try:
            deleted = session.query(FavoriteColor).filter_by(
                user_id=user_id, hex_code=hex_code.upper()
            ).delete()
            session.commit()
            return deleted > 0
        except Exception as e:
            session.rollback()
            print(f"Ошибка при удалении цвета: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def update_favorite_color(user_id, old_hex, new_hex):
        session = Session()
        try:
            color = session.query(FavoriteColor).filter_by(user_id=user_id, hex_code=old_hex.upper()).first()
            if color:
                color.hex_code = new_hex.upper()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Ошибка при обновлении цвета: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def clear_user_favorites(user_id):
        session = Session()
        try:
            session.query(FavoriteColor).filter_by(user_id=user_id).delete()
            session.query(FavoritePalette).filter_by(user_id=user_id).delete()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Ошибка при очистке избранного: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def get_user_stats(user_id):
        session = Session()
        try:
            color_count = session.query(FavoriteColor).filter_by(user_id=user_id).count()
            palette_count = session.query(FavoritePalette).filter_by(user_id=user_id).count()
            return color_count, palette_count
        finally:
            session.close()