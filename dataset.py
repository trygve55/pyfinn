import finncode
import finn
from tqdm import tqdm
import pandas as pd

if __name__ == '__main__':
    codes = finncode.scrape_category("https://www.finn.no/realestate/homes/search.html?geoLocationName=Kristiansund%2C+M%C3%B8re+og+Romsdal&lat=63.11045&lon=7.72795&radius=300")
    ads = []
    for code in tqdm(codes):
        ads.append(finn.scrape_ad(code))

    df = pd.DataFrame(ads)
    df.to_csv(r'test.csv')

    print("Saved CSV file to test.csv")
