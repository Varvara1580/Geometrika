from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.Models import Base

DATABASE_URL = 'sqlite:///task.db'

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind = engine)


def get_db():
    with SessionLocal() as db:
        yield db