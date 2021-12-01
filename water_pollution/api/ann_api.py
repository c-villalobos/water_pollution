from water_pollution.api import ann_utils as util

from fastapi import FastAPI

import pandas as pd


from tensorflow.keras import models



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

    predicteddf = util.get_station_weather_prediction_df(station_id)

    if predicteddf is None :
        return { 'error':'station_id unknown'}

    # FORMAT THE DF TO JSON HERE

    return {
        'date': list(predicteddf.index.strftime('%Y-%m-%d')),
        'precipitation': list(predicteddf.precipitation),
        'temp': list(predicteddf.temp),
        'prediction': list(predicteddf.prediction)
    }
