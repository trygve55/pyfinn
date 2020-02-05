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
    finn_codes = []
    data_lists = html.find('article')
    for el in data_lists:
        finn_codes.append(el.find('a')[0].attrs["id"].split("-")[-1])
    return finn_codes


def scrape_category(search_URL:str):
    page = 1
    finn_codes = []
    while True:
        url = search_URL + "&page=" + str(page)
        page += 1
        r = session.get(url, headers={'user-agent': ua.random})
        r.raise_for_status()
        html = r.html
        temp_codes = _parse_data_lists(html)
        if len(temp_codes) <= 1:
            break
        finn_codes.extend(temp_codes)
    return list(set(finn_codes))




if __name__ == '__main__':
    print(len(scrape_category("https://www.finn.no/realestate/homes/search.html?location=0.20016&location=1.20016.20318")))
