import json
import os
import pandas as pd

SAONE_SOURCE_COORD = (48.09424356970123, 6.180176804824726)

def get_saone_stations_dict():
    """
    Reads the json files in cooked_data/saone/stations
    and builds a dict of stations :

    key : id_station
    values : {
        'id' : id (int),
        'label' : label (str),
        'alt' : altitude (int),
        'river_id' : id of the river (str),
        'river_label' : name of the river (str),
        'coord' : GPS coordinates (lat,lon),
    }
    """

    json_dir = '../../cooked_data/saone/stations'

    # Paths of the json files in the directory
    json_paths = []
    for filename in os.listdir(json_dir):
        if filename.endswith('.json'):
            json_paths.append(os.path.join(json_dir, filename))


    # For each file, extracts the infos and builds the dictionary

    stations = {}

    for path in json_paths:
        with open(path) as file:

            data = json.load(file)

            st = {}

            st_id = int(
                data['features'][0]['properties']['CdStationMesureEauxSurface'])
            st['id'] = st_id
            st['label'] = data['features'][0]['properties'][
                'LbStationMesureEauxSurface']
            st['alt'] = int(
                data['features'][0]['properties']['AltitudePointCaracteritisque'])
            st['river_id'] = data['features'][0]['properties'][
                'CdEntiteHydrographique']
            st['river_label'] = data['features'][0]['properties'][
                'NomEntiteHydrographique']

            lat = data['features'][0]['geometry']['coordinates'][1]
            lon = data['features'][0]['geometry']['coordinates'][0]
            st['coord'] = (lat, lon)

            stations[st_id] = st

    return stations

def get_saone_stations_df():
    """Returns a df with data on the Saone stations"""

    stations_dict = get_saone_stations_dict()
    stations_list = [ st for st in stations_dict.values() ]
    stations_df = pd.DataFrame(stations_list)

    #stations_df.set_index('id',inplace=True)

    return stations_df
