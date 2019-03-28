import requests
from bs4 import BeautifulSoup


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
    result_event = []
    for event in all_event:
        data_event = event.find(
            'div',
            class_="t778__descr t-descr t-descr_xxs no-underline").text
        price_event = event.find(
            'div',
            class_="t778__price t778__price-item t-name t-name_xs").text
        availability = event.find(
            'div',
            class_="t778__imgwrapper").text
        url = event.find(
            'div',
            class_="t778__bgimg t778__bgimg_first_hover t-bgimg js-product-img")['data-original']
        result_event.append({
            'data_event': data_event,
            'price_event': price_event,
            'availability': availability,
            'url': url
            })
        print(result_event)
    return result_event


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


if __name__ == '__main__':
    check_stand_up_site_page()
