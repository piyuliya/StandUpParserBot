# Импорт стандартных библиотек
from datetime import datetime
import locale
import logging


# Импорт телеграмм 
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler,\
                        RegexHandler, ConversationHandler, Filters
from telegram.ext import messagequeue as mq

# Импорт внутренних библиотек
import settings
from utils import get_keyboard

from db import Events, User, session
from user_status import save_user, remove_user

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )

# Устанавливаем верную локаль для Linux
locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")


def main():
    mybot = Updater(settings.token, request_kwargs=settings.PROXY)
    mybot.bot._msg_queue = mq.MessageQueue()
    mybot.bot._is_messages_queued_default = True
    logging.info('Бот запускается')
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(RegexHandler('^(Посмотреть афишу)$', get_schedule))
    dp.add_handler(RegexHandler('^(Подписаться на обновления)$', subscribe))
    dp.add_handler(RegexHandler('^(Отписаться)$', unsubscribe))
    mybot.job_queue.run_repeating(chek_new_event, interval=120)

    mybot.start_polling()
    mybot.idle()


def greet_user(bot, update):
    initial_message = """
Привет!\nУ нас ты можешь подписаться на обновление афиши \
StandUp Store Moscow и получать уведомление, \
как только интересующее тебя мероприятние появится на сайте!
"""

    my_keyboard = ReplyKeyboardMarkup([
        ['Посмотреть афишу', 'Подписаться на обновления', 'Отписаться']
        ], resize_keyboard=True
        )
    update.message.reply_text(initial_message, reply_markup=get_keyboard())


@mq.queuedmessage
def get_schedule(bot, update):
    now_time = datetime.now()
    for data_event, price_event, url in session.query(
        Events.data_event,
        Events.price_event,
        Events.url)\
            .filter(Events.data_event >= now_time)\
            .filter(Events.availability != 'Нет мест'):

        data_event = data_event.strftime('%d %B %H:%M')
        message_text = f"""
Есть места {data_event} цена: {price_event}
перейти на сайт\n[https://standupstore.ru/]
    """
        bot.send_photo(
            chat_id=update.message.chat.id,
            photo=url,
            caption=message_text,
            parse_mode='Markdown'
            )


@mq.queuedmessage
def chek_new_event(bot, job):
    now_time = datetime.now()
    for data_event, price_event, url, status in session.query(
        Events.data_event,
        Events.price_event,
        Events.url,
        Events.status)\
            .filter(Events.data_event >= now_time)\
            .filter(Events.availability != 'Нет мест')\
            .filter(Events.status == True):
        data_event = data_event.strftime('%d %B %H:%M')
        message_text = f"""
Новое мероприятие {data_event} цена: {price_event}
перейти на сайт\n[https://standupstore.ru/]
    """
        for chat_id in session.query(
            User.chat_id,
            User.subscribe
        ).filter(User.subscribe == True):
            bot.send_photo(
                chat_id=chat_id.chat_id,
                photo=url,
                caption=message_text,
                parse_mode='Markdown'
                )
        change_status(data_event)


def change_status(send_data_event):
    change_status_data_event = datetime.strftime(
            datetime.now(),
            '%Y') + ' ' + send_data_event
    change_status_data_event = datetime.strptime(
        change_status_data_event,
        '%Y %d %B %H:%M'
        )
    session.query(
        Events.data_event,
        Events.status
    ).filter(Events.data_event == change_status_data_event)\
        .update({"status": False})
    session.commit()


session.close()


def subscribe(bot, update):
    subscribe_chat_id = update.message.chat_id
    if session.query(User.chat_id)\
        .filter(User.chat_id == subscribe_chat_id)\
            .filter(User.subscribe == True).count():
        update.message.reply_text('Вы уже подписаны')
    else:
        save_user(subscribe_chat_id)
        update.message.reply_text('Вы подписались')
        logging.info(subscribe_chat_id)


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


if __name__ == "__main__":
    main()
