import json
import re
import sys

import dateparser
from fake_useragent import UserAgent
from requests_html import HTMLSession
import requests_html




session = HTMLSession()
ua = UserAgent()


'''Args:
finn_code as str
Returns:
Html of the "people" stats page at nabolag.no
'''
def nabolag_people_html(finn_code:str):
    complete_url = "https://profil.nabolag.no/" + finn_code + "/menneskene"
    request = session.get(complete_url, headers={'user-agent': ua.random})
    request.raise_for_status()
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
Finn codes as strings
Returns:
Function that returns 1-normalized income distribution for neighborhood through finncode, 
Brackets are formatted as:
[<0-100000>, <100000-200000>, <200000-400000>, <400000-500000>, <500000-800000>, <800000->]
"""
def income_distribution(finn_code: str) -> list:
    html = nabolag_people_html(finn_code)
    cards = html.find(".BarChart-sc-1yklinr-0")
    bars = cards[1].find(".BarChart__BarWrapper-sc-1yklinr-1")
    return one_normalized_list_from_html_graph(bars)



"""
Args:
finn codes as strings
Returns:
One normalized age distribution of property neighborhood
Formatted as:
[<0-12>, <13-18>, <19-34>, <35-64>, <65+>]
"""
def age_distribution(finn_code: str) -> list:
    html = nabolag_people_html(finn_code)
    cards = html.find(".BarChart-sc-1yklinr-0")
    bars = cards[0].find(".BarChart__BarWrapper-sc-1yklinr-1")
    return one_normalized_list_from_html_graph(bars)



"""
Args:
finn code as string
Returns:
One normalized marital status distribrution of property neighborhood
Formatted as:
[<Not married>, <Married>, <Separated>, <Widow>]
"""
def marital_status_distribution(finn_code: str) -> list:
    html = nabolag_people_html(finn_code)
    print(html.find(".recharts-responsive-container"))
    

if __name__ == "__main__":
    marital_status_distribution("147637977")