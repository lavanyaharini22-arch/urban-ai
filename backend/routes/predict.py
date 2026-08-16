import json
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form

from routes.auth import require_auth
from services.predictor import PredictorService
from services.synthetic_data import generate_time_series, generate_synthetic_reading
from database.db import get_conn

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg"}


def _log_prediction(email: str, result: dict):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO prediction_logs
               (user_email, hazard, risk_level, confidence, image_contribution,
                sensor_contribution, data_mode)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (email, result["hazard"], result["risk_level"], result["confidence"],
             result.get("image_contribution"), result.get("sensor_contribution"),
             result["data_mode"]),
        )


@router.post("/image-predict")
async def image_predict(file: UploadFile = File(...), email: str = Depends(require_auth)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG and PNG images are supported.")
    try:
        content = await file.read()
        if not content:
            raise ValueError("Empty file")
    except Exception:
        raise HTTPException(status_code=400, detail="Uploaded image could not be read.")

    try:
        result = PredictorService.instance().predict(image_bytes=content)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not process image: {e}")

    _log_prediction(email, result)
    return result


@router.post("/sensor-predict")
async def sensor_predict(payload: dict, email: str = Depends(require_auth)):
    try:
        result = PredictorService.instance().predict(sensor_dict=payload)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not process sensor data: {e}")
    _log_prediction(email, result)
    return result


@router.post("/multimodal-predict")
async def multimodal_predict(
    sensor_json: str = Form(...),
    file: UploadFile = File(None),
    email: str = Depends(require_auth),
):
    try:
        sensor_dict = json.loads(sensor_json) if sensor_json else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid sensor JSON payload.")

    image_bytes = None
    if file is not None:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="Only JPG and PNG images are supported.")
        image_bytes = await file.read()

    try:
        result = PredictorService.instance().predict(image_bytes=image_bytes, sensor_dict=sensor_dict)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Prediction failed: {e}")

    _log_prediction(email, result)
    return result


@router.get("/sensor-data")
def sensor_data(scenario: str = "random", points: int = 24, email: str = Depends(require_auth)):
    points = max(1, min(points, 200))
    return {"data_mode": "DEMO", "series": generate_time_series(points, scenario)}


@router.get("/metrics")
def metrics(email: str = Depends(require_auth)):
    # Demo evaluation metrics for the three-way model comparison
    # (sensor-only vs image-only vs multimodal). Replace with real
    # evaluation output once trained on an actual dataset.
    return {
        "data_mode": PredictorService.instance().data_mode,
        "models": [
            {"name": "Sensor-only", "accuracy": 0.78, "precision": 0.76, "recall": 0.74, "f1": 0.75},
            {"name": "Image-only", "accuracy": 0.81, "precision": 0.80, "recall": 0.79, "f1": 0.79},
            {"name": "Multimodal (ViT + Sensor Fusion)", "accuracy": 0.91, "precision": 0.90, "recall": 0.89, "f1": 0.90},
        ],
    }


@router.get("/model/status")
def model_status(email: str = Depends(require_auth)):
    return PredictorService.instance().gpu_status()
