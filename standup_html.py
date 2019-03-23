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
    for event in all_event:
        data_event = event.find(
            'div',
            class_="t778__descr t-descr t-descr_xxs no-underline").text
        print(data_event)


if __name__ == '__main__':
    page = 1
    while page < 6:
        html = get_html('https://standupstore.ru/page/%s' % page)
        if html:
            get_event(html)
            with open('standup.html', 'w', encoding='utf8') as f:
                f.write(html)
        page += 1
