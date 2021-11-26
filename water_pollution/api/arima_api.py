from fastapi import FastAPI
from water_pollution.model import arima

import pandas as pd


STATIONS = [
    {
        'id':6059500,
        'label': 'SAONE A LYON 1',
        'coord':  [ 4.831905651439411, 45.796538771031791 ]
    },
    {
        'id':6000990,
        'label': 'SAONE A BELRUPT',
        'coord': [ 6.101940890815991, 48.090273327987276 ]
    },
    {
        'id':6001000,
        'label': 'SAONE A CENDRECOURT',
        'coord':  [ 5.917378095285407, 47.840260837412551 ]
    },
    {
        'id':6002500,
        'label': 'SAONE A PORT-SUR-SAONE',
        'coord':  [ 6.039291564176292, 47.691078334268859 ]
    },
    {
        'id':6003600,
        'label': 'SAONE A SCEY-SUR-SAONE',
        'coord':  [ 5.972459738821173, 47.661731120409826 ]
    },
    {
        'id':6005500,
        'label': 'SAONE A APREMONT 1',
        'coord':  [ 5.544088676925676, 47.39571566626848 ]
    },

]

STATION_IDS = [station['id'] for station in STATIONS]


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

@app.get('/stations')
def stations():
    """
    Returns a list of station dicts, with :
        'id':6059500,
        'label': 'NAME OF THE STATION',
        'coord':  [ x_coord, y_coord ]
    """

    return STATIONS
