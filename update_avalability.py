import os
from datetime import datetime
import locale
import platform
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, sessionmaker
import requests
from bs4 import BeautifulSoup
from parser import *

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


"""
По сути, большая часть кода в этом скрипте повторяет код update_url 
А мы следуем методу DRY - Do not repeate yourself
Поэтому надо сделать так, чтобы код не повторялся
Ну и исправить комментарии в update_py
"""


def get_html(url):
    try:
        result = requests.get(url)
        result.raise_for_status()
        return result.text
    except(requests.RequestExeption, ValueError):
        return False


def get_update_avalability(html):
    soup = BeautifulSoup(html, 'html.parser')
    all_event = soup.findAll('div', class_="t778__wrapper no-underline")
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
        except(ValueError):
            data_event = datetime.now()
        availability = event.find(
            'div',
            class_="t778__imgwrapper"
            ).text.strip()
        print(data_event, availability)
        update_availability(data_event, availability)


def pages(html):
    page = 1
    while page < 5:
        html = get_html('https://standupstore.ru/page/%s' % page)
        if html:
            get_update_avalability(html)
        page += 1


def check_update_availability():
    html = get_html('https://standupstore.ru/')
    if html:
        pages(html)


def update_availability(data_event, availability):
    session.query(Events.availability, Events.data_event).filter(Events.data_event == data_event).update({"availability":(availability)})
    session.commit()


if __name__ == '__main__':
    check_update_availability()
