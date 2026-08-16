"""
Loads the paired sensor-CSV + image dataset (joined by sample_id) for
training and evaluation. Falls back gracefully if the dataset hasn't been
generated yet.

Expected files (created by preprocessing/build_dataset.py):
    data/raw/sensor_data.csv   - one row per sample, with sample_id,
                                  timestamp, location_id, hazard_label,
                                  image_path, and sensor feature columns
    data/images/<sample_id>.jpg - matching image for each row

If these files are missing, `PairedHazardDataset.available()` returns
False so callers (e.g. training/train.py) can fall back to the pure
synthetic in-memory dataset instead of crashing.
"""
import csv
import os

import torch
from torch.utils.data import Dataset
from PIL import Image, UnidentifiedImageError

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV_PATH = os.path.join(ROOT, "data", "raw", "sensor_data.csv")
IMAGES_DIR = os.path.join(ROOT, "data", "images")

import sys
sys.path.append(os.path.join(ROOT, "backend"))
from models.sensor_net import vectorize_sensor_dict  # noqa: E402
from models.fusion_net import HAZARD_CATEGORIES  # noqa: E402
from models.vision_net import VisionEncoder  # noqa: E402


class PairedHazardDataset(Dataset):
    """Real (well, dataset-provided) paired sensor + image samples, joined
    by sample_id. Missing or corrupted images are handled gracefully with
    a blank fallback image rather than crashing the run."""

    def __init__(self, csv_path=CSV_PATH, images_dir=IMAGES_DIR):
        self.images_dir = images_dir
        self.rows = []
        if not os.path.exists(csv_path):
            return
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.rows.append(row)
        self.transform = VisionEncoder.preprocess()

    @staticmethod
    def available(csv_path=CSV_PATH, images_dir=IMAGES_DIR):
        return os.path.exists(csv_path) and os.path.isdir(images_dir) and len(os.listdir(images_dir)) > 0

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx):
        row = self.rows[idx]
        label_idx = HAZARD_CATEGORIES.index(row["hazard_label"])

        image_name = os.path.basename(row["image_path"])
        image_file = os.path.join(self.images_dir, image_name)
        try:
            img = Image.open(image_file).convert("RGB")
            image_tensor = self.transform(img)
        except (FileNotFoundError, UnidentifiedImageError, OSError):
            # Missing/corrupted image -> safe blank fallback, never crash.
            image_tensor = torch.zeros(3, 224, 224)

        sensor_dict = {k: float(row[k]) for k in
                       ["temperature", "humidity", "aqi", "pm25", "pm10", "co", "no2",
                        "so2", "rainfall", "wind_speed", "pressure", "traffic_density"]
                       if row.get(k) not in (None, "")}
        sensor_tensor = vectorize_sensor_dict(sensor_dict)

        return image_tensor, sensor_tensor, label_idx
