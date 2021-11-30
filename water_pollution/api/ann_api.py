from water_pollution.api import ann_utils as util
from fastapi import FastAPI

import time
import pandas as pd

app = FastAPI()

# ROOT `/` ENDPOINT
@app.get("/")
def index():
    return {"ok": True}



@app.get("/predictstation")
def predictstation(station_id,predict_length):


    # Build date list to request to the API

    # Gets the scaler and the model
    scaler,model = util.get_scaler_model()
