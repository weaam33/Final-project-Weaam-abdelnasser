from fastapi import APIRouter, HTTPException

from app.schemas.prediction import HealthResponse, PredictionRequest, PredictionResponse
from app.services.inference import model_service
from app.services.preprocessing import request_to_dataframe

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    if not model_service.is_ready:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return HealthResponse(status="ok")


@router.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    try:
        row = request_to_dataframe(payload)
        price = model_service.predict(row)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc
    return PredictionResponse(predicted_price=round(price, 2))
