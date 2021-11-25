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
    - lower confidence interval serie (pd serie)
    - upper confidence interval serie (pd serie)
    '''
    # Multiplicative seasonal decomposition
    result_mul = seasonal_decompose(df['1340'], model = 'multiplicative', period = 12)
    df['deseasonalized'] = df['1340'].values/result_mul.seasonal

    # Log-linearization
    df['linearized'] = np.log(df['deseasonalized'])
    print(df['linearized'])

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

# import matplotlib.pyplot as plt

# def plot_forecast(df, length, forecast, upper=None, lower=None):
#     '''
#     Plots last 24 values of the serie and the forecast for the next 'length' months.
#     '''
#     # df, forecast, lower and upper preparation
#     df = df['1340']
#     df = df[-24:]
#     forecast = pd.concat([df[[-1]], forecast])
#     lower = pd.concat([df[[-1]], lower])
#     upper = pd.concat([df[[-1]], upper])
#     index = df.index[-(length + 2):-1] + df.index.freq*(length + 1)

#     # Plot
#     plt.figure(figsize = (10,4), dpi = 100)
#     plt.plot(df, label = 'Last 24 months', color = 'black')
#     plt.plot(forecast, label = f'Next {length} months Forecast', color = 'orange', ls = '--')
#     plt.fill_between(lower.index, lower, upper, color = 'k', alpha = 0.15)
#     plt.title(f'Nitrate Concentration Forecast for the next {length} months')
#     plt.legend(loc = 'upper left', fontsize = 8)

# fore_12 = predict(df, 12)

# forecast = fore_12[0]
# lower = fore_12[1]
# upper = fore_12[2]

# plot_forecast(df, 12, forecast, lower, upper)
