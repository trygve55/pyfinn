from tqdm.contrib.concurrent import process_map  # or thread_map
import pandas as pd
import time
import numpy as np
from multiprocessing import Manager
import traceback
from tqdm import tqdm
import os.path
from os import path

import geocode
import finncode
import finn
import neighborhood
import eiendomspriser
from zip import zip_price_estimate

if __name__ == '__main__':
    finn_codes = finncode.scrape_category("https://www.finn.no/realestate/homes/search.html?filters=&location=0.20061&location=0.22030&location=1.22030.20046&location=1.22030.20045&location=1.22030.22105&location=1.22030.20052")

    #set up list as shared
    manager = Manager()
    ads = manager.list()
    old_codes = []
    bad_codes = []
    old_bad_codes = np.asarray([])

    if path.exists("test.csv"):
        old_df = pd.read_csv("test.csv")
        for url in list(old_df['url']):
            old_codes.append(url.split('=')[1])
        finn_codes = list(set(finn_codes) - set(old_codes))
    
    if path.exists("bad_codes.npy"):
        old_bad_codes = np.load("bad_codes.npy")
    
    finn_codes = list(set(finn_codes) - set(old_bad_codes))

    def scrape_and_process(finn_code):
        tries_left = 3
        while tries_left:
            try:
                tries_left -= 1
                ad_data = finn.scrape_ad(finn_code)

                if ad_data and 'Totalpris' not in ad_data and 'Verditakst' not in ad_data:
                    bad_codes.append(finn_code)
                    return

                ad_data = finn.interpolate_data_(ad_data)
                ad_data = finn.data_cleaner(ad_data)
                print(ad_data['Bruksareal'])
                print(ad_data['Postnummer'])
                ad_data['zip_price_estimate'] = zip_price_estimate(int(ad_data['Bruksareal']), str(ad_data['Postnummer']))
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
                if 'Byggeår' in ad_data and 'Totalpris' in ad_data:
                    ads.append(ad_data)
                else:
                    bad_codes.append(finn_code)
                break
            except Exception as e:
                print('error on', finn_code)
                traceback.print_tb(e.__traceback__)
                bad_codes.append(finn_code)
                time.sleep(2)

    #kommenter inn denne for å kjøre prosessen parallellt (fungerer kun på linux?)
    r = process_map(scrape_and_process, finn_codes, max_workers=32)
    
    #kommenter inn denne for å kjøre prosessen singulært (fungerer på windows og linux)
    #for code in tqdm(finn_codes):
    #    scrape_and_process(code)

    df = pd.DataFrame(list(ads))


    thresh = len(df) * .9
    df.dropna(thresh=thresh, axis=1, inplace=True)

    for col in df.columns:
        if np.issubdtype(df[col].dtype, np.number):
            df[col].fillna((df[col].mean()), inplace=True)

    df.columns = [col.lower().replace(' ', '_').replace('æ', 'ae').replace('ø', 'oe').replace('å', 'aa') for col in df.columns]

    np.save("bad_codes.npy", np.concatenate((np.array(bad_codes),old_bad_codes)))
    #rare
    #df = df.dropna(axis=1)
    if path.exists("test.csv"):
        df = pd.concat([old_df,df],ignore_index=True)
    df.to_csv(r'test.csv', index=False)

    print("Saved CSV file to test.csv")