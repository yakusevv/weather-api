import pymongo
import requests

from . import settings

def get_data_collection():
    client = pymongo.MongoClient(
        'mongodb://mongodb:27017/',
        username=settings.DB_USER,
        password=settings.DB_PASSWORD
    )
    return client[settings.DB_NAME].temperature_info


def get_temperature():
    resp = requests.get(
        'https://api.openweathermap.org/data/2.5/weather?'
        f'lat={settings.LAT}&lon={settings.LON}&appid={settings.API_KEY}&units=metric'
    )
    # TODO: retry later if there is no response?
    if resp.status_code != 200:
        raise Exception(f'openweather api error: {resp.status_code}, {resp.reason}')
    return resp.json()['main'].get('temp')
