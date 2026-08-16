from pydantic import BaseModel, Field
from typing import Optional, List


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str
    password: str
    confirm_password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None


class SensorInput(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    aqi: Optional[float] = None
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    co: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    rainfall: Optional[float] = None
    wind_speed: Optional[float] = None
    pressure: Optional[float] = None
    traffic_density: Optional[float] = None


class PredictionResponse(BaseModel):
    hazard: str
    risk_level: str
    confidence: float
    image_contribution: Optional[float] = None
    sensor_contribution: Optional[float] = None
    top_signals: List[str] = []
    data_mode: str
    recommended_action: str
