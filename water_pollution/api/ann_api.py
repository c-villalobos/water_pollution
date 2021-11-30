from water_pollution.api import ann_utils as util

from fastapi import FastAPI

import pandas as pd
import numpy as np

import pickle
from sklearn.externals import joblib
from tensorflow.keras import models



app = FastAPI()

@app.get("/")
def index():
    return {"ok": True}



@app.get("/predictstation")
def predictstation(station_id):

    predicteddf = util.get_station_weather_prediction_df(station_id)

    # FORMAT THE DF TO JSON HERE
