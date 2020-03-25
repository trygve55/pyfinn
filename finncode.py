import sys

from fake_useragent import UserAgent
from requests_html import HTMLSession


session = HTMLSession()
ua = UserAgent()


def _parse_data_lists(html:HTMLSession):
    finn_codes = []
    data_lists = html.find('article')
    for el in data_lists:
        finn_codes.append(el.find('a')[0].attrs["href"].split("=")[-1])
    return finn_codes


def scrape_category(search_URL:str, show_progress=False):
    page = 1
    finn_codes = []
    while True:
        if show_progress:
            print('Processing search page ' + str(page) + ', found ' + str(len(finn_codes)) + ' Finn-codes.', end='\r')

        url = search_URL + "&page=" + str(page)
        page += 1
        r = session.get(url, headers={'user-agent': ua.random})
        r.raise_for_status()
        html = r.html
        temp_codes = _parse_data_lists(html)
        if len(temp_codes) <= 1:
            break
        finn_codes.extend(temp_codes)

    if show_progress:
        print('\n')
    return list(set(finn_codes))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Invalid number of arguments.\n\nUsage:\n$ python finn.py "Search URL"')
        exit(1)

    search_url = sys.argv[1]
    print(scrape_category(search_url))
