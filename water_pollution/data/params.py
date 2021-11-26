## PHYSICO CHIMICAL PARAMETERS

# 'ID' : 'Description' of the parameters extracted from the raw data

PARAM_LABELS = {
    1301: "Température de l'Eau",
    1302: "Potentiel en Hydrogène (pH)",
    1303: "Conductivité à 25°C",
    1311: "Oxygène dissous",
    1350: "Phosphore total",
    1433: "Orthophosphates (PO4)",

    1340: "Nitrates",

    # 1312: "Taux de saturation en oxygène",
    # 1841: "Carbone Organique",
    # 1295: "Turbidité Formazine Néphélométrique",
    # 1335: "Ammonium",
    # 1314: "Demande Chimique en Oxygène (DCO)",
    # 1313: "Demande Biochimique en oxygène en 5 jours (D.B.O.5)",
    # 1319: "Azote Kjeldahl",
    # 1339: "Nitrites",
    # 1305: "Matières en suspension",
    # 1342: "Silicates",
}

# List of the IDs of extracted from the raw data
PARAM_IDS = [k for k in PARAM_LABELS]

# Default station (if needed by a function)
STATION_ID = 6059500 # Saone - Caluire
