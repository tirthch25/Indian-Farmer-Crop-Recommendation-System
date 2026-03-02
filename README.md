# 🌾 Indian Farmer Crop Recommendation System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-150458?style=for-the-badge&logo=pandas)
![scikit-learn](https://img.shields.io/badge/Scikit--Learn-ML-F7931E?style=for-the-badge&logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A nationwide, season-aware, AI-powered crop recommendation system for Indian farmers — covering 700+ districts across all major Indian states.**

[Features](#-features) • [How It Works](#-how-it-works) • [Installation](#-installation) • [API Docs](#-api-endpoints) • [Tech Stack](#-tech-stack) • [Project Structure](#-project-structure)

</div>

---

## 🧭 Overview

The **Indian Farmer Crop Recommendation System** (v3.0) is a full-stack intelligent advisory platform built to help farmers across India make data-driven decisions about which crops to grow. It combines **real-time weather data**, **zone-level historical climate records**, **ML-powered forecasting** (LSTM + XGBoost ensemble), **crop suitability prediction** (Random Forest), **risk assessment**, **pest warnings**, and a **planting calendar** — all accessible through a clean web UI and a RESTful API.

Farmers interact through a **bilingual Hindi/English web interface**, while developers can access all features via a **FastAPI REST API** with Swagger documentation.

---

## ✨ Features

### 🗺️ Nationwide Regional Coverage
- **700+ Indian Agricultural Districts** across all major states
- Region IDs follow `<STATE_CODE>_<DISTRICT>` format (e.g., `MH_PUNE`, `UP_LUCKNOW`, `PB_LUDHIANA`)
- Each region includes geographic coordinates, elevation, climate zone, soil type, and supported seasons
- **Haversine-based nearest region finder** (150 km radius) for GPS coordinate-based lookups

### 🌦️ Weather & Historical Climate Data
- Real-time weather fetched from **[Open-Meteo API](https://open-meteo.com/)** — no API key needed
- **Zone-level historical climate normals** (monthly averages for 6 zones: North, South, East, West, Central, Northeast)
- Medium-range **17–90 day agricultural forecast** including temperature, rainfall, dry-spell risk, and humidity
- Month-wise (Jan–Dec) climate chart on the web interface with current-month highlighting

### 🤖 Machine Learning Models
- **Weather Forecasting** — LSTM and XGBoost models trained on historical zone data; ensemble fallback to climatology
- **Crop Suitability** — Random Forest model blending rule-based scores with data-driven predictions
- **ML score blending** — when models are trained, their predictions are automatically weighted with the rule-based engine

### 🌱 Comprehensive Crop Database
- **50+ Short-Duration Crops** (15–90 days):
  - **Millets**: Bajra, Jowar, Ragi, Foxtail Millet
  - **Pulses**: Moong, Urad, Cowpea, Guar
  - **Oilseeds**: Sesame, Sunflower, Soybean
  - **Vegetables**: Tomato, Brinjal, Okra, Bottle Gourd, Cucumber, Ridge Gourd, Bitter Gourd, Carrot, Radish, Beetroot, Turnip, French Beans, Cluster Beans, Spring Onion
  - **Leafy Greens**: Spinach, Fenugreek (Methi), Coriander (Dhaniya), Amaranth, Mustard Greens, Lettuce
  - *…and many more*
- Per-crop metadata: temperature range, water requirements, drought tolerance, soil needs, zone/regional suitability, seasonal suitability, yield estimates, market demand, growing tips, and recommended varieties

### 🧪 Intelligent Scoring Engine
Multi-factor **suitability score (0–100)** calculated across 6 dimensions:

| Factor | Weight |
|--------|--------|
| Temperature Compatibility | 25% |
| Water Availability | 25% |
| Soil Compatibility | 15% |
| Regional Suitability | 15% |
| Seasonal Adjustment | 10% |
| Drought Tolerance | 10% |

### 🛡️ Risk Assessment Engine
- Evaluates **drought risk**, **temperature stress**, and **extreme weather events**
- Per-crop risk scoring using weather forecast + crop thresholds
- Integrated into `/recommend` response and available standalone via `/risk-assessment`

### 🐛 Pest & Disease Warning System
- Weather-triggered pest and disease warnings
- Region and crop-specific warnings based on current conditions
- Returns top 3 most likely threats per crop in the recommendation

### 📅 Planting Calendar
- Season-aware milestone dates: sowing → germination → flowering → harvest
- Per-phase care tips for each crop
- Available standalone via `/planting-calendar/{crop_id}`

### 🌿 Soil Compatibility Analysis
- Soil model with texture, pH, organic matter, and drainage
- Automated amendment suggestions: pH adjustments (lime/sulfur), texture improvements, drainage fixes
- Default soil profiles for all regions

### 📅 Season-Aware Logic
- **Automatic season detection**: Kharif (Jun–Sep), Rabi (Oct–Feb), Zaid (Mar–May)
- Season transition handling within a **30-day threshold**
- Seasonal water adjustments: Kharif −15% (monsoon benefit), Rabi −5%, Zaid +10%

### 🌐 Web Interface
- **Bilingual UI** (Hindi + English) — accessible and farmer-friendly
- Visual suitability score bars (🟢 High / 🟠 Medium / 🔴 Low)
- Month-wise weather forecast chart (Jan–Dec)
- Color-coded **risk level badges** and pest warnings per crop
- Mobile-responsive design — no login required

---

## 🖥️ How It Works

```
     Farmer Input
     (Region / GPS + Soil + Irrigation)
              │
              ▼
   ┌──────────────────────┐
   │  Open-Meteo API      │  → Real-time weather data
   │  Zone Climate Normals│  → Monthly historical averages
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────┐
   │  Feature Engineering │  → Agri-specific features
   │  ML Forecast Engine  │  → LSTM + XGBoost ensemble (17–90 days)
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────┐
   │  CropSuitabilityRF   │  → Random Forest suitability scoring
   │  Rule-Based Engine   │  → 6-factor score (fallback / blend)
   │  Risk Engine         │  → Drought / temperature / event risk
   │  Pest Warning System │  → Weather-triggered crop threats
   │  Planting Calendar   │  → Season-phased milestone dates
   └──────────┬───────────┘
              │
              ▼
     Top 10 Crops Ranked
     (Score, Risk, Warnings, Calendar, Water, Duration)
```

---

## 🚀 Installation

### Prerequisites
- Python **3.8+**
- pip

### 1. Clone the Repository
```bash
git clone https://github.com/tirthch25/Indian-Farmer-Crop-Recommendation-System.git
cd Indian-Farmer-Crop-Recommendation-System/agri_crop_recommendation
```

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Train the Crop Suitability ML Model
```bash
python scripts/train_model.py
```
> Generates training data and trains the Random Forest crop suitability model. This is optional — the system gracefully falls back to pure rule-based scoring if the model is not present.

### 5. Start the Web Server
```bash
python run_website.py
```

### 6. Open in Your Browser
```
http://localhost:8000          ← Web Interface
http://localhost:8000/docs     ← Swagger API Docs
```

---

## 📡 API Endpoints

### `POST /recommend`
Generate ML-enhanced crop recommendations for a region.

**Request (by Region ID):**
```json
{
  "region_id": "MH_PUNE",
  "irrigation": "Limited",
  "planning_days": 90
}
```

**Request (by GPS Coordinates + Custom Soil):**
```json
{
  "latitude": 18.5204,
  "longitude": 73.8567,
  "season": "Kharif",
  "soil": {
    "texture": "Loam",
    "ph": 6.8,
    "organic_matter": "Medium",
    "drainage": "Good"
  },
  "irrigation": "Full"
}
```

**Response includes:**
- `region` — resolved region metadata
- `season` — detected / provided season + transition guidance
- `soil` — resolved soil profile
- `medium_range_forecast` — 17–90 day outlook + monthly chart data (Jan–Dec)
- `recommended_crops` — top 10 crops with score, risk, pest warnings, planting calendar, growing tips
- `planting_calendars` — milestone dates for each recommended crop

---

### `GET /forecast/{region_id}?days=N`
Get ML-powered weather forecast for a region.
- Uses LSTM + XGBoost ensemble when models are available
- Falls back to climatology-based estimation

### `POST /risk-assessment`
Get comprehensive risk assessment (drought, temperature stress, extreme events) for a specific crop in a region.

```json
{
  "region_id": "MH_PUNE",
  "crop_id": "BAJRA_01",
  "season": "Kharif",
  "irrigation": "Limited"
}
```

### `GET /pest-warnings/{region_id}?crop_id=CROP_ID`
Get weather-triggered pest and disease warnings for a region. Optionally filter by crop.

### `GET /planting-calendar/{crop_id}?season=Kharif&region_id=MH_PUNE`
Get sowing-to-harvest planting calendar with care tips for a specific crop.

### `GET /regions`
Returns all 700+ supported agricultural regions with metadata.

### `GET /health`
Health check — confirms API is running and reports ML model status.

### `GET /docs`
Interactive Swagger UI for exploring and testing all endpoints.

---

## 📁 Project Structure

```
agri_crop_recommendation/
│
├── src/                              # Core application source code
│   ├── api/
│   │   └── app.py                   # FastAPI app — all REST endpoints
│   │
│   ├── crops/
│   │   ├── database.py              # 50+ crops with all attributes
│   │   ├── models.py                # CropInfo data model
│   │   └── soil.py                  # SoilInfo model + compatibility scoring
│   │
│   ├── ml/
│   │   ├── pipeline.py              # Training data generation & feature engineering
│   │   └── predictor.py             # Random Forest crop suitability model
│   │
│   ├── services/                    # Domain business logic
│   │   ├── recommender.py           # Multi-factor crop recommendation engine
│   │   ├── calendar.py              # Season-phased planting calendar
│   │   ├── pests.py                 # Weather-triggered pest & disease warnings
│   │   └── risk.py                  # Drought / temperature / event risk scoring
│   │
│   ├── utils/
│   │   ├── regions.py               # RegionManager — 700+ districts
│   │   └── seasons.py               # Season detection & transition logic
│   │
│   └── weather/
│       ├── fetcher.py               # Open-Meteo real-time API integration
│       ├── forecast.py              # Medium-range forecast (17–90 days)
│       └── history.py               # Zone-level historical climate normals
│
├── data/
│   ├── reference/
│   │   ├── regions.json             # 700+ region profiles (all Indian states)
│   │   └── crop_knowledge.json      # Growth phases, pest DB, planting windows
│   └── weather/
│       └── zone/
│           └── historical_weather.csv  # Zone-level monthly climate normals
│
├── models/
│   └── crop_suitability/            # Trained Random Forest artifacts
│       ├── rf_model.joblib
│       ├── label_encoders.joblib
│       └── metadata.json
│
├── templates/
│   └── index.html                   # Bilingual web UI (Hindi + English)
│
├── static/
│   ├── css/style.css                # Agricultural theme, responsive
│   └── js/app.js                    # Frontend JavaScript logic
│
├── scripts/
│   ├── train_model.py               # Generate training data & train RF model
│   ├── setup_weather.py             # Fetch & persist zone weather history
│   ├── test_api.py                  # API endpoint smoke tests
│   └── test_recommend.py            # Recommendation integration tests
│
├── main.py                          # Quick CLI demo
├── run_website.py                   # Web server startup script
└── requirements.txt
```

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend API** | Python 3.8+, FastAPI, Uvicorn |
| **Frontend** | HTML5, CSS3, JavaScript (Jinja2 templates) |
| **Data Storage** | JSON (regions/crop knowledge), CSV (zone climate) |
| **Data Processing** | Pandas, NumPy |
| **Machine Learning** | scikit-learn (Random Forest) |
| **Weather API** | Open-Meteo (free, no API key required) |
| **ML Serialization** | joblib |

---

## ⚙️ System Requirements

| Component | Minimum |
|-----------|---------|
| Python | 3.8+ |
| RAM | 2 GB (4 GB recommended if training LSTM) |
| Storage | 100 MB (no large Parquet files needed) |
| Browser | Chrome, Firefox, Safari, Edge (latest) |

---

## 🛣️ Roadmap

- [x] Historical weather data infrastructure
- [x] Soil compatibility analysis + amendment suggestions
- [x] Season-aware recommendation logic with transition handling
- [x] FastAPI REST endpoints with Swagger docs
- [x] End-to-end API integration tests
- [x] Crop suitability prediction model (Random Forest — ML blended scoring)
- [x] Risk assessment engine (drought, temperature stress, extreme events)
- [x] Pest/disease warning system (50+ crops covered)
- [ ] Planting calendar with crop images

---

## 🙏 Acknowledgements

- **[Open-Meteo](https://open-meteo.com/)** — Free, open-source weather API
- **C-DAC (Centre for Development of Advanced Computing)** — Project incubation
- Indian farmers — The end users who inspired this project

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.



---

<div align="center">
  <strong>Built with ❤️ for Indian Farmers</strong><br/>
  <em>Empowering agriculture through data and technology</em>
</div>
