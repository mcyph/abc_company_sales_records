import os
import pycountry
import pandas as pd
from pathlib import Path

from address_to_long_lat import address_to_long_lat


SCRIPT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
COUNTRY_CACHE = {}


def __get_sales_data():
    with open(SCRIPT_DIR / '..' / 'data' / 'sales_data_sample.csv',
              'r', encoding='windows-1252') as f:

        df = pd.read_csv(f, na_filter=False, dtype={
            'ORDERNUMBER': 'uint32',
            'QUANTITYORDERED': 'uint32',
            'PRICEEACH': 'float64',
            'ORDERLINENUMBER': 'uint32',
            'SALES': 'float64',
            'ORDERDATE': 'unicode',  # 2/24/2003 0:00
            #'STATUS': 'category',  # pd.Categorical(categories=('Shipped', 'Disputed', 'In Process', 'Cancelled')),

            # Time info
            'QTR_ID': 'uint8',
            'MONTH_ID': 'uint8',
            'YEAR_ID': 'uint16',

            # Product info
            #'PRODUCTLINE': 'category',
            'MSRP': 'float64',  # Could probably be uint32
            'PRODUCTCODE': 'unicode',

            # Customer info (name/address/region)
            'CUSTOMERNAME': 'unicode',  # Name of business
            'PHONE': 'unicode',
            'ADDRESSLINE1': 'unicode',
            'ADDRESSLINE2': 'unicode',
            'CITY': 'unicode',
            'STATE': 'unicode',
            'POSTALCODE': 'unicode',
            #'COUNTRY': 'category',
            #'TERRITORY': 'category',
            'CONTACTLASTNAME': 'unicode',
            'CONTACTFIRSTNAME': 'unicode',

            # Order categorization
            #'DEALSIZE': 'category',  # pd.Categorical(categories=('Small', 'Medium', 'Large')),
        })

    # American dates :P
    # All the times seem to be 0:00
    df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'],
                                     dayfirst=False,
                                     yearfirst=False)
    #df['COUNTRYCODE'] = FIXME

    #print(df.STATUS.unique())
    #print(df.PRODUCTLINE.unique())
    #print(df.COUNTRY.unique())
    #print(df.TERRITORY.unique())
    #print(df.DEALSIZE.unique())

    lats = []
    longs = []
    alpha3s = []
    alpha2s = []

    for x, row in df.iterrows():
        longlat = address_to_long_lat(row['CITY'], row['STATE'],
                                      row['ADDRESSLINE1'], row['ADDRESSLINE2'],
                                      row['POSTALCODE'], row['COUNTRY'])
        if longlat:
            long, lat = longlat
            lats.append(lat)
            longs.append(long)
        else:
            lats.append(None)
            longs.append(None)

        if not row['COUNTRY'] in COUNTRY_CACHE:
            try:
                COUNTRY_CACHE[row['COUNTRY']] = pycountry.countries.get(name=row['COUNTRY'])
                if not COUNTRY_CACHE[row['COUNTRY']]:
                    raise KeyError()
            except KeyError:
                COUNTRY_CACHE[row['COUNTRY']] = pycountry.countries.search_fuzzy(row['COUNTRY'])[0]

        country_dict = COUNTRY_CACHE[row['COUNTRY']]
        alpha2s.append(country_dict.alpha_2)
        alpha3s.append(country_dict.alpha_3)

    df['LAT'] = lats
    df['LONG'] = longs
    df['ALPHA2'] = alpha2s
    df['ALPHA3'] = alpha3s
    return df


df = __get_sales_data()

ACRONYM_TO_TERRITORIES = {
    'APAC': 'Asia Pacific',
    'NA': 'North America',
    'EMEA': 'Europe, Middle East and Africa',
    'Japan': 'Japan',
}
TERRITORIES_TO_ACRYONYM = {
    v: k for k, v in ACRONYM_TO_TERRITORIES.items()
}
TERRITORIES_TO_COUNTRIES = {
    k: list(df[df.TERRITORY == k].COUNTRY.unique()) for k in ACRONYM_TO_TERRITORIES
}


def get_sales_data():
    return df


if __name__ == '__main__':
    print(get_sales_data())
