import json
import re
import sys

import dateparser
from fake_useragent import UserAgent
from requests_html import HTMLSession


session = HTMLSession()
ua = UserAgent()


def error_check(code_list):
    for string in code_list:
        try:
            int(string)
        except ValueError:
            print("expected string of integers, got: " + string)
            return 1
    return 0


def _parse_data_lists(html:HTMLSession):
    data = {}
    skip_keys = ['Mobil', 'Fax']  # Unhandled data list labels
    finn_codes = {}
    data_lists = html.find('article')
    for el in data_lists:
        finn_codes.append(el.find('a')[0].attrs["id"].split("-")[-1])
        '''
        values_list = iter(el.find('dt, dd'))
        for a in values_list:
            _key = a.text
            a = next(values_list)
            if _key in skip_keys:
                continue'''
    #if(error_check(values_list)):
    #    return {}
    return data




'''
def _scrape_viewings(html):
    viewings = set()
    els = html.find('time')
    for el in els:
        # Ninja parse dt range string in norwegian locale. Example: "søndag 08. april, kl. 13:00–14:00"
        split_space = el.text.strip().split(' ')
        if len(split_space) < 5:
            continue
        date, time_range = ' '.join(split_space[1:]).replace(' kl. ', '').split(',')
        # start_hour, start_min = time_range.split('–')[0].split(':')
        dt = dateparser.parse(date, languages=['nb'])
        if dt:
            # dt = dt.replace(hour=int(start_hour), minute=int(start_min))
            viewings.add(dt.date().isoformat())
    return list(viewings)
'''


def scrape_category(search_URL:str):
    url = search_URL
    while True:
        r = session.get(url, headers={'user-agent': ua.random})
        r.raise_for_status()
        html = r.html
        finn_codes = _parse_data_lists(html)
    return finn_codes


def search_URL_to_codes(search_URL):
    data = {}
    data.append(_parse_data_lists)
    while length(_parse_data_lists)

if __name__ == '__main__':
    '''
    if len(sys.argv) != 2:
        print('Invalid number of arguments.\n\nUsage:\n$ python finn.py FINNKODE')
        exit(1)

    ad_url = sys.argv[1]
    ad = scrape_category(ad_url)
    print(json.dumps(ad, indent=2, ensure_ascii=False))'''
    scrape_category("https://www.finn.no/realestate/homes/search.html?location=0.20016&location=1.20016.20318")

