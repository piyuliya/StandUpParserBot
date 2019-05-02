import os
from datetime import datetime
import locale
import platform
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, sessionmaker
import requests
from bs4 import BeautifulSoup
from parser import *
from parser import Events
from get_text import detect_text_uri

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


def get_html(url):
    try:
        result = requests.get(url)
        result.raise_for_status()
        return result.text
    except(requests.RequestExeption, ValueError):
        return False # Перехватила ошибку и что?


def get_update_url(html):
    soup = BeautifulSoup(html, 'html.parser')
    all_event = soup.findAll('div', class_="t778__wrapper no-underline") # Название переменной нужно точней
    for event in all_event:
        data_parser = event.find( 
            'div',
            class_="t778__descr t-descr t-descr_xxs no-underline"
            ).text.replace(',', '').strip()
        try:
            data_fo_check = datetime.strptime(data_parser, '%d %B %H:%M')
            if datetime.strftime(data_fo_check, '%B') == 'январь':
                data_event = datetime.strftime(datetime.now().timedelta(days=50), '%Y') + ' ' + data_parser
                data_event = datetime.strptime(data_event, '%Y %d %B %H:%M')
            else:
                data_event = datetime.strftime(datetime.now(), '%Y') + ' ' + data_parser
                data_event = datetime.strptime(data_event, '%Y %d %B %H:%M')
        except ValueError:
            data_event = datetime.now() # Почему если нет даты эвента, пишешь  сегодняшнюю?
        url = event.find(
            'div',
            class_="t778__bgimg t778__bgimg_first_hover t-bgimg js-product-img"
            )['data-original']
        print(data_event, url) # Для логгирования подключи logging, принты в консоль уже не нужны, ты уже умеешь логгировать как профессионал)
        
        update_url(data_event, url)


def pages(html):
    page = 1 # Используй генератор range, а не рукописный цикл.
    while page < 5:
        html = get_html('https://standupstore.ru/page/%s' % page)
        if html:
            get_update_url(html)
        page += 1


def check_update_url():
    html = get_html('https://standupstore.ru/')
    if html:
        pages(html) # А если нет? Обработку ошибок добавь


def update_url(data_event, url):
    session.query(Events.url, Events.data_event)\
        .filter(Events.data_event == data_event)\
        .update({"url":(url)})
    session.commit()
 
     # А сессию закрывать кто будет?)


if __name__ == '__main__':
    check_update_url()
    #recognize_url()