import logging
import os

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler, ConversationHandler, Filters # Длина

from handlers import *

import settings

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )


def main():
    mybot = Updater(settings.token, request_kwargs=settings.PROXY)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(RegexHandler('^(Посмотреть афишу)$', get_schedule))
    dp.add_handler(RegexHandler('^(Подписаться на обновления)$', subscribe))
    dp.add_handler(RegexHandler('^(Отписаться)$', unsubscribe))

    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()
