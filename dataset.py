import finncode
import finn
from tqdm import tqdm
import pandas as pd
import time
from finn import _interpolate_data_, _data_cleaner
import numpy as np

if __name__ == '__main__':
    codes = finncode.scrape_category("https://www.finn.no/realestate/homes/search.html?geoLocationName=Kristiansund%2C+M%C3%B8re+og+Romsdal&lat=63.11045&lon=7.72795&radius=1500")
    ads = []
    for code in tqdm(codes):
        tries_left = 3
        ad_data = None
        while tries_left:
            try:
                tries_left -= 1
                ad_data = finn.scrape_ad(code)
                ad_data = _interpolate_data_(ad_data)
                ad_data = _data_cleaner(ad_data)

                if 'Byggeår' in ad_data:
                    ads.append(ad_data)
                break
            except:
                print('error on', code)
                time.sleep(2)

    df = pd.DataFrame(ads)

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
