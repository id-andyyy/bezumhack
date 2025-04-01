from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String, unique=True)
    title = Column(String)
    photo = Column(String)
    description = Column(String)
    price = Column(Float)
    plashka = Column(String)
    card_number = Column(String(16))
    card_expiry = Column(Date)
    card_cvv = Column(String(3))
    card_pin = Column(String(4))
