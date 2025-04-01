from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=True, index=True)
    password = Column(String, nullable=True)
    admin = Column(String, default='Дима Иблан', nullable=True)
    credit_card = Column(String, nullable=True)
    is_product = Column(Integer, default=0)
    name = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, nullable=True)
    secret_info = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    gif_base64 = Column(Text, nullable=True)
    
class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("users.id"))
    messages = Column(Text, default="[]")  # JSON-строка с историей сообщений
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)