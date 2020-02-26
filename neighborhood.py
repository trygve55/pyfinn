import requests
import sys
import json


def scrape(lat, lon):
    headers = {
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Sec-Fetch-Dest': 'empty',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36',
        'DNT': '1',
        'Accept': '*/*',
        'Origin': 'https://profil.nabolag.no',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://profil.nabolag.no/171527942/sammenlign/2056029/ChIJ-dpIdbAxbUYRGvdYORPSMKs',
        'Accept-Language': 'nb-NO,nb;q=0.9,no;q=0.8,nn;q=0.7,en-US;q=0.6,en;q=0.5,da;q=0.4'
    }

    params = {
        "orderLineId": 2056029,
        "lat": lat,
        "lon": lon
    }

    url = "https://profil2-api.nabolag.no/AddressSearch/compare"

    r = requests.post(url, headers=headers, params=params)

    return fix_json(r.json())


def fix_json(data, path="neighborhood"):
    if isinstance(data, dict) and 'location' in data:
        del data['location']

    output = {}

    if isinstance(data, dict):
        for key in data.keys():
            output.update(fix_json(data[key], path + "_" + str(key)))
    elif isinstance(data, list):
        for i in range(len(data)):
            if isinstance(data[i], dict) and ('group' in data[i].keys() or 'name' in data[i].keys()):
                if 'group' in data[i].keys():
                    output.update({(path + '_' + data[i]['group']).lower(): data[i]['percent']['B']})
                elif 'name' in data[i].keys():
                    output.update({(path + '_' + data[i]['name'].replace(' ', '_')).lower(): data[i]['score']['B']})
            else:
                output.update(fix_json(data[i], path + "_" + str(i)))
    else:
        return {path: data}
    return output


if __name__ == '__main__':
    if len(sys.argv) != 3 and sys.argv[1].isdigit() and sys.argv[2].isdigit():
        print('Invalid number of arguments.\n\nUsage:\n$ python neighborhood.py "lat" "lon"')
        exit(1)

    lat = float(sys.argv[1])
    lon = float(sys.argv[2])
    data = scrape(lat, lon)
    print(json.dumps(data, indent=2, ensure_ascii=False))
