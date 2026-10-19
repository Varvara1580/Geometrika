from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.Models import Base
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind = engine)


def get_db():
    with SessionLocal() as db:
        yield db