from telegram import ReplyKeyboardMarkup


def get_keyboard():
    my_keyboard = ReplyKeyboardMarkup([
        ['Посмотреть афишу', 'Подписаться на обновления', 'Отписаться']
        ], resize_keyboard=True
        )
    return my_keyboard
