from fake_useragent import UserAgent
from requests_html import HTMLSession
import requests_html
from time import sleep
import traceback
from random import random


session = HTMLSession()
ua = UserAgent()







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


def krogsveen_html(zip_code_str : str) -> requests_html.HTML:
    return fetch("https://www.krogsveen.no/prisstatistikk?zipCode=" + zip_code_str)


def zip_square_meter_mean_price(zip_code_str : str) -> int:
    krog_html = krogsveen_html(zip_code_str)
    return int(krog_html.find(".Typography__GigaSans-sc-1delhdg-0")[1].text.replace(' ', ''))


def zip_price_estimate(size : int, zip : str) -> int:
    return int(size) * zip_square_meter_mean_price(zip)







if __name__ == "__main__":
    print(zip_price_estimate(100, "0257"))

