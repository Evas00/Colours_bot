from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os

os.makedirs('data', exist_ok=True)

Base = declarative_base()

# 1. Пользователи
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String(50))
    first_name = Column(String(50))
    joined_at = Column(DateTime, default=datetime.now)
    
    favorite_colors = relationship("FavoriteColor", back_populates="user", cascade="all, delete-orphan")
    palettes = relationship("Palette", back_populates="user", cascade="all, delete-orphan")

# 2. Избранные цвета
class FavoriteColor(Base):
    __tablename__ = 'favorite_colors'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    hex_code = Column(String(7))
    added_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="favorite_colors")

# 3. Палитры
class Palette(Base):
    __tablename__ = 'palettes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    theme = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="palettes")
    colors = relationship("PaletteColor", back_populates="palette", cascade="all, delete-orphan")

# 4. Цвета внутри палитры
class PaletteColor(Base):
    __tablename__ = 'palette_colors'
    id = Column(Integer, primary_key=True)
    palette_id = Column(Integer, ForeignKey('palettes.id'), index=True)
    hex_code = Column(String(7))
    
    palette = relationship("Palette", back_populates="colors")

# 5. Журнал действий (для генерации больших данных)
class ActionLog(Base):
    __tablename__ = 'action_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    action_type = Column(String(50))
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)

# Создание движка
engine = create_engine('sqlite:///data/colors.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)