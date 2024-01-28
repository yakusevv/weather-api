FROM python:3.10.2-slim-bullseye

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
