import os
from datetime import datetime
import locale
import platform

from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, sessionmaker

from get_text import detect_text_uri
import requests
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from handlers import * 

if platform.system() == 'Windows':
    locale.setlocale(locale.LC_ALL, "russian")
else:
    locale.setlocale(locale.LC_TIME, "ru_RU")


keydir = os.path.abspath(os.path.dirname(__file__))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(keydir, 'StandUp-382484bc62e0.json')


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


base.metadata.create_all(engine)


def get_html(url):
    try:
        result = requests.get(url)
        result.raise_for_status()
        return result.text
    except(requests.RequestExeption, ValueError):
        return False


def get_event(html):
    soup = BeautifulSoup(html, 'html.parser')
    all_event = soup.findAll('div', class_="t778__wrapper no-underline")
    for event in all_event:
        data_parser = event.find(
            'div',
            class_="t778__descr t-descr t-descr_xxs no-underline").text.replace(',', '').strip()
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
        price_event = event.find(
            'div',
            class_="t778__price t778__price-item t-name t-name_xs").text.strip()[:-2]
        availability = event.find(
            'div',
            class_="t778__imgwrapper").text.strip()
        url = event.find(
            'div',
            class_="t778__bgimg t778__bgimg_first_hover t-bgimg js-product-img")['data-original']
        #print(data_event, price_event, availability, url)
        save_events(data_event, price_event, availability, url)


def pages(html):
    page = 1
    while page < 5:
        html = get_html('https://standupstore.ru/page/%s' % page)
        if html:
            get_event(html)
            with open('standup.html', 'w', encoding='utf8') as f:
                f.write(html)
        page += 1


def check_stand_up_site_page():
    html = get_html('https://standupstore.ru/')
    if html:
        pages(html)


def save_events(data_event, price_event, availability, url):
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
        #send_new_event(new_event)

if __name__ == '__main__':
    check_stand_up_site_page()
