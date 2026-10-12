from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.Models import Base
import sqlite3

DATABASE_URL = 'sqlite:////app/data/task.db'

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind = engine)


def get_db():
    with SessionLocal() as db:
        yield db