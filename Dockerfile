FROM python:3.8.12-buster

COPY /requirements.txt requirements.txt
COPY water_pollution water_pollution
COPY /cooked_data/station_data_2011_2021 /cooked_data/station_data_2011_2021

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD uvicorn water_pollution.api.predict:app --host 0.0.0.0 --port $PORT
