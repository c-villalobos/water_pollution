from sklearn.externals import joblib
from tensorflow.keras import models
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import requests

from dotenv import load_dotenv
load_dotenv()  # Loads env variable from the root .env file

SAV_PATH = '../../api_data/'


def get_scaler_model():

    model_path = SAV_PATH + 'model'
    model = models.load_model(model_path,
                              custom_objects=None,
                              compile=True,
                              options=None)

    scaler_path = SAV_PATH + 'scaler.save'
    scaler = joblib.load(scaler_path)

    return scaler, model


def get_train_val_df():

    traindf_path = SAV_PATH + 'traindf.pickle'
    traindf = pd.read_pickle(traindf_path)

    valdf_path = SAV_PATH + 'valdf.pickle'
    valdf = pd.read_pickle(valdf_path)

    return traindf, valdf

def get_stations_df():

    path = SAV_PATH + 'stationsdf.pickle'
    stationsdf = pd.read_pickle(path)

    return stationsdf

def get_stations_dict():

    path = SAV_PATH + 'stationsdf.pickle'
    stationsdf = pd.read_pickle(path)

    stations_dict = stationsdf.to_dict(orient='index')

    return stations_dict

## API REQUESTS

def get_station_weather_data(station_id):

    ## Stations DF, used below
    stationsdf = get_stations_df()

    #### API REQUESTS

    coords = stationsdf.loc[station_id, 'coord']
    lat, lon = coords[0], coords[1]
    coord_str = str(lat) + ',' + str(lon)

    # General params

    key = os.getenv('WEATHERKEY')
    url_hist = 'http://api.weatherapi.com/v1/history.json'
    url_prev = 'http://api.weatherapi.com/v1/forecast.json'

    # Built list of weather information
    weather_list = []

    # API FORECAST REQUEST

    params = {
        'key': key,
        'q': coord_str,
        'days': 15,
    }

    response = requests.get(url_prev, params=params)

    jr = response.json()

    forecast = jr.get('forecast').get('forecastday')

    for f in forecast:
        weather_list.append((f.get('date'), f.get('day').get('avgtemp_c'),
                             f.get('day').get('totalprecip_mm')))

    # API HISTORY REQUESTS

    # Total date range
    now = datetime.now()
    month_first = now.replace(day=1)
    month_m4_first = month_first - relativedelta(months=5)

    date_range = pd.date_range(start=month_m4_first, end=now, freq='D')

    # Date ranges by month
    date_ranges = []
    for m in set(date_range.month):
        date_ranges.append(date_range[date_range.month == m])

    # Ranges
    string_ranges = []

    for dr in date_ranges:
        dt = dr[0].strftime("%Y-%m-%d")
        end_dt = dr[-1].strftime("%Y-%m-%d")
        string_ranges.append((dt, end_dt))

    for string_range in string_ranges:

        params = {
            'key': key,
            'q': coord_str,
            'dt': string_range[0],
            'end_dt': string_range[1],
        }

        response = requests.get(url_hist, params=params)

        if not response:  # if response is not 200
            pass  # traiter les exceptions...

        jr = response.json()

        forecast = jr.get('forecast').get('forecastday')

        for f in forecast:

            weather_list.append((f.get('date'), f.get('day').get('avgtemp_c'),
                                 f.get('day').get('totalprecip_mm')))

    ## FINAL DF OPERATIONS

    weatherdf = pd.DataFrame(weather_list)
    weatherdf.columns = ['date', 'temp', 'precipitation']
    weatherdf['date'] = pd.to_datetime(weatherdf['date'])
    weatherdf.drop_duplicates('date', inplace=True)
    weatherdf.set_index('date', inplace=True)

    # Does the windows and shifts

    precdf = weatherdf[['precipitation']].copy()
    precdf = precdf.rolling(window=35).mean().dropna()  # Window of 40
    precdf.index = precdf.index + timedelta(15)  # delta of 15

    tempdf = weatherdf[['temp']].copy()
    tempdf = tempdf.rolling(window=40).mean().dropna()  # Window of 40
    tempdf.index = tempdf.index + timedelta(15)  # delta of 15

    weatherdf = pd.merge(precdf, tempdf, left_index=True, right_index=True)

    # Adds the Nitrate Mean of the station
    weatherdf['mean_station'] = stationsdf.loc[station_id, 'mean_nitrate']

    # Adds the day of year sin and cos
    weatherdf['sin_doy'] = np.sin(
        (weatherdf.index.day_of_year - 1) * 2 * np.pi / 365)
    weatherdf['cos_doy'] = np.cos(
        (weatherdf.index.day_of_year - 1) * 2 * np.pi / 365)

    return weatherdf


def get_station_weather_prediction_df(station_id):

    ### API CALL / FEATURES DF

    # Checks that the station_id is known
    stationsdf = get_stations_df()
    if station_id not in stationsdf.index:
        return {'error': 'station_id unknown'}

    # Gets and weather forecast and history
    # and builds the features df

    try:
        weatherdf = get_station_weather_data(station_id)
    except:
        return {'error': "Can't get Weather Datas"}

    ### SCALER / MODEL LOADING

    sav_path = '../../cooked_data/saone/best_model/'

    model_path = sav_path + 'model'
    model = models.load_model(model_path,
                              custom_objects=None,
                              compile=True,
                              options=None)

    scaler_path = sav_path + 'scaler.save'
    scaler = joblib.load(scaler_path)

    # DATA PREPARATION

    feature_cols = [
        'sin_doy', 'cos_doy', 'mean_station', 'precipitation', 'temp'
    ]

    # DataPrep
    X = weatherdf[feature_cols]
    X = scaler.transform(X)

    # PREDICTION
    y_pred = model.predict(X)

    weatherdf['prediction'] = y_pred

    return weatherdf
