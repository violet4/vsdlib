#!/usr/bin/env python3
"""
courtesy of chatgpt.
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# create SQLite database engine and session factory
engine = create_engine('sqlite:///todos.db')
Session = sessionmaker(bind=engine)

# create base class for declarative model definition
Base = declarative_base()

# define Todo model class
class Todo(Base):
    __tablename__ = 'todo'

    tid = Column(Integer, primary_key=True)
    name = Column(String)
    created = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f'Todo {self.tid}: {self.name} ({self.created})'

# create table in database if it doesn't exist
Base.metadata.create_all(engine)

# session = Session()
# new_todo = Todo(name='Buy milk')
# session.add(new_todo)
# session.commit()
# print(session.query(Todo).all())

# print the new todo object (with its tid and created fields automatically filled in)
# print(new_todo)

