"""
Urban Environmental Hazard AI — FastAPI backend entrypoint.

Run with:
    python app.py
or:
    uvicorn app:app --reload --port 8000
"""
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database.db import init_db
from routes import auth as auth_routes
from routes import predict as predict_routes

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("urban-hazard-ai")

app = FastAPI(title="Urban Environmental Hazard AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()
    logger.info("SQLite database ready.")
    try:
        from services.predictor import PredictorService
        svc = PredictorService.instance()
        logger.info(f"Model loaded. Data mode: {svc.data_mode}, vision backbone: {svc.vision_encoder.mode}")
    except Exception as e:
        logger.error(f"Model failed to initialize, predictions will error until fixed: {e}")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.exception("Unhandled error")
    return JSONResponse(status_code=500, content={"detail": "Internal server error. Please try again."})


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth_routes.router, tags=["auth"])
app.include_router(predict_routes.router, tags=["prediction"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
