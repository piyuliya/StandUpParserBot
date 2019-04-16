import os
from datetime import datetime
import locale
import platform

from utils import get_keyboard
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ParseMode
from parser import *

from parser import Events
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

if platform.system() == 'Windows':
    locale.setlocale(locale.LC_ALL, "russian")
else:
    locale.setlocale(locale.LC_TIME, "ru_RU")

basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(basedir, 'event.db'))
Base = declarative_base(engine)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def greet_user(bot, update):
    text = 'Привет! \nУ нас ты можешь подписаться на обновление афиши \
        StandUp Store Moscow и получать уведомление, как только интересующее\
        тебя мероприятние появится на сайте! \nВыбери вариант для себя: \
        \n обновление афиши; \n выбрать раздел; \n выбрать комика '
    my_keyboard = ReplyKeyboardMarkup([
        ['Посмотреть афишу', 'Подписаться на обновления']
        ], resize_keyboard=True
        )
    update.message.reply_text(text, reply_markup=get_keyboard())


def get_schedule(bot, update):
    for data_event, price_event, url in session.query(Events.data_event, Events.price_event, Events.url).filter(Events.availability != 'Нет мест'):
        data_event = data_event.strftime('%d %B %H:%M')
        user_text = 'Есть места {} цена: {}'.format(data_event, price_event)
        bot.send_photo ( chat_id = update.message.chat.id, photo = url, caption = user_text )

