from tqdm.contrib.concurrent import process_map  # or thread_map
import pandas as pd
import time
import numpy as np
from multiprocessing import Manager
import traceback

import geocode
import finncode
import finn
import neighborhood
import eiendomspriser

if __name__ == '__main__':
    finn_codes = finncode.scrape_category("https://www.finn.no/realestate/homes/search.html?geoLocationName=Trondheim&lat=63.42128&lon=10.42544&radius=3000")

    #set up list as shared
    manager = Manager()
    ads = manager.list()

    def scrape_and_process(finn_code):
        tries_left = 3
        while tries_left:
            try:
                tries_left -= 1
                ad_data = finn.scrape_ad(finn_code)

                if 'Totalpris' not in ad_data and 'Verditakst' not in ad_data:
                    return

                ad_data = finn.interpolate_data_(ad_data)
                ad_data = finn.data_cleaner(ad_data)

                #eiendomspriser
                processed_address = ad_data['Postadresse'].split(',')[0].split('-')[0].split('/')[0]
                sale = eiendomspriser.scrape(processed_address)
                if len(sale['Properties']) > 0:
                    ad_data['lat'] = sale['Properties'][0]['Coordinate']['Lat']
                    ad_data['lon'] = sale['Properties'][0]['Coordinate']['Lon']
                else:
                    ad_data.update(geocode.get_geocode(ad_data['Postadresse'].split(',')[-1]))

                #Nabolag profil
                ad_data.update(neighborhood.scrape(ad_data['lat'], ad_data['lon']))

                #Ignore unbuilt listings
                if 'Byggeår' in ad_data:
                    ads.append(ad_data)
                break
            except Exception as e:
                print('error on', finn_code)
                traceback.print_tb(e.__traceback__)
                time.sleep(2)

    r = process_map(scrape_and_process, finn_codes, max_workers=12)

    df = pd.DataFrame(list(ads))

    #soverom
    df['Soverom'] = pd.to_numeric(df['Soverom'])
    df = df[df['Soverom'].notna()]

    #pris
    df['Totalpris'].replace('  ', np.nan, inplace=True)
    df = df.dropna(subset=['Totalpris'])

    df = df.loc[:, df.isnull().mean() < .9]

    #rare
    #df = df.dropna(axis=1)
    df.to_csv(r'test.csv', index=False)

    print("Saved CSV file to test.csv")
