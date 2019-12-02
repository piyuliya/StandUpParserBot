from datetime import datetime
import locale
import logging

from db import Events, session
from get_text import detect_text_uri

import requests
from bs4 import BeautifulSoup


logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )

# Устанавливаем верную локаль для Linux
locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")


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
    for page in range(1, 7):
        try:
            html = get_html(f'https://standupstore.ru/page/{page}')
            if html:
                get_event(html)
        except Exception:
            logging.info('Error URL')


def get_event(html):
    soup = BeautifulSoup(html, 'html.parser')
    all_event = soup.findAll('div', class_="t778__wrapper no-underline")
    for event in all_event:
        data_parser = event.find(
            'div',
            class_="t778__descr t-descr t-descr_xxs no-underline"
            ).text.replace(',', '').strip()
        data_event = datetime.strftime(
            datetime.now(),
            '%Y') + ' ' + data_parser
        data_event = datetime.strptime(data_event, '%Y %d %B %H:%M')

        # ОБРАБОТЧИК ЯНВАРЯ - ПЛОХОЙ НЕЯСНЫЙ КОД. НУЖНО УПРОСИТЬ ДОРАБОТАТЬ
        # try:
        #    check_date = datetime.strptime(data_parser, '%d %B %H:%M')
        #    if datetime.strftime(check_date, '%B') == '01' 
        #    and datetime.strftime(datetime.now(), '%B') == '12':
        #        data_event = datetime.strftime(
        #        datetime.now().timedelta(days=62), '%Y') + ' ' + data_parser
        #        data_event = datetime.strptime(data_event, '%Y %d %B %H:%M')
        #    else:
        #        data_event = datetime.strftime(
        #            datetime.now(),
        #            '%Y') + ' ' + data_parser
        #        data_event = datetime.strptime(data_event, '%Y %d %B %H:%M')
        # except(ValueError):
        #    data_event = datetime.now()

        price_event = event.find(
            'div',
            class_="t778__price t778__price-item t-name t-name_xs"
            ).text.strip()[:-2]

        availability = event.find(
            'div',
            class_="t778__imgwrapper").text.strip()

        url = event.find(
            'div',
            class_="t778__bgimg t778__bgimg_first_hover t-bgimg js-product-img"
            )['data-original']

        save_event(data_event, price_event, availability, url)
        update_availability(data_event, availability)
        update_url(data_event, price_event, availability, url)


def save_event(data_event, price_event, availability, url):
    event_exists = session.query(Events.data_event)\
        .filter(Events.data_event == data_event).count()

    if not event_exists:
        new_event = Events(
            data_event=data_event,
            price_event=price_event,
            availability=availability,
            url=url,
            status=True
            )
        session.add(new_event)
        session.commit()

        new_comic = detect_text_uri(new_event.url)
        session.query(Events.url, Events.comic)\
            .filter(Events.url == new_event.url)\
            .update({"comic": (new_comic)})
        session.commit()


def update_availability(data_event, availability):
    session.query(Events.availability, Events.data_event)\
        .filter(Events.data_event == data_event)\
        .update({"availability": availability})
    session.commit()


def update_url(data_event, price_event, availability, url):
    url_exists = session.query(Events.url)\
        .filter(Events.url == url).count()
    if not url_exists:
        new_comic = detect_text_uri(url)
        session.query(Events.url, Events.data_event)\
            .filter(Events.data_event == data_event)\
            .update({"url": (url)})
        session.query(Events.url, Events.comic)\
            .filter(Events.url == url)\
            .update({"comic": (new_comic)})
        session.query(Events.url, Events.status)\
            .filter(Events.url == url)\
            .update({"status": (True)})

    session.commit()


session.close()

if __name__ == '__main__':
    check_stand_up_site_page()
