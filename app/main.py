import os
import requests

from fastapi import FastAPI

app = FastAPI()


API_KEY = os.environ.get('API_KEY')
LAT = os.environ.get('LAT')
LON = os.environ.get('LON')

def get_temperature():
    resp = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric'
    )
    if resp.status_code != 200:
        raise Exception(f'openweather api error: {resp.status_code}, {resp.reason}')
    return resp.json()['main'].get('temp')

# test
@app.get("/api/temperature_info/")
def get_temperature_info(date: str):
    try:
        temp = get_temperature()
    except Exception as exc:
        return {'error': str(exc)}
    return {'test': temp}
