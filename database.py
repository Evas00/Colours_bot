from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os

# Создаем папку для базы данных
os.makedirs('data', exist_ok=True)

Base = declarative_base()

# Таблица 1: Пользователи
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String(50))
    first_name = Column(String(50))
    joined_at = Column(DateTime, default=datetime.now)
    
    # Связь с другими таблицами
    favorite_colors = relationship("FavoriteColor", back_populates="user", cascade="all, delete-orphan")
    favorite_palettes = relationship("FavoritePalette", back_populates="user", cascade="all, delete-orphan")

# Таблица 2: Избранные цвета
class FavoriteColor(Base):
    __tablename__ = 'favorite_colors'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    hex_code = Column(String(7))  # Например: #FF5733
    added_at = Column(DateTime, default=datetime.now)
    
    # Связь
    user = relationship("User", back_populates="favorite_colors")

# Таблица 3: Избранные палитры (пока не используется, но оставим)
class FavoritePalette(Base):
    __tablename__ = 'favorite_palettes'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    palette_name = Column(String(100))
    colors = Column(String(500))  # Храним цвета через запятую
    added_at = Column(DateTime, default=datetime.now)
    
    # Связь
    user = relationship("User", back_populates="favorite_palettes")

# Создаем базу данных
engine = create_engine(f'sqlite:///data/colors.db')
Base.metadata.create_all(engine)

# Для работы с БД
Session = sessionmaker(bind=engine)

class Database:
    """Класс для работы с базой данных"""
    
    @staticmethod
    def get_session():
        return Session()
    
    @staticmethod
    def add_user(telegram_id, username, first_name):
        """Добавляем пользователя в БД"""
        session = Session()
        try:
            # Проверяем, есть ли уже такой пользователь
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name
                )
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
        """Добавляем цвет в избранное"""
        session = Session()
        try:
            # Проверяем, нет ли уже такого цвета у пользователя
            existing = session.query(FavoriteColor).filter_by(
                user_id=user_id,
                hex_code=color_hex.upper()
            ).first()
            
            if not existing:
                favorite = FavoriteColor(user_id=user_id, hex_code=color_hex.upper())
                session.add(favorite)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Ошибка при добавлении цвета в избранное: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def get_user_favorite_colors(user_id):
        """Получить избранные цвета пользователя"""
        session = Session()
        try:
            favorites = session.query(FavoriteColor).filter_by(user_id=user_id).order_by(FavoriteColor.added_at.desc()).all()
            return [fav.hex_code for fav in favorites]
        finally:
            session.close()
    
    @staticmethod
    def clear_user_favorites(user_id):
        """Очистить все избранное пользователя"""
        session = Session()
        try:
            # Удаляем цвета
            session.query(FavoriteColor).filter_by(user_id=user_id).delete()
            # Удаляем палитры
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
        """Получить статистику пользователя"""
        session = Session()
        try:
            color_count = session.query(FavoriteColor).filter_by(user_id=user_id).count()
            palette_count = session.query(FavoritePalette).filter_by(user_id=user_id).count()
            return color_count, palette_count
        finally:
            session.close()