import os
from datetime import datetime
import locale

from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, sessionmaker

import requests
from bs4 import BeautifulSoup

# Устанавливаем верную локаль для Linux
locale.setlocale(locale.LC_ALL, "ru_RU.utf8")

basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(basedir, 'event.db'))
base = declarative_base(engine)
base.metadata.create_all(engine)
session = sessionmaker(bind=engine)
session = session()


class Events(base):
    __tablename__ = 'Events'
    id = Column(Integer, primary_key=True)
    data_event = Column(DateTime, unique=True, nullable=False)
    price_event = Column(String, nullable=True)
    availability = Column(String, nullable=True)
    url = Column(String, nullable=False)
    comic = Column(String, nullable=True)

    def __init__(self, data_event, price_event, availability, url):
        self.data_event = data_event
        self.price_event = price_event
        self.availability = availability
        self.url = url

    def __repr__(self):
        return '<Events {} {}>'.format(self.data_event, self.price_event)


def check_stand_up_site_page():
    html = get_html('https://standupstore.ru/')
    if html:
        parse_pages(html)


def get_html(url):
    try:
        result = requests.get(url)
        result.raise_for_status()
        return result.text
    except(requests.RequestExeption, ValueError):
        return False


def parse_pages(html):
    for page in range(1, 5):
        html = get_html(f'https://standupstore.ru/page/{page}')
        if html:
            get_event(html)
        # СДЕЛАТЬ ОБРАБОТКУ ОШИБОК


def get_event(html):
    soup = BeautifulSoup(html, 'html.parser')
    all_event = soup.findAll('div', class_="t778__wrapper no-underline")
    for event in all_event:
        data_parser = event.find(
            'div',
            class_="t778__descr t-descr t-descr_xxs no-underline").text.replace(',', '').strip()
        data_event = datetime.strftime(datetime.now(), '%Y') + ' ' + data_parser
        data_event = datetime.strptime(data_event, '%Y %d %B %H:%M')

        # ОБРАБОТЧИК ЯНВАРЯ - ПЛОХОЙ НЕЯСНЫЙ КОД. ПОДУМАЙ, КАК ЕГО УПРОСИТЬ
        # try:
        #    check_date = datetime.strptime(data_parser, '%d %B %H:%M')
        #    if datetime.strftime(check_date, '%B') == '01':
        #        data_event = datetime.strftime(datetime.now().timedelta(days=50), '%Y') + ' ' + data_parser
        #        data_event = datetime.strptime(data_event, '%Y %d %B %H:%M')
        #    else:
        #        data_event = datetime.strftime(datetime.now(), '%Y') + ' ' + data_parser
        #        data_event = datetime.strptime(data_event, '%Y %d %B %H:%M')
        # except(ValueError):
        #    data_event = datetime.now()

        price_event = event.find(
            'div',
            class_="t778__price t778__price-item t-name t-name_xs").text.strip()[:-2]

        availability = event.find(
            'div',
            class_="t778__imgwrapper").text.strip()

        url = event.find(
            'div',
            class_="t778__bgimg t778__bgimg_first_hover t-bgimg js-product-img")['data-original']

        save_event(data_event, price_event, availability, url)
        update_availability(data_event, availability)
        update_url(data_event, url)


def save_event(data_event, price_event, availability, url):
    event_exists = session.query(Events.data_event)\
        .filter(Events.data_event == data_event).count()

    if not event_exists:
        new_event = Events(
            data_event=data_event,
            price_event=price_event,
            availability=availability,
            url=url,
            )
        session.add(new_event)
        session.commit()


def update_availability(data_event, availability):
    session.query(Events.availability, Events.data_event)\
        .filter(Events.data_event == data_event)\
        .update({"availability": availability})
    session.commit()


def update_url(data_event, url):
    session.query(Events.url, Events.data_event)\
        .filter(Events.data_event == data_event)\
        .update({"url":(url)})
    session.commit()


session.close()

if __name__ == '__main__':
    check_stand_up_site_page()
