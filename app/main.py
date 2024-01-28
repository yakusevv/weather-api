import datetime
import os
import requests
import pymongo

from fastapi import FastAPI
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from fastapi_scheduler import SchedulerAdmin

API_KEY = os.environ.get('API_KEY')
LAT = os.environ.get('LAT')
LON = os.environ.get('LON')


app = FastAPI()

site = AdminSite(settings=Settings(database_url_async='sqlite+aiosqlite:///amisadmin.db'))
scheduler = SchedulerAdmin.bind(site)
site.mount_app(app)


def get_data_collection():
    client = pymongo.MongoClient(
        'mongodb://mongodb:27017/',
        username=os.environ.get('MONGO_USER'),
        password=os.environ.get('MONGO_PASS')
    )
    return client[os.environ.get('MONGO_DB')].temperature_info


def get_temperature():
    resp = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric'
    )
    if resp.status_code != 200:
        raise Exception(f'openweather api error: {resp.status_code}, {resp.reason}')
    return resp.json()['main'].get('temp')

# testing
# @scheduler.scheduled_job('cron', hour='0-23', minute='0-59', second='0,10,20,30,40,50')
# @scheduler.scheduled_job('cron', hour='0-23', minute='0-59')
@scheduler.scheduled_job('cron', hour='0-23')
def cron_task_test():
    now = datetime.datetime.now()

    try:
        temp = get_temperature()
    except Exception as exc:
        temp = None

    col = get_data_collection()
    col.update_one(
        {'_id': now.strftime('%Y-%m-%d')}, {'$set': {now.strftime('%H'): temp}},
        # {'_id': now.strftime('%Y-%m-%d')}, {'$set': {now.strftime('%H:%M'): temp}},
        upsert=True
    )
    # print(f'get temp for {now}')


@app.get("/api/temperature_info/")
def get_temperature_info(date: str):
        
    try:
        data = get_data_collection().find_one({'_id': date}) or {}
    except Exception as exc:
        return {'error': str(exc)}
    return {
        f'{str(k).zfill(2)}:00': data.get(str(k).zfill(2), '-') for k in range(0,24)
    }
    
    # try:
    #     temp = get_temperature()
    # except Exception as exc:
    #     return {'error': str(exc)}
    # return {'test': temp}
    


@app.on_event("startup")
async def startup():
    scheduler.start()
