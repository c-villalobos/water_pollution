from datetime import timedelta
import pandas as pd
import os

from dateutil.relativedelta import relativedelta

def get_saone_weather_df(window_size=1,delta=0):
    """
    Returns a df with weather information on saone stations between 2011-11
    and 2021-11, windowed, window size in days.
    Columns :
    - date
    - precipitation
    - temperature
    - station_id

    Needs the extracted weather csv files in cooked_data/saone/weather
    """

    csv_dir = '../../cooked_data/saone/weather/api_extraction/'
    csv_ids_paths = []

    ## READS THE CSV FILES AND CREATES A DICT OF DFs

    # (station_id,'path') for each file
    for filename in os.listdir(csv_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(csv_dir,filename)
            station_id = int(filename.strip('.csv'))

            csv_ids_paths.append((station_id,file_path))


    swdfs = {} # Station Weather dfs

    for id_path in csv_ids_paths :

        station_id = id_path[0]
        swdf = pd.read_csv(id_path[1])
        swdf.set_index('date',inplace=True)

        swdfs[station_id] = swdf

    ## DOES THE WINDOW AND CONCATENATE THE RESULT IN A DF
    if window_size > 60 : window_size = 60 # 25 days max window

    swdfs_win = []  # Station Weather df windowed

    for station_id, swdf in swdfs.items():

        swdf_win = swdf.rolling(window=window_size).mean().dropna()
        swdf_win['station_id'] = station_id
        swdfs_win.append(swdf_win)

    weather_win = swdfs_win[0]

    for swdf_win in swdfs_win[1:]:
        weather_win = pd.concat([weather_win, swdf_win])

    weather_win = weather_win.reset_index()
    weather_win['date'] = pd.to_datetime(weather_win['date'])

    if delta > 0 :
        weather_win['date'] = weather_win['date'] + timedelta(delta)

    return weather_win
