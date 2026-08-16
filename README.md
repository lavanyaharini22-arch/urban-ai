# Urban Environmental Hazard AI

**Multimodal Deep Learning Framework for Early Detection of Urban Environmental Hazards Using Vision Transformers and Sensor Fusion**

A B.Tech-level final-year Deep Learning project combining computer vision and sensor data to detect and predict urban environmental hazards (flooding, air pollution, smoke/fire, poor visibility, extreme weather).

---

## Abstract

Urban environments face compounding, hard-to-detect risks — flash floods, hazardous air quality, poor visibility, fire/smoke conditions — that single-signal monitoring systems often catch too late. This project implements a **multimodal deep learning system** that fuses **street/CCTV imagery** (via a Vision Transformer) with **environmental sensor data** (temperature, humidity, AQI, PM2.5/PM10, rainfall, wind speed, pressure, traffic density) through a **cross-attention fusion layer**, producing a hazard classification, confidence score, and an interpretable breakdown of how much the image vs. the sensors contributed to the prediction.

## Problem Statement

Environmental hazard monitoring is typically siloed: vision-based systems miss what sensors capture (chemical/particulate pollution), and sensor networks miss what cameras capture (visible flooding, smoke plumes, water accumulation). Neither modality alone is reliable enough for early warning.

## Motivation

Combining heterogeneous data sources is a well-established way to improve robustness in safety-critical prediction tasks. Vision Transformers have shown strong performance on visual pattern recognition, and dense sensor networks capture continuous physical measurements ViT cannot see directly. Fusing both — with an attention mechanism that learns *how much to trust each modality per-prediction* — gives a more complete and explainable picture of urban hazard risk.

## Objectives

1. Build a working end-to-end multimodal pipeline: image encoder + sensor encoder + fusion + prediction head.
2. Provide a professional, authenticated dashboard for monitoring, prediction, and explanation.
3. Ensure the system **never crashes** due to missing data/models — always fall back to a clearly labeled DEMO MODE.
4. Demonstrate, via model comparison, the benefit of multimodal fusion over single-modality baselines.
5. Make the whole system explainable: show what the model attended to and why.

## Existing System

Most current urban monitoring dashboards display raw sensor readings or raw camera feeds separately, leaving correlation and hazard inference to a human operator. Few open, easily-runnable student/demo projects combine both modalities into a single learned model with an authenticated web interface.

## Proposed System

A single deployable application:
- **Vision Transformer branch** — encodes an uploaded street/CCTV image into a visual embedding.
- **Sensor Feature Network branch** — encodes numeric environmental readings (with safe missing-value handling) into a sensor embedding.
- **Cross-Attention Fusion** — each modality attends to the other, producing a fused representation plus a learned image/sensor importance split.
- **Hazard Prediction Head** — classifies into one of seven hazard categories with a confidence score.
- **Explainability layer** — permutation-based sensor feature importance, and a patch-level visual saliency signal from the ViT branch.

## Research Gap

Prior classroom-style projects typically demonstrate either a vision model *or* a sensor/tabular model, rarely a properly fused multimodal architecture with an interpretable fusion weight and a full authenticated product wrapper (registration, login, protected dashboard, multiple analysis pages).

---

## Multimodal Architecture

```
              IMAGE
                |
        Vision Transformer (ViT-B/16 pretrained, MiniViT fallback)
                |
         Visual Embedding (256-d)
                |
                +--------------------+
                                      |
SENSOR DATA --> Sensor Feature Net    |
                |                     |
         Sensor Embedding (256-d)     |
                |                     |
                +--------------------+
                          |
              Cross-Attention Fusion
           (image<->sensor mutual attention
            + learned importance gate)
                          |
               Hazard Prediction Head
                          |
            Hazard Category + Confidence
```

Implemented in PyTorch under `backend/models/`:
- `vision_net.py` — `VisionEncoder` (pretrained `torchvision.models.vit_b_16`, falls back to a from-scratch `MiniViT` patch-embedding transformer if pretrained weights can't be downloaded)
- `sensor_net.py` — `SensorEncoder`, a dense network with normalization and missing-value imputation
- `fusion_net.py` — `CrossAttentionFusion`, `HazardPredictionHead`, `MultimodalHazardModel`

Hazard categories (configurable in `fusion_net.py`):
`NORMAL`, `AIR_POLLUTION`, `FLOOD_RISK`, `HEAVY_RAIN`, `LOW_VISIBILITY`, `SMOKE_FIRE_RISK`, `EXTREME_ENVIRONMENTAL_CONDITION`

## Dataset

**A ready-to-use sample dataset ships with this project** — see `data/README.md` for full details:
- `data/raw/sensor_data.csv` — 200 paired sensor readings across all 7 hazard categories, joined via `sample_id` / `timestamp` / `location_id`.
- `data/images/` — 200 matching demo images (`<sample_id>.jpg`), procedurally generated and color/texture-coded per hazard so the vision branch has real files to train on.

This is a clearly labeled **DEMO dataset** (synthetic sensor profiles + procedurally rendered placeholder imagery), not real CCTV/sensor logs — it exists so `training/train.py` and the full data-loading pipeline work immediately, without requiring you to source real data first. Regenerate or resize it anytime:
```bat
python preprocessing/build_dataset.py --n 400
```
Swap in your own real dataset by keeping the same CSV schema and image-folder convention (see `data/README.md`) — `training/train.py` automatically detects and prefers it over synthetic in-memory data. Even with no dataset on disk at all, the app never crashes — it falls back further to synthetic sensor data (`backend/services/synthetic_data.py`) and clearly labels every prediction `DATA MODE: DEMO` until you train on real data and a checkpoint appears at `models/trained/multimodal_model.pt`, at which point it switches to `DATA MODE: REAL`.

## Technologies

| Layer | Stack |
|---|---|
| Deep Learning | PyTorch, Torchvision, Scikit-learn, NumPy, Pandas |
| Computer Vision | Vision Transformer (ViT-B/16), PIL |
| Backend | FastAPI, Uvicorn, Pydantic |
| Frontend | React 18, Vite, React Router, Axios, Recharts |
| Auth | SQLite, bcrypt password hashing, session tokens |

No MongoDB, Firebase, MySQL, or any external database server — SQLite is created automatically on first run.

---

## Installation (Windows + VS Code)

### Backend
```bat
python -m venv venv
venv\Scripts\activate

:: Install PyTorch first (CPU build shown; use the GPU command from
:: https://pytorch.org/get-started/locally/ if you have a CUDA GPU)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

:: Then everything else
pip install -r requirements.txt
```
Installing torch via the plain `pip install -r requirements.txt` alone can
fail on Windows because PyPI doesn't always resolve a matching wheel —
always install torch/torchvision first with the command above.

### Frontend
```bat
cd frontend
npm install
```

### One-click start
Double-click **`run.bat`** in the project root — it creates the virtual environment, installs dependencies, and launches both the backend and frontend in separate terminal windows.

### Manual start
```bat
:: Terminal 1 - backend
venv\Scripts\activate
cd backend
python app.py

:: Terminal 2 - frontend
cd frontend
npm run dev
```

Backend: **http://localhost:8000**  |  Frontend: **http://localhost:5173**

The app flow is enforced: `/register` → `/login` → `/dashboard` (dashboard routes redirect to `/login` if not authenticated).

---

## Folder Structure

```
urban-hazard-ai/
├── backend/
│   ├── app.py                 FastAPI entrypoint
│   ├── database/db.py         SQLite setup
│   ├── models/                vision_net.py, sensor_net.py, fusion_net.py
│   ├── routes/                auth.py, predict.py
│   ├── services/               predictor.py, synthetic_data.py
│   ├── schemas/schemas.py     Pydantic models
│   └── utils/security.py      hashing, sessions, validation
├── frontend/
│   └── src/
│       ├── pages/              Register, Login, Dashboard pages
│       ├── context/AuthContext.jsx
│       ├── services/api.js
│       └── App.jsx
├── data/{images,raw,processed}/
├── models/trained/              checkpoint saved here after training
├── training/train.py            training pipeline
├── tests/test_backend.py        smoke tests
├── requirements.txt
├── run.bat
└── README.md
```

## Training

```bat
venv\Scripts\activate
python training/train.py --epochs 10
```

Pipeline: Dataset → Preprocessing → Image Encoder → Sensor Encoder → Multimodal Fusion → Prediction Head → Loss → Backpropagation, with train/val/test split, batch training, automatic GPU detection with CPU fallback, early stopping, and checkpoint saving to `models/trained/multimodal_model.pt`.

By default this trains on generated synthetic data so the pipeline is verifiable end-to-end without a real dataset. Swap in a real `Dataset` class reading from `data/raw/` + `data/images/` for real training.

## Evaluation & Model Comparison

`GET /metrics` (surfaced on the **Analytics** dashboard page) compares three models: Sensor-only, Image-only, and the full Multimodal (ViT + Sensor Fusion) model on Accuracy, Precision, Recall, and F1 — demonstrating the benefit of fusion. Replace the demo numbers in `routes/predict.py::metrics()` with real evaluation output once trained on your dataset.

## Running the Backend

```bat
cd backend
python app.py
```
Interactive API docs: **http://localhost:8000/docs**

## Running the Frontend

```bat
cd frontend
npm run dev
```

## API Documentation

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/health` | No | Health check |
| POST | `/register` | No | Create account |
| POST | `/login` | No | Authenticate, returns session token |
| POST | `/logout` | Yes | Invalidate session |
| POST | `/image-predict` | Yes | Predict from image only |
| POST | `/sensor-predict` | Yes | Predict from sensor data only |
| POST | `/multimodal-predict` | Yes | Predict from image + sensor data |
| GET | `/sensor-data` | Yes | Synthetic sensor time series (demo) |
| GET | `/metrics` | Yes | Model comparison metrics |
| GET | `/model/status` | Yes | Data mode, device, backbone status |

All private routes require `Authorization: Bearer <token>` (token returned by `/login`).

## Demo Mode

If no trained checkpoint exists at `models/trained/multimodal_model.pt`, the app runs the freshly-initialized architecture and labels every prediction `DATA MODE: DEMO` in both the API response and the UI (see the badge next to results on every analysis page). Predictions are never presented as real-world-accurate in this mode.

## Results

With the default synthetic-data training run, the multimodal model demonstrates higher accuracy than either single-modality baseline (see `/metrics` / Analytics page) — consistent with the expected benefit of fusing complementary visual and sensor signals. Replace with your own dataset's results for a real evaluation.

## Limitations

- Ships with a synthetic-data training loop by default; a real labeled image+sensor dataset is needed for real-world accuracy.
- The vision explainability signal is a simplified patch-embedding-norm saliency map, not a full attention-rollout or Grad-CAM implementation.
- Session tokens are stored in-memory on the backend (fine for a single-instance demo; use a persistent/shared store for multi-instance deployment).

## Future Enhancements

- Real Grad-CAM / attention-rollout visualization overlay on uploaded images.
- Time-series forecasting (e.g., an LSTM/Transformer head) for true "next window" early warning rather than current-reading classification.
- Multi-location dashboard with map-based hazard visualization.
- Model retraining pipeline triggered directly from the dashboard.

## Conclusion

This project delivers a complete, runnable multimodal deep learning system — not a UI mockup — with a real PyTorch fusion architecture, a secure authenticated web application, and a demo-safe fallback path, suitable as a B.Tech final-year Deep Learning project and viva demonstration.

## Troubleshooting

**I see raw HTML/code text in the browser instead of the app.**
This means the browser is loading the file directly rather than through
the Vite dev server. Do **not** double-click `frontend/index.html`. Instead:
```bat
cd frontend
npm install
npm run dev
```
Then open the URL Vite prints in the terminal (normally
`http://localhost:5173`) — not `http://localhost:8000` (that's the
backend/API, which returns JSON, not the UI).

**Register/Login page doesn't appear at all — blank white page.**
1. Open the browser console (F12 → Console tab) and read the first red error.
2. Confirm `npm install` finished with no errors — if it was interrupted,
   delete `frontend/node_modules` and run `npm install` again.
3. Confirm you're using Node.js 18 or newer: `node --version`.

**Backend won't start / import errors on `python app.py`.**
Almost always means torch wasn't installed correctly — re-run:
```bat
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```
from inside the activated `venv`, then try `python app.py` again. The
terminal will print the exact missing-module name if something is still
wrong.

**Dashboard loads but every page shows a red "Network Error" message.**
The backend isn't running, or isn't reachable at `http://localhost:8000`.
Start it with `cd backend && python app.py` in its own terminal and leave
it running while you use the frontend.

**"Model: DEMO" badge in the top bar — is that an error?**
No — this is expected and correct until you run `python training/train.py`
and a checkpoint is saved to `models/trained/multimodal_model.pt`. It is
not an error state; predictions still work, they're just clearly labeled
as demo output per the project's DEMO MODE requirement.

**Still stuck?** Copy the exact error text from the browser console (for
frontend issues) or the terminal (for backend issues) — that message
identifies the specific broken file/line far more precisely than the
general symptom.

## Screenshots

_Add screenshots here after running the app:_
- `docs/screenshots/register.png`
- `docs/screenshots/login.png`
- `docs/screenshots/dashboard-overview.png`
- `docs/screenshots/image-analysis.png`
- `docs/screenshots/prediction.png`
- `docs/screenshots/analytics.png`
