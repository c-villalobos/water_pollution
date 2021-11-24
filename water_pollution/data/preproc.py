import pandas as pd

from water_pollution.data.params import *


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
        'CdQualAna'  # Code de la qualification du résultat :
        # 1 -> correcte / autre, à filtrer
    ]

    # Unused columns, can be interesting for mesure selection
    potential_col = [
        'SymUniteMesure',  # symbole de l'unité de mesure (°C...)
        'LQAna',  # limite de quantification (sous laquelle la mesure n'est pas fidèle)
        'LSAna',  # limite de saturation
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
