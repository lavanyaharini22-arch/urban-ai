"""
Training pipeline for the multimodal hazard model.

Dataset -> Preprocessing -> Image Encoder -> Sensor Encoder ->
Multimodal Fusion -> Prediction Head -> Loss -> Backpropagation

Usage:
    python training/train.py --epochs 10 --synthetic

If no real dataset is found under data/raw (paired sensor CSV + image
folder with a sample_id/timestamp/location_id join key), this script
automatically trains on generated synthetic data so the pipeline always
runs end-to-end. This is DEMO training, not a real-world-accurate model.
"""
import argparse
import os
import sys
import random

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.append(os.path.join(ROOT, "backend"))
sys.path.append(ROOT)

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split

from models.vision_net import VisionEncoder, IMG_SIZE
from models.sensor_net import SensorEncoder, SENSOR_FEATURES, vectorize_sensor_dict
from models.fusion_net import MultimodalHazardModel, HAZARD_CATEGORIES
from services.synthetic_data import generate_synthetic_reading
from preprocessing.dataset import PairedHazardDataset

CHECKPOINT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models", "trained")


class SyntheticHazardDataset(Dataset):
    """Generates paired synthetic (sensor, label) samples for pipeline
    verification and demo training. Image branch uses random noise tensors
    standing in for real street/CCTV imagery when no dataset is provided."""

    def __init__(self, n_samples=800, use_images=True):
        self.n = n_samples
        self.use_images = use_images
        self.samples = [self._make_sample() for _ in range(n_samples)]

    def _make_sample(self):
        label_idx = random.randrange(len(HAZARD_CATEGORIES))
        label = HAZARD_CATEGORIES[label_idx]
        scenario = {
            "FLOOD_RISK": "flood", "HEAVY_RAIN": "flood",
            "AIR_POLLUTION": "pollution", "SMOKE_FIRE_RISK": "pollution",
            "NORMAL": "normal",
        }.get(label, "random")
        reading = generate_synthetic_reading(scenario)
        return reading, label_idx

    def __len__(self):
        return self.n

    def __getitem__(self, idx):
        reading, label_idx = self.samples[idx]
        sensor_vec = vectorize_sensor_dict(reading)
        image_tensor = torch.randn(3, IMG_SIZE, IMG_SIZE) * 0.1  # placeholder imagery
        return image_tensor, sensor_vec, label_idx


def train(epochs=10, batch_size=16, lr=1e-4, use_synthetic=True, save=True):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[INFO] Using device: {device}")

    if PairedHazardDataset.available():
        dataset = PairedHazardDataset()
        print(f"[INFO] DATA MODE: REAL — loaded {len(dataset)} paired samples from "
              f"data/raw/sensor_data.csv + data/images/. "
              f"Run 'python preprocessing/build_dataset.py' if this file is missing or you want to regenerate it.")
    else:
        dataset = SyntheticHazardDataset(n_samples=800)
        print("[INFO] DATA MODE: DEMO — no dataset found at data/raw/sensor_data.csv. "
              "Run 'python preprocessing/build_dataset.py' to generate the sample dataset, "
              "training on purely synthetic in-memory data for now.")

    train_len = int(0.7 * len(dataset))
    val_len = int(0.15 * len(dataset))
    test_len = len(dataset) - train_len - val_len
    train_ds, val_ds, test_ds = random_split(dataset, [train_len, val_len, test_len])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)
    test_loader = DataLoader(test_ds, batch_size=batch_size)

    vision_encoder = VisionEncoder(pretrained=True)
    sensor_encoder = SensorEncoder()
    model = MultimodalHazardModel(vision_encoder, sensor_encoder).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    best_val_acc = 0.0
    patience, patience_counter = 3, 0

    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for images, sensors, labels in train_loader:
            images, sensors, labels = images.to(device), sensors.to(device), labels.to(device)
            optimizer.zero_grad()
            logits, _ = model(images, sensors)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * images.size(0)

        train_loss = total_loss / len(train_ds)
        val_acc = evaluate(model, val_loader, device)
        print(f"[EPOCH {epoch}/{epochs}] train_loss={train_loss:.4f} val_acc={val_acc:.4f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            if save:
                torch.save(model.state_dict(), os.path.join(CHECKPOINT_DIR, "multimodal_model.pt"))
                print(f"[INFO] Checkpoint saved (val_acc={val_acc:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print("[INFO] Early stopping triggered.")
                break

    test_acc = evaluate(model, test_loader, device)
    print(f"[RESULT] Final test accuracy: {test_acc:.4f}")


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    correct, total = 0, 0
    for images, sensors, labels in loader:
        images, sensors, labels = images.to(device), sensors.to(device), labels.to(device)
        logits, _ = model(images, sensors)
        preds = logits.argmax(dim=-1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)
    return correct / max(total, 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--synthetic", action="store_true", default=True)
    args = parser.parse_args()
    train(epochs=args.epochs, batch_size=args.batch_size, lr=args.lr, use_synthetic=args.synthetic)
