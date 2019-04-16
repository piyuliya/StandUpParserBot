import os
from datetime import datetime
import locale
import platform

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, sessionmaker

import requests
from bs4 import BeautifulSoup

# Пустые строки) слишком много)
from parser import *
from parser import Events

if platform.system() == 'Windows':
    locale.setlocale(locale.LC_ALL, "russian")
else:
    locale.setlocale(locale.LC_TIME, "ru_RU")


basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(basedir, 'event.db'))
Base = declarative_base(engine)
Base.metadata.create_all(engine) # Аналогично файлу update_url
Session = sessionmaker(bind=engine)
session = Session()


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
        data_event = event.find(
            'div',
            class_="t778__descr t-descr t-descr_xxs no-underline").text
        data_event = data_event.replace(',', '').strip()
        try:
            data_event = datetime.strptime(data_event, '%d %B %H:%M')
        except(ValueError):
            data_event = datetime.now()
        price_event = event.find(
            'div',
            class_="t778__price t778__price-item t-name t-name_xs").text
        price_event = price_event.strip()[:-2]
        availability = event.find(
            'div',
            class_="t778__imgwrapper").text
        availability = availability.strip()
        url = event.find(
            'div',
            class_="t778__bgimg t778__bgimg_first_hover t-bgimg js-product-img")['data-original']
        print(data_event, price_event, availability, url)
        update_availability(data_event, price_event, availability, url)


def pages(html):
    page = 1
    while page < 5:
        html = get_html('https://standupstore.ru/page/%s' % page)
        if html:
            get_update_avalability(html)
        page += 1


def check_stand_up_site_page():
    html = get_html('https://standupstore.ru/')
    if html:
        pages(html)


def update_availability(data_event, price_event, availability, url):
    session.query(Events.availability, Events.data_event).filter(Events.data_event == data_event).update({"availability":(availability)})
    session.commit()


if __name__ == '__main__':
    check_stand_up_site_page()
