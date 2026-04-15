"""
Historical Weather Reader for Indian Agro-Climatic Zones

Reads the generated historical_weather.csv and provides:
  - Zone-level climatological baselines (10-year monthly averages)
  - Region -> Zone mapping using state prefix codes
  - Seasonal baselines (avg temp, monthly rainfall, humidity) used by:
      • forecast.py  (climatology forecast fallback)
      • recommender.py  (weather_conditions humidity)
      • app.py  (monthly climate chart for the UI)

Zone reference:
  North    : UP, Punjab, Haryana, Rajasthan, Himachal, Uttarakhand, Delhi, J&K
  South    : Karnataka, Tamil Nadu, AP, Telangana, Kerala
  East     : West Bengal, Bihar, Odisha, Jharkhand
  West     : Maharashtra, Gujarat
  Central  : MP, Chhattisgarh
  Northeast: Assam, Arunachal, Manipur, Meghalaya, Sikkim, Nagaland, Tripura
"""

import csv
import os
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Default data path (relative to working directory = agri_crop_recommendation/) ──
_DEFAULT_CSV = os.path.join("data", "weather", "zone", "historical_weather.csv")

# ── Region-prefix → Zone mapping ──────────────────────────────────────────────
_STATE_TO_ZONE: Dict[str, str] = {
    # North
    "UP": "North", "PB": "North", "HR": "North", "HP": "North",
    "UK": "North", "DL": "North", "JK": "North", "RJ": "North",
    # South
    "KA": "South", "TN": "South", "AP": "South", "TS": "South", "KL": "South",
    # East
    "WB": "East",  "BR": "East",  "OD": "East",  "JH": "East",
    # West
    "MH": "West",  "GJ": "West",
    # Central
    "MP": "Central", "CG": "Central",
    # Northeast
    "AS": "Northeast", "AR": "Northeast", "MN": "Northeast",
    "MG": "Northeast", "SK": "Northeast", "NL": "Northeast", "TR": "Northeast",
}


def get_zone_for_region(region_id: Optional[str]) -> str:
    """
    Derive the agro-climatic zone from a region_id like 'UP_LUCKNOW'.
    Defaults to 'North' if unknown.
    """
    if not region_id:
        return "North"
    state_code = region_id.split("_")[0].upper()
    return _STATE_TO_ZONE.get(state_code, "North")


# ── In-memory cache keyed by CSV path ─────────────────────────────────────────
_cache: Dict[str, Dict] = {}


def _load_csv(csv_path: str) -> Dict:
    """
    Load and aggregate historical_weather.csv into nested lookup:
      { zone: { month: { 'temperature': float, 'rainfall': float, 'humidity': float } } }
    Averages over all years in the file.
    """
    if csv_path in _cache:
        return _cache[csv_path]

    # Accumulator: { zone: { month: [values] } }
    acc: Dict[str, Dict[int, Dict[str, list]]] = {}

    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                zone  = row["zone"]
                month = int(row["month"])
                temp  = float(row["temperature"])
                rain  = float(row["rainfall"])
                hum   = float(row["humidity"])

                acc.setdefault(zone, {}).setdefault(month, {
                    "temperature": [], "rainfall": [], "humidity": []
                })
                acc[zone][month]["temperature"].append(temp)
                acc[zone][month]["rainfall"].append(rain)
                acc[zone][month]["humidity"].append(hum)

        # Average over years
        result: Dict[str, Dict[int, Dict[str, float]]] = {}
        for zone, months in acc.items():
            result[zone] = {}
            for month, vals in months.items():
                result[zone][month] = {
                    "temperature": round(sum(vals["temperature"]) / len(vals["temperature"]), 1),
                    "rainfall":    round(sum(vals["rainfall"])    / len(vals["rainfall"]),    1),
                    "humidity":    round(sum(vals["humidity"])     / len(vals["humidity"]),    1),
                }

        _cache[csv_path] = result
        logger.info(f"Historical weather loaded: {len(result)} zones from {csv_path}")
        return result

    except FileNotFoundError:
        logger.warning(f"Historical weather CSV not found at {csv_path}. Run scripts/generate_historical_weather.py first.")
        return {}
    except Exception as e:
        logger.error(f"Error loading historical weather: {e}")
        return {}


def get_monthly_climate(
    zone: str,
    month: int,
    csv_path: str = _DEFAULT_CSV
) -> Dict[str, float]:
    """
    Return average temperature (°C), monthly rainfall (mm), and humidity (%)
    for a zone and calendar month (1–12).

    Returns sensible defaults if data is unavailable.
    """
    data = _load_csv(csv_path)
    fallback = {"temperature": 28.0, "rainfall": 80.0, "humidity": 60.0}
    if not data:
        return fallback
    zone_data = data.get(zone, data.get("North", {}))
    return zone_data.get(month, fallback)


def get_seasonal_climate(
    zone: str,
    season: str,
    csv_path: str = _DEFAULT_CSV
) -> Dict[str, float]:
    """
    Return aggregated temperature (avg), total rainfall (mm), and mean
    humidity (%) for an agricultural season.

    Season → Calendar months:
        Kharif : June–October  (6–10)
        Rabi   : November–March (11, 12, 1, 2, 3)
        Zaid   : April–May     (4, 5)
    """
    season_months = {
        "Kharif": [6, 7, 8, 9, 10],
        "Rabi":   [11, 12, 1, 2, 3],
        "Zaid":   [4, 5],
    }
    months = season_months.get(season, [6, 7, 8, 9, 10])

    temps, rains, hums = [], [], []
    for m in months:
        clim = get_monthly_climate(zone, m, csv_path)
        temps.append(clim["temperature"])
        rains.append(clim["rainfall"])
        hums.append(clim["humidity"])

    return {
        "avg_temperature":   round(sum(temps) / len(temps), 1),
        "total_rainfall_mm": round(sum(rains), 1),
        "avg_humidity":      round(sum(hums)  / len(hums),  1),
    }


def get_climate_for_region(
    region_id: Optional[str],
    season: str,
    csv_path: str = _DEFAULT_CSV
) -> Dict[str, float]:
    """
    Convenience: derive zone from region_id and return seasonal climate.
    """
    zone = get_zone_for_region(region_id)
    return get_seasonal_climate(zone, season, csv_path)
