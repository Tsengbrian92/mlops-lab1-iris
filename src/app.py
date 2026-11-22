from pathlib import Path

import joblib
from fastapi import FastAPI
from pydantic import BaseModel, Field


MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"
if not MODEL_PATH.exists():
    MODEL_PATH = Path(__file__).resolve().parents[1] / "model.pkl"
model = joblib.load(MODEL_PATH)
app = FastAPI(title="Iris Model API", version="1.0.0")


class PredictionRequest(BaseModel):
    instances: list[list[float]] = Field(min_length=1)


@app.post("/predict")
def predict(request: PredictionRequest) -> dict[str, list[int]]:
    predictions = model.predict(request.instances)
    return {"predictions": predictions.tolist()}


@app.get("/healthz")
async def healthz() -> dict[str, bool]:
    return {"ok": True}

