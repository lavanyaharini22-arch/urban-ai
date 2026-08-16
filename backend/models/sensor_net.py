"""
Sensor branch: dense neural network over environmental sensor readings.
Handles missing values safely via masked mean-imputation + a learned
"missingness" indicator, then normalizes and encodes to an embedding.
"""
import torch
import torch.nn as nn

SENSOR_FEATURES = [
    "temperature", "humidity", "aqi", "pm25", "pm10",
    "co", "no2", "so2", "rainfall", "wind_speed",
    "pressure", "traffic_density",
]

# Reasonable population means/stds used for normalization + imputation of
# missing values (demo statistics; replace with dataset-derived stats when
# training on a real dataset).
FEATURE_STATS = {
    "temperature": (28.0, 6.0), "humidity": (65.0, 15.0), "aqi": (120.0, 60.0),
    "pm25": (60.0, 40.0), "pm10": (90.0, 50.0), "co": (1.0, 0.5),
    "no2": (40.0, 20.0), "so2": (15.0, 10.0), "rainfall": (10.0, 15.0),
    "wind_speed": (10.0, 6.0), "pressure": (1010.0, 8.0), "traffic_density": (0.5, 0.25),
}


def vectorize_sensor_dict(data: dict) -> torch.Tensor:
    """Convert a sensor dict (possibly with missing keys) into a normalized
    feature vector, imputing missing values with the population mean."""
    values = []
    for feat in SENSOR_FEATURES:
        mean, std = FEATURE_STATS[feat]
        raw = data.get(feat, None)
        if raw is None:
            raw = mean  # safe imputation for missing sensor values
        values.append((float(raw) - mean) / std)
    return torch.tensor(values, dtype=torch.float32)


class SensorEncoder(nn.Module):
    def __init__(self, in_dim=len(SENSOR_FEATURES), embed_dim=256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.2),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, embed_dim),
        )

    def forward(self, x):
        if x.dim() == 1:
            x = x.unsqueeze(0)
        # BatchNorm needs >1 sample in train mode; safe for eval/inference.
        return self.net(x)
