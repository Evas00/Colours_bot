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
    favorites = relationship("Favorite", back_populates="user")
    history = relationship("History", back_populates="user")

# Таблица 2: Цвета
class Color(Base):
    __tablename__ = 'colors'
    
    id = Column(Integer, primary_key=True)
    hex_code = Column(String(7), unique=True)  # Например: #FF5733
    name = Column(String(50))
    source = Column(String(20))  # github или custom
    
    # Связь
    favorites = relationship("Favorite", back_populates="color")

# Таблица 3: Избранное
class Favorite(Base):
    __tablename__ = 'favorites'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    color_id = Column(Integer, ForeignKey('colors.id'))
    added_at = Column(DateTime, default=datetime.now)
    
    # Связи
    user = relationship("User", back_populates="favorites")
    color = relationship("Color", back_populates="favorites")

# Таблица 4: Палитры
class Palette(Base):
    __tablename__ = 'palettes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    colors = Column(String(200))  # Храним цвета через запятую
    source = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)

# Таблица 5: История запросов
class History(Base):
    __tablename__ = 'history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(50))  # Например: 'get_colors', 'get_palette'
    timestamp = Column(DateTime, default=datetime.now)
    
    # Связь
    user = relationship("User", back_populates="history")

# Создаем базу данных
engine = create_engine(f'sqlite:///data/colors.db')
Base.metadata.create_all(engine)

# Для работы с БД
Session = sessionmaker(bind=engine)

class Database:
    """Простой класс для работы с базой данных"""
    
    User = User
    Color = Color
    Favorite = Favorite
    Palette = Palette
    History = History

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
    def log_action(user_id, action):
        """Записываем действие в историю"""
        session = Session()
        try:
            history = History(user_id=user_id, action=action)
            session.add(history)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Ошибка при логировании: {e}")
        finally:
            session.close()
    
    @staticmethod
    def add_favorite(user_id, color_hex):
        """Добавляем цвет в избранное"""
        session = Session()
        try:
            # Ищем цвет
            color = session.query(Color).filter_by(hex_code=color_hex).first()
            if not color:
                # Создаем новый цвет
                color = Color(hex_code=color_hex, source='user')
                session.add(color)
                session.commit()
            
            # Проверяем, нет ли уже в избранном
            existing = session.query(Favorite).filter_by(
                user_id=user_id,
                color_id=color.id
            ).first()
            
            if not existing:
                favorite = Favorite(user_id=user_id, color_id=color.id)
                session.add(favorite)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Ошибка при добавлении в избранное: {e}")
            return False
        finally:
            session.close()
    @staticmethod
    def get_user_favorites(user_id):
        """Получить избранные цвета пользователя"""
        session = Session()
        try:
            favorites = session.query(Favorite).filter_by(user_id=user_id).all()
            colors = []
            for fav in favorites:
                color = session.query(Color).filter_by(id=fav.color_id).first()
                if color:
                    colors.append(color.hex_code)
            return colors
        finally:
            session.close()
    
    @staticmethod
    def get_user_stats(user_id):
        """Получить статистику пользователя"""
        session = Session()
        try:
            fav_count = session.query(Favorite).filter_by(user_id=user_id).count()
            history_count = session.query(History).filter_by(user_id=user_id).count()
            return fav_count, history_count
        finally:
            session.close()