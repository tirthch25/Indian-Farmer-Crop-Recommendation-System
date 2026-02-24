"""
Comprehensive Crop Knowledge Base for Indian Agriculture

Contains 20+ short-duration crops (70-90 days) with detailed information including
temperature requirements, water needs, soil compatibility, and regional suitability
for all major Indian agricultural regions.
"""

from typing import Dict, List, Optional
from src.crops.models import CropInfo
from src.soil.models import SoilInfo, calculate_soil_compatibility_score, get_soil_amendment_suggestions
import logging

logger = logging.getLogger(__name__)


# Comprehensive crop database with 20+ short-duration crops
CROPS_DATA = [
    # Millets
    CropInfo(
        crop_id="BAJRA_01",
        common_name="Bajra (Pearl Millet)",
        scientific_name="Pennisetum glaucum",
        duration_days=75,
        duration_range=(70, 85),
        temp_min=20, temp_optimal_min=25, temp_optimal_max=35, temp_max=42,
        water_requirement_mm=400,
        drought_tolerance="High",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=8.0,
        suitable_soil_textures=["Sandy", "Sandy-Loam", "Loam"],
        nutrient_requirements={"N": "Medium", "P": "Medium", "K": "Medium"},
        regional_suitability={
            "PUNE": 0.85, "SOLAPUR": 0.90, "NASHIK": 0.80,
            "AHMEDNAGAR": 0.85, "AURANGABAD": 0.88, "JALGAON": 0.75,
            "SANGLI": 0.82, "KOLHAPUR": 0.70, "SATARA": 0.78, "LATUR": 0.90
        },
        successful_regions=["SOLAPUR", "AURANGABAD", "LATUR", "AHMEDNAGAR"],
        seasons=["Kharif"],
        varieties=["GHB-558", "GHB-732", "ICMH-356"],
        typical_yield_kg_per_ha=1500,
        market_demand="High"
    ),
    
    CropInfo(
        crop_id="JOWAR_01",
        common_name="Jowar (Sorghum)",
        scientific_name="Sorghum bicolor",
        duration_days=85,
        duration_range=(75, 90),
        temp_min=18, temp_optimal_min=25, temp_optimal_max=35, temp_max=40,
        water_requirement_mm=450,
        drought_tolerance="High",
        waterlogging_tolerance="Low",
        soil_ph_min=5.5, soil_ph_max=8.5,
        suitable_soil_textures=["Clay", "Clay-Loam", "Loam"],
        nutrient_requirements={"N": "Medium", "P": "Medium", "K": "Low"},
        regional_suitability={
            "PUNE": 0.88, "SOLAPUR": 0.92, "NASHIK": 0.85,
            "AHMEDNAGAR": 0.90, "AURANGABAD": 0.90, "JALGAON": 0.82,
            "SANGLI": 0.88, "KOLHAPUR": 0.75, "SATARA": 0.85, "LATUR": 0.92
        },
        successful_regions=["SOLAPUR", "AHMEDNAGAR", "AURANGABAD", "LATUR"],
        seasons=["Kharif", "Rabi"],
        varieties=["CSH-16", "CSV-15", "M-35-1"],
        typical_yield_kg_per_ha=1800,
        market_demand="High"
    ),
    
    CropInfo(
        crop_id="RAGI_01",
        common_name="Ragi (Finger Millet)",
        scientific_name="Eleusine coracana",
        duration_days=80,
        duration_range=(75, 85),
        temp_min=18, temp_optimal_min=22, temp_optimal_max=30, temp_max=35,
        water_requirement_mm=500,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=5.0, soil_ph_max=8.2,
        suitable_soil_textures=["Sandy-Loam", "Loam", "Clay-Loam"],
        nutrient_requirements={"N": "Medium", "P": "Medium", "K": "Medium"},
        regional_suitability={
            "PUNE": 0.75, "SOLAPUR": 0.70, "NASHIK": 0.80,
            "AHMEDNAGAR": 0.72, "AURANGABAD": 0.70, "JALGAON": 0.78,
            "SANGLI": 0.75, "KOLHAPUR": 0.85, "SATARA": 0.82, "LATUR": 0.68
        },
        successful_regions=["KOLHAPUR", "SATARA", "NASHIK"],
        seasons=["Kharif"],
        varieties=["GPU-28", "ML-365", "VL-149"],
        typical_yield_kg_per_ha=1200,
        market_demand="Moderate"
    ),
    
    CropInfo(
        crop_id="FOXTAIL_01",
        common_name="Foxtail Millet",
        scientific_name="Setaria italica",
        duration_days=70,
        duration_range=(65, 75),
        temp_min=20, temp_optimal_min=25, temp_optimal_max=32, temp_max=38,
        water_requirement_mm=350,
        drought_tolerance="High",
        waterlogging_tolerance="Low",
        soil_ph_min=5.5, soil_ph_max=7.5,
        suitable_soil_textures=["Sandy", "Sandy-Loam", "Loam"],
        nutrient_requirements={"N": "Low", "P": "Low", "K": "Low"},
        regional_suitability={
            "PUNE": 0.70, "SOLAPUR": 0.75, "NASHIK": 0.72,
            "AHMEDNAGAR": 0.73, "AURANGABAD": 0.75, "JALGAON": 0.70,
            "SANGLI": 0.72, "KOLHAPUR": 0.68, "SATARA": 0.70, "LATUR": 0.75
        },
        successful_regions=["SOLAPUR", "AURANGABAD", "LATUR"],
        seasons=["Kharif"],
        varieties=["SiA-3156", "Prasad", "Lepakshi"],
        typical_yield_kg_per_ha=1000,
        market_demand="Moderate"
    ),
    
    # Pulses
    CropInfo(
        crop_id="MOONG_01",
        common_name="Green Gram (Moong)",
        scientific_name="Vigna radiata",
        duration_days=70,
        duration_range=(65, 75),
        temp_min=20, temp_optimal_min=25, temp_optimal_max=35, temp_max=40,
        water_requirement_mm=350,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Sandy-Loam", "Loam", "Clay-Loam"],
        nutrient_requirements={"N": "Low", "P": "Medium", "K": "Medium"},
        regional_suitability={
            "PUNE": 0.82, "SOLAPUR": 0.85, "NASHIK": 0.80,
            "AHMEDNAGAR": 0.83, "AURANGABAD": 0.85, "JALGAON": 0.82,
            "SANGLI": 0.80, "KOLHAPUR": 0.75, "SATARA": 0.78, "LATUR": 0.85
        },
        successful_regions=["SOLAPUR", "AURANGABAD", "AHMEDNAGAR", "LATUR"],
        seasons=["Kharif", "Rabi"],
        varieties=["Pusa-105", "SML-668", "IPM-02-3"],
        typical_yield_kg_per_ha=800,
        market_demand="High"
    ),
    
    CropInfo(
        crop_id="URAD_01",
        common_name="Black Gram (Urad)",
        scientific_name="Vigna mungo",
        duration_days=75,
        duration_range=(70, 80),
        temp_min=20, temp_optimal_min=25, temp_optimal_max=35, temp_max=40,
        water_requirement_mm=400,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=6.5, soil_ph_max=7.5,
        suitable_soil_textures=["Loam", "Clay-Loam", "Sandy-Loam"],
        nutrient_requirements={"N": "Low", "P": "Medium", "K": "Medium"},
        regional_suitability={
            "PUNE": 0.78, "SOLAPUR": 0.80, "NASHIK": 0.75,
            "AHMEDNAGAR": 0.78, "AURANGABAD": 0.80, "JALGAON": 0.77,
            "SANGLI": 0.75, "KOLHAPUR": 0.72, "SATARA": 0.75, "LATUR": 0.80
        },
        successful_regions=["SOLAPUR", "AURANGABAD", "AHMEDNAGAR"],
        seasons=["Kharif"],
        varieties=["TAU-1", "PU-31", "LBG-752"],
        typical_yield_kg_per_ha=700,
        market_demand="High"
    ),
    
    CropInfo(
        crop_id="COWPEA_01",
        common_name="Cowpea",
        scientific_name="Vigna unguiculata",
        duration_days=75,
        duration_range=(70, 80),
        temp_min=20, temp_optimal_min=25, temp_optimal_max=35, temp_max=40,
        water_requirement_mm=400,
        drought_tolerance="High",
        waterlogging_tolerance="Moderate",
        soil_ph_min=5.5, soil_ph_max=7.5,
        suitable_soil_textures=["Sandy", "Sandy-Loam", "Loam", "Clay-Loam"],
        nutrient_requirements={"N": "Low", "P": "Medium", "K": "Medium"},
        regional_suitability={
            "PUNE": 0.80, "SOLAPUR": 0.82, "NASHIK": 0.78,
            "AHMEDNAGAR": 0.80, "AURANGABAD": 0.82, "JALGAON": 0.80,
            "SANGLI": 0.78, "KOLHAPUR": 0.75, "SATARA": 0.77, "LATUR": 0.82
        },
        successful_regions=["SOLAPUR", "AURANGABAD", "JALGAON"],
        seasons=["Kharif"],
        varieties=["Pusa-578", "Arka-Garima", "Kashi-Kanchan"],
        typical_yield_kg_per_ha=900,
        market_demand="Moderate"
    ),
    
    CropInfo(
        crop_id="GUAR_01",
        common_name="Cluster Bean (Guar)",
        scientific_name="Cyamopsis tetragonoloba",
        duration_days=85,
        duration_range=(80, 90),
        temp_min=20, temp_optimal_min=25, temp_optimal_max=35, temp_max=42,
        water_requirement_mm=350,
        drought_tolerance="High",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=8.5,
        suitable_soil_textures=["Sandy", "Sandy-Loam", "Loam"],
        nutrient_requirements={"N": "Low", "P": "Medium", "K": "Medium"},
        regional_suitability={
            "PUNE": 0.75, "SOLAPUR": 0.85, "NASHIK": 0.70,
            "AHMEDNAGAR": 0.78, "AURANGABAD": 0.82, "JALGAON": 0.72,
            "SANGLI": 0.75, "KOLHAPUR": 0.65, "SATARA": 0.70, "LATUR": 0.85
        },
        successful_regions=["SOLAPUR", "AURANGABAD", "LATUR"],
        seasons=["Kharif"],
        varieties=["RGC-1066", "HG-563", "Pusa-Navbahar"],
        typical_yield_kg_per_ha=1200,
        market_demand="Moderate"
    ),
    
    # Oilseeds
    CropInfo(
        crop_id="SESAME_01",
        common_name="Sesame (Til)",
        scientific_name="Sesamum indicum",
        duration_days=85,
        duration_range=(80, 90),
        temp_min=20, temp_optimal_min=25, temp_optimal_max=35, temp_max=40,
        water_requirement_mm=400,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=5.5, soil_ph_max=8.0,
        suitable_soil_textures=["Sandy-Loam", "Loam", "Clay-Loam"],
        nutrient_requirements={"N": "Medium", "P": "Medium", "K": "Medium"},
        regional_suitability={
            "PUNE": 0.75, "SOLAPUR": 0.78, "NASHIK": 0.72,
            "AHMEDNAGAR": 0.75, "AURANGABAD": 0.77, "JALGAON": 0.73,
            "SANGLI": 0.75, "KOLHAPUR": 0.70, "SATARA": 0.72, "LATUR": 0.78
        },
        successful_regions=["SOLAPUR", "AURANGABAD", "AHMEDNAGAR"],
        seasons=["Kharif", "Rabi"],
        varieties=["Phule-Til", "N-32", "TKG-22"],
        typical_yield_kg_per_ha=600,
        market_demand="High"
    ),
    
    CropInfo(
        crop_id="SUNFLOWER_01",
        common_name="Sunflower (Short-duration)",
        scientific_name="Helianthus annuus",
        duration_days=85,
        duration_range=(80, 90),
        temp_min=15, temp_optimal_min=20, temp_optimal_max=30, temp_max=35,
        water_requirement_mm=500,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam", "Clay-Loam", "Sandy-Loam"],
        nutrient_requirements={"N": "High", "P": "High", "K": "High"},
        regional_suitability={
            "PUNE": 0.80, "SOLAPUR": 0.75, "NASHIK": 0.82,
            "AHMEDNAGAR": 0.80, "AURANGABAD": 0.75, "JALGAON": 0.80,
            "SANGLI": 0.78, "KOLHAPUR": 0.82, "SATARA": 0.80, "LATUR": 0.73
        },
        successful_regions=["PUNE", "NASHIK", "KOLHAPUR", "SATARA"],
        seasons=["Kharif", "Rabi"],
        varieties=["KBSH-44", "Phule-Bhaskar", "DRSH-1"],
        typical_yield_kg_per_ha=1500,
        market_demand="High"
    ),
    
    CropInfo(
        crop_id="SOYBEAN_01",
        common_name="Soybean (Early variety)",
        scientific_name="Glycine max",
        duration_days=85,
        duration_range=(80, 90),
        temp_min=20, temp_optimal_min=25, temp_optimal_max=30, temp_max=35,
        water_requirement_mm=500,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Moderate",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam", "Clay-Loam", "Sandy-Loam"],
        nutrient_requirements={"N": "Low", "P": "High", "K": "High"},
        regional_suitability={
            "PUNE": 0.78, "SOLAPUR": 0.72, "NASHIK": 0.80,
            "AHMEDNAGAR": 0.77, "AURANGABAD": 0.73, "JALGAON": 0.82,
            "SANGLI": 0.75, "KOLHAPUR": 0.80, "SATARA": 0.78, "LATUR": 0.70
        },
        successful_regions=["JALGAON", "NASHIK", "KOLHAPUR"],
        seasons=["Kharif"],
        varieties=["JS-335", "MAUS-71", "Phule-Kalyani"],
        typical_yield_kg_per_ha=1800,
        market_demand="High"
    ),
    
    # Vegetables
    CropInfo(
        crop_id="TOMATO_01",
        common_name="Tomato (Short-duration)",
        scientific_name="Solanum lycopersicum",
        duration_days=75,
        duration_range=(70, 80),
        temp_min=15, temp_optimal_min=20, temp_optimal_max=28, temp_max=35,
        water_requirement_mm=600,
        drought_tolerance="Low",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.0,
        suitable_soil_textures=["Loam", "Sandy-Loam", "Clay-Loam"],
        nutrient_requirements={"N": "High", "P": "High", "K": "High"},
        regional_suitability={
            "PUNE": 0.85, "SOLAPUR": 0.70, "NASHIK": 0.88,
            "AHMEDNAGAR": 0.80, "AURANGABAD": 0.72, "JALGAON": 0.82,
            "SANGLI": 0.78, "KOLHAPUR": 0.85, "SATARA": 0.83, "LATUR": 0.68
        },
        successful_regions=["PUNE", "NASHIK", "KOLHAPUR", "SATARA"],
        seasons=["Kharif", "Rabi"],
        varieties=["Abhinav", "Pusa-Ruby", "Arka-Vikas"],
        typical_yield_kg_per_ha=25000,
        market_demand="High"
    ),
    
    CropInfo(
        crop_id="BRINJAL_01",
        common_name="Brinjal (Eggplant)",
        scientific_name="Solanum melongena",
        duration_days=80,
        duration_range=(75, 85),
        temp_min=18, temp_optimal_min=22, temp_optimal_max=30, temp_max=38,
        water_requirement_mm=550,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=5.5, soil_ph_max=7.0,
        suitable_soil_textures=["Loam", "Sandy-Loam", "Clay-Loam"],
        nutrient_requirements={"N": "High", "P": "High", "K": "High"},
        regional_suitability={
            "PUNE": 0.82, "SOLAPUR": 0.75, "NASHIK": 0.85,
            "AHMEDNAGAR": 0.80, "AURANGABAD": 0.75, "JALGAON": 0.82,
            "SANGLI": 0.80, "KOLHAPUR": 0.85, "SATARA": 0.82, "LATUR": 0.72
        },
        successful_regions=["PUNE", "NASHIK", "KOLHAPUR", "SATARA"],
        seasons=["Kharif", "Rabi"],
        varieties=["Pusa-Purple-Long", "Arka-Shirish", "Phule-Prakash"],
        typical_yield_kg_per_ha=20000,
        market_demand="High"
    ),
    
    CropInfo(
        crop_id="OKRA_01",
        common_name="Okra (Bhindi)",
        scientific_name="Abelmoschus esculentus",
        duration_days=70,
        duration_range=(65, 75),
        temp_min=20, temp_optimal_min=25, temp_optimal_max=35, temp_max=40,
        water_requirement_mm=500,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam", "Sandy-Loam", "Clay-Loam"],
        nutrient_requirements={"N": "High", "P": "Medium", "K": "Medium"},
        regional_suitability={
            "PUNE": 0.80, "SOLAPUR": 0.78, "NASHIK": 0.82,
            "AHMEDNAGAR": 0.80, "AURANGABAD": 0.78, "JALGAON": 0.82,
            "SANGLI": 0.80, "KOLHAPUR": 0.82, "SATARA": 0.80, "LATUR": 0.75
        },
        successful_regions=["PUNE", "NASHIK", "JALGAON", "KOLHAPUR"],
        seasons=["Kharif", "Rabi"],
        varieties=["Pusa-Sawani", "Arka-Anamika", "Phule-Utkarsha"],
        typical_yield_kg_per_ha=12000,
        market_demand="High"
    ),
    
    CropInfo(
        crop_id="BOTTLEGOURD_01",
        common_name="Bottle Gourd (Lauki)",
        scientific_name="Lagenaria siceraria",
        duration_days=75,
        duration_range=(70, 80),
        temp_min=18, temp_optimal_min=22, temp_optimal_max=32, temp_max=38,
        water_requirement_mm=550,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Moderate",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam", "Sandy-Loam", "Clay-Loam"],
        nutrient_requirements={"N": "High", "P": "Medium", "K": "Medium"},
        regional_suitability={
            "PUNE": 0.78, "SOLAPUR": 0.72, "NASHIK": 0.80,
            "AHMEDNAGAR": 0.77, "AURANGABAD": 0.73, "JALGAON": 0.80,
            "SANGLI": 0.75, "KOLHAPUR": 0.80, "SATARA": 0.78, "LATUR": 0.70
        },
        successful_regions=["PUNE", "NASHIK", "JALGAON", "KOLHAPUR"],
        seasons=["Kharif", "Rabi"],
        varieties=["Pusa-Summer-Prolific-Long", "Arka-Bahar", "Samrat"],
        typical_yield_kg_per_ha=18000,
        market_demand="Moderate"
    )
]


class CropDatabase:
    """
    Manages crop information and provides querying functionality.
    """
    
    def __init__(self):
        """Initialize crop database."""
        self.crops: Dict[str, CropInfo] = {}
        self._load_crops()
    
    def _load_crops(self) -> None:
        """Load crops into database."""
        for crop in CROPS_DATA:
            self.crops[crop.crop_id] = crop
        logger.info(f"Loaded {len(self.crops)} crops into database")
    
    def get_crop(self, crop_id: str) -> Optional[CropInfo]:
        """Get crop by ID."""
        return self.crops.get(crop_id)
    
    def get_all_crops(self) -> List[CropInfo]:
        """Get all crops."""
        return list(self.crops.values())
    
    def get_crops_by_season(self, season: str) -> List[CropInfo]:
        """Get crops suitable for a season."""
        return [crop for crop in self.crops.values() if crop.is_suitable_for_season(season)]
    
    def get_crops_by_region(self, region_id: str, threshold: float = 0.3) -> List[CropInfo]:
        """Get crops suitable for a region."""
        return [crop for crop in self.crops.values() if crop.is_suitable_for_region(region_id, threshold)]
    
    def filter_by_soil(self, crops: List[CropInfo], soil: SoilInfo, min_score: float = 50.0) -> List[CropInfo]:
        """
        Filter crops by soil compatibility.
        
        Args:
            crops: List of crops to filter
            soil: Soil information
            min_score: Minimum compatibility score (0-100)
            
        Returns:
            List of compatible crops
        """
        compatible_crops = []
        for crop in crops:
            score = calculate_soil_compatibility_score(crop, soil)
            if score >= min_score:
                compatible_crops.append(crop)
        return compatible_crops
    
    def get_crops_with_soil_scores(self, crops: List[CropInfo], soil: SoilInfo) -> List[tuple]:
        """
        Get crops with their soil compatibility scores.
        
        Args:
            crops: List of crops
            soil: Soil information
            
        Returns:
            List of tuples (crop, score, amendments)
        """
        results = []
        for crop in crops:
            score = calculate_soil_compatibility_score(crop, soil)
            amendments = get_soil_amendment_suggestions(crop, soil)
            results.append((crop, score, amendments))
        return sorted(results, key=lambda x: x[1], reverse=True)
    
    def get_short_duration_crops(self, min_days: int = 70, max_days: int = 90) -> List[CropInfo]:
        """Get short-duration crops (70-90 days)."""
        return [crop for crop in self.crops.values() if crop.is_short_duration(min_days, max_days)]
    
    def get_crop_count(self) -> int:
        """Get total number of crops."""
        return len(self.crops)


# Global crop database instance
crop_db = CropDatabase()
