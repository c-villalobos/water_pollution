import pandas as pd

# Liste des Codes paramètre exploités dans les fichiers brut Physico-chimiques

param_ids = [
    1303, # Conductivité à 25°C
    1311, # Oxygène dissous
    1301, # Température de l'Eau
    1302, # Potentiel en Hydrogène (pH)
    1312, # Taux de saturation en oxygène
    1841, # Carbone Organique
    1295, # Turbidité Formazine Néphélométrique
    1335, # Ammonium
    1314, # Demande Chimique en Oxygène (DCO)
    1433, # Orthophosphates (PO4)
    1313, # Demande Biochimique en oxygène en 5 jours (D.B.O.5)
    1350, # Phosphore total
    1319, # Azote Kjeldahl
    1340, # Nitrates <---------------------------------------------- TARGET
    1339, # Nitrites
    1305, # Matières en suspension
    1342, # Silicates
]

station_id = 6059500 # Par défaut, la station SAONE CALUIRE


def get_phychi_data(file_path,station_id=station_id,param_ids=param_ids):
    """From PhyChi data, returns a df
    each column is a parameter from param_ids (column name = param_id)
    index = timestamp
    """

    # Columns used for data cleaning
    selected_col = [
        'CdStationMesureEauxSurface', # id station
        'LbStationMesureEauxSurface', # label station
        'DatePrel',                   # date mesure
        'CdParametre',                # code du paramètre
        'LbLongParamètre',            # label du paramètre
        'RsAna',                      # resultat de la mesure
        'CdQualAna'                   # Code de la qualification du résultat :
                                      # 1 -> correcte / autre, à filtrer
    ]

    # Unused columns, can be interesting to treat
    potential_col = [
        'SymUniteMesure',             # symbole de l'unité de mesure (°C...)
        'LQAna',                      # limite de quantification (sous laquelle la mesure n'est pas fidèle)
        'LSAna',                      # limite de saturation
        'IncertAna',                  # incertitude analytique

    ]

    # Final columns of each df before merge
    final_col = [
        'DatePrel',                   # date mesure
        'RsAna',                      # resultat de la mesure
    ]


    # Reads the csv file
    phys_df = pd.read_csv(file_path,sep=';',on_bad_lines='skip')

    # Filters on columns
    filtered_phys_df = phys_df[selected_col]

    # Filters on the given station
    station_bool = filtered_phys_df['CdStationMesureEauxSurface'] == station_id
    filtered_phys_df = filtered_phys_df[station_bool]

    # Creates a df for each parameter, stores them in a dictionary
    # key = param_id / value = df
    df_dict = {}

    for param_id in param_ids :

        param_bool = filtered_phys_df['CdParametre'] == param_id
        df_dict[param_id] = filtered_phys_df[param_bool][final_col]
        df_dict[param_id].rename(columns={'RsAna':f'{param_id}'},inplace=True)
        df_dict[param_id].sort_values('DatePrel',inplace=True)

        # merges mesures done the same day, does the mean
        # (must be done for the chained outer joins to come)
        df_dict[param_id] = \
            df_dict[param_id].groupby('DatePrel',as_index=False).mean()

    merged_df = None

    for df in df_dict.values() :

        if merged_df is None :
            merged_df = df.copy() # merged_df = df for the first element

        else :
            merged_df = pd.merge(merged_df,df,how='outer',
                                 on='DatePrel',suffixes=('','_dup'))
            merged_df.drop(merged_df.filter(regex='_dup$').columns.tolist(),
                           axis=1, inplace=True)

    merged_df.sort_values('DatePrel',inplace=True)

    # Converts 'DatePrel' to datetime and sets it as index
    merged_df['DatePrel'] =  pd.to_datetime(merged_df['DatePrel'])
    merged_df = merged_df.set_index('DatePrel')

    ## Fill NaN values

    # First row NaN values filled with mean
    merged_df.iloc[0,:] = merged_df.iloc[0,:].fillna(merged_df.mean())

    # Next NaN values filled with previous non NaN values
    merged_df = merged_df.fillna(method='ffill')

    return merged_df
