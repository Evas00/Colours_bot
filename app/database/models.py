# app/database/models.py
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

# Создание движка и таблиц
engine = create_engine('sqlite:///data/colors.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)