from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from starlette.requests import Request

from src.weather.open_meteo import fetch_weather
from src.preprocessing.features import add_agri_features
from src.forecasting.medium_range import forecast_days_17_90
from src.recommendation.recommender import recommend_crops
from src.data.regions import RegionManager
from src.soil.models import SoilInfo
from src.utils.seasons import detect_season, is_season_transition, format_season_guidance

app = FastAPI(
    title="Indian Farmer Crop Recommendation API",
    description="Comprehensive crop recommendation system for Indian farmers covering all regions with historical data, soil analysis, and season-aware recommendations",
    version="2.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize managers
region_manager = RegionManager()


# ----------- Request Schema -----------

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
    planning_days: int = Field(90, ge=70, le=120, description="Planning horizon in days")


# ----------- API Endpoints -----------

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    """Serve the main web interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/favicon.ico")
async def favicon():
    """Return favicon to prevent 404 errors."""
    from fastapi.responses import Response
    # Simple 1x1 transparent PNG
    return Response(
        content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82',
        media_type="image/x-icon"
    )


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "regions_loaded": len(region_manager.get_all_regions()),
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
    Generate crop recommendations based on region, season, soil, and irrigation.
    
    Returns comprehensive recommendations with suitability scores, risk assessments,
    and cultivation guidance.
    """
    try:
        # 1. Determine region
        if request.region_id:
            region = region_manager.get_region_profile(request.region_id)
            if not region:
                raise HTTPException(status_code=404, detail=f"Region {request.region_id} not found")
            latitude = region.latitude
            longitude = region.longitude
        elif request.latitude and request.longitude:
            latitude = request.latitude
            longitude = request.longitude
            # Find nearest region
            region = region_manager.find_nearest_region(latitude, longitude, max_distance_km=100)
            if not region:
                raise HTTPException(
                    status_code=404,
                    detail="No region found within 100km of specified coordinates"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either region_id or latitude/longitude must be provided"
            )
        
        # 2. Determine season
        current_date = datetime.now()
        if request.season:
            season = request.season
            if season not in ["Kharif", "Rabi", "Zaid"]:
                raise HTTPException(status_code=400, detail="Invalid season. Must be Kharif, Rabi, or Zaid")
        else:
            season = detect_season(current_date, region.region_id)
        
        # Check for season transition
        is_transition, next_season = is_season_transition(current_date)
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
            # Use region default
            soil = region.get_default_soil()
            if not soil:
                soil = SoilInfo(texture="Loam", ph=7.0, organic_matter="Medium", drainage="Medium")
        
        # 4. Fetch weather
        weather = fetch_weather(latitude, longitude)
        
        # 5. Preprocess
        weather = add_agri_features(weather)
        
        # 6. Medium-range forecast
        forecast = forecast_days_17_90(weather, request.planning_days)
        
        # 7. Determine irrigation availability
        irrigation_map = {"None": False, "Limited": True, "Full": True}
        irrigation_available = irrigation_map.get(request.irrigation, True)
        
        # 8. Generate recommendations
        crops = recommend_crops(
            weather_df=weather,
            season=season,
            region_id=region.region_id,
            soil=soil,
            irrigation_available=irrigation_available,
            planning_days=request.planning_days
        )
        
        # 9. Build response
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
            "recommended_crops": crops[:10],  # Top 10
            "total_crops_analyzed": len(crops)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
