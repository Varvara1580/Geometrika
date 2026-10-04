from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import Table, create_engine, Integer, String, select, ForeignKey, Table, Column, DateTime, Text, LargeBinary, Boolean
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session, Mapped, mapped_column, relationship
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass
geometry_members = Table(
    'geometry_members',
    Base.metadata,
    Column('geometry_id', ForeignKey('geometry_classes.id'), primary_key = True),
    Column('user_id', ForeignKey('users.id'), primary_key = True)
)
class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(200))
    var_1: Mapped[str] = mapped_column(String(200))
    var_2: Mapped[str] = mapped_column(String(200))
    var_3: Mapped[str] = mapped_column(String(200))
    var_4: Mapped[str] = mapped_column(String(200))
    otv: Mapped[str] = mapped_column(String(200))
    #draft: Mapped[bytes] = mapped_column(LargeBinary)
    #solution: Mapped[bytes] = mapped_column(LargeBinary)
    topic_id: Mapped[int] = mapped_column(ForeignKey('topics.id'))
    #topic: Mapped["Topic"] = relationship(back_populates = 'tasks', lazy = True)
    #progress: Mapped[list["User_progress"]] = relationship(back_populates = 'tasks', lazy = True)

class Topic(Base):
    __tablename__ = 'topics'
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    name: Mapped[str] = mapped_column(String(200))
    #tasks: Mapped[list["Task"]] = relationship(back_populates = 'topic', lazy = True)

class Geometry_class(Base):
    __tablename__ = 'geometry_classes'
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    name: Mapped[str] = mapped_column(String(200))
    password: Mapped[str] = mapped_column(String(200))
    creator_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    creator: Mapped["User"] = relationship(back_populates = 'created', foreign_keys = [creator_id], overlaps = 'members')
    members: Mapped[list["User"]] = relationship(secondary = geometry_members, back_populates = 'classes', overlaps = 'creator')
    own_topics: Mapped[list["Own_topic"]] = relationship(back_populates = 'geometry_class')

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    name: Mapped[str] = mapped_column(String(200))
    surname: Mapped[str] = mapped_column(String(200))
    username: Mapped[str] = mapped_column(String(200))
    password: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(200))
    schedule: Mapped[str] = mapped_column(String(200), default = 'Обучение')
    classes: Mapped[list["Geometry_class"]] = relationship(secondary = geometry_members,
                                                           primaryjoin = 'User.id == geometry_members.c.user_id',
                                                           secondaryjoin = 'Geometry_class.id == geometry_members.c.geometry_id',
                                                           back_populates = 'members',
                                                           overlaps = 'created')
    #progress: Mapped[list["User_progress"]] = relationship(back_populates = 'user')
    created: Mapped[list["Geometry_class"]] = relationship(back_populates = 'creator', foreign_keys = [Geometry_class.creator_id], overlaps = 'classes')
    refresh_tokens: Mapped[list["Refresh_token"]] = relationship(back_populates='user')

class User_progress(Base):
    __tablename__ = 'user_progresses'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'))
    #task_number: Mapped[int] = mapped_column(ForeignKey('tasks.number'))
    is_correct: Mapped[bool] = mapped_column(Boolean)
    is_correct_1: Mapped[bool] = mapped_column(Boolean)
    user_result: Mapped[int] = mapped_column(Integer)
    saved: Mapped[bool] = mapped_column(Boolean, default = False)

class Refresh_token(Base):
    __tablename__ = 'refresh_tokens'
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    token: Mapped[str] = mapped_column(String(500), unique = True)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped["User"] = relationship(back_populates='refresh_tokens')

class Own_topic(Base):
    __tablename__ = 'own_topics'
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    name: Mapped[str] = mapped_column(String(200))
    creator_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    geometry_class_id: Mapped[int] = mapped_column(ForeignKey('geometry_classes.id'))
    geometry_class: Mapped["Geometry_class"] = relationship(back_populates = 'own_topics')
    own_tasks: Mapped[list["Own_task"]] = relationship(back_populates = 'own_topic')

class Own_task(Base):
    __tablename__ = 'own_tasks'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(200))
    text: Mapped[str] = mapped_column(String(1000))
    otv: Mapped[str] = mapped_column(String(200))
    draft: Mapped[str] = mapped_column(String(1000))
    solution: Mapped[str] = mapped_column(String(1000))
    creator_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    own_topic_id: Mapped[int] = mapped_column(ForeignKey('own_topics.id'))
    own_topic: Mapped["Own_topic"] = relationship(back_populates='own_tasks')

class User_progress_own(Base):
    __tablename__ = 'user_progresses_own'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    own_topic_id: Mapped[int] = mapped_column(ForeignKey('own_topics.id'))
    own_task_id: Mapped[int] = mapped_column(ForeignKey('own_tasks.id'))
    is_correct: Mapped[bool] = mapped_column(Boolean)
    is_correct_1: Mapped[bool] = mapped_column(Boolean)
    #user_result: Mapped[int] = mapped_column(Integer)
    saved: Mapped[bool] = mapped_column(Boolean, default=False)