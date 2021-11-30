from sklearn.externals import joblib
from tensorflow.keras import models
import pandas as pd

import matplotlib.pyplot as plt

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
