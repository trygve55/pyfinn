import finncode
import finn
from tqdm.contrib.concurrent import process_map  # or thread_map
import pandas as pd
import time
from finn import _interpolate_data_, _data_cleaner
import numpy as np
from multiprocessing import Manager
import traceback
from neihgborhood_analyzer.neighbor import neighborhood_profiler

if __name__ == '__main__':
    finn_codes = finncode.scrape_category("https://www.finn.no/realestate/homes/search.html?geoLocationName=Trondheim&lat=63.42128&lon=10.42544&radius=500")

    #set up list as shared
    manager = Manager()
    ads = manager.list()

    def scrape_and_process(finn_code):
        tries_left = 3
        while tries_left:
            try:
                tries_left -= 1
                ad_data = finn.scrape_ad(finn_code)
                ad_data = _interpolate_data_(ad_data)
                ad_data = _data_cleaner(ad_data)
                ad_data.update(neighborhood_profiler(finn_code))

                #Ignore unbuilt listings
                if 'Byggeår' in ad_data:
                    ads.append(ad_data)
                break
            except Exception as e:
                print('error on', finn_code)
                traceback.print_tb(e.__traceback__)
                time.sleep(2)

    r = process_map(scrape_and_process, finn_codes, max_workers=1)

    df = pd.DataFrame(list(ads))

    #soverom
    df['Soverom'] = pd.to_numeric(df['Soverom'])
    df = df[df['Soverom'].notna()]

    #pris
    df['Totalpris'].replace('  ', np.nan, inplace=True)
    df = df.dropna(subset=['Totalpris'])

    #rare
    #df = df.dropna(axis=1)
    df.to_csv(r'test.csv', index=False)

    print("Saved CSV file to test.csv")
