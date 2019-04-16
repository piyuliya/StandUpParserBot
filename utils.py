from telegram import ReplyKeyboardMarkup


def get_keyboard():
    my_keyboard = ReplyKeyboardMarkup([ # Обрати внимание на PEP8, квадратные скобки можно расположить поудачней)
        ['Посмотреть афишу', 'Подписаться на обновления']
        ], resize_keyboard=True
        )
    return my_keyboard

