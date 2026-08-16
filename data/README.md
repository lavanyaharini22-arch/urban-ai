# Dataset

This folder ships with a **ready-to-use sample dataset** so the project trains and runs end-to-end out of the box — you don't have to source real data before you can demo it.

## What's here

- **`raw/sensor_data.csv`** — 200 paired samples. Columns: `sample_id, timestamp, location_id, hazard_label, image_path` + the 12 sensor features (`temperature, humidity, aqi, pm25, pm10, co, no2, so2, rainfall, wind_speed, pressure, traffic_density`).
- **`images/`** — 200 matching `.jpg` images, one per `sample_id`, named `<sample_id>.jpg` (e.g. `S00000.jpg`), referenced by `image_path` in the CSV.
- Records are joined via **`sample_id`** (and carry `timestamp` / `location_id` for time-series and location-based analysis), exactly as required by the multimodal data loader (`preprocessing/dataset.py`).

## Important: this is a labeled DEMO dataset

The sensor readings are procedurally generated from per-hazard statistical profiles, and the images are procedurally rendered placeholder scenes (color/texture coded per hazard) — **not real CCTV footage or real sensor logs.** This exists so:

- `training/train.py` has real, on-disk paired data to train against immediately.
- The vision and sensor branches both see genuine files (not just in-memory tensors), exercising the full data-loading path.
- You can swap in real data without changing any code, as long as you keep the same CSV schema and image-folder convention.

The app always labels predictions `DATA MODE: DEMO` until you train on your own real dataset and the resulting checkpoint is loaded.

## Regenerating or resizing the dataset

```bat
venv\Scripts\activate
python preprocessing/build_dataset.py --n 400
```

`--n` controls how many paired samples to generate (default 200). Re-running overwrites `raw/sensor_data.csv` and regenerates matching images.

## Using a real dataset instead

Replace the contents of `raw/sensor_data.csv` and `images/` with your own data, keeping:
- One CSV row per sample with the same column names.
- One image file per sample named to match `image_path`.
- Consistent `sample_id` values joining the two.

Then run `python training/train.py` — it automatically detects and prefers the real dataset over synthetic in-memory data (see `preprocessing/dataset.py::PairedHazardDataset.available()`).
