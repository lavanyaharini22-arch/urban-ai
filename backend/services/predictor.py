"""
Singleton inference service. Loads a trained checkpoint if one exists at
models/trained/multimodal_model.pt (DATA MODE: REAL); otherwise runs the
freshly-initialized architecture in DATA MODE: DEMO so predictions are
clearly labeled as demonstration output and never as real-world results.
"""
import os
import io
import torch
import torch.nn.functional as F
from PIL import Image

from models.vision_net import VisionEncoder
from models.sensor_net import SensorEncoder, SENSOR_FEATURES, vectorize_sensor_dict
from models.fusion_net import MultimodalHazardModel, HAZARD_CATEGORIES, risk_level_for

CHECKPOINT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "models", "trained", "multimodal_model.pt",
)

RECOMMENDATIONS = {
    "NORMAL": "No action required. Continue routine monitoring.",
    "AIR_POLLUTION": "Limit outdoor exposure; advise sensitive groups to stay indoors.",
    "FLOOD_RISK": "Issue flood advisory; monitor drainage and low-lying areas.",
    "HEAVY_RAIN": "Prepare drainage systems; alert traffic authorities.",
    "LOW_VISIBILITY": "Advise reduced vehicle speed and increased following distance.",
    "SMOKE_FIRE_RISK": "Dispatch inspection; alert fire and emergency services.",
    "EXTREME_ENVIRONMENTAL_CONDITION": "Activate emergency response protocol.",
}

SIGNAL_LABELS = {
    "temperature": "Temperature", "humidity": "Humidity", "aqi": "Air Quality Index",
    "pm25": "PM2.5", "pm10": "PM10", "co": "Carbon Monoxide", "no2": "NO2",
    "so2": "SO2", "rainfall": "Rainfall", "wind_speed": "Wind Speed",
    "pressure": "Atmospheric Pressure", "traffic_density": "Traffic Density",
}


class PredictorService:
    _instance = None

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.vision_encoder = VisionEncoder(pretrained=True)
        self.sensor_encoder = SensorEncoder()
        self.model = MultimodalHazardModel(self.vision_encoder, self.sensor_encoder)
        self.model.to(self.device)
        self.model.eval()
        self.data_mode = "DEMO"

        if os.path.exists(CHECKPOINT_PATH):
            try:
                state = torch.load(CHECKPOINT_PATH, map_location=self.device)
                self.model.load_state_dict(state)
                self.data_mode = "REAL"
            except Exception:
                self.data_mode = "DEMO"

        self.vision_transform = VisionEncoder.preprocess()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = PredictorService()
        return cls._instance

    def gpu_status(self):
        return {
            "cuda_available": torch.cuda.is_available(),
            "device": str(self.device),
            "vision_backbone": self.vision_encoder.mode,
            "data_mode": self.data_mode,
        }

    def _load_image_tensor(self, image_bytes: bytes):
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = self.vision_transform(img).unsqueeze(0).to(self.device)
        return tensor

    @torch.no_grad()
    def predict(self, image_bytes: bytes = None, sensor_dict: dict = None):
        image_tensor = self._load_image_tensor(image_bytes) if image_bytes else None
        sensor_tensor = None
        if sensor_dict is not None:
            sensor_tensor = vectorize_sensor_dict(sensor_dict).unsqueeze(0).to(self.device)

        logits, importance = self.model(image_tensor, sensor_tensor)
        probs = F.softmax(logits, dim=-1).squeeze(0)
        confidence, pred_idx = torch.max(probs, dim=0)
        hazard = HAZARD_CATEGORIES[pred_idx.item()]
        confidence = float(confidence.item())
        risk = risk_level_for(hazard, confidence)

        img_w, sensor_w = importance.squeeze(0).tolist()
        top_signals = self._top_signals(sensor_dict) if sensor_dict else []

        return {
            "hazard": hazard,
            "risk_level": risk,
            "confidence": round(confidence * 100, 2),
            "image_contribution": round(img_w * 100, 2) if image_bytes else None,
            "sensor_contribution": round(sensor_w * 100, 2) if sensor_dict else None,
            "top_signals": top_signals,
            "data_mode": self.data_mode,
            "recommended_action": RECOMMENDATIONS.get(hazard, "Monitor situation."),
        }

    def _top_signals(self, sensor_dict: dict, k=4):
        """Permutation-style importance: perturb each sensor feature toward
        its population mean and measure the resulting shift in predicted
        hazard probability. Larger shift => more influential feature.
        This is a model-derived interpretability signal, not a causal
        explanation."""
        base_tensor = vectorize_sensor_dict(sensor_dict).unsqueeze(0).to(self.device)
        with torch.no_grad():
            base_logits, _ = self.model(None, base_tensor)
            base_probs = F.softmax(base_logits, dim=-1).squeeze(0)
            base_top = base_probs.max().item()

        scores = {}
        for i, feat in enumerate(SENSOR_FEATURES):
            perturbed = base_tensor.clone()
            perturbed[0, i] = 0.0  # neutralize to population mean (already normalized)
            with torch.no_grad():
                logits, _ = self.model(None, perturbed)
                probs = F.softmax(logits, dim=-1).squeeze(0)
            shift = abs(base_top - probs.max().item())
            scores[feat] = shift

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
        return [SIGNAL_LABELS.get(f, f) for f, _ in ranked]
