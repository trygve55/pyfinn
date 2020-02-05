import json
import re
import sys

import dateparser
from fake_useragent import UserAgent
from requests_html import HTMLSession
from geopy.geocoders import Nominatim
from geopy import distance

session = HTMLSession()
ua = UserAgent()

geolocator = Nominatim(user_agent="finnpy")

keywords =[['parkering', 'carport', 'karport', 'car-port', 'kar-port', 'garasjen', 'garasje', 'parkeringsplass', 'p-plass'],
    ['fiber', 'fibernett', 'fibertilkobling', 'fiber-nett', 'fiber nett', 'fiber-tilkobling', 'fiber tilkobling'],
    ['kabel-tv', 'kabeltv', 'kabel tv'],
    ['tg 0', 'tg0', 'tilstandsgrad 0', 'tg: 0', 'tg:0'],
    ['tg 1', 'tg1', 'tilstandsgrad 1', 'tg: 1', 'tg:1'],
    ['tg 2', 'tg2', 'tilstandsgrad 2', 'tg: 2', 'tg:2'],
    ['vedovn', 'peis', 'vedfyring', 'ved ovn', 'ved fyring'],
    ['varmepumpe', 'varme pumpe', 'varme-pumpe', 'air-condition', 'air condition'],
    ['fjernvarme', 'fjern varme', 'fjern-varme', 'jord-varme', 'jordvarme', 'jord varme', 'grunnvarme', 'grunn varme', 'grunn-varme'],
    ['terasse', 'terrasse', 'balkong', 'veranda', 'takterasse', 'takterrasse', 'markterrasse', 'markterasse'],
    ['utsikt', 'panoramautsikt', 'sjøutsikt', 'havutsikt', 'fjordutsikt'],
    ['kjøkkenøy', 'integrert hvitevarer', 'integrert kjøkken', 'hth', 'kvik'],
    ['hage', 'plen'],
    ['garderobe', 'walk-in', 'walk in', 'walkin'],
    ['oppusset', 'renovert', 'totalrenovert', 'moderne'],
    ['oppussingsobjekt', 'oppussingsprosjekt', 'oppussings prosjekt', 'oppussingsobjekt'],
    ['bod', 'utebod', 'utehus', 'skur', 'vedskjul']]


def _clean(text):
    text = text.replace('\xa0', ' ').replace(',-', '').replace(' m²', '')
    try:
        text = int(re.sub(r'kr$', '', text).replace(' ', ''))
    except ValueError:
        pass

    return text


def _parse_neighbourhood_info(html):
    html.render()
    for el in html.find('div'):
        if 'class' in el.attrs and 'nabolag-widget' in el.attrs['class']:
            print(el)


def _parse_keywords(html):
    data = {}
    for el in html.find('div'):
        if 'data-owner' in el.attrs and el.attrs['data-owner'] == 'adView':
            text = el.text
            for words in keywords:
                data[words[0]] = False
                for i in words:
                    if i in text:
                        data[words[0]] = True
                        break
    return data


def _parse_data_lists(html):
    data = {}
    skip_keys = ['Mobil', 'Fax']  # Unhandled data list labels

    data_lists = html.find('dl')
    for el in data_lists:
        values_list = iter(el.find('dt, dd'))
        for a in values_list:
            _key = a.text

            a = next(values_list)
            if _key in skip_keys:
                continue
            #Cleanup tomteareal
            if _key == 'Tomteareal':
                _key = 'Tomteareal (eiet)'
                data[_key] = int(_clean(a.text).split()[0])
            else:
                data[_key] = _clean(a.text)

    return data


def _get_geocode(address):
    new_address = address.split(',')
    new_new_address = ""
    for s in new_address[0].split():
        new_new_address += s
        if s.isdigit():
            break
        new_new_address += " "

    if len(new_address) == 2:
        new_address = new_new_address + "," + new_address[1]

    location = geolocator.geocode(new_address)
    return location


def _get_distance_to_city_center(location):
    location2 = (63.4304324, 10.3946152) #Trondheim
    return distance.geodesic((location.latitude, location.longitude), location2).km


def _parse_geodata(address):
    data = {}
    location = _get_geocode(address)
    data['latitude'] = location.latitude
    data['longitude'] = location.longitude
    data['distance_to_centrum'] = _get_distance_to_city_center(location)

    return data


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


def _calc_price(ad_data):
    debt = ad_data.get('Fellesgjeld', 0)
    cost = ad_data.get('Omkostninger', 0)
    return ad_data['Totalpris'] - debt - cost


def scrape_ad(finnkode):
    url = 'https://www.finn.no/realestate/homes/ad.html?finnkode={code}'.format(code=finnkode)
    r = session.get(url, headers={'user-agent': ua.random})

    r.raise_for_status()

    html = r.html

    postal_address_element = html.find('h1 + p', first=True)
    if not postal_address_element:
        return

    ad_data = {
        'Postadresse': postal_address_element.text,
        'url': url,
    }

    ad_data.update(_parse_data_lists(html))
    ad_data.update(_parse_geodata(ad_data['Postadresse']))
    ad_data.update(_parse_keywords(html))
    #print(_parse_neighbourhood_info(html))

    ad_data['Prisantydning'] = _calc_price(ad_data)

    return ad_data


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Invalid number of arguments.\n\nUsage:\n$ python finn.py FINNKODE')
        exit(1)

    ad_url = sys.argv[1]
    ad = scrape_ad(ad_url)
    print(json.dumps(ad, indent=2, ensure_ascii=False))
