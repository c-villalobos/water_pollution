import pandas as pd
import numpy as np

from water_pollution.data.params import *
from water_pollution.data.utils import haversine
from water_pollution.data import stations


class Station():
    """
    Simple class to store :
    - id (int) of the station
    - label (str) of the station
    - DataFrame
    """

    def __init__(self,id,label,df):
        self.id = int(id)
        self.label = str(label)
        self.df = df

    def __str__(self):
        return f"Station : id {self.id} / {self.label})"

    def __repr__(self):
        return f"Station({self.id},{self.label},df)"

def get_rawdf_from_file(file_path,param_ids=PARAM_IDS):
    """From a PhyCh csv file :
    Returns a df :
    - with usefull columns only
    - with rows of selected params only"""

    df = pd.read_csv(file_path, sep=';',
                     on_bad_lines='skip',
                     low_memory=False)


    # Columns used for data cleaning
    selected_col = [
        'CdStationMesureEauxSurface',  # id station
        'LbStationMesureEauxSurface',  # label station
        'DatePrel',  # date mesure
        'CdParametre',  # code du paramètre
        'LbLongParamètre',  # label du paramètre
        'RsAna',  # resultat de la mesure
        'CdQualAna',  # Code de la qualification du résultat :
        # 1 -> correcte / autre, à filtrer
        'LqAna',  # limite de quantification (renseignée)
    ]

    # Unused columns, can be interesting for mesure selection
    potential_col = [
        'SymUniteMesure',  # symbole de l'unité de mesure (°C...)
        'LsAna',  # limite de saturation (pas renseignée)
        'IncertAna',  # incertitude (pas renseignée)
        'IncertAna',  # incertitude analytique
    ]

    df = df[selected_col]
    param_bool = df['CdParametre'].isin(param_ids)
    df = df[param_bool]

    return df

def split_rawdf_to_stations(df):
    """
    From a raw df containing data for multiple stations :
    returns a dict with station_id:Station object
    """

    # df with station id and label
    station_infos = df.groupby('CdStationMesureEauxSurface',as_index=False).first()
    station_infos = station_infos[['CdStationMesureEauxSurface','LbStationMesureEauxSurface']]
    station_infos.columns = ['id','label']


    stations = {}

    for _, row in station_infos.iterrows():
        st_id = row['id']
        st_label = row['label']
        st_df = df[df['CdStationMesureEauxSurface'] == st_id]

        station = Station(st_id, st_label, st_df)
        stations[st_id] = station

    return stations

def cook_rawdf(df):
    """
    From a raw df, returns a df formatted with timestamp as index
    and parameters as columns
    """

    # Final columns of each df before merge
    final_col = ['DatePrel','RsAna']

    # lists all parameters in the df
    param_ids = list(df['CdParametre'].unique())

    # Creates a df for each parameter, stores them in a dictionary
    # key = param_id / value = df

    df_dict = {}

    for param_id in param_ids:

        param_bool = df['CdParametre'] == param_id
        df_dict[param_id] = df[param_bool][final_col]
        df_dict[param_id].rename(columns={'RsAna': f'{param_id}'}, inplace=True)
        df_dict[param_id].sort_values('DatePrel', inplace=True)

        # merges mesures done the same day, does the mean
        # (must be done for the chained outer joins to come)
        df_dict[param_id] = \
            df_dict[param_id].groupby('DatePrel',as_index=False).mean()

    merged_df = None

    for tdf in df_dict.values():

        if merged_df is None:
            merged_df = tdf.copy()  # merged_df = df for the first element

        else:
            merged_df = pd.merge(merged_df,
                                tdf,
                                how='outer',
                                on='DatePrel',
                                suffixes=('', '_dup'))
            merged_df.drop(merged_df.filter(regex='_dup$').columns.tolist(),
                        axis=1,
                        inplace=True)

    merged_df.sort_values('DatePrel', inplace=True)

    # Converts 'DatePrel' to datetime and sets it as index
    merged_df['DatePrel'] = pd.to_datetime(merged_df['DatePrel'])
    merged_df = merged_df.set_index('DatePrel')

    ## Fill NaN values

    # First row NaN values filled with mean
    merged_df.iloc[0, :] = merged_df.iloc[0, :].fillna(merged_df.mean())

    # Next NaN values filled with previous non NaN values
    merged_df = merged_df.fillna(method='ffill')

    return merged_df

def turn_df_to_month(df):
    """From a cooked df, returns a df with data by month"""

    df = df.copy()

    df['month'] = df.index.month
    df['year'] = df.index.year
    df = df.groupby(['year', 'month'], as_index=False).mean()
    df['date'] = pd.to_datetime(dict(year=df.year, month=df.month, day=1),
                                format='%Y%m')
    df = df.drop(columns=['year', 'month'])
    df = df.set_index('date')
    df = df.asfreq(freq='MS', method='pad')

    return df


def get_station_month_df_from_file(file_path,station_id,param_ids=PARAM_IDS):


    raw_df = get_rawdf_from_file(file_path, param_ids=PARAM_IDS)

    stations = split_rawdf_to_stations(raw_df)
    df = stations[station_id].df  # df de la station caluire
    df = cook_rawdf(df)
    df = turn_df_to_month(df)

    return df

def build_saone_base_training_data(rawdf):
    """
    Takes a rawdf of saone stations params
    Returns a df with :
    - date
    - year
    - sin_doy               sinus(day of year)
    - cos_doy
    - id_station
    - source_dist           distance from the source
    - nitrate
    """


    # Filters on Nitrate measures
    # Selects and rename columns

    nitrate_bool = rawdf['CdParametre'] == 1340
    selected_col = ['CdStationMesureEauxSurface','DatePrel','RsAna']

    nitratedf = rawdf[nitrate_bool][selected_col].copy()
    nitratedf.columns = ['station_id','date','nitrate']

    # Format date
    nitratedf['date'] = pd.to_datetime(nitratedf['date'])
    nitratedf['doy'] = nitratedf['date'].dt.dayofyear # doy = day of year
    nitratedf['year'] = nitratedf['date'].dt.year

    # Turns day of year to cyclical feature (sin,cos)
    nitratedf['sin_doy'] = np.sin( (nitratedf['doy']-1) * 2 * np.pi / 365 )
    nitratedf['cos_doy'] = np.cos( (nitratedf['doy']-1) * 2 * np.pi / 365 )

    ### Distance from source to the measure


    # Gets the stations dataFrame and source coord
    stationsdf = stations.get_saone_stations_df()
    SOURCE_COORD = stations.SAONE_SOURCE_COORD

    # Adds distance from source to the stationsdf
    stationsdf['source_dist'] =\
        stationsdf['coord'].apply(lambda x : haversine(x[0],x[1],*SOURCE_COORD))

    # Keeps only source_dist and _station
    stationsdf = stationsdf[['id', 'source_dist']]
    stationsdf.columns = ['station_id', 'source_dist']

    finaldf = pd.merge(nitratedf, stationsdf, how='left', on='station_id')
    finaldf = finaldf[[
        'date', 'year', 'sin_doy', 'cos_doy',
        'station_id', 'source_dist',
        'nitrate'
    ]]

    return finaldf
