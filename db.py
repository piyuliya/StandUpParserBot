import os

from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, sessionmaker

# Подключаемся к базе данных
basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(basedir, 'event.db'))
base = declarative_base(engine)  # TODO разобраться с подключением?
session = sessionmaker(bind=engine)
session = session()


class Events(base):
    __tablename__ = 'Events'
    id = Column(Integer, primary_key=True)
    data_event = Column(DateTime, unique=True, nullable=False)
    price_event = Column(String, nullable=True)
    availability = Column(String, nullable=True)
    url = Column(String, nullable=False)
    comic = Column(String, nullable=True)

    def __init__(self, data_event, price_event, availability, url):
        self.data_event = data_event
        self.price_event = price_event
        self.availability = availability
        self.url = url

    def __repr__(self):
        return '<Events {} {}>'.format(self.data_event, self.price_event)


class User(base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, index=True, unique=True, nullable=False)
    subscribe = Column(String, nullable=True)

    def __init__(self, chat_id, subscribe):
        self.chat_id = chat_id
        self.subscribe = subscribe

    def __repr__(self):
        return '<User {}>'.format(self.chat_id)


base.metadata.create_all(engine)
