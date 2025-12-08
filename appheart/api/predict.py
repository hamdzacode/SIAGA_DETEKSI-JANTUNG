from typing import Dict

from fastapi import FastAPI
from pydantic import BaseModel

from ml.cardio_model import CardioRiskModel


app = FastAPI(title="SIAGA Jantung API")


class PredictRequest(BaseModel):
    age_years: int
    gender: int
    bmi: float
    map: float
    cholesterol: int
    gluc: int
    smoke: int
    alco: int
    active: int


class PredictResponse(BaseModel):
    probability: float
    label: int
    risk_category: str


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    model = CardioRiskModel()
    proba = model.predict_proba(req.dict())
    label = model.predict_label(req.dict(), threshold=0.5)

    risk_percent = proba * 100
    if risk_percent < 30:
        risk_cat = "Rendah"
    elif risk_percent < 60:
        risk_cat = "Sedang"
    else:
        risk_cat = "Tinggi"

    return PredictResponse(
        probability=proba,
        label=label,
        risk_category=risk_cat,
    )
