import os
from datetime import datetime
import locale
import platform
import logging

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler, ConversationHandler, Filters # Длина

import settings
from utils import get_keyboard

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from parser import *
from user_status import User, save_user, remove_user

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )


if platform.system() == 'Windows':
    locale.setlocale(locale.LC_ALL, "russian")
else:
    locale.setlocale(locale.LC_TIME, "ru_RU")

basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(basedir, 'event.db'))
base = declarative_base(engine)
base.metadata.create_all(engine)
session = sessionmaker(bind=engine)
session = session()


def main():
    mybot = Updater(settings.token, request_kwargs=settings.PROXY)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(RegexHandler('^(Посмотреть афишу)$', get_schedule))
    dp.add_handler(RegexHandler('^(Подписаться на обновления)$', subscribe))
    dp.add_handler(RegexHandler('^(Отписаться)$', unsubscribe))

    mybot.start_polling()
    mybot.idle()


def greet_user(bot, update):
    text = 'Привет! \nУ нас ты можешь подписаться на обновление афиши \
StandUp Store Moscow и получать уведомление, как только интересующее\
тебя мероприятние появится на сайте! \nВыбери вариант для себя: \
\n- обновление афиши; \n- выбрать раздел(в разработке);\
\n- выбрать комика(в разработке)'
    my_keyboard = ReplyKeyboardMarkup([
        ['Посмотреть афишу', 'Подписаться на обновления', 'Отписаться']
        ], resize_keyboard=True
        )
    update.message.reply_text(text, reply_markup=get_keyboard())


def get_schedule(bot, update):
    now = datetime.now()
    for data_event, price_event, url in session.query(
        Events.data_event,
        Events.price_event,
        Events.url).filter(Events.data_event >= now)\
            .filter(Events.availability != 'Нет мест'):
        data_event = data_event.strftime('%d %B %H:%M')
        user_text = 'Есть места {} цена: {}'.format(data_event, price_event)
        bot.send_photo(
            chat_id=update.message.chat.id,
            photo=url,
            caption=user_text)


def subscribe(bot, update):
    subscribe_chat_id = update.message.chat_id
    if session.query(User.chat_id)\
        .filter(User.chat_id == subscribe_chat_id)\
            .filter(User.subscribe == True).count():
        update.message.reply_text('Вы уже подписаны')
    else:
        save_user(subscribe_chat_id)
        update.message.reply_text('Вы подписались')
        print(subscribe_chat_id)


def unsubscribe(bot, update):
    unsubscribe_chat_id = update.message.chat_id
    if not session.query(User.chat_id)\
        .filter(User.chat_id == unsubscribe_chat_id)\
            .filter(User.subscribe == False).count():
        remove_user(unsubscribe_chat_id)
        update.message.reply_text('Вы отписались')
    else:
        update.message.reply_text('Вы не подписаны, нажмите на\
    "Подписаться на обновления" чтобы подписаться')


def send_new_event(new_event):
    global bot
    global update
    send_message_to_user(bot, update, new_event)


def send_message_to_user(bot, update, new_event):
    for chat_id in session.query(User.chat_id, User.subscribe)\
        .filter(User.chat_id == chat_id).filter(User.subscribe == True):
        data_event = new_event.data_event.strftime('%d %B %H:%M')
        print(new_event.data_event)
        user_text = 'Новое мероприятие {} цена: {}'\
            .format(data_event, new_event.price_event)
        bot.send_photo(chat_id=chat_id, photo=new_event.url, caption=user_text)


if __name__ == "__main__":
    main()
