from fastapi import FastAPI
from water_pollution.model import arima

import pandas as pd

app = FastAPI()


# define a root `/` endpoint
@app.get("/")
def index():
    return {"ok": True}

@app.get("/predict")
def predict(station_id,predict_length):

    folder_path = 'cooked_data/station_data_2011_2021/'
    file_name = str(station_id) + '.pickle'

    file_path = folder_path + file_name
    station_df = pd.read_pickle(file_path)

    initial_series = station_df['1340']

    

    return {
        "initial_series": initial_series,
        "int_test": 12,
    }
