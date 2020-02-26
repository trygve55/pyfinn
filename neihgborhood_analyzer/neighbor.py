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
def income_distribution(nabolag_html: requests_html.HTML) -> dict:
    cards = nabolag_html.find(".BarChart-sc-1yklinr-0")
    bars = cards[1].find(".BarChart__BarWrapper-sc-1yklinr-1")
    one_normalized_list = one_normalized_list_from_html_graph(bars)
    return {
        "neighborhood_income_0_100000" : distribution[0],
        "neighborhood_income_100000_200000" : distribution[1],
        "neighborhood_income_200000_400000" : distribution[2],
        "neighborhood_income_400000_500000" : distribution[3],
        "neighborhood_income_500000_800000" : distribution[4],
        "neighborhood_income_800000+" : distribution[5]
    }



"""
Args:
nabolag_html, can be extracted from nabolag_people_html_render()
Returns:
One normalized age distribution of property neighborhood
Formatted as:
[<0-12>, <13-18>, <19-34>, <35-64>, <65+>]
"""
def age_distribution(nabolag_HTML : requests_html.HTML) -> dict:
    cards = nabolag_html.find(".BarChart-sc-1yklinr-0")
    bars = cards[0].find(".BarChart__BarWrapper-sc-1yklinr-1")
    distribution =  one_normalized_list_from_html_graph(bars)

    retun {
        "neighborhood_age_0_12" : distribution[0],
        "neighborhood_age_13_18" : distribution[1],
        "neighborhood_age_19_34" : distribution[2],
        "neighborhood_age_35_64" : distribution[3],
        "neighborhood_age_65+" : distribution[4]
    }




"""
Args:
nabolag_html, can be extracted from nabolag_people_html_render()
Returns:
One normalized marital status distribrution of property neighborhood
Formatted as:
[<Not married>, <Married>, <Separated>, <Widow>]
"""
def marital_status_distribution(people_html: requests_html.HTML) -> dict:
    responsive_container = people_html.find(".Legend__LegendValue-e29sxx-3")
    marital_status = []
    for el in responsive_container:
        marital_status.append(int(str(el.text).split("%")[0])/100)
    return {
        "Not_married" : marital_status[0],
        "Married" : marital_status[1],
        "Separated" : marital_status[2],
        "Widow" : marital_status[3]
    }



"""
Args:
env_html, can be extracted from nabolag_env_html_render()
Returns:
One normalized house age distribution of property neighborhood
Formatted as:
[<0 - 10 yrs>, <10 - 30 yrs>, <30 - 50yrs>, <more than 50yrs>]
"""
def house_age_distribution(env_html: requests_html.HTML) -> dict:
    ages = []
    cards = env_html.find(".Card__Wrapper-q6bwfy-0")
    for card in cards:
        if(len(card.find("#housing_age")) > 0):
            ages = []
            for el in card.find(".Legend__LegendValue-e29sxx-3"):
                ages.append(int(str(el.text).split("%")[0])/100)
    return {
        "neighborhood_ages_0_10yr" : ages[0],
        "neighborhood_ages_10_30yr" : ages[1],
        "neighborhood_ages_30_50yr" : ages[2],
        "neighborhood_ages_50+yrs" : ages[3]
    }

"""
Args:
env_html, can be extracted from nabolag_env_html_render()
Returns:
One normalized housing type of property neighborhood
Formatted as:
[<Mansion>, <Rowhouse>, <Appartment in block>, <Others>]
"""
def housing_type(env_html: requests_html.HTML) -> dict:
    types = []
    cards = env_html.find(".Card__Wrapper-q6bwfy-0")
    for card in cards:
        if(len(card.find("#housing_stock")) > 0):
            for el in card.find(".PieChart__SmallLabel-oxga1c-7"):
                if "%" in str(el.text):
                    types.append(int(str(el.text).split("%")[0])/100)
    return {
        "Neighborhood_Mansion_rate" : types[0]
        "Neighborhood_Rowhouse_rate" : types[1]
        "Neighborhood_block_appartment_rate" : types[2]
        "Neighborhood_Others_rate" : types[3]
    }

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
def polling_env_variables(env_html: requests_html.HTML) -> dict:
    poll_data = []
    ratings = env_html.find(".Rating__RatingHeader-ys2jkg-3")
    for rating in ratings:
        poll_data.append(int(str(rating.text).split(" ")[0])/100)
    return {
        "Neihgborhood_safety_rating" : poll_data[0],
        "Neihgborhood_noise_rating" : poll_data[1],
        "Neihgborhood_friendly_neighboors_rating" : poll_data[2],
        "Neihgborhood_nice_gardens_rating" : poll_data[3],
        "Neihgborhood_roads_rating" : poll_data[4]
    }



"""
Args:
env_html, can be extracted from nabolag_env_html_render()
Returns:
One normalized list of housing size in property neighborhood
Formatted as:
[<0 - 60m²>, <60 - 120m²>, <120m² - 200m²>, <Over 200m²>]
"""
def housing_size(env_html: requests_html.HTML) -> dict:
    size_list = []
    cards = env_html.find(".Card__Wrapper-q6bwfy-0")
    for card in cards:
        if(len(card.find("#housing_area")) > 0):
            for el in card.find(".Legend__LegendValue-e29sxx-3"):
                if "%" in str(el.text):
                    size_list.append(int(str(el.text).split("%")[0])/100)
    return {
        "Neighborhood_house_size_0m_60m" : size_list[0]
        "Neighborhood_house_size_60m_120m" : size_list[1]
        "Neighborhood_house_size_120m_200m" : size_list[2]
        "Neighborhood_house_size_over200m" : size_list[3]
    }


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
def housing_price_distribution(env_html: requests_html.HTML) -> dict:
    cards = env_html.find(".Card__Wrapper-q6bwfy-0")
    bars = []
    for card in cards:
        if len(card.find("#housing_prices")) > 0:
            bars = card.find(".BarChart__BarWrapper-sc-1yklinr-1")
    one_normalized_list = one_normalized_list_from_html_graph(bars)
    return {
        "neighborhood_housing_prices_0M_2M" : one_normalized_list[0]
        "neighborhood_housing_prices_2M_3M" : one_normalized_list[1]
        "neighborhood_housing_prices_3M_4M" : one_normalized_list[2]
        "neighborhood_housing_prices_4M_5M" : one_normalized_list[3]
        "neighborhood_housing_prices_5M_6M" : one_normalized_list[4]
        "neighborhood_housing_prices_6M+" : one_normalized_list[5]
    }

def neighborhood_profiler(finn_code: str) -> dict:
    env_html = nabolag_env_html_render(finn_code)
    family_html = nabolag_family_html(finn_code)
    people_html = nabolag_people_html(finn_code)
    transport_html = nabolag_transport_html(finn_code)

    data = {}

    data.update(house_age_distribution(env_html))
    data.update(housing_price_distribution(env_html))
    data.update(housing_size(env_html))
    data.update(polling_env_variables(env_html))
    data.update(housing_type(env_html))
    data.update(marital_status_distribution(people_html))
    data.update(age_distribution(people_html))
    data.update(income_distribution(people_html))

    data["neighborhood_home_ownership_rate"] = home_ownership_rate(env_html)
    data["neighborhood_school_quality"] = school_quality(family_html)
    data["neighborhood_traffic_rating"] = traffic_rating(transport_html)
    data["neighborhood_public_transport_rating"] = public_transport_rating(transport_html)
    #data["neighborhood_"] =

    return data


#test if run by main.
if __name__ == "__main__":
    test_code = "147637977"
    env_html = nabolag_env_html_render(test_code)
    print(env_html.find(".Card__Wrapper-q6bwfy-0"))
    print(housing_price_distribution(env_html))