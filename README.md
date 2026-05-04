# 🌾 Indian Farmer Crop Recommendation System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi)
![PyTorch](https://img.shields.io/badge/PyTorch-LSTM-EE4C2C?style=for-the-badge&logo=pytorch)
![XGBoost](https://img.shields.io/badge/XGBoost-Weather-007ACC?style=for-the-badge)
![scikit-learn](https://img.shields.io/badge/Scikit--Learn-ML-F7931E?style=for-the-badge&logo=scikit-learn)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-4285F4?style=for-the-badge&logo=google)
![Version](https://img.shields.io/badge/Version-2.2-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A nationwide, season-aware, AI-powered crop recommendation system for Indian farmers — covering all 640 districts across all major Indian states.**

[Features](#-features) • [How It Works](#-how-it-works) • [Installation](#-installation) • [API Docs](#-api-endpoints) • [Tech Stack](#-tech-stack) • [Project Structure](#-project-structure)

</div>

---

## 🧭 Overview

The **Indian Farmer Crop Recommendation System** (v2.2) is a full-stack intelligent agricultural advisory platform that helps Indian farmers make data-driven decisions about crop selection and planning. It combines:

- **Real-time + historical weather data** — Open-Meteo API, 640+ districts, 10+ years
- **ML-powered weather forecasting** — LSTM + XGBoost ensemble (district-aware)
- **Crop suitability prediction** — Random Forest, 6-factor ML-blended scoring
- **Gemini-powered regional enrichment** — pre-computed, district-level crop approval database (640 districts)
- **Gemini LLM integration** — farmer-friendly AI explanations + farming chat
- **Risk assessment, pest warnings, planting calendar** — complete crop advisory pipeline
- **Premium web UI** — bilingual (Hindi/English), Chart.js visualizations, responsive design

Farmers interact through a **farmer-friendly web interface**, while developers can access all features via a **FastAPI REST API** with Swagger documentation at `/docs`.

---

## ✨ Features

### 🗺️ Nationwide Regional Coverage
- **All 640 Indian Agricultural Districts** across 34 states and union territories
- Region IDs follow `<STATE_CODE>_<DISTRICT>` format (e.g., `MH_PUNE`, `UP_LUCKNOW`, `PB_LUDHIANA`)
- Each region includes geographic coordinates, elevation, climate zone, soil type, and supported seasons
- **Full agro-climatic zone coverage**: every region receives a zone-based suitability score (0.75) — eliminating the prior 552-region gap
- **Haversine-based nearest region finder** (150 km radius) for GPS coordinate-based lookups

### 🗄️ Pre-Computed Regional Crop Enrichment (NEW in v2.1)
The most significant upgrade in v2.1 is a **one-time Gemini-powered enrichment pipeline** that maps all 640 districts to their approved crops and per-crop suitability scores:

- **`enrich_regional_crops.py`** queries `gemini-2.5-flash` for every district and caches results in `data/reference/regional_crops.json`
- Scores range from **0.50** (possible with irrigation) to **1.00** (district is famous for the crop)
- Results are loaded at server startup from `regional_crops.json` — **zero runtime LLM calls needed for filtering**
- The recommendation engine uses a priority chain:
  1. ✅ **Enrichment JSON** (fast, deterministic, district-specific)
  2. 🔄 **Runtime LLM filter** (for districts not yet enriched)
  3. 📋 **Static zone-based scores** (guaranteed fallback)
- Supports `--only-missing` flag to resume enrichment across quota resets
- Saves progress incrementally every 10 districts — safe to interrupt

```bash
# Run once to enrich all 640 districts (resumes where left off)
python scripts/enrich_regional_crops.py --only-missing

# Enrich a single state only
python scripts/enrich_regional_crops.py --state MH
```

### 🌦️ Weather & Historical Climate Data
- Real-time weather from **[Open-Meteo API](https://open-meteo.com/)** — no API key needed
- **Per-district accurate temperatures**: Open-Meteo is called with each district's exact lat/lon — so Leh (3524 m) shows ~8°C in May, not the plains average of 40°C
- **District-level historical weather data** for 640+ districts across 34 states
- **Zone-level historical climate normals** used *only* for **humidity** (which Open-Meteo free tier omits) — temperature is never zone-blended
- Medium-range **17–90 day agricultural forecast** including temperature, rainfall, dry-spell risk, and humidity
- Month-wise (Jan–Dec) climate chart — anchored to live API temperature, not zone averages

### 🤖 Machine Learning Models

| Model | Type | Purpose | Performance |
|-------|------|---------|-------------|
| **LSTM Weather Forecaster** | PyTorch (2-layer LSTM) | 7-day weather forecast | Trained on 455 districts, RMSE 0.4502 |
| **XGBoost Weather Forecaster** | Gradient Boosted Trees | temp_max, temp_min, rainfall | 455 districts, 74 lag/rolling features |
| **Random Forest Crop Suitability** | Scikit-learn RF | Suitability score 0–100 | ML-blended 60:40 |

### 🧠 Gemini LLM Integration
Powered by **Google Gemini (`gemini-2.5-flash`)** via the **`google-genai`** SDK (new, actively maintained):

> ⚠️ **SDK Note**: This project uses the **`google-genai`** package (`from google import genai`). The older `google-generativeai` package is deprecated and no longer receives updates.

#### 🏗️ District Enrichment Pipeline (`enrich_regional_crops.py`)
- Queries Gemini once per district to approve crops and assign suitability scores (0.50–1.00)
- Results cached in `regional_crops.json` — no repeated API calls at serve time
- Gracefully handles daily quota limits with exponential back-off and `--only-missing` resume

#### 🔍 Runtime Regional Crop Filter (`llm_filter.py`)
- Used for districts **not yet in** `regional_crops.json`
- Sends ML-ranked crop shortlist to Gemini with district name, state, zone, and season context
- Graceful fallback to unfiltered ML list if Gemini is unavailable

#### 💬 Farmer-Friendly Explainer (`llm_explainer.py`)
- 2-sentence AI explanations for the **top 3 recommended crops** in English, Hindi, or Marathi
- Each explanation: `english` reason, `why_good` (key benefit), `watch_out` (key risk), optional regional language
- `/recommend` response includes `"llm_powered": true` when explanations are active

#### 🗣️ AI Farming Chat (`/chat`)
- Free-form farmer question answering grounded in district + season context
- Powered by Gemini; graceful fallback message if API key not set

> **Note**: Set `GEMINI_API_KEY` in `.env` to enable LLM features. **The system works fully without it** — all LLM steps fall back gracefully.

### 🌱 Comprehensive Crop Database (50+ Crops)
- **Millets**: Bajra, Jowar, Ragi, Foxtail Millet
- **Pulses**: Moong, Urad, Cowpea, Guar
- **Oilseeds**: Sesame, Sunflower, Soybean
- **Vegetables**: Tomato, Brinjal, Okra, Bottle Gourd, Cucumber, Ridge Gourd, Bitter Gourd, Carrot, Radish, Beetroot, Turnip, French Beans, Cluster Beans, Spring Onion
- **Leafy Greens**: Spinach, Fenugreek, Coriander, Amaranth, Mustard Greens, Lettuce
- *…and many more (15–90 day crops)*
- Per-crop metadata: temperature range, water requirements, drought tolerance, soil needs, zone suitability, yield estimates, market demand, growing tips, recommended varieties

### 🧪 Intelligent Scoring Engine
Multi-factor **suitability score (0–100)** across 6 dimensions:

| Factor | Weight |
|--------|--------|
| Temperature Compatibility | 25% |
| Water Availability | 25% |
| Soil Compatibility | 15% |
| Regional Suitability | 15% |
| Seasonal Adjustment | 10% |
| Drought Tolerance | 10% |

### 🛡️ Risk Assessment Engine
- Evaluates **drought risk**, **temperature stress**, and **extreme weather events** per crop
- Integrated into `/recommend` response and available standalone via `/risk-assessment`

### 🐛 Pest & Disease Warning System
- Weather-triggered pest and disease warnings (50+ crops covered)
- Region and crop-specific warnings based on current conditions

### 📅 Planting Calendar
- Season-aware milestone dates: sowing → germination → flowering → harvest
- Per-phase care tips; visual timeline in the UI

### 🌿 Soil Compatibility Analysis
- Soil model: texture, pH, organic matter, drainage
- Automated amendment suggestions and default soil profiles for all regions

---

### 🌡️ Per-District Temperature Accuracy (v2.2)

A key fix in v2.2 eliminates wrong temperature values that previously affected **high-altitude, island, and several incorrectly-mapped state districts**:

| What changed | Detail |
|---|---|
| **Temperature source** | Now **100% Open-Meteo live API** per district lat/lon — zone averaging completely removed |
| **Zone data scope** | Zone data now used **only for humidity** (Open-Meteo free tier doesn't include it) |
| **Monthly chart** | Anchored to live API temperature + zone seasonal shape offset — not raw zone averages |
| **Ladakh `LA`** | New `Highland` zone with IMD station data (Leh: −7°C Jan → +19°C Jul) |
| **Mizoram `MZ`** | Was missing → defaulted to North/39°C; now correctly `Northeast` |
| **Meghalaya `ML`** | Was missing → defaulted to North/39°C; now correctly `Northeast` |
| **Telangana `TL`** | `regions.json` uses `TL` not `TS`; now explicitly mapped to `South` |
| **Goa `GA`** | Was missing → defaulted to North; now `West` (coastal) |
| **Puducherry `PY`** | Was missing → defaulted to North; now `South` |
| **Andaman `AN`** | Was missing → defaulted to North; now `South` (tropical island) |
| **Chandigarh `CH`** | Was implicitly defaulting; now explicitly `North` |

Example temperature improvements (May readings):

| District | Before fix | After fix |
|---|---|---|
| Leh, Ladakh | ~~39.8°C~~ | ~8°C ✅ |
| Ri Bhoi / Shillong, Meghalaya | ~~39.8°C~~ | ~22°C ✅ |
| Aizawl, Mizoram | ~~39.8°C~~ | ~21°C ✅ |
| Tawang, Arunachal Pradesh | 24.8°C zone avg | ~9°C ✅ |
| Gangtok, Sikkim | 24.8°C zone avg | ~17°C ✅ |
| Shimla, Himachal Pradesh | 39.8°C zone avg | ~14°C ✅ |

---

## 🖥️ How It Works

```
     Farmer Input
     (Region / GPS + Soil + Irrigation)
               │
               ▼
   ┌──────────────────────────────────┐
   │  Open-Meteo API                  │  -> Real-time + historical weather
   │  District Historical Data        │  -> 640+ districts, 34 states
   └──────────┬───────────────────────┘
               │
               ▼
   ┌──────────────────────────────────┐
   │  Feature Engineering             │  -> Agri-specific features
   │  LSTM Weather Model              │  -> PyTorch, 30-day lookback
   │  XGBoost Weather Models          │  -> Lag + rolling features
   │  Ensemble Forecast               │  -> Blended 7-day ahead forecast
   └──────────┬───────────────────────┘
               │
               ▼
   ┌──────────────────────────────────┐
   │  Regional Enrichment Gate        │  -> Pre-computed JSON (fast, deterministic)
   │    regional_crops.json           │     district -> approved crops + scores
   │  [Fallback] LLM Runtime Filter   │  -> Runtime Gemini call (unenriched districts)
   │  [Fallback] Zone-based scores    │  -> Static 0.75 score guarantee
   └──────────┬───────────────────────┘
               │
               ▼
   ┌──────────────────────────────────┐
   │  CropSuitabilityRF               │  -> Random Forest suitability scoring
   │  Rule-Based Engine               │  -> 6-factor score (fallback / blend)
   │  Risk Engine                     │  -> Drought / temperature / event risk
   │  Pest Warning System             │  -> Weather-triggered crop threats
   │  Planting Calendar               │  -> Season-phased milestone dates
   └──────────┬───────────────────────┘
               │
               ▼
   ┌──────────────────────────────────┐
   │  Gemini LLM Explainer            │  -> 2-sentence farmer-friendly reason
   │  (gemini-2.5-flash)              │  -> Hindi / Marathi / English output
   └──────────┬───────────────────────┘
               │
               ▼
     Top 10 Crops Ranked
     (Score • Risk • Pest Alerts • Calendar • AI Explanation)
```

---

## 🚀 Installation

### Prerequisites
- Python **3.8+**
- pip
- A free **[Google Gemini API key](https://aistudio.google.com/app/apikey)** *(optional — enables LLM features)*

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

### 4. Configure Environment Variables
Create a `.env` file inside `agri_crop_recommendation/`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
> **Without a key**: runs fully in ML-only mode. All LLM steps are silently skipped.

### 5. (Optional but Recommended) Run Regional Crop Enrichment
```bash
python scripts/enrich_regional_crops.py --only-missing
```
> Queries `gemini-2.5-flash` once per district and caches results in `data/reference/regional_crops.json`.
> The free Gemini tier supports ~1,500 requests/day. Re-run with `--only-missing` on subsequent days to continue.
> **Without this step**: the system uses runtime LLM filtering or static zone scores — fully functional but slightly less accurate per-district.

### 6. (Optional) Fetch District-Level Weather Data
```bash
python scripts/fetch_district_weather.py
```
> Downloads 10 years of daily weather data for 640+ districts. Required for full LSTM/XGBoost weather model accuracy. Takes several hours due to API rate limits.

### 7. (Optional) Train the Weather & Crop Suitability Models
```bash
python scripts/train_model.py --model all --epochs 20
```
> Trains LSTM, XGBoost weather forecasters, and Random Forest crop suitability model.

### 8. Start the Web Server
```bash
python run_website.py
```

### 9. Open in Your Browser
```
http://localhost:8000          <- Web Interface
http://localhost:8000/docs     <- Swagger API Docs
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
- `medium_range_forecast` — 17–90 day outlook + monthly chart data
- `recommended_crops` — top 10 crops with suitability score, risk, pest warnings, planting calendar, and AI explanation (top 3)
- `planting_calendars` — milestone dates for each recommended crop
- `llm_powered` — `true` when Gemini explanations are active

### `GET /forecast/{region_id}?days=N`
ML-powered weather forecast. Uses LSTM + XGBoost ensemble when district models are available.

### `POST /risk-assessment`
Comprehensive risk assessment (drought, temperature stress, extreme events) for a specific crop.

### `GET /pest-warnings/{region_id}?crop_id=CROP_ID`
Weather-triggered pest and disease warnings for a region.

### `GET /planting-calendar/{crop_id}?season=Kharif&region_id=MH_PUNE`
Sowing-to-harvest planting calendar with care tips.

### `POST /chat`
AI farming chat — answer any farmer question grounded in district + season context (Gemini LLM).

### `GET /regions`
Returns all 640+ supported agricultural regions with metadata.

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
│   │   └── app.py                   # FastAPI app — all REST endpoints (v3.0)
│   │
│   ├── crops/
│   │   ├── database.py              # 50+ crops + regional_crops.json loader
│   │   ├── models.py                # CropInfo data model
│   │   └── soil.py                  # SoilInfo model + compatibility scoring
│   │
│   ├── ml/
│   │   ├── pipeline.py              # Training data generation & feature engineering
│   │   ├── predictor.py             # Random Forest crop suitability model
│   │   ├── lstm_weather.py          # PyTorch LSTM weather forecasting model
│   │   └── xgboost_weather.py       # XGBoost weather forecasting model
│   │
│   ├── services/                    # Domain business logic
│   │   ├── recommender.py           # Multi-factor crop recommendation engine
│   │   ├── calendar.py              # Season-phased planting calendar
│   │   ├── pests.py                 # Weather-triggered pest & disease warnings
│   │   ├── risk.py                  # Drought / temperature / event risk scoring
│   │   ├── llm_filter.py            # Gemini LLM runtime regional crop filter (fallback)
│   │   ├── llm_explainer.py         # Gemini LLM farmer-friendly explanation generator
│   │   └── llm_chat.py              # Gemini LLM farming Q&A chat
│   │
│   ├── utils/
│   │   ├── regions.py               # RegionManager — 640+ districts
│   │   └── seasons.py               # Season detection & transition logic
│   │
│   └── weather/
│       ├── fetcher.py               # Open-Meteo real-time API integration
│       ├── forecast.py              # Medium-range forecast (17–90 days)
│       └── history.py               # Zone-level historical climate normals
│
├── data/
│   ├── reference/
│   │   ├── regions.json             # 640+ region profiles (all Indian states)
│   │   ├── regional_crops.json      # Gemini-enriched district crop approvals (generated)
│   │   └── crop_knowledge.json      # Growth phases, pest DB, planting windows
│   └── weather/
│       ├── zone/
│       │   └── historical_weather.csv  # Zone-level monthly climate normals
│       └── district/                   # District-level daily weather (640+ districts)
│           ├── AP_GUNTUR/
│           ├── MH_PUNE/
│           └── ...                     # One folder per district
│
├── models/
│   ├── crop_suitability/            # Trained Random Forest artifacts
│   │   ├── rf_model.joblib
│   │   ├── label_encoders.joblib
│   │   └── metadata.json
│   ├── weather_lstm/                # Trained LSTM weather model (PyTorch)
│   │   ├── lstm_weights.pt
│   │   └── metadata.json
│   └── weather_xgboost/             # Trained XGBoost weather models
│       ├── temp_max_model.joblib
│       ├── temp_min_model.joblib
│       ├── rainfall_model.joblib
│       └── metadata.json
│
├── templates/
│   └── index.html                   # Bilingual web UI (Hindi + English) v2.0
│
├── static/
│   ├── css/style.css                # Agricultural theme, responsive (v2.0)
│   └── js/app.js                    # Frontend JavaScript (v2.0)
│
├── scripts/
│   ├── enrich_regional_crops.py     # Gemini-powered district crop enrichment (NEW)
│   ├── fetch_district_weather.py    # Fetch district-level weather from Open-Meteo
│   ├── train_model.py               # Train RF, LSTM & XGBoost weather models
│   ├── setup_weather.py             # Fetch & persist zone weather history
│   ├── test_api.py                  # API endpoint smoke tests
│   ├── test_recommend.py            # Recommendation integration tests
│   └── test_planning_days.py        # Planning days filter validation tests
│
├── .env                             # GEMINI_API_KEY (create manually — not committed)
├── .env.example                     # Environment variable template
├── main.py                          # Quick CLI demo
├── run_website.py                   # Web server startup script
└── requirements.txt
```

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend API** | Python 3.8+, FastAPI v2.0, Uvicorn |
| **Frontend** | HTML5, CSS3, JavaScript (Jinja2 templates) |
| **Data Storage** | JSON (regions/crop knowledge/enrichment), CSV (zone climate), Parquet (district weather) |
| **Data Processing** | Pandas, NumPy |
| **Machine Learning** | scikit-learn (Random Forest), PyTorch (LSTM), XGBoost (weather) |
| **LLM (AI Layer)** | Google Gemini API (`gemini-2.5-flash`) via **`google-genai`** SDK |
| **Weather API** | Open-Meteo (free, no API key required) |
| **ML Serialization** | joblib (XGBoost / RF), torch.save (LSTM) |
| **Config** | python-dotenv (`.env` for API keys) |

> **SDK notice**: This project uses the **`google-genai`** package (`pip install google-genai`), which is the current, actively maintained Google AI Python SDK. The older `google-generativeai` package is deprecated.

---

## ⚙️ System Requirements

| Component | Minimum |
|-----------|---------|
| Python | 3.8+ |
| RAM | 4 GB (8 GB recommended for training LSTM + XGBoost) |
| Storage | ~600 MB (with district weather data & trained models) |
| Browser | Chrome, Firefox, Safari, Edge (latest) |
| Gemini API Key | Optional — free tier at [aistudio.google.com](https://aistudio.google.com/app/apikey) |

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Optional | Google Gemini API key for regional crop enrichment, LLM filtering, AI explanations, and farming chat. Get one free at [aistudio.google.com](https://aistudio.google.com/app/apikey). |

Create `.env` inside `agri_crop_recommendation/`:
```env
GEMINI_API_KEY=your_key_here
```

---

## 📊 Regional Enrichment Progress

The `enrich_regional_crops.py` script processes all 640 districts using the Gemini API. Due to free-tier API quotas, this is run incrementally across multiple days using `--only-missing`.

| Metric | Value |
|--------|-------|
| Total districts | 640 |
| Enrichment output | `data/reference/regional_crops.json` |
| Model used | `gemini-2.5-flash` |
| Score range | 0.50 (possible) → 1.00 (district famous for crop) |
| Resume support | `--only-missing` flag |
| Quota handling | Auto-detects daily limit; saves & stops gracefully |

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
- [x] District-level weather data fetching (640+ districts, 34 states)
- [x] LSTM weather forecasting model (PyTorch, district-aware)
- [x] XGBoost weather forecasting models (temp_max, temp_min, rainfall)
- [x] Full agro-climatic zone suitability for all 640 regions (0.75 score)
- [x] Gemini LLM runtime regional crop filter (removes geographically wrong crops per district)
- [x] Gemini LLM farmer-friendly explainer (Hindi / Marathi / English, top 3 crops)
- [x] Planting calendar with visual phase timeline and crop emoji icons
- [x] **v2.0 UI overhaul** — premium light theme, AI badge, LLM explanation rendering
- [x] **AI Farming Chat** — `POST /chat` powered by Gemini for free-form farmer Q&A
- [x] **v2.1 — Gemini Regional Crop Enrichment** — pre-computed district crop database (`regional_crops.json`) via `google-genai` SDK + `gemini-2.5-flash`
- [ ] Complete enrichment for all 640 districts (in progress — incremental daily runs)
- [ ] Market price integration (Agmarknet / data.gov.in API)

---

## 🙏 Acknowledgements

- **[Open-Meteo](https://open-meteo.com/)** — Free, open-source weather API (weather data + soil moisture)
- **[Google Gemini](https://ai.google.dev/)** — LLM API powering regional crop enrichment, AI explanations and farming chat
- **C-DAC (Centre for Development of Advanced Computing)** — Project incubation
- Indian farmers — The end users who inspired this project

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <strong>Built with ❤️ for Indian Farmers</strong><br/>
  <em>Empowering agriculture through data and technology — C-DAC Pune</em>
</div>
