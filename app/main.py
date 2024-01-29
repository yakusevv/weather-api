import datetime

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi_amis_admin.admin.settings import Settings as AdminSettings
from fastapi_amis_admin.admin.site import AdminSite
from fastapi_amis_admin import i18n
from fastapi_scheduler import SchedulerAdmin
from pydantic import BaseModel

from .utils import get_data_collection, get_temperature
from . import settings


i18n.set_language(language='en_US')

app = FastAPI()
site = AdminSite(
    settings=AdminSettings(
        database_url_async='sqlite+aiosqlite:///amisadmin.db',
    )
)
scheduler = SchedulerAdmin.bind(site)
site.mount_app(app)


class ResponseModel(BaseModel):
    error: str | None
    data: dict | None


@scheduler.scheduled_job('cron', hour='0-23', minute='0')
def cron_task_test():
    now = datetime.datetime.now()

    try:
        temp = get_temperature()
    except Exception as exc:
        temp = None

    col = get_data_collection()
    col.update_one(
        {'_id': now.strftime('%Y-%m-%d')}, {'$set': {now.strftime('%H:%M'): temp}},
        upsert=True
    )


def middleware(x_token: str = Header(pattern='.{32}')):
    if x_token != settings.X_TOKEN:
      raise HTTPException(status_code=403, detail='wrong x-token')


@app.get(
    "/api/temperature_info/",
    dependencies=[Depends(middleware)],
    response_model=ResponseModel)
def get_temperature_info(date: datetime.date):
    response = {
        'data': None,
        'error': None
    }

    try:
        data = get_data_collection().find_one({'_id': date.strftime('%Y-%m-%d')})
    except Exception as exc:
        response['error'] = f'error while getting data: {exc}'
    else:
        if data is None:
            response['error'] = f'there is no data for this date: {date}'
        else:
            response['data'] = {
                # just to fill empty values
                # WARN: for now cron makes requests every hour
                # and data is stored with key in format '%H:%M'
                # if timing will be changed we may get empty dict here
                # TODO: return data as it is instead? (without empty values filling)
                f'{"%02d" % k}:00': data.get(f'{"%02d" % k}:00')
                for k in range(0,24)
            }
    return response



@app.on_event("startup")
async def startup():
    scheduler.start()
