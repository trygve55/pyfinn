from fake_useragent import UserAgent
from requests_html import HTMLSession
import requests_html
from time import sleep
import traceback
from random import random


session = HTMLSession()
ua = UserAgent()


'''
Below are HTML object getting functions
Args:
finn_code as str
Returns:
Html-object of the respective page on profil.nabolag.no
'''


def fetch(url: str) -> requests_html.HTML:
    tries = 6

    while tries:
        request = session.get(url, headers={'user-agent': ua.random})

        if request.status_code == 500:
            raise Exception
        elif request.status_code == 200:
            return request.html
        else:
            print(request.status_code)
            print(url)

        sleep(random()*1.3+0.3)
        tries -= 1

    raise Exception


def fetch_render(url: str) -> requests_html.HTML:
    html = fetch(url)

    tries = 4
    while tries:
        try:
            html.render()
        except Exception as e:
            traceback.print_tb(e)
            print(url)

        sleep(random()*1.3+0.3)
        tries -= 1

    return html


def nabolag_people_html(finn_code: str) -> requests_html.HTML:
    complete_url = "https://profil.nabolag.no/" + finn_code + "/menneskene"

    return fetch(complete_url)


def nabolag_people_html_render(finn_code: str) -> requests_html.HTML:
    complete_url = "https://profil.nabolag.no/" + finn_code + "/menneskene"

    return fetch_render(complete_url)


def nabolag_env_html_render(finn_code: str) -> requests_html.HTML:
    complete_url = "https://profil.nabolag.no/" + finn_code + "/bomiljo"

    return fetch_render(complete_url)


def nabolag_transport_html(finn_code: str) -> requests_html.HTML:
    complete_url = "https://profil.nabolag.no/" + finn_code + "/transport"

    return fetch(complete_url)


def nabolag_family_html(finn_code: str) -> requests_html.HTML:
    complete_url = "https://profil.nabolag.no/" + finn_code + "/familie"

    return fetch(complete_url)


"""
Args:
html, can be extracted from the nabolag_*_html functions above.
Returns:
A dict containing all parsed values from the HTML as floats
"""


def parse_values(html: requests_html.HTML) -> dict:
    data = {}
    cards = html.find(".Card__Wrapper-q6bwfy-0")
    for card in cards:
        #PieChart
        card_name = card.find('div', first=True).find('h4', first=True).text
        for el in card.find('.PieChart__TableRow-oxga1c-5'):
            sub_el = el.find('td')
            value = float(sub_el[0].text.replace('%', '')) / 100
            var_name = sub_el[1].text.replace('/', '')
            data['neighborhood_' + card_name + '_' + var_name] = value

        #Value percent
        h4_text = card.find('.Rating__RatingHeader-ys2jkg-3', first=True)
        if h4_text != None:
            data['neighborhood_' + card_name] = float(h4_text.text.split(' ')[0]) / 100

        #BarChart
        barchart = card.find('.BarChart-sc-1yklinr-0', first=True)
        if barchart:
            max_percent = float(barchart.find('.BarChart__LabelValue-sc-1yklinr-5')[1].text.replace('%', '')) / 100
            for bar in barchart.find('.BarChart__BarWrapper-sc-1yklinr-1'):
                bar_name = bar.find('span', first=True).text.replace(u'\xa0', '')
                value = float(bar.find('.BarChart__Bar-sc-1yklinr-2', first=True).attrs['style'].split(':')[1].replace('%', '')) / 100 * max_percent
                data['neighborhood_' + card_name + '_' + bar_name] = value

        #PieChartComparison
        chart = card.find('.PieChartComparison__Wrapper-sc-1ik4tkv-0', first=True)
        if chart:
            for el in chart.find('.Legend__LegendValue-e29sxx-3'):
                text = el.element.text.split(' ', 1)
                value_name = text[1]
                value = float(text[0].replace('%', '')) / 100
                data['neighborhood_' + card_name + '_' + value_name] = value

        #TextChart   utdanning...

        #PoiMap

    return data


def neighborhood_profiler(finn_code: str) -> dict:
    env_html = family_html = people_html = transport_html = None

    try:
        env_html = nabolag_env_html_render(finn_code)
        family_html = nabolag_family_html(finn_code)
        people_html = nabolag_people_html_render(finn_code)
        transport_html = nabolag_transport_html(finn_code)
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        return {}

    data = {}

    data.update(parse_values(env_html))
    data.update(parse_values(people_html))
    data.update(parse_values(family_html))
    data.update(parse_values(transport_html))

    return data


if __name__ == "__main__":
    test_code = "155458816"
    print(neighborhood_profiler(test_code))
