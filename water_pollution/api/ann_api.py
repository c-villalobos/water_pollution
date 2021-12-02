from water_pollution.api import ann_utils as util

from fastapi import FastAPI
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date, timedelta
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()  # Loads env variable from the root .env file
SAV_PATH = os.getenv('API_SAV_DIR')


app = FastAPI()

@app.get("/")
def index():
    return {"ok": True}

@app.get("/predict")
def predict(station_id):

    try:
        station_id = int(station_id)
    except:
        return { 'error':'bad format for station_id '}

    # Build the cache filename
    stamp = date.today().strftime('%Y%m%d')
    cachefile_name = stamp + str(station_id) + '.cache'
    cachefile_path = SAV_PATH + 'cache/' + cachefile_name

    # If cache file exists, loads from it
    if os.path.isfile(cachefile_path):
        predicteddf = pd.read_pickle(cachefile_path)
    # Else, builds the prediction from WeatherAPI
    else:
        predicteddf = util.get_station_weather_prediction_df(station_id)
        if predicteddf is None :
            return { 'error':'station_id unknown'}

        predicteddf.to_pickle(cachefile_path)



    # FORMAT THE DF TO JSON HERE

    return {
        'date': list(predicteddf.index.strftime('%Y-%m-%d')),
        'precipitation': list(predicteddf.precipitation),
        'temp': list(predicteddf.temp),
        'prediction': list(predicteddf.prediction)
    }
