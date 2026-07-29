from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import joblib
import json
import pandas as pd


# --- LOAD MODEL ---

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load('data/xg_model_v1.pkl')
scaler = joblib.load('data/scaler.pkl')

with open('data/X_cols.json') as f:
    X_cols = json.load(f)


# --- ESTABLISH/FORMAT X ---

class Input(BaseModel):
    distance: float
    angle: float
    under_pressure: int
    one_on_one: int
    first_time: int
    shot_technique: str
    body_part: str
    shot_type: str


@app.post("/predict")
def predict(shot: Input):

    row = {col: 0 for col in X_cols}

    row['distance'] = shot.distance
    row['angle'] = shot.angle
    row['under_pressure'] = shot.under_pressure
    row['shot_one_on_one'] = shot.one_on_one
    row['shot_first_time'] = shot.first_time

    print("Incoming one_on_one:", shot.one_on_one)
    print("Row value:", row['shot_one_on_one'])

    technique_col = f"shot_technique_{shot.shot_technique}"
    body_part_col = f"shot_body_part_{shot.body_part}"
    type_col = f"shot_type_{shot.shot_type}"

    for col in [technique_col, body_part_col, type_col]:
        if col in row:
            row[col] = 1
        else:
            return {"col error": f"{col}"}
        
    X_new = pd.DataFrame([row])[X_cols]
    X_new[['distance', 'angle']] = scaler.transform(X_new[['distance', 'angle']])

    
    # --- RUN PREDICTION AND RETURN VALUE ---

    xG = model.predict_proba(X_new)[:,1][0]
    return {"xG": round(float(xG), 4)}

app.mount("/", StaticFiles(directory="UI", html=True), name="UI")