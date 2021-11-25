from fastapi import FastAPI
from water_pollution.model import arima

import pandas as pd



STATION_IDS = [
    6059500 # SAONE CALUIRE
    ]



app = FastAPI()

# define a root `/` endpoint
@app.get("/")
def index():
    return {"ok": True}

@app.get("/predict")
def predict(station_id,predict_length):

    ## PREDICT_LENGTH CHECK
    # Casts predict_length to an int in [1;24]
    # If cast to int impossible, default to 12

    try :
        predict_length = int(predict_length)
    except :
        predict_length = 12

    if predict_length > 24 : predict_length = 24
    if predict_length < 1: predict_length = 1

    ## STATION CHECK
    # Sets station_id to id of 'Saone Caluire' if invalid
    # Sets station_id to id of 'Saone Caluire' if unknown

    try:
        station_id = int(station_id)
    except:
        station_id = STATION_IDS[0]

    if station_id not in STATION_IDS : station_id = STATION_IDS[0]

    folder_path = 'cooked_data/station_data_2011_2021/'
    file_name = str(station_id) + '.pickle'

    file_path = folder_path + file_name
    station_df = pd.read_pickle(file_path)
    predict_length = int(predict_length)

    forecast, lower, upper = arima.predict(station_df, predict_length)

    return {
        'initial': station_df['1340'],
        'forecast': forecast,
        'lower': lower,
        'upper': upper
    }
