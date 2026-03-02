from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from starlette.requests import Request

from src.weather.fetcher import fetch_weather
from src.ml.pipeline import add_agri_features
from src.weather.forecast import forecast_days_17_90
from src.services.recommender import recommend_crops
from src.utils.regions import RegionManager
from src.crops.soil import SoilInfo
from src.utils.seasons import detect_season, is_season_transition, format_season_guidance
from src.services.risk import RiskAssessmentEngine
from src.services.pests import PestWarningSystem
from src.services.calendar import PlantingCalendar

app = FastAPI(
    title="Indian Farmer Crop Recommendation API",
    description="ML-powered crop recommendation system with weather forecasting (LSTM + XGBoost), "
                "crop suitability prediction (Random Forest), risk assessment, pest warnings, "
                "and planting calendar for Indian farmers.",
    version="3.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize managers
region_manager = RegionManager()
risk_engine = RiskAssessmentEngine()
pest_system = PestWarningSystem()
planting_calendar = PlantingCalendar()


# ----------- Request Schemas -----------

class SoilRequest(BaseModel):
    texture: str = Field(..., description="Soil texture: Clay, Loam, Sandy, Clay-Loam, Sandy-Loam")
    ph: float = Field(..., ge=0, le=14, description="Soil pH (0-14)")
    organic_matter: str = Field(..., description="Organic matter: Low, Medium, High")
    drainage: Optional[str] = Field("Medium", description="Drainage: Poor, Medium, Good")


class RegionRequest(BaseModel):
    region_id: Optional[str] = Field(None, description="Region ID (e.g., PUNE, SOLAPUR)")
    latitude: Optional[float] = Field(None, description="Latitude (if region_id not provided)")
    longitude: Optional[float] = Field(None, description="Longitude (if region_id not provided)")
    season: Optional[str] = Field(None, description="Season: Kharif, Rabi, Zaid (auto-detected if not provided)")
    soil: Optional[SoilRequest] = Field(None, description="Soil information (uses region default if not provided)")
    irrigation: str = Field("Limited", description="Irrigation: None, Limited, Full")
    planning_days: int = Field(90, ge=15, le=365, description="Planning horizon in days (15-365)")


class RiskRequest(BaseModel):
    region_id: str = Field(..., description="Region ID")
    crop_id: str = Field(..., description="Crop ID (e.g., BAJRA_01)")
    season: Optional[str] = Field(None, description="Season (auto-detected if not provided)")
    irrigation: str = Field("Limited", description="Irrigation: None, Limited, Full")


# ----------- Helper Functions -----------

def _resolve_region(region_id=None, latitude=None, longitude=None):
    """Resolve region from ID or coordinates."""
    if region_id:
        region = region_manager.get_region_profile(region_id)
        if not region:
            raise HTTPException(status_code=404, detail=f"Region {region_id} not found")
        return region, region.latitude, region.longitude
    elif latitude and longitude:
        region = region_manager.find_nearest_region(latitude, longitude, max_distance_km=150)
        if not region:
            raise HTTPException(status_code=404, detail="No region found within 100km")
        return region, latitude, longitude
    else:
        raise HTTPException(status_code=400, detail="Either region_id or coordinates required")


def _get_weather_and_season(region, latitude, longitude, season=None):
    """Fetch weather, detect season, create forecast."""
    current_date = datetime.now()
    
    if season:
        if season not in ["Kharif", "Rabi", "Zaid"]:
            raise HTTPException(status_code=400, detail="Invalid season. Must be Kharif, Rabi, or Zaid")
    else:
        season = detect_season(current_date, region.region_id)
    
    is_transition, next_season = is_season_transition(current_date)
    
    # Pass region_id and season so fetch_weather can enrich with historical humidity
    weather = fetch_weather(latitude, longitude, region_id=region.region_id, season=season)
    weather = add_agri_features(weather)
    
    return weather, season, is_transition, next_season


# ----------- API Endpoints -----------

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    """Serve the main web interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/favicon.ico")
async def favicon():
    """Return favicon to prevent 404 errors."""
    from fastapi.responses import Response
    return Response(
        content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82',
        media_type="image/x-icon"
    )


@app.get("/health")
def health_check():
    """Health check endpoint."""
    # Check ML model availability
    ml_status = {}
    try:
        from src.ml.predictor import CropSuitabilityRF
        rf_model = CropSuitabilityRF.load()
        ml_status['crop_suitability_rf'] = 'loaded' if rf_model else 'not_trained'
    except Exception:
        ml_status['crop_suitability_rf'] = 'not_available'
    
    return {
        "status": "healthy",
        "version": "3.0",
        "regions_loaded": len(region_manager.get_all_regions()),
        "ml_models": ml_status,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/regions")
def get_regions():
    """Get list of all supported regions."""
    regions = region_manager.get_all_regions()
    return {
        "regions": [
            {
                "region_id": r.region_id,
                "name": r.name,
                "state": getattr(r, 'state', 'Unknown'),
                "latitude": r.latitude,
                "longitude": r.longitude,
                "climate_zone": r.climate_zone,
                "typical_soil_types": r.typical_soil_types
            }
            for r in regions
        ]
    }


@app.post("/recommend")
def recommend(request: RegionRequest):
    """
    Generate ML-enhanced crop recommendations.
    
    Returns recommendations with suitability scores (ML-blended when available),
    risk assessments, pest warnings, and planting calendar.
    """
    try:
        # 1. Resolve region
        region, latitude, longitude = _resolve_region(
            request.region_id, request.latitude, request.longitude
        )
        
        # 2. Get weather and season
        weather, season, is_transition, next_season = _get_weather_and_season(
            region, latitude, longitude, request.season
        )
        season_guidance = format_season_guidance(season, is_transition, next_season)
        
        # 3. Determine soil
        if request.soil:
            soil = SoilInfo(
                texture=request.soil.texture,
                ph=request.soil.ph,
                organic_matter=request.soil.organic_matter,
                drainage=request.soil.drainage
            )
        else:
            soil = region.get_default_soil()
            if not soil:
                soil = SoilInfo(texture="Loam", ph=7.0, organic_matter="Medium", drainage="Medium")
        
        # 4. Medium-range forecast (ML-enhanced)
        forecast = forecast_days_17_90(weather, request.planning_days, region_id=region.region_id)
        
        # 5. Determine irrigation
        irrigation_map = {"None": False, "Limited": True, "Full": True}
        irrigation_available = irrigation_map.get(request.irrigation, True)
        
        # 6. Generate crop recommendations (ML-blended scoring)
        crops = recommend_crops(
            weather_df=weather,
            season=season,
            region_id=region.region_id,
            soil=soil,
            irrigation_available=irrigation_available,
            planning_days=request.planning_days
        )
        
        # 7. Add risk assessment and pest warnings to each crop
        weather_conditions = {
            'avg_temp_max': float(weather['temp_max'].mean()),
            'avg_temp_min': float(weather['temp_min'].mean()),
            'avg_temp': float(weather['temp_avg'].mean()) if 'temp_avg' in weather.columns else float((weather['temp_max'].mean() + weather['temp_min'].mean()) / 2),
            'total_rainfall': float(forecast.get('expected_rainfall_mm', 0)),
            'avg_humidity': 65,
            'forecast_days': request.planning_days
        }
        
        for crop_rec in crops[:10]:
            # Risk assessment
            crop_info = {
                'water_requirement_mm': crop_rec['water_required_mm'],
                'drought_tolerance': crop_rec['drought_tolerance'],
                'temp_min': 15,  # General defaults
                'temp_max': 40,
            }
            
            # Try to get actual crop temp limits
            try:
                from src.crops.database import crop_db
                crop_detail = crop_db.get_crop(crop_rec['crop_id'])
                if crop_detail:
                    crop_info['temp_min'] = crop_detail.temp_min
                    crop_info['temp_max'] = crop_detail.temp_max
                    crop_info['temp_optimal_min'] = crop_detail.temp_optimal_min
                    crop_info['temp_optimal_max'] = crop_detail.temp_optimal_max
                    crop_rec['growing_tip'] = getattr(crop_detail, 'growing_tip', '')
                    crop_rec['duration_range'] = list(crop_detail.duration_range)
            except Exception:
                crop_rec.setdefault('growing_tip', '')
                crop_rec.setdefault('duration_range', [])
            
            risk = risk_engine.assess_risk(
                crop_info=crop_info,
                weather_forecast=forecast,
                season=season,
                irrigation_available=irrigation_available
            )
            crop_rec['risk_assessment'] = risk
            
            # Pest warnings
            pest_warnings = pest_system.get_warnings(
                crop_rec['crop_id'], weather_conditions, season
            )
            crop_rec['pest_warnings'] = pest_warnings[:3]  # Top 3
        
        # 8. Generate planting calendars for top crops
        calendars = planting_calendar.get_multiple_calendars(crops[:10], season)
        
        # 9. Build month-wise forecast from historical zone data (Jan–Dec)
        MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        monthly_forecast = []
        try:
            from src.weather.history import get_zone_for_region, get_monthly_climate
            zone = get_zone_for_region(region.region_id)
            for m in range(1, 13):
                clim = get_monthly_climate(zone, m)
                monthly_forecast.append({
                    "month":       MONTH_NAMES[m - 1],
                    "month_num":   m,
                    "temperature": clim["temperature"],
                    "rainfall":    clim["rainfall"],
                    "humidity":    clim["humidity"],
                })
        except Exception:
            pass
        forecast["monthly_forecast"] = monthly_forecast
        
        # 10. Build response
        return {
            "region": {
                "region_id": region.region_id,
                "name": region.name,
                "latitude": latitude,
                "longitude": longitude,
                "climate_zone": region.climate_zone
            },
            "season": {
                "current": season,
                "is_transition": is_transition,
                "next_season": next_season,
                "guidance": season_guidance
            },
            "soil": {
                "texture": soil.texture,
                "ph": soil.ph,
                "organic_matter": soil.organic_matter,
                "drainage": soil.drainage,
                "source": "user_provided" if request.soil else "region_default"
            },
            "irrigation": request.irrigation,
            "medium_range_forecast": forecast,
            "recommended_crops": crops[:10],
            "planting_calendars": calendars,
            "total_crops_analyzed": len(crops)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ----------- New ML-Enhanced Endpoints -----------

@app.get("/forecast/{region_id}")
def get_forecast(region_id: str, days: int = 7):
    """
    Get ML-powered weather forecast for a region.
    
    Uses ensemble of LSTM + XGBoost models when available,
    falls back to climatology-based estimation.
    """
    try:
        region = region_manager.get_region_profile(region_id.upper())
        if not region:
            raise HTTPException(status_code=404, detail=f"Region {region_id} not found")
        
        # Fetch current weather
        weather = fetch_weather(region.latitude, region.longitude)
        weather = add_agri_features(weather)
        
        # Generate ML forecast
        forecast = forecast_days_17_90(weather, planning_days=days, region_id=region.region_id)
        
        return {
            "region_id": region.region_id,
            "region_name": region.name,
            "forecast_days": days,
            "current_weather": {
                "avg_temp_max": round(float(weather['temp_max'].mean()), 2),
                "avg_temp_min": round(float(weather['temp_min'].mean()), 2),
                "total_rainfall_recent": round(float(weather['rainfall'].sum()), 2)
            },
            "forecast": forecast
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")


@app.post("/risk-assessment")
def assess_risk(request: RiskRequest):
    """
    Get comprehensive risk assessment for a crop in a region.
    
    Evaluates drought risk, temperature stress, and extreme weather events.
    """
    try:
        region = region_manager.get_region_profile(request.region_id.upper())
        if not region:
            raise HTTPException(status_code=404, detail=f"Region {request.region_id} not found")
        
        # Get crop info
        from src.crops.database import crop_db
        crop = crop_db.get_crop(request.crop_id)
        if not crop:
            raise HTTPException(status_code=404, detail=f"Crop {request.crop_id} not found")
        
        # Fetch weather and forecast
        weather = fetch_weather(region.latitude, region.longitude)
        weather = add_agri_features(weather)
        
        season = request.season or detect_season(datetime.now(), region.region_id)
        forecast = forecast_days_17_90(weather, planning_days=90, region_id=region.region_id)
        
        irrigation_map = {"None": False, "Limited": True, "Full": True}
        
        # Run risk assessment
        crop_info = {
            'water_requirement_mm': crop.water_requirement_mm,
            'drought_tolerance': crop.drought_tolerance,
            'temp_min': crop.temp_min,
            'temp_max': crop.temp_max,
            'temp_optimal_min': crop.temp_optimal_min,
            'temp_optimal_max': crop.temp_optimal_max
        }
        
        risk = risk_engine.assess_risk(
            crop_info=crop_info,
            weather_forecast=forecast,
            season=season,
            irrigation_available=irrigation_map.get(request.irrigation, True)
        )
        
        return {
            "region_id": region.region_id,
            "crop": crop.common_name,
            "crop_id": crop.crop_id,
            "season": season,
            "risk_assessment": risk
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk assessment error: {str(e)}")


@app.get("/pest-warnings/{region_id}")
def get_pest_warnings(region_id: str, crop_id: Optional[str] = None):
    """
    Get pest and disease warnings for a region based on current weather conditions.
    
    Optionally filter by crop_id.
    """
    try:
        region = region_manager.get_region_profile(region_id.upper())
        if not region:
            raise HTTPException(status_code=404, detail=f"Region {region_id} not found")
        
        # Get current weather
        weather = fetch_weather(region.latitude, region.longitude)
        
        weather_conditions = {
            'avg_temp_max': float(weather['temp_max'].mean()),
            'avg_temp_min': float(weather['temp_min'].mean()),
            'avg_temp': float((weather['temp_max'].mean() + weather['temp_min'].mean()) / 2),
            'total_rainfall': float(weather['rainfall'].sum()),
            'avg_humidity': 65,
            'forecast_days': len(weather)
        }
        
        if crop_id:
            warnings = pest_system.get_warnings(crop_id, weather_conditions)
            return {
                "region_id": region.region_id,
                "crop_id": crop_id,
                "weather_conditions": weather_conditions,
                "warnings": warnings
            }
        else:
            all_warnings = pest_system.get_region_warnings(weather_conditions)
            return {
                "region_id": region.region_id,
                "weather_conditions": weather_conditions,
                "warnings_by_crop": all_warnings,
                "total_warnings": sum(len(w) for w in all_warnings.values())
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pest warning error: {str(e)}")


@app.get("/planting-calendar/{crop_id}")
def get_planting_calendar_endpoint(
    crop_id: str,
    season: Optional[str] = None,
    region_id: Optional[str] = None
):
    """
    Get planting calendar with milestone dates for a crop.
    
    Returns sowing date, growth phases, and harvest date with care tips.
    """
    try:
        from src.crops.database import crop_db
        crop = crop_db.get_crop(crop_id)
        if not crop:
            raise HTTPException(status_code=404, detail=f"Crop {crop_id} not found")
        
        if not season:
            season = detect_season(datetime.now())
        
        calendar = planting_calendar.get_calendar(
            crop_id=crop.crop_id,
            season=season,
            duration_days=crop.duration_days,
            crop_name=crop.common_name,
            region_id=region_id
        )
        
        return {
            "crop": crop.common_name,
            "calendar": calendar
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calendar error: {str(e)}")
