import os
import json
import time
import dotenv
import traceback
import portalocker
from os import environ
from pathlib import Path
from geopy.geocoders import MapBox


dotenv.load_dotenv(override=True)
GEOLOCATOR = [None]
SCRIPT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))


def address_to_long_lat(city, state, addressline1, addressline2, postcode, country):
    """

    :param city: e.g.
    :param state: e.g.
    :param addressline1: e.g.
    :param addressline2: e.g.
    :param postcode: e.g.
    :param country: e.g.
    :return:
    """
    with open(SCRIPT_DIR / '..' / 'data' / 'geolocate_cache.json',
              'r', encoding='utf-8') as f:

        portalocker.lock(f, portalocker.LOCK_SH)
        try:
            address_cache = json.loads(f.read())
        finally:
            portalocker.unlock(f)

    address = []
    if addressline2:
        address.append(addressline2)
    if addressline1:
        address.append(addressline1)
    if city:
        address.append(city)
    if state:
        address.append(state)
    if postcode:
        address.append(postcode)
    if country:
        address.append(country)
    address = ', '.join(address)

    if address in address_cache:
        item = address_cache[address]
        if item or True:
            return item

    if not GEOLOCATOR[0]:
        GEOLOCATOR[0] = MapBox(api_key=environ['MAPBOX_KEY'], user_agent='https://www.covid-19-au.com')

    try:
        location = GEOLOCATOR[0].geocode(address)
        if location:
            longlat = (location.longitude, location.latitude)
    except:
        # Make sure it doesn't keep trying to get the lat/long
        # when the service didn't find the location!
        traceback.print_exc()
        longlat = None

    time.sleep(1)
    address_cache[address] = longlat

    with open(SCRIPT_DIR / '..' / 'data' / 'geolocate_cache.json',
              'w', encoding='utf-8') as f:

        portalocker.lock(f, portalocker.LOCK_EX)
        try:
            f.write(json.dumps(address_cache, ensure_ascii=False, indent=2))
        finally:
            portalocker.unlock(f)

    return longlat
