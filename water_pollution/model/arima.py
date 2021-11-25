import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARIMA

def predict(df, length):
    '''
    Input:
    - time serie                          (pd.serie)
    - forecast length in months           (int)

    It performs an ARIMA prediction of the time series for the next 'length' months.

    Returns:
    - deseasonalized and linearized serie (pd serie)
    - forecast serie                      (pd serie)
    - std_err                             (np.ndarray)
    - confidence interval serie           (np.ndarray)
    - forecast length in months           (np.ndarray)
    '''
    result_mul = seasonal_decompose(df['1340'], model = 'multiplicative', period = 12)

    df['deseasonalized'] = df['1340'].values/result_mul.seasonal
    df['linearized'] = np.log(df['deseasonalized'])

    train = df['linearized']
    p, d, q = 3, 1, 2

    arima = ARIMA(train, order=(p,d,q)).fit()
    forecast, std_err, confidence_int = arima.forecast(length, alpha=0.05)
    forecast = np.exp(forecast)*result_mul.seasonal[-length:]
    train = np.exp(train)*result_mul.seasonal
    lower = np.exp(confidence_int)[:,0]*result_mul.seasonal[-length:]
    upper = np.exp(confidence_int)[:,1]*result_mul.seasonal[-length:]
    return train, forecast, std_err, confidence_int, length
