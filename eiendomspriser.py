import requests
import urllib.parse
import sys
import json

def encode_url_norwegian(params):
        return urllib.parse.urlencode(params)


def scrape(address):
    headers = {
        "Host": "siste.eiendomspriser.no",
        "Connection": "keep-alive",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "DNT": "1",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Referer": "https://siste.eiendomspriser.no/?utm_source=www.auraavis.no&utm_campaign=Widget&utm_medium=Overdragelser%20i%20kart&utm_content=Logo",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "nb-NO,nb;q=0.9,no;q=0.8,nn;q=0.7,en-US;q=0.6,en;q=0.5,da;q=0.4",
        "Cookie": "ASP.NET_SessionId=sqed5hzbx4ltpszdu03hhkco; __uzma=d395d52c-874b-4f1c-854e-f846111093fb; __uzmb=1580308189; 1881_boligpriser_news_v1=true; 1881_boligpriser_tips_v2=true; __uzmc=747534074486; __uzmd=1580986384"
    }

    params = {
        "query": address,
        "sort": "01",
        "fromDate": "",
        "toDate": "",
        "placeFilter": "",
        "municipalities": "",
        "_": 1580986385084
    }

    url = "https://siste.eiendomspriser.no/service/search"
    url = url + "?" + encode_url_norwegian(params)

    r = requests.get(url, headers=headers)

    return r.json()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Invalid number of arguments.\n\nUsage:\n$ python finn.py "Adresse"')
        exit(1)

    address = sys.argv[1]
    data = scrape(address)
    print(json.dumps(data, indent=2, ensure_ascii=False))
