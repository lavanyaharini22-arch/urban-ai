"""
Builds the required sample dataset shipped with the project:
  - data/raw/sensor_data.csv   (paired sensor readings + labels)
  - data/images/<sample_id>.jpg (matching demo street/CCTV-style images)

Records are joined via sample_id / timestamp / location_id, as required by
the data loader design (see preprocessing/dataset.py).

This is clearly a labeled DEMO dataset (procedurally generated), not a
real-world CCTV/sensor collection — it exists so the project runs and
trains end-to-end out of the box. Replace with a real dataset by keeping
the same CSV schema and image-folder convention.

Usage:
    python preprocessing/build_dataset.py --n 200
"""
import argparse
import csv
import os
import random
import time

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_RAW = os.path.join(ROOT, "data", "raw")
DATA_IMAGES = os.path.join(ROOT, "data", "images")

LOCATIONS = ["LOC-001", "LOC-002", "LOC-003", "LOC-004", "LOC-005"]

HAZARDS = [
    "NORMAL", "AIR_POLLUTION", "FLOOD_RISK", "HEAVY_RAIN",
    "LOW_VISIBILITY", "SMOKE_FIRE_RISK", "EXTREME_ENVIRONMENTAL_CONDITION",
]

# Rough per-hazard sensor profiles (mean, std) used to generate believable,
# separable synthetic readings for each label.
PROFILES = {
    "NORMAL":                          dict(temperature=(26, 3), humidity=(55, 8),  aqi=(45, 15),  pm25=(20, 8),   pm10=(35, 10),  rainfall=(1, 1),   wind_speed=(8, 3),  pressure=(1012, 4)),
    "AIR_POLLUTION":                   dict(temperature=(30, 4), humidity=(50, 10), aqi=(260, 50), pm25=(180, 40), pm10=(230, 45), rainfall=(0, 1),   wind_speed=(4, 2),  pressure=(1009, 4)),
    "FLOOD_RISK":                      dict(temperature=(24, 3), humidity=(90, 5),  aqi=(60, 15),  pm25=(25, 10),  pm10=(40, 12),  rainfall=(65, 15),  wind_speed=(15, 5), pressure=(998, 5)),
    "HEAVY_RAIN":                      dict(temperature=(22, 3), humidity=(85, 6),  aqi=(50, 12),  pm25=(20, 8),   pm10=(35, 10),  rainfall=(45, 10),  wind_speed=(20, 6), pressure=(1001, 5)),
    "LOW_VISIBILITY":                  dict(temperature=(20, 4), humidity=(80, 8),  aqi=(150, 30), pm25=(110, 25), pm10=(150, 30), rainfall=(5, 3),    wind_speed=(3, 2),  pressure=(1010, 4)),
    "SMOKE_FIRE_RISK":                 dict(temperature=(38, 5), humidity=(30, 8),  aqi=(320, 60), pm25=(240, 50), pm10=(280, 55), rainfall=(0, 0.5),  wind_speed=(6, 3),  pressure=(1006, 4)),
    "EXTREME_ENVIRONMENTAL_CONDITION": dict(temperature=(41, 4), humidity=(92, 5),  aqi=(300, 55), pm25=(200, 45), pm10=(260, 50), rainfall=(80, 20),  wind_speed=(35, 8), pressure=(994, 6)),
}

COLORS = {
    "NORMAL": (90, 160, 210),
    "AIR_POLLUTION": (150, 140, 100),
    "FLOOD_RISK": (60, 90, 160),
    "HEAVY_RAIN": (70, 80, 120),
    "LOW_VISIBILITY": (140, 140, 145),
    "SMOKE_FIRE_RISK": (120, 70, 50),
    "EXTREME_ENVIRONMENTAL_CONDITION": (100, 40, 40),
}


def gauss(mean, std):
    return round(max(0, random.gauss(mean, std)), 2)


def make_reading(hazard):
    p = PROFILES[hazard]
    reading = {
        "temperature": gauss(*p["temperature"]),
        "humidity": min(100, gauss(*p["humidity"])),
        "aqi": gauss(*p["aqi"]),
        "pm25": gauss(*p["pm25"]),
        "pm10": gauss(*p["pm10"]),
        "co": round(max(0, random.gauss(1.0, 0.5)), 2),
        "no2": round(max(0, random.gauss(35, 15)), 2),
        "so2": round(max(0, random.gauss(12, 8)), 2),
        "rainfall": gauss(*p["rainfall"]),
        "wind_speed": gauss(*p["wind_speed"]),
        "pressure": gauss(*p["pressure"]),
        "traffic_density": round(random.uniform(0.1, 0.9), 2),
    }
    return reading


def make_demo_image(hazard, size=224):
    """Procedurally generated placeholder 'street scene' image, color-coded
    and textured per hazard type, so the vision branch has real image files
    to load. Clearly a synthetic stand-in for genuine CCTV imagery."""
    base = COLORS[hazard]
    img = Image.new("RGB", (size, size), base)
    draw = ImageDraw.Draw(img)

    # Simple horizon + ground-plane silhouette so images aren't flat color.
    horizon_y = size // 2 + random.randint(-15, 15)
    ground_color = tuple(max(0, c - 40) for c in base)
    draw.rectangle([0, horizon_y, size, size], fill=ground_color)

    # Random blocky "buildings"/silhouettes for texture.
    for _ in range(random.randint(3, 7)):
        x0 = random.randint(0, size - 20)
        w = random.randint(15, 40)
        h = random.randint(20, 80)
        y0 = horizon_y - h
        shade = tuple(max(0, c - random.randint(20, 60)) for c in base)
        draw.rectangle([x0, y0, x0 + w, horizon_y], fill=shade)

    # Hazard-specific overlay texture.
    if hazard in ("FLOOD_RISK", "HEAVY_RAIN", "EXTREME_ENVIRONMENTAL_CONDITION"):
        for _ in range(60):
            x, y = random.randint(0, size - 1), random.randint(0, size - 1)
            draw.line([x, y, x + 2, y + 8], fill=(200, 210, 230), width=1)
    if hazard in ("AIR_POLLUTION", "LOW_VISIBILITY", "SMOKE_FIRE_RISK"):
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(2, 5)))
    if hazard == "SMOKE_FIRE_RISK":
        overlay = Image.new("RGB", (size, size), (60, 60, 60))
        img = Image.blend(img, overlay, alpha=0.25)

    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    return img


def build(n=200, seed=42):
    random.seed(seed)
    os.makedirs(DATA_RAW, exist_ok=True)
    os.makedirs(DATA_IMAGES, exist_ok=True)

    csv_path = os.path.join(DATA_RAW, "sensor_data.csv")
    fieldnames = ["sample_id", "timestamp", "location_id", "hazard_label", "image_path",
                  "temperature", "humidity", "aqi", "pm25", "pm10", "co", "no2", "so2",
                  "rainfall", "wind_speed", "pressure", "traffic_density"]

    start_ts = int(time.time()) - n * 300
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(n):
            sample_id = f"S{i:05d}"
            hazard = random.choice(HAZARDS)
            reading = make_reading(hazard)
            location = random.choice(LOCATIONS)
            timestamp = start_ts + i * 300  # every 5 minutes

            image_name = f"{sample_id}.jpg"
            image_path = os.path.join(DATA_IMAGES, image_name)
            make_demo_image(hazard).save(image_path, quality=88)

            row = {
                "sample_id": sample_id,
                "timestamp": timestamp,
                "location_id": location,
                "hazard_label": hazard,
                "image_path": f"data/images/{image_name}",
                **reading,
            }
            writer.writerow(row)

    print(f"[OK] Wrote {n} paired samples to {csv_path}")
    print(f"[OK] Wrote {n} demo images to {DATA_IMAGES}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=200, help="Number of paired samples to generate")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    build(n=args.n, seed=args.seed)
