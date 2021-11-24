from fastapi import FastAPI

app = FastAPI()


# define a root `/` endpoint
@app.get("/")
def index():
    return {"ok": True}

@app.get("/predict")
def predict(station_id,predict_length):

    return {
        "station_id": station_id,
        "predict_length": predict_length,
        }
