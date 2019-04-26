import os
from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, sessionmaker

basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(basedir, 'event.db'))
base = declarative_base(engine)
base.metadata.create_all(engine)
session = sessionmaker(bind=engine)
session = session()


class User(base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, index=True, unique=True, nullable=False)
    subscribe = Column(String, nullable=True)

    def __init__(self, chat_id, subscribe):
        self.chat_id = chat_id
        self.subscribe = subscribe
      
    def __repr__(self):
        return '<User {} {}>'.format(self.chat_id)

base.metadata.create_all(engine)


def save_user(chat_id):
    new_chat_id = session.query(User.chat_id).filter(User.chat_id == chat_id).count()
    if not new_chat_id:
        new_user = User(
            chat_id=chat_id,
            subscribe=True,
            )
        session.add(new_user)
        session.commit()
    else:
        session.query(User.chat_id, User.subscribe).filter(User.chat_id == chat_id).update({"subscribe":(True)})
        session.commit()


def remove_user(chat_id):
    session.query(User.chat_id, User.subscribe).filter(User.chat_id == chat_id).update({"subscribe":(False)})
    session.commit()
