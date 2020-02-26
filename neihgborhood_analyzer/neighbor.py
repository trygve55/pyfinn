import json
import re
import sys

import dateparser
from fake_useragent import UserAgent
from requests_html import HTMLSession
import requests_html




session = HTMLSession()
ua = UserAgent()


'''
Below are HTML object getting functions
Args:
finn_code as str
Returns:
Html-object of the respective page on profil.nabolag.no
'''


def nabolag_people_html(finn_code: str) -> requests_html.HTML:
    complete_url = "https://profil.nabolag.no/" + finn_code + "/menneskene"
    request = session.get(complete_url, headers={'user-agent': ua.random})
    request.raise_for_status()
    return request.html


def nabolag_people_html_render(finn_code: str) -> requests_html.HTML:
    complete_url = "https://profil.nabolag.no/" + finn_code + "/menneskene"
    request = session.get(complete_url, headers={'user-agent': ua.random})
    request.raise_for_status()
    request.html.render()
    return request.html


def nabolag_env_html_render(finn_code: str) -> requests_html.HTML:
    complete_url = "https://profil.nabolag.no/" + finn_code + "/bomiljo"
    request = session.get(complete_url, headers={'user-agent': ua.random})
    request.raise_for_status()
    request.html.render()
    return request.html


def nabolag_transport_html(finn_code: str) -> requests_html.HTML:
    complete_url = "https://profil.nabolag.no/" + finn_code + "/transport"
    request = session.get(complete_url, headers={'user-agent': ua.random})
    request.raise_for_status()
    request.html.render()
    return request.html


def nabolag_family_html(finn_code: str) -> requests_html.HTML:
    complete_url = "https://profil.nabolag.no/" + finn_code + "/familie"
    request = session.get(complete_url, headers={'user-agent': ua.random})
    request.raise_for_status()
    request.html.render()
    return request.html


'''
Args:
html of "graph-card" on nabolag.no
Returns:
one-normalized list of floats
'''
def one_normalized_list_from_html_graph(html_graph: requests_html.HTML) -> list:
    """
    NB!
    This code is what we can technically define as "fucky",
    it reads HTML-graphs through string-parsing assuming the HTML won't
    ever be altered.
    BUGS WILL MOST LIKELY BE IN THIS FUNCTION!
    I couldn't find a more robust way to do this.
    """
    raw_list_elements = []
    for bar in html_graph:
        html_el = bar.find(".BarChart__Bar-sc-1yklinr-2")
        attribute = html_el[0].attrs["style"]
        widths = str(attribute).split("%")[0]
        width_string = widths.split(":")[1]
        width = float(width_string)
        raw_list_elements.append(width)
    width_sums = sum(raw_list_elements)
    one_normalized = [None] * len(raw_list_elements)
    for i in range(len(raw_list_elements)):
        one_normalized[i] = raw_list_elements[i]/width_sums
    return one_normalized



"""
Args:
nabolag_html, can be extracted from nabolag_people_html_render()
Returns:
Function that returns 1-normalized income distribution for neighborhood through finncode, 
Brackets are formatted as:
[<0-100000>, <100000-200000>, <200000-400000>, <400000-500000>, <500000-800000>, <800000->]
"""
def income_distribution(nabolag_html: requests_html.HTML) -> list:
    cards = nabolag_html.find(".BarChart-sc-1yklinr-0")
    bars = cards[1].find(".BarChart__BarWrapper-sc-1yklinr-1")
    return one_normalized_list_from_html_graph(bars)



"""
Args:
nabolag_html, can be extracted from nabolag_people_html_render()
Returns:
One normalized age distribution of property neighborhood
Formatted as:
[<0-12>, <13-18>, <19-34>, <35-64>, <65+>]
"""
def age_distribution(nabolag_HTML : requests_html.HTML) -> list:
    cards = nabolag_html.find(".BarChart-sc-1yklinr-0")
    bars = cards[0].find(".BarChart__BarWrapper-sc-1yklinr-1")
    return one_normalized_list_from_html_graph(bars)



"""
Args:
nabolag_html, can be extracted from nabolag_people_html_render()
Returns:
One normalized marital status distribrution of property neighborhood
Formatted as:
[<Not married>, <Married>, <Separated>, <Widow>]
"""
def marital_status_distribution(nabolag_html: requests_html.HTML) -> list:
    responsive_container = nabolag_html.find(".Legend__LegendValue-e29sxx-3")
    marital_status = []
    for el in responsive_container:
        marital_status.append(int(str(el.text).split("%")[0])/100)
    print(marital_status)



"""
Args:
env_html, can be extracted from nabolag_env_html_render()
Returns:
One normalized house age distribution of property neighborhood
Formatted as:
[<0 - 10 yrs>, <10 - 30 yrs>, <30 - 50yrs>, <more than 50yrs>]
"""
def house_age_distribution(env_html: requests_html.HTML) -> list:
    ages = []
    cards = env_html.find(".Card__Wrapper-q6bwfy-0")
    for card in cards:
        if(len(card.find("#housing_age")) > 0):
            ages = []
            for el in card.find(".Legend__LegendValue-e29sxx-3"):
                ages.append(int(str(el.text).split("%")[0])/100)
    return ages

"""
Args:
env_html, can be extracted from nabolag_env_html_render()
Returns:
One normalized housing type of property neighborhood
Formatted as:
[<Mansion>, <Rowhouse>, <Appartment in block>, <Others>]
"""
def housing_type(env_html: requests_html.HTML) -> list:
    types = []
    cards = env_html.find(".Card__Wrapper-q6bwfy-0")
    for card in cards:
        if(len(card.find("#housing_stock")) > 0):
            for el in card.find(".PieChart__SmallLabel-oxga1c-7"):
                if "%" in str(el.text):
                    types.append(int(str(el.text).split("%")[0])/100)
    return types

"""
Args:
env_html, can be extracted from nabolag_env_html_render()
Returns:
Home ownership rate of property neighborhood (float, 0.00 - 1.00)
"""
def home_ownership_rate(env_html: requests_html.HTML) -> float:
    ownership_rate = 0
    cards = env_html.find(".Card__Wrapper-q6bwfy-0")
    for card in cards:
        if(len(card.find("#housing_ownership")) > 0):
            ownership_rate = (int(str(card.find(".PieChart__SmallLabel-oxga1c-7")[0].text).split("%")[0])/100)
    return ownership_rate



"""
Args:
env_html, can be extracted from nabolag_env_html_render()
Returns:
One normalized polling data of neighborhood variables
Formatted as:
[<Safety>, <Noise>, <Friendly neighbors>, <Nice gardens>, <Great roads>]
"""
def polling_env_variables(env_html: requests_html.HTML) -> list:
    poll_data = []
    ratings = env_html.find(".Rating__RatingHeader-ys2jkg-3")
    for rating in ratings:
        poll_data.append(int(str(rating.text).split(" ")[0])/100)
    return poll_data



"""
Args:
env_html, can be extracted from nabolag_env_html_render()
Returns:
One normalized list of housing size in property neighborhood
Formatted as:
[<0 - 60m²>, <60 - 120m²>, <120m² - 200m²>, <Over 200m²>]
"""
def housing_size(env_html: requests_html.HTML) -> list:
    size_list = []
    cards = env_html.find(".Card__Wrapper-q6bwfy-0")
    for card in cards:
        if(len(card.find("#housing_area")) > 0):
            for el in card.find(".Legend__LegendValue-e29sxx-3"):
                if "%" in str(el.text):
                    size_list.append(int(str(el.text).split("%")[0])/100)
    return size_list


"""
Args:
env_html, can be extracted from nabolag_transport_html()
Returns:
neighborhood public transport rating (float, 0.00 - 1.00)
"""
def public_transport_rating(transport_html: requests_html.HTML) -> float:
    rating = 0.00
    for card in transport_html.find(".Card__Wrapper-q6bwfy-0"):
        if len(card.find("#1010")) > 0:
            rating = int(str(card.find(".Rating__RatingHeader-ys2jkg-3")[0].text).split(" ")[0])/100
    return rating

"""
Args:
env_html, can be extracted from nabolag_transport_html()
Returns:
neighborhood public transport rating (float, 0.00 - 1.00)
"""
def traffic_rating(transport_html: requests_html.HTML) -> float:
    rating = 0.00
    for card in transport_html.find(".Card__Wrapper-q6bwfy-0"):
        if len(card.find("#1012")) > 0:
            rating = int(str(card.find(".Rating__RatingHeader-ys2jkg-3")[0].text).split(" ")[0])/100
    return rating


"""
Args:
env_html, can be extracted from nabolag_family_html()
Returns:
neighborhood school rating (float, 0.00 - 1.00)
"""
def school_quality(family_html: requests_html.HTML) -> float:
    rating = 0.00
    for card in family_html.find(".Card__Wrapper-q6bwfy-0"):
        if len(card.find("#1007")) > 0:
            rating = int(str(card.find(".Rating__RatingHeader-ys2jkg-3")[0].text).split(" ")[0])/100
    return rating


"""
Args:
env_html, can be extracted from nabolag_env_html_render()
Returns:
One normalized list of housing size in property neighborhood
Formatted as:
[<0 - 2M>, <2M - 3M>, <3M - 4M>, <4M - 5M>, <5M - 6M>, <6M+>]
"""
def housing_price_distribution(env_html: requests_html.HTML) -> list:
    cards = env_html.find(".Card__Wrapper-q6bwfy-0")
    bars = []
    for card in cards:
        if len(card.find("#housing_prices")) > 0:
            bars = card.find(".BarChart__BarWrapper-sc-1yklinr-1")
            print(bars)
    return one_normalized_list_from_html_graph(bars)




#test if run by main.
if __name__ == "__main__":
    test_code = "147637977"
    env_html = nabolag_env_html_render(test_code)
    print(env_html.find(".Card__Wrapper-q6bwfy-0"))
    print(housing_price_distribution(env_html))