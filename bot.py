# Импорт стандартных библиотек
import os
import locale
import logging
from datetime import datetime

# Импорт телеграмм 
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler,\
                        RegexHandler, ConversationHandler, Filters

# Импорт внутренних библиотек
import settings
from utils import get_keyboard

# Импорт алхимии
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from user_status import User, save_user, remove_user

from parser import Events

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )

# Устанавливаем верную локаль для Linux
locale.setlocale(locale.LC_ALL, "ru_RU.utf8")

# Подключаемся к базе данных
basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(basedir, 'event.db'))
base = declarative_base(engine)  # TODO разобраться с подключением?
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
    initial_message = """
            Привет!\nУ нас ты можешь подписаться на обновление афиши
            StandUp Store Moscow и получать уведомление,
            как только интересующее тебя мероприятние появится на сайте!\n
        """
    update.message.reply_text(initial_message, reply_markup=get_keyboard())


def get_schedule(bot, update):
    now_time = datetime.now()
    for data_event, price_event, url in session.query(
        Events.data_event,
        Events.price_event,
        Events.url)\
            .filter(Events.data_event >= now_time)\
            .filter(Events.availability != 'Нет мест'):

        data_event = data_event.strftime('%d %B %H:%M')
        message_text = f'Есть места {data_event} цена: {price_event}'
        bot.send_photo(
            chat_id=update.message.chat.id,
            photo=url,
            caption=message_text)


def subscribe(bot, update):
    subscribe_chat_id = update.message.chat_id
    if session.query(User.chat_id)\
        .filter(User.chat_id == subscribe_chat_id)\
            .filter(User.subscribe == True).count():
        update.message.reply_text('Вы уже подписаны')
    else:
        save_user(subscribe_chat_id)
        update.message.reply_text('Вы подписались')
        print(subscribe_chat_id) # СДЕЛАТЬ ЛОГГИРОВАНИЕ НЕ ЧЕРЕЗ ПРИНТЫ


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
