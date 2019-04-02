import logging

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler, Filters

import settings

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )


def greet_user(bot, update):
    text = 'Привет! \nУ нас ты можешь подписаться на обновление афиши \
        StandUp Store Moscow и получать уведомление, как только интересующее\
        тебя мероприятние появится на сайте! \nВыбери вариант для себя: \
        \n обновление афиши; \n выбрать раздел; \n выбрать комика '
    my_keyboard = ReplyKeyboardMarkup([['WTF?!']])
    update.message.reply_text(text, reply_markup=my_keyboard)


def talk_to_me(bot, update):
    user_text = update.message.text 
    print(user_text)
    update.message.reply_text(user_text)


def main():
    mybot = Updater(settings.token, request_kwargs=settings.PROXY)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(RegexHandler('^(WTF?!)$', greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()
