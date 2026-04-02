# 🌾 Indian Farmer Crop Recommendation System — Setup Guide

> **Who is this for?**  
> This guide is for anyone who wants to **run this project locally** for the first time — students, developers, researchers, or curious farmers. No prior setup experience required.

---

## 📋 Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Install Python](#2-install-python)
3. [Clone the Repository](#3-clone-the-repository)
4. [Create a Virtual Environment](#4-create-a-virtual-environment)
5. [Install Dependencies](#5-install-dependencies)
6. [Run the Application](#6-run-the-application)
7. [(Optional) Fetch District Weather Data](#7-optional-fetch-district-weather-data)
8. [(Optional) Train the ML Models](#8-optional-train-the-ml-models)
9. [Using the Web Interface](#9-using-the-web-interface)
10. [Using the API](#10-using-the-api)
11. [Troubleshooting](#11-troubleshooting)
12. [Project Folder Overview](#12-project-folder-overview)

---

## 1. System Requirements

Before you start, make sure your computer meets these requirements:

| Component  | Minimum                        | Recommended                   |
|------------|-------------------------------|-------------------------------|
| **OS**     | Windows 10 / macOS 11 / Ubuntu 20.04 | Windows 11 / macOS 13 / Ubuntu 22.04 |
| **Python** | 3.8+                          | 3.10 or 3.11                  |
| **RAM**    | 4 GB                          | 8 GB (needed if training LSTM/XGBoost) |
| **Storage**| 1 GB free                     | 2 GB free (with full weather data) |
| **Internet**| Required (for weather data)  | Stable broadband               |
| **Browser**| Chrome / Firefox / Edge / Safari (latest) | Any modern browser |

> ✅ **No API keys needed.** The app fetches weather from [Open-Meteo](https://open-meteo.com/) for free.

---

## 2. Install Python

> Skip this step if Python 3.8 or newer is already installed. Check by running `python --version` in your terminal.

### 🪟 Windows
1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download the latest **Python 3.x** installer
3. Run the installer — ⚠️ **Check the box "Add Python to PATH"** before clicking Install
4. Verify installation:
   ```powershell
   python --version
   pip --version
   ```

### 🍎 macOS
```bash
# Using Homebrew (recommended)
brew install python

# Verify
python3 --version
pip3 --version
```

### 🐧 Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# Verify
python3 --version
```

---

## 3. Clone the Repository

You need **Git** installed to clone. Check with `git --version`.  
If not installed → [https://git-scm.com/downloads](https://git-scm.com/downloads)

```bash
git clone https://github.com/tirthch25/Indian-Farmer-Crop-Recommendation-System.git
```

After cloning, navigate into the project:
```bash
cd Indian-Farmer-Crop-Recommendation-System
```

> 💡 Alternatively, you can download the ZIP from GitHub (green "Code" button → Download ZIP) and extract it manually.

---

## 4. Create a Virtual Environment

A virtual environment keeps project dependencies isolated from your system Python. **Highly recommended.**

Navigate to the app directory first:
```bash
cd agri_crop_recommendation
```

Then create and activate the virtual environment:

### 🪟 Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\activate
```

> If you get a policy error in PowerShell, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then try activating again.

### 🍎 macOS / 🐧 Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**How to know it worked:** Your terminal prompt should now show `(.venv)` at the beginning.

To **deactivate** the environment later:
```bash
deactivate
```

---

## 5. Install Dependencies

Make sure your virtual environment is **active** (you see `(.venv)` in your prompt), then run:

```bash
pip install -r requirements.txt
```

This installs all required packages:

| Package          | Purpose                                   |
|-----------------|-------------------------------------------|
| `fastapi`        | Web API framework                         |
| `uvicorn`        | ASGI web server                           |
| `torch`          | PyTorch — LSTM weather forecasting        |
| `xgboost`        | XGBoost — weather forecasting             |
| `scikit-learn`   | Random Forest — crop suitability          |
| `pandas`         | Data processing                           |
| `numpy`          | Numerical computing                       |
| `requests`       | HTTP calls to weather API                 |
| `jinja2`         | Web template rendering                    |
| `pyarrow`        | Parquet file support (weather data)       |
| `joblib`         | Model serialization                       |
| `matplotlib`     | Plotting (used during training)           |

> ⏳ Installation may take **3–10 minutes** as PyTorch is a large package (~700 MB).

---

## 6. Run the Application

Make sure you are inside the `agri_crop_recommendation/` folder with the virtual environment active.

```bash
python run_website.py
```

You should see output like:
```
======================================================================
🌾 FARMER CROP RECOMMENDATION SYSTEM
======================================================================

Starting web server...

📍 Access the website at: http://localhost:8000
📍 API documentation at: http://localhost:8000/docs

Press CTRL+C to stop the server

======================================================================
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ The server is now running! Open your browser and go to:

| URL                              | What you see                         |
|----------------------------------|--------------------------------------|
| `http://localhost:8000`          | 🌾 Farmer-friendly Web Interface      |
| `http://localhost:8000/docs`     | 📡 Interactive Swagger API Docs       |
| `http://localhost:8000/health`   | 🟢 API health check (JSON response)   |
| `http://localhost:8000/regions`  | 📍 List of all 640+ supported regions |

To **stop the server**, press `Ctrl + C` in the terminal.

---

## 7. (Optional) Fetch District Weather Data

> ⚠️ **This step is optional.** The app works without it using zone-level climate data fallback. Do this only if you want full district-level LSTM/XGBoost accuracy.

This script downloads historical daily weather data for **640+ districts across 34 Indian states** from the Open-Meteo API.

```bash
python scripts/fetch_district_weather.py
```

> ⏳ **Estimated time:** 2–6 hours depending on your internet speed and API rate limits.  
> 💾 **Disk space:** ~300–500 MB for the full district dataset.  
> ✅ Progress is saved incrementally — you can stop and resume safely.

---

## 8. (Optional) Train the ML Models

> ⚠️ **This step is optional.** The app works perfectly without it — it falls back to rule-based scoring automatically. Train only if you want full ML-enhanced predictions.

The system has **three separate ML models**, each trained by the same script using the `--model` flag.

### 🔁 Model Overview

| Model | Flag | Requires District Data? | What it does |
|-------|------|------------------------|--------------|
| **Random Forest** | `--model rf` | ❌ No | Predicts crop suitability scores |
| **XGBoost Weather** | `--model xgboost_weather` | ✅ Yes (Step 7) | Forecasts temperature & rainfall |
| **LSTM Weather** | `--model lstm_weather` | ✅ Yes (Step 7) | Deep learning weather forecasting |
| **All three** | `--model all` | ✅ Yes (Step 7) | Trains RF → XGBoost → LSTM in sequence |

---

### 8a. Train the Random Forest (Crop Suitability)

> ✅ **No district weather data needed.** This is the easiest model to train and is recommended as a starting point.

```bash
python scripts/train_model.py --model rf
```

**What happens:**
1. Generates synthetic training data (~50 weather scenarios per crop/region combination)
2. Trains a Random Forest model to predict crop suitability scores (0–100)
3. Prints top feature importances (temperature, water, soil, etc.)
4. Saves the model to `models/crop_suitability/`

**Expected terminal output:**
```
============================================================
  Crop Recommendation System — Model Trainer
  Model target: RF
============================================================

============================================================
  RANDOM FOREST — Crop Suitability
============================================================
  Generating training data (50 scenarios/combo) — streaming to disk...
  ✓ Saved 45,000 records → data/ml/training/crop_suitability/...

  Top features:
    temp_compatibility        0.2341 ████████████████████████
    water_availability        0.1987 ████████████████████
    ...

  ✓ Model saved → models/crop_suitability/
  Train R²: 0.9512 | Test R²: 0.8934 | RMSE: 4.2301
```

**Output files created:**
```
models/crop_suitability/
├── rf_model.joblib           ← Trained model
├── label_encoders.joblib     ← Encoded region/soil labels
├── metadata.json             ← Training metadata
└── feature_importance.png    ← Feature importance chart
```

**Optional flags for RF:**

| Flag | Default | Description |
|------|---------|-------------|
| `--scenarios N` | `50` | Weather scenarios per crop/region combo. Use `100`+ for better accuracy |
| `--estimators N` | `200` | Number of trees. More = slower but better |
| `--max-depth N` | `15` | Max tree depth. Higher = more complex model |
| `--regenerate` | off | Force re-generate training data even if it already exists |

**Example — higher quality training:**
```bash
python scripts/train_model.py --model rf --scenarios 100 --estimators 300
```

---

### 8b. Train the XGBoost Weather Model

> ⚠️ **Requires district weather data** — complete Step 7 first.

```bash
python scripts/train_model.py --model xgboost_weather
```

**What happens:**
1. Reads Parquet files from `data/weather/district/` (all 640+ districts)
2. Engineers lag features and rolling statistics for temperature and rainfall
3. Trains **three separate XGBoost models**: `temp_max`, `temp_min`, `rainfall`
4. Saves models to `models/weather_xgboost/`

**Expected terminal output:**
```
============================================================
  XGBOOST — Weather Forecasting
============================================================
  Loading district data from data/weather/district ...
  Training temp_max model on 640 districts...
  Training temp_min model on 640 districts...
  Training rainfall model on 640 districts...
  [OK] XGBoost weather model saved -> models/weather_xgboost/
```

**Output files created:**
```
models/weather_xgboost/
├── temp_max_model.joblib    ← Max temperature model
├── temp_min_model.joblib    ← Min temperature model
├── rainfall_model.joblib    ← Rainfall model
└── metadata.json            ← District encoder + training info
```

**Optional flags for XGBoost:**

| Flag | Default | Description |
|------|---------|-------------|
| `--estimators N` | `200` | Number of boosting trees |
| `--sample N` | all | Only use N districts (useful for quick testing) |
| `--data-dir PATH` | `data/weather/district` | Custom path to district data |

**Quick test run (10 districts only):**
```bash
python scripts/train_model.py --model xgboost_weather --sample 10
```

> ⏳ **Estimated time:** 5–20 minutes (full 640 districts). Use `--sample 10` for a 1-minute test run.

---

### 8c. Train the LSTM Weather Model (PyTorch)

> ⚠️ **Requires district weather data** — complete Step 7 first.

```bash
python scripts/train_model.py --model lstm_weather
```

**What happens:**
1. Reads district weather Parquet files and builds 30-day lookback sequences
2. Trains a PyTorch LSTM network to forecast temperature and rainfall 7 days ahead
3. Encodes each district as an embedding for district-aware predictions
4. Saves weights to `models/weather_lstm/`

**Expected terminal output:**
```
============================================================
  LSTM — Weather Forecasting (PyTorch)
============================================================
  Loading district data...
  Building sequences for 640 districts...
  Epoch [1/20] Loss: 0.4821
  Epoch [2/20] Loss: 0.3915
  ...
  Epoch [20/20] Loss: 0.1034
  [OK] LSTM weather model saved -> models/weather_lstm/
```

**Output files created:**
```
models/weather_lstm/
├── lstm_weights.pt     ← PyTorch model weights
└── metadata.json       ← District encoder, RMSE, epoch count
```

**Optional flags for LSTM:**

| Flag | Default | Description |
|------|---------|-------------|
| `--epochs N` | `20` | Training epochs. More = better but slower |
| `--batch-size N` | `512` | Batch size. Lower if running out of RAM |
| `--device cpu/cuda` | `cpu` | Use `cuda` if you have an NVIDIA GPU |
| `--sample N` | all | Only use N districts (for quick testing) |
| `--data-dir PATH` | `data/weather/district` | Custom path to district data |

**Quick test run (10 districts, 5 epochs):**
```bash
python scripts/train_model.py --model lstm_weather --sample 10 --epochs 5
```

**GPU training (much faster if available):**
```bash
python scripts/train_model.py --model lstm_weather --device cuda --epochs 30
```

> ⏳ **Estimated time:** 15–60 minutes on CPU (full dataset). ~5–10 minutes with a GPU.

---

### 8d. Train All Models at Once

Trains Random Forest → XGBoost → LSTM in sequence:

```bash
python scripts/train_model.py --model all
```

**Production-quality full training:**
```bash
python scripts/train_model.py --model all --epochs 30 --estimators 300 --scenarios 100
```

> ⏳ **Estimated total time:** 1–3 hours on CPU with full district data.

---

### 8e. Verify Models Are Loaded

After training, start the server and check `/health`:

```bash
python run_website.py
```

Then open `http://localhost:8000/health` in your browser. You should see:
```json
{
  "status": "healthy",
  "version": "1.0",
  "regions_loaded": 640,
  "ml_models": {
    "crop_suitability_rf": "loaded"
  }
}
```

You can also run the model verification script:
```bash
python scripts/verify_models.py
```

Expected output:
```
LSTM: 640 districts, final_rmse=0.1034, epochs=20
XGB:  640 districts trained
...
PASSED - LSTM inference working for new districts
```

---

## 9. Using the Web Interface

Once the server is running, open `http://localhost:8000` in your browser.

### Step-by-step:

1. **Select your Region** — Choose your district from the dropdown (e.g., `MH_PUNE` for Pune, Maharashtra)  
   OR enter GPS coordinates (latitude/longitude)

2. **Set Soil Information** *(optional)* — Provide soil texture, pH, organic matter, and drainage.  
   Defaults are used if you skip this.

3. **Select Irrigation Level** — `None`, `Limited`, or `Full`

4. **Set Planning Days** — How many days ahead you want to plan (15–365 days)

5. **Click "Get Recommendations"** — The system will:
   - Fetch real-time weather from Open-Meteo
   - Detect the current season (Kharif / Rabi / Zaid)
   - Score 50+ crops using ML + rule-based engine
   - Return top 10 crops with scores, risks, pest warnings, and planting calendar

### Interface features:
- 🌐 **Hindi/English bilingual** — Switch languages using the toggle
- 📊 Green/Orange/Red **suitability score bars**
- 🌡️ **Month-wise climate chart** (Jan–Dec) with current month highlighted
- 🐛 **Pest warning badges** per crop
- 📅 **Planting calendar** — sowing → germination → flowering → harvest dates

---

## 10. Using the API

The REST API is accessible at `http://localhost:8000`. Full interactive documentation is at `/docs`.

### Quick Example — Get Crop Recommendations

**Request:**
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "region_id": "MH_PUNE",
    "irrigation": "Limited",
    "planning_days": 90
  }'
```

**Using GPS coordinates:**
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 18.5204,
    "longitude": 73.8567,
    "irrigation": "Full",
    "planning_days": 60
  }'
```

### Other Endpoints

| Method | Endpoint                             | Description                                  |
|--------|--------------------------------------|----------------------------------------------|
| `POST` | `/recommend`                         | Get top 10 crop recommendations              |
| `GET`  | `/forecast/{region_id}?days=7`       | ML weather forecast for a region             |
| `POST` | `/risk-assessment`                   | Drought/temperature/event risk for a crop    |
| `GET`  | `/pest-warnings/{region_id}`         | Pest & disease warnings for a region         |
| `GET`  | `/planting-calendar/{crop_id}`       | Sowing-to-harvest calendar for a crop        |
| `GET`  | `/regions`                           | List all 640+ supported regions              |
| `GET`  | `/health`                            | API health check + ML model status           |
| `GET`  | `/docs`                              | Swagger interactive API explorer             |

---

## 11. Troubleshooting

### ❌ `python` not found / `'python' is not recognized`
- Make sure Python is installed and added to PATH (see Step 2)
- On macOS/Linux, try using `python3` instead of `python`

### ❌ Virtual environment activation fails on Windows
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\activate
```

### ❌ `pip install -r requirements.txt` fails
- Make sure your virtual environment is **active** (`(.venv)` prefix in prompt)
- Try upgrading pip first:
  ```bash
  pip install --upgrade pip
  ```
- If `torch` fails to install, visit [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/) to get the exact install command for your OS/CUDA version.

### ❌ Port 8000 already in use
Run the server on a different port:
```bash
python -c "import uvicorn; uvicorn.run('src.api.app:app', host='0.0.0.0', port=8080)"
```
Then open `http://localhost:8080`.

### ❌ `ModuleNotFoundError: No module named 'src'`
Make sure you are running from inside the `agri_crop_recommendation/` folder:
```bash
cd agri_crop_recommendation
python run_website.py
```

### ❌ Weather data fetch is very slow
This is normal — the Open-Meteo API rate-limits requests. The script fetches ~640 districts and will take several hours. You can safely stop with `Ctrl+C` and resume later; progress is saved.

### ❌ ML models not loaded (shows "not_trained" in `/health`)
This is expected if you haven't run Step 8. The app falls back to rule-based scoring automatically. Run `python scripts/train_model.py` to enable ML predictions.

---

## 12. Project Folder Overview

```
Indian-Farmer-Crop-Recommendation-System/
│
└── agri_crop_recommendation/          ← Main application folder (work here)
    │
    ├── run_website.py                 ← ▶ START HERE — runs the web server
    ├── requirements.txt               ← All Python dependencies
    │
    ├── src/                           ← Core source code
    │   ├── api/app.py                 ← FastAPI routes & endpoints
    │   ├── crops/                     ← Crop database & soil models
    │   ├── ml/                        ← LSTM, XGBoost, Random Forest
    │   ├── services/                  ← Recommender, risk, pest, calendar
    │   ├── utils/                     ← Region manager, season detection
    │   └── weather/                   ← Open-Meteo fetcher & forecast engine
    │
    ├── data/
    │   ├── reference/                 ← regions.json, crop_knowledge.json
    │   └── weather/
    │       ├── zone/                  ← Zone-level monthly climate normals (CSV)
    │       └── district/              ← District-level daily weather (Parquet, after Step 7)
    │
    ├── models/                        ← Trained ML model files (after Step 8)
    │   ├── crop_suitability/          ← Random Forest (rf_model.joblib)
    │   ├── weather_lstm/              ← LSTM weights (lstm_weights.pt)
    │   └── weather_xgboost/           ← XGBoost models (temp/rainfall .joblib)
    │
    ├── templates/index.html           ← Web UI (bilingual Hindi/English)
    ├── static/css/style.css           ← Frontend styles
    ├── static/js/app.js               ← Frontend JavaScript
    │
    └── scripts/
        ├── fetch_district_weather.py  ← Step 7: Download district weather data
        ├── train_model.py             ← Step 8: Train all ML models
        ├── test_api.py                ← API smoke tests
        └── test_recommend.py         ← Recommendation integration tests
```

---

## ✅ Quick Start Checklist

```
[ ] Python 3.8+ installed
[ ] Repository cloned or downloaded
[ ] cd into agri_crop_recommendation/
[ ] Virtual environment created and activated
[ ] pip install -r requirements.txt completed
[ ] python run_website.py running
[ ] Browser opened at http://localhost:8000
```

---

## 📞 Need Help?

- 📂 **GitHub Issues:** [Open an issue](https://github.com/tirthch25/Indian-Farmer-Crop-Recommendation-System/issues)
- 📖 **API Docs (interactive):** `http://localhost:8000/docs` (once the server is running)
- 📄 **Full Feature Documentation:** See [`README.md`](./README.md)

---

<div align="center">
  <strong>🌾 Built with ❤️ for Indian Farmers</strong><br/>
  <em>Empowering agriculture through data and technology — C-DAC</em>
</div>
