import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARIMA

def predict(df, length):
    '''
    Input:
    - time serie                      (pd.serie)
    - forecast length in months       (int)

    It performs an ARIMA prediction of the time series for the next 'length' months.

    Returns:
    - forecast serie                  (pd serie)
    - lower confidence interval serie (np.ndarray)
    - upper confidence interval serie (np.ndarray)
    '''
    # Multiplicative seasonal decomposition
    result_mul = seasonal_decompose(df['1340'], model = 'multiplicative', period = 12)
    df['deseasonalized'] = df['1340'].values/result_mul.seasonal

    # Log-linearization
    df['linearized'] = np.log(df['deseasonalized'])

    df = df['linearized']
    p, d, q = 3, 1, 2

    # Model
    arima = ARIMA(df, order=(p,d,q)).fit()
    forecast, std_err, confidence_int = arima.forecast(length, alpha=0.05)

    # Exponentialization and reseasonalization
    forecast = np.exp(forecast)*result_mul.seasonal[-length:]
    lower = np.exp(confidence_int)[:,0]*result_mul.seasonal[-length:]
    upper = np.exp(confidence_int)[:,1]*result_mul.seasonal[-length:]

    # Updates the indexes of the forecast, lower and upper
    fc_index = pd.date_range(df.index[-1], periods=length+1, freq='MS')[1:]
    forecast.index = fc_index
    lower.index = fc_index
    upper.index = fc_index

    return forecast, lower, upper
