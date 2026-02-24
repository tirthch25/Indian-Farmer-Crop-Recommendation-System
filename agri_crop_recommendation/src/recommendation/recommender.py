"""
Enhanced Crop Recommendation Engine

Integrates historical data, ML predictions, soil compatibility, risk assessment,
and season-aware logic to provide comprehensive crop recommendations for Indian farmers.
"""

from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
import logging

from src.crops.crop_db import crop_db
from src.crops.models import CropInfo
from src.soil.models import SoilInfo, calculate_soil_compatibility_score
from src.data.regions import RegionManager
from src.data.historical_store import HistoricalDataStore
from src.utils.seasons import detect_season, is_season_transition, get_season_water_adjustment

logger = logging.getLogger(__name__)


def recommend_crops(
    weather_df: pd.DataFrame,
    season: str,
    region_id: Optional[str] = None,
    soil: Optional[SoilInfo] = None,
    irrigation_available: bool = True,
    planning_days: int = 90
) -> List[Dict]:
    """
    Generate crop recommendations based on weather, soil, and regional data.
    
    Args:
        weather_df: Weather forecast DataFrame
        season: Agricultural season (Kharif, Rabi, Zaid)
        region_id: Region identifier (optional)
        soil: Soil information (optional)
        irrigation_available: Whether irrigation is available
        planning_days: Planning horizon in days
        
    Returns:
        List of crop recommendations sorted by suitability score
    """
    logger.info(f"Generating recommendations for season={season}, region={region_id}")
    
    # Calculate weather statistics
    avg_temp = weather_df["temp_avg"].mean()
    avg_daily_rain = weather_df["rainfall"].mean()
    max_dry_spell = weather_df["dry_spell_days"].max()
    
    # Climatological fallback
    if avg_daily_rain < 0.5:
        avg_daily_rain = 1.5
    
    expected_rainfall = avg_daily_rain * planning_days
    
    # Get crops for season
    season_crops = crop_db.get_crops_by_season(season)
    logger.info(f"Found {len(season_crops)} crops for {season} season")
    
    # Filter by region if provided
    if region_id:
        season_crops = [c for c in season_crops if c.is_suitable_for_region(region_id, threshold=0.5)]
        logger.info(f"Filtered to {len(season_crops)} crops suitable for {region_id}")
    
    # Filter by soil if provided
    if soil:
        season_crops = crop_db.filter_by_soil(season_crops, soil, min_score=40.0)
        logger.info(f"Filtered to {len(season_crops)} crops compatible with soil")
    
    # Score each crop
    recommendations = []
    for crop in season_crops:
        score = calculate_suitability_score(
            crop=crop,
            avg_temp=avg_temp,
            expected_rainfall=expected_rainfall,
            max_dry_spell=max_dry_spell,
            season=season,
            region_id=region_id,
            soil=soil,
            irrigation_available=irrigation_available
        )
        
        # Calculate water requirements
        irrigation_buffer = 50 if irrigation_available else 0
        water_available = expected_rainfall + irrigation_buffer
        irrigation_needed = max(0, crop.water_requirement_mm - expected_rainfall)
        
        # Determine risk
        risk = determine_risk_level(crop, max_dry_spell, water_available)
        
        recommendations.append({
            "crop": crop.common_name,
            "crop_id": crop.crop_id,
            "suitability_score": float(round(score, 2)),
            "expected_rainfall_mm": float(round(expected_rainfall, 1)),
            "water_required_mm": crop.water_requirement_mm,
            "irrigation_needed_mm": float(round(irrigation_needed, 1)),
            "growth_duration_days": crop.duration_days,
            "risk_note": risk,
            "drought_tolerance": crop.drought_tolerance,
            "regional_suitability": crop.regional_suitability.get(region_id, 0.5) if region_id else 0.5
        })
    
    # Sort by suitability score
    recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
    
    logger.info(f"Generated {len(recommendations)} recommendations")
    return recommendations


def calculate_suitability_score(
    crop: CropInfo,
    avg_temp: float,
    expected_rainfall: float,
    max_dry_spell: int,
    season: str,
    region_id: Optional[str] = None,
    soil: Optional[SoilInfo] = None,
    irrigation_available: bool = True
) -> float:
    """
    Calculate comprehensive suitability score (0-100).
    
    Scoring components:
    - Temperature compatibility: 25%
    - Water availability: 25%
    - Soil compatibility: 15%
    - Regional suitability: 15%
    - Seasonal adjustment: 10%
    - Drought tolerance bonus: 10%
    
    Args:
        crop: Crop information
        avg_temp: Average temperature
        expected_rainfall: Expected rainfall in mm
        max_dry_spell: Maximum dry spell days
        season: Current season
        region_id: Region identifier
        soil: Soil information
        irrigation_available: Whether irrigation is available
        
    Returns:
        Suitability score (0-100)
    """
    score = 0.0
    
    # 1. Temperature score (25%)
    temp_score = calculate_temperature_score(crop, avg_temp)
    score += temp_score * 0.25
    
    # 2. Water score (25%)
    water_score = calculate_water_score(crop, expected_rainfall, irrigation_available, season)
    score += water_score * 0.25
    
    # 3. Soil score (15%)
    if soil:
        soil_score = calculate_soil_compatibility_score(crop, soil)
    else:
        soil_score = 70.0  # Default if no soil info
    score += soil_score * 0.15
    
    # 4. Regional score (15%)
    if region_id:
        regional_score = crop.regional_suitability.get(region_id, 0.5) * 100
    else:
        regional_score = 50.0  # Default if no region
    score += regional_score * 0.15
    
    # 5. Seasonal adjustment (10%)
    seasonal_score = 100.0 if season in crop.seasons else 50.0
    score += seasonal_score * 0.10
    
    # 6. Drought tolerance bonus (10%)
    drought_score = calculate_drought_tolerance_score(crop, max_dry_spell)
    score += drought_score * 0.10
    
    return min(score, 100.0)


def calculate_temperature_score(crop: CropInfo, avg_temp: float) -> float:
    """Calculate temperature compatibility score (0-100)."""
    if crop.temp_optimal_min <= avg_temp <= crop.temp_optimal_max:
        return 100.0
    elif crop.temp_min <= avg_temp <= crop.temp_max:
        # Linear decay from optimal range
        if avg_temp < crop.temp_optimal_min:
            range_size = crop.temp_optimal_min - crop.temp_min
            distance = crop.temp_optimal_min - avg_temp
        else:
            range_size = crop.temp_max - crop.temp_optimal_max
            distance = avg_temp - crop.temp_optimal_max
        
        if range_size > 0:
            return 100.0 - (distance / range_size) * 40.0
        return 60.0
    else:
        return 0.0


def calculate_water_score(
    crop: CropInfo,
    expected_rainfall: float,
    irrigation_available: bool,
    season: str
) -> float:
    """Calculate water availability score (0-100)."""
    # Adjust water requirement based on season
    adjusted_requirement = get_season_water_adjustment(season, crop.water_requirement_mm)
    
    # Calculate available water
    irrigation_buffer = 50 if irrigation_available else 0
    water_available = expected_rainfall + irrigation_buffer
    
    # Calculate ratio
    water_ratio = water_available / adjusted_requirement if adjusted_requirement > 0 else 1.0
    
    if water_ratio >= 1.0:
        # Sufficient water
        return 100.0
    elif water_ratio >= 0.8:
        # Slight deficit
        if crop.drought_tolerance == "High":
            return 90.0
        elif crop.drought_tolerance == "Moderate":
            return 75.0
        else:
            return 60.0
    elif water_ratio >= 0.6:
        # Moderate deficit
        if crop.drought_tolerance == "High":
            return 75.0
        elif crop.drought_tolerance == "Moderate":
            return 50.0
        else:
            return 30.0
    else:
        # Severe deficit
        if crop.drought_tolerance == "High":
            return 50.0
        else:
            return 0.0


def calculate_drought_tolerance_score(crop: CropInfo, max_dry_spell: int) -> float:
    """Calculate drought tolerance bonus score (0-100)."""
    if max_dry_spell <= 4:
        return 100.0  # Low drought risk
    elif max_dry_spell <= 7:
        # Moderate drought risk
        if crop.drought_tolerance == "High":
            return 100.0
        elif crop.drought_tolerance == "Moderate":
            return 70.0
        else:
            return 40.0
    else:
        # High drought risk
        if crop.drought_tolerance == "High":
            return 80.0
        elif crop.drought_tolerance == "Moderate":
            return 40.0
        else:
            return 0.0


def determine_risk_level(crop: CropInfo, max_dry_spell: int, water_available: float) -> str:
    """Determine overall risk level."""
    risks = []
    
    # Drought risk
    if max_dry_spell > 7:
        if crop.drought_tolerance == "Low":
            risks.append("High drought risk")
        elif crop.drought_tolerance == "Moderate":
            risks.append("Moderate drought risk")
    
    # Water deficit risk
    water_ratio = water_available / crop.water_requirement_mm if crop.water_requirement_mm > 0 else 1.0
    if water_ratio < 0.8:
        risks.append("Water deficit risk")
    
    if not risks:
        return "Low risk"
    elif len(risks) == 1:
        return risks[0]
    else:
        return "Multiple risks: " + ", ".join(risks)
