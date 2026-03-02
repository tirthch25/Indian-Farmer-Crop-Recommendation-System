"""
Medium-Range Weather Forecasting (ML-Enhanced)

Provides weather forecasts for agricultural planning:
- Uses ML ensemble (LSTM + XGBoost) when trained models are available
- Falls back to climatology-based estimation otherwise

This module replaces the original simple climatology extrapolation
with ML-powered predictions while maintaining backward compatibility.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def forecast_days_17_90(weather_df: pd.DataFrame, planning_days: int = 90, region_id: str = None) -> Dict:
    """
    Generate medium-range weather forecast for agricultural planning.
    
    Attempts ML-based forecasting first, falls back to climatology.
    
    Args:
        weather_df: Recent weather DataFrame with temp_avg, rainfall, dry_spell_days
        planning_days: Planning horizon in days
        region_id: Region ID for loading ML models (optional)
        
    Returns:
        Dictionary with expected temperature, rainfall, and risk levels
    """
    ml_forecast = None
    
    # --- Try ML-based forecasting ---
    if region_id:
        ml_forecast = _get_ml_forecast(weather_df, planning_days, region_id)
    
    if ml_forecast:
        logger.info(f"Using ML forecast for region {region_id}")
        return {
            "expected_avg_temp": ml_forecast['summary'].get('avg_temp', 25.0),
            "expected_rainfall_mm": ml_forecast['summary'].get('total_rainfall', 100.0),
            "dry_spell_risk": _calculate_dry_spell_risk(ml_forecast),
            "forecast_source": ml_forecast.get('model_used', 'ML ensemble'),
            "confidence": ml_forecast.get('confidence', 'medium'),
            "daily_predictions": ml_forecast.get('predictions', []),
            "ml_summary": ml_forecast.get('summary', {})
        }
    
    # --- Fallback: Climatology-based estimation (uses historical zone data) ---
    logger.info("Using historical/climatology-based forecast (no ML models available)")
    return _climatology_forecast(weather_df, planning_days, region_id=region_id)


def _get_ml_forecast(weather_df: pd.DataFrame, planning_days: int, region_id: str) -> Optional[Dict]:
    """
    ML-based forecast placeholder.

    LSTM/XGBoost district models were removed (district Parquet data no longer
    available). This function is a stub for future re-implementation. The
    climatology + historical zone blend fallback is used instead.
    """
    return None



def _climatology_forecast(weather_df: pd.DataFrame, planning_days: int, region_id: str = None) -> Dict:
    """
    Climatology-based forecast (fallback when no ML models).

    Uses IMD-reference historical zone averages from data/weather/zone/historical_weather.csv
    when available; falls back to the original API-extrapolation approach if not.
    """
    current_month = datetime.now().month

    # ── Try to use historical zone data ──────────────────────────────────────
    hist_temp = None
    hist_rain = None
    hist_hum  = None
    try:
        from src.weather.history import get_zone_for_region, get_monthly_climate, get_seasonal_climate
        from src.utils.seasons import detect_season

        zone = get_zone_for_region(region_id)

        # Determine season from current month
        from datetime import datetime as _dt
        season = detect_season(_dt.now(), region_id)

        # Get full seasonal aggregate (total rainfall, avg temp, avg humidity)
        seas = get_seasonal_climate(zone, season)
        hist_rain = seas["total_rainfall_mm"]
        hist_temp = seas["avg_temperature"]
        hist_hum  = seas["avg_humidity"]

        # Scale rainfall if planning period differs from season length
        season_lengths = {"Kharif": 153, "Rabi": 151, "Zaid": 61}
        season_days = season_lengths.get(season, 120)
        if planning_days != season_days:
            hist_rain = round(hist_rain * (planning_days / season_days), 1)

        logger.info(
            f"Historical forecast for zone={zone} season={season}: "
            f"temp={hist_temp}°C rain={hist_rain}mm hum={hist_hum}%"
        )
    except Exception as e:
        logger.debug(f"Historical weather data not available: {e}")

    # ── Short-term signals (Days 1–16 from API) ───────────────────────────────
    avg_temp_api    = float(weather_df["temp_avg"].mean())
    avg_daily_rain  = float(weather_df["rainfall"].mean())
    dry_spell_risk  = int(weather_df["dry_spell_days"].max())

    if avg_daily_rain < 0.5:
        avg_daily_rain = 1.5  # conservative climatological floor

    # ── Blend API recent data (30%) with historical baseline (70%) ────────────
    if hist_temp is not None:
        expected_temp = round(0.3 * avg_temp_api + 0.7 * hist_temp, 1)
        expected_rain = round(0.3 * (avg_daily_rain * planning_days) + 0.7 * hist_rain, 1)
        expected_hum  = hist_hum
        forecast_source = "historical_zone_blend"
        confidence = "medium"
    else:
        # Pure API extrapolation (original fallback)
        temp_trend = (
            weather_df["temp_avg"].iloc[-5:].mean() - weather_df["temp_avg"].iloc[:5].mean()
        )
        temp_adjustment = 1.0 if temp_trend > 0 else (-1.0 if temp_trend < 0 else 0)
        expected_temp = round(avg_temp_api + temp_adjustment, 2)
        expected_rain = round(avg_daily_rain * planning_days, 1)
        expected_hum  = float(weather_df.get("humidity", pd.Series([65.0])).mean()) if "humidity" in weather_df.columns else 65.0
        forecast_source = "climatology"
        confidence = "low"

    return {
        "expected_avg_temp":     expected_temp,
        "expected_rainfall_mm":  expected_rain,
        "expected_humidity":     round(expected_hum, 1),
        "dry_spell_risk": (
            "High"     if dry_spell_risk > 7 else
            "Moderate" if dry_spell_risk > 4 else
            "Low"
        ),
        "forecast_source": forecast_source,
        "confidence":      confidence,
        "daily_predictions": [],
        "ml_summary": {}
    }



def _calculate_dry_spell_risk(forecast: Dict) -> str:
    """Calculate dry spell risk from ML forecast predictions."""
    predictions = forecast.get('predictions', [])
    
    if not predictions:
        return "Unknown"
    
    # Count consecutive days with < 2mm rainfall
    max_dry_spell = 0
    current_dry = 0
    
    for pred in predictions:
        if pred.get('rainfall', 0) < 2.0:
            current_dry += 1
            max_dry_spell = max(max_dry_spell, current_dry)
        else:
            current_dry = 0
    
    if max_dry_spell > 7:
        return "High"
    elif max_dry_spell > 4:
        return "Moderate"
    else:
        return "Low"
