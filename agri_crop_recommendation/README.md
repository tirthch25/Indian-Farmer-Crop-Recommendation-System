# 🌾 Indian Farmer Crop Recommendation System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-150458?style=for-the-badge&logo=pandas)
![scikit-learn](https://img.shields.io/badge/Scikit--Learn-ML-F7931E?style=for-the-badge&logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A region-specific, season-aware, AI-powered crop recommendation system for Indian farmers — covering 10 major agricultural districts of Maharashtra.**

[Features](#-features) • [Demo](#-how-it-works) • [Installation](#-installation) • [API Docs](#-api-endpoints) • [Tech Stack](#-tech-stack) • [Project Structure](#-project-structure)

</div>

---

## 🧭 Overview

The **Indian Farmer Crop Recommendation System** is a full-stack intelligent advisory platform built to help farmers in Maharashtra make data-driven decisions about which crops to grow. It combines **real-time weather data**, **10 years of historical climate records**, **soil compatibility analysis**, and **season-aware logic** to recommend the most suitable short-duration crops (70–90 days) for each region.

Farmers interact through a **bilingual Hindi/English web interface**, while developers can access all features via a **RESTful API** with Swagger documentation.

---

## ✨ Features

### 🗺️ Regional Coverage
- **10 Indian Agricultural Districts**: Pune, Solapur, Nashik, Ahmednagar, Aurangabad, Jalgaon, Sangli, Kolhapur, Satara, Latur
- Each region includes geographic coordinates, elevation, climate zone, soil type, and supported seasons
- **Haversine-based nearest region finder** (50 km radius) for coordinate-based lookups

### 🌦️ Weather & Historical Data
- Real-time weather fetched from **[Open-Meteo API](https://open-meteo.com/)**
- **10 years of historical data** (2014–2024): 40,180 records across all regions stored in **Parquet format**
- Medium-range **17–90 day agricultural forecast** including temperature, rainfall, and dry-spell risk
- Climatological statistics for seasonal planning

### 🌱 Comprehensive Crop Database
- **15 Short-Duration Crops** (70–90 days):
  - **Millets**: Bajra, Jowar, Ragi, Foxtail Millet
  - **Pulses**: Moong, Urad, Cowpea, Guar
  - **Oilseeds**: Sesame, Sunflower, Soybean
  - **Vegetables**: Tomato, Brinjal, Okra, Bottle Gourd
- Per-crop metadata: temperature range, water requirements, drought tolerance, soil needs, regional suitability scores, seasonal suitability, yield, and market demand

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

### 🌿 Soil Compatibility Analysis
- Soil model with texture, pH, organic matter, and drainage
- Automated amendment suggestions: pH adjustments (lime/sulfur), texture improvements, drainage fixes
- Default soil profiles for all 10 regions

### 📅 Season-Aware Logic
- **Automatic season detection**: Kharif (June–Sep), Rabi (Oct–Feb), Zaid (Mar–May)
- Season transition handling within a **30-day threshold**
- Seasonal water adjustments: Kharif −15% (monsoon benefit), Rabi −5%, Zaid +10%

### 🌐 Web Interface
- **Bilingual UI** (Hindi + English) — accessible and farmer-friendly
- Visual suitability score bars (🟢 High / 🟠 Medium / 🔴 Low)
- Color-coded **risk level badges**
- Mobile-responsive design
- No login required

---

## 🖥️ How It Works

```
     Farmer Input
     (Region / GPS + Soil + Irrigation)
              │
              ▼
   ┌──────────────────────┐
   │  Open-Meteo Weather  │  → Real-time weather data
   │  Historical Store    │  → 10-yr climatology (Parquet)
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────┐
   │  Feature Engineering │  → Agri-specific features
   │  Medium-Range Fcst   │  → 17–90 day outlook
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────┐
   │  RecommendationEngine│  → 6-factor scoring
   │  Soil & Season Logic │  → Compatibility + adjustments
   └──────────┬───────────┘
              │
              ▼
     Top 10 Crops Ranked
     (Score, Risk, Water, Duration)
```

---

## 🚀 Installation

### Prerequisites
- Python **3.8+**
- pip

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/agri_crop_recommendation.git
cd agri_crop_recommendation
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

### 4. Generate Historical Data (First-Time Setup)
```bash
python scripts/generate_historical_data.py
```

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
Get crop recommendations by region ID **or** GPS coordinates.

**Request (by Region ID):**
```json
{
  "region_id": "PUNE",
  "irrigation": "Limited",
  "planning_days": 90
}
```

**Request (by Coordinates + Custom Soil):**
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

**Response (excerpt):**
```json
{
  "region": "Pune",
  "season": "Rabi",
  "recommendations": [
    {
      "crop": "Jowar (Sorghum)",
      "suitability_score": 83.7,
      "growth_duration_days": 90,
      "water_required_mm": 450,
      "risk_note": "Low Risk: Suitable conditions",
      "drought_tolerance": "High",
      "regional_suitability": 0.90
    }
  ]
}
```

### `GET /regions`
Returns a list of all 10 supported agricultural regions with metadata.

### `GET /health`
Health check endpoint — confirms the API is running.

### `GET /docs`
Interactive Swagger UI for exploring and testing all endpoints.

---

## 📁 Project Structure

```
agri_crop_recommendation/
│
├── src/                          # Core application source code
│   ├── api/
│   │   └── app.py                # FastAPI app with all endpoints
│   ├── crops/
│   │   ├── models.py             # CropInfo data model
│   │   └── crop_db.py            # 15 crops with detailed attributes
│   ├── data/
│   │   ├── historical_store.py   # Parquet-based historical data store
│   │   └── regions.py            # RegionManager (10 regions + soil defaults)
│   ├── soil/
│   │   └── models.py             # SoilInfo model + compatibility scoring
│   ├── utils/
│   │   └── seasons.py            # Season detection & transition logic
│   ├── weather/
│   │   └── open_meteo.py         # Open-Meteo weather API integration
│   ├── preprocessing/
│   │   └── features.py           # Agricultural feature engineering
│   ├── forecasting/
│   │   └── medium_range.py       # Medium-range forecast (17–90 days)
│   └── recommendation/
│       └── recommender.py        # Enhanced multi-factor recommendation engine
│
├── data/
│   ├── regions.json              # Region metadata (coordinates, climate, soil)
│   └── historical/               # 10 years × 10 regions (Parquet)
│       ├── PUNE/
│       │   ├── 2014.parquet
│       │   └── ... (2024.parquet)
│       └── ... (9 more regions)
│
├── templates/
│   └── index.html                # Bilingual web UI (Hindi + English)
│
├── static/
│   ├── css/style.css             # Green agricultural theme, responsive
│   └── js/app.js                 # Frontend JavaScript logic
│
├── scripts/
│   └── generate_historical_data.py  # Data generation utility
│
├── test_system.py                # Foundation unit tests
├── test_enhanced_system.py       # End-to-end integration tests
├── main.py                       # Quick CLI demo (Pune Rabi season)
├── run_website.py                # Web server startup script
├── requirements.txt
├── IMPLEMENTATION_SUMMARY.md     # Detailed feature implementation log
└── WEBSITE_README.md             # Web UI usage guide
```

---

## 🧪 Running Tests

### Foundation Tests
```bash
python test_system.py
```
> Covers: historical data retrieval, climatology calculation, region management, nearest region finder, crop database, soil scoring, and integrated queries.

### Integration Tests
```bash
python test_enhanced_system.py
```
> Covers: complete workflow tests, multiple region comparisons, irrigation scenario testing, season detection.

### Quick CLI Demo
```bash
python main.py
```
> Runs a quick recommendation for Pune in Rabi season and prints a forecast + ranked crop list.

---

## 📊 Sample Results

**Pune District | Rabi Season | Clay-Loam Soil | Limited Irrigation**

| Rank | Crop | Score | Duration | Risk |
|------|------|-------|----------|------|
| 1 | Jowar (Sorghum) | 83.7 | 90 days | Low |
| 2 | Green Gram (Moong) | 66.3 | 75 days | Low |
| 3 | Sunflower | 66.0 | 85 days | Low |

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend API** | Python 3.8+, FastAPI, Uvicorn |
| **Frontend** | HTML5, CSS3, JavaScript (Jinja2 templates) |
| **Data Storage** | Apache Parquet (historical), JSON (region/crop config) |
| **Data Processing** | Pandas, NumPy |
| **Machine Learning** | scikit-learn |
| **Weather API** | Open-Meteo (free, no API key required) |
| **Testing** | Custom test suites (unittest-style) |

---

## ⚙️ System Requirements

| Component | Minimum |
|-----------|---------|
| Python | 3.8+ |
| RAM | 2 GB |
| Storage | 500 MB (for historical Parquet data) |
| Browser | Chrome, Firefox, Safari, Edge (latest) |

---

## 🛣️ Roadmap

- [x] Historical weather data infrastructure (40,180 records)
- [x] 10-region management system with soil profiles
- [x] 15-crop database with multi-factor scoring
- [x] Soil compatibility analysis + amendment suggestions
- [x] Season-aware recommendation logic
- [x] Enhanced FastAPI REST endpoints
- [x] Bilingual web interface (Hindi + English)
- [x] End-to-end integration tests
- [ ] ML-based weather forecasting (LSTM + XGBoost)
- [ ] Crop suitability prediction model (Random Forest)
- [ ] Risk assessment engine (drought, temperature stress, extreme events)
- [ ] Market price integration
- [ ] Pest/disease warnings
- [ ] SMS / WhatsApp alerts
- [ ] Offline mode support
- [ ] Planting calendar with crop images

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/add-new-crop`)
3. Commit your changes (`git commit -m 'Add: new crop variety support'`)
4. Push to the branch (`git push origin feature/add-new-crop`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- **[Open-Meteo](https://open-meteo.com/)** — Free, open-source weather API
- **C-DAC (Centre for Development of Advanced Computing)** — Project incubation
- Maharashtra Agricultural Department — Domain knowledge and regional data
- Indian farmers — The end users who inspired this project

---

<div align="center">
  <strong>Built with ❤️ for Indian Farmers</strong><br/>
  <em>Empowering agriculture through data and technology</em>
</div>
