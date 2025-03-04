from tqdm.contrib.concurrent import process_map  # or thread_map
import pandas as pd
import time
import numpy as np
from multiprocessing import Manager
import traceback
import sys
import os
from tqdm import tqdm

import geocode
import finncode
import finn
import neighborhood
import eiendomspriser
from zip import zip_price_estimate


def is_windows():
    return os.name == 'nt'


if __name__ == '__main__':
    if not (len(sys.argv) == 2 or len(sys.argv) == 3):
        print('Invalid number of arguments.\n\nUsage:\n$ python dataset.py finn_search_url [output-file.csv]\n',
              'Example: python dataset.py "https://www.finn.no/realestate/homes/search.html?filters=&geoLocationName=Trondheim&lat=63.42128&lon=10.42544&radius=1200"\n'
              'Example: python dataset.py "https://www.finn.no/realestate/homes/search.html?filters=&geoLocationName=Trondheim&lat=63.42128&lon=10.42544&radius=1200" finn_dataset.csv\n')
        exit(1)

    finn_search_url = sys.argv[1]

    output_file = '../finn_dataset.csv'
    if len(sys.argv) == 3:
        output_file = sys.argv[2]

    print('\nFetching Finn-codes...')
    finn_codes = finncode.scrape_category(finn_search_url, show_progress=True)

    # set up list as shared
    manager = Manager()
    ads = manager.list()

    old_codes = []
    bad_codes = []
    old_bad_codes = np.asarray([])
    old_df = None

    if os.path.exists(output_file):
        old_df = pd.read_csv(output_file)
        for url in list(old_df['url']):
            old_codes.append(url.split('=')[1])
        finn_codes = list(set(finn_codes) - set(old_codes))

    if os.path.exists("bad_codes.npy"):
        old_bad_codes = np.load("bad_codes.npy")

    finn_codes = list(set(finn_codes) - set(old_bad_codes))

    def scrape_and_process(finn_code):
        tries_left = 10
        while tries_left:
            try:
                tries_left -= 1
                ad_data = finn.scrape_ad(finn_code)

                if ad_data and 'Totalpris' not in ad_data and 'Verditakst' not in ad_data:
                    bad_codes.append(finn_code)
                    return

                ad_data = finn.interpolate_data_(ad_data)
                ad_data = finn.data_cleaner(ad_data)

                # Get average square meter price for this zip code
                ad_data['zip_price_estimate'] = zip_price_estimate(int(ad_data['Bruksareal']),
                                                                   str(ad_data['Postnummer']))
                # eiendomspriser
                processed_address = ad_data['Postadresse'].split(',')[0].split('-')[0].split('/')[0]
                sale = eiendomspriser.scrape(processed_address)
                if len(sale['Properties']) > 0:
                    ad_data['lat'] = sale['Properties'][0]['Coordinate']['Lat']
                    ad_data['lon'] = sale['Properties'][0]['Coordinate']['Lon']
                else:
                    ad_data.update(geocode.get_geocode(ad_data['Postadresse'].split(',')[-1]))

                # Nabolag profil
                ad_data.update(neighborhood.scrape(ad_data['lat'], ad_data['lon']))

                # Ignore unbuilt listings
                if 'Byggeår' in ad_data and 'Totalpris' in ad_data:
                    ads.append(ad_data)
                else:
                    bad_codes.append(finn_code)
                break
            except ConnectionError as e:
                time.sleep(2)

            except Exception as e:
                print('error on', finn_code)
                traceback.print_tb(e.__traceback__)
                bad_codes.append(finn_code)
                break

    print('Fetching ads...')
    if is_windows():
        # kommenter inn denne for å kjøre prosessen singulært (fungerer på windows og linux)
        print('Running Windows compatible version. This program runs faster on Linux or Linux subsystem for Windows.')
        for code in tqdm(finn_codes):
            scrape_and_process(code)
    else:
        # kommenter inn denne for å kjøre prosessen parallellt (fungerer kun på linux?)
        r = process_map(scrape_and_process, finn_codes, max_workers=32)

    df = pd.DataFrame(list(ads))

    # Removing columns with few values
    thresh = len(df) * .9
    df.dropna(thresh=thresh, axis=1, inplace=True)

    # Filling missing values
    for col in df.columns:
        if np.issubdtype(df[col].dtype, np.number):
            df[col].fillna((df[col].mean()), inplace=True)

    # To camelcase and remove æøå
    df.columns = [col.lower().replace(' ', '_').replace('æ', 'ae').replace('ø', 'oe').replace('å', 'aa') for col in
                  df.columns]

    np.save("bad_codes.npy", np.concatenate((np.array(bad_codes), old_bad_codes)))
    # rare

    # df = df.dropna(axis=1)
    if old_df is not None:
        df = pd.concat([old_df, df], ignore_index=True)
    df.to_csv(output_file, index=False)

    print("Saved CSV file to", output_file)
