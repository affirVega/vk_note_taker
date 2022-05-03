from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, true
from sqlalchemy.orm import declarative_base, relationship
import json

with open('options.json', 'r') as f:
    options = json.load(f)

engine = create_engine(options['DB_URL'], echo=True, future=True)

Base = declarative_base()

class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    text = Column(String)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    vk_id = Column(Integer)

    notes = relationship('Note', backref='user')

Base.metadata.create_all(engine)