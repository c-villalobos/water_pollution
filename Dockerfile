FROM python:3.8.12-buster

COPY /requirements.txt requirements.txt
COPY water_pollution water_pollution
COPY /cooked_data/station_data_2011_2021 /cooked_data/station_data_2011_2021
COPY api_data api_data
COPY .env .env

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD uvicorn water_pollution.api.ann_api:app --host 0.0.0.0 --port $PORT
