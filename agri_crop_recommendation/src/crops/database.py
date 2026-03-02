"""
Comprehensive Crop Knowledge Base for Indian Agriculture

Contains short-duration crops (15-90 days) with detailed information including
temperature requirements, water needs, soil compatibility, and regional suitability
for all major Indian agricultural regions.
"""

from typing import Dict, List, Optional
from src.crops.models import CropInfo
from src.crops.soil import SoilInfo, calculate_soil_compatibility_score, get_soil_amendment_suggestions
import logging

logger = logging.getLogger(__name__)


# ── Zone → Region ID mapping (for nationwide suitability coverage) ──────────
# Each zone maps to key representative region IDs from regions.json.
# Suitability 0.75 is assigned whenever a crop's zone matches.
# Regions not in this dict get the recommender's 0.65 fallback.
ZONE_REGIONS = {
    "North": [
        "UP_LUCKNOW","UP_VARANASI","UP_AGRA","UP_KANPUR","UP_ALLAHABAD",
        "UP_MEERUT","UP_BAREILLY","UP_GORAKHPUR","UP_MORADABAD","UP_ALIGARH",
        "PB_LUDHIANA","PB_AMRITSAR","PB_JALANDHAR","PB_PATIALA",
        "HR_AMBALA","HR_HISAR","HR_KARNAL","HR_ROHTAK",
        "RJ_JAIPUR","RJ_JODHPUR","RJ_UDAIPUR","RJ_AJMER","RJ_BIKANER",
        "HP_SHIMLA","HP_KANGRA","UK_DEHRADUN","UK_HARIDWAR",
        "DL_NEW_DELHI","JK_JAMMU","JK_SRINAGAR",
    ],
    "South": [
        "KA_BENGALURU","KA_MYSURU","KA_HUBLI","KA_DHARWAD","KA_BELAGAVI",
        "TN_CHENNAI","TN_COIMBATORE","TN_MADURAI","TN_TIRUNELVELI",
        "AP_VISAKHAPATNAM","AP_GUNTUR","AP_KRISHNA","AP_KURNOOL","AP_CHITTOOR",
        "TS_HYDERABAD","TS_WARANGAL","TS_NIZAMABAD","TS_KARIMNAGAR",
        "KL_THIRUVANANTHAPURAM","KL_KOZHIKODE","KL_THRISSUR",
    ],
    "West": [
        "MH_PUNE","MH_NASHIK","MH_AURANGABAD","MH_SOLAPUR","MH_KOLHAPUR",
        "MH_NAGPUR","MH_AHMEDNAGAR","MH_LATUR","MH_JALGAON","MH_SATARA",
        "GJ_AHMEDABAD","GJ_SURAT","GJ_VADODARA","GJ_RAJKOT","GJ_ANAND",
        "GJ_MEHSANA","GJ_JUNAGADH","GJ_BHARUCH",
        "RJ_JODHPUR","RJ_BIKANER",
    ],
    "East": [
        "WB_KOLKATA","WB_HOWRAH","WB_BURDWAN","WB_NADIA","WB_MURSHIDABAD",
        "WB_MALDA","WB_PURBA_MEDINIPUR","WB_PASCHIM_MEDINIPUR",
        "BR_PATNA","BR_MUZAFFARPUR","BR_GAYA","BR_BHAGALPUR","BR_DARBHANGA",
        "OD_BHUBANESWAR","OD_CUTTACK","OD_PURI","OD_SAMBALPUR",
        "JH_RANCHI","JH_DHANBAD","JH_JAMSHEDPUR",
    ],
    "Central": [
        "MP_BHOPAL","MP_INDORE","MP_GWALIOR","MP_JABALPUR","MP_UJJAIN",
        "CG_RAIPUR","CG_BILASPUR","CG_DURG","CG_RAJNANDGAON",
        "MH_NAGPUR","MH_AURANGABAD","MH_LATUR",
    ],
    "Northeast": [
        "AS_KAMRUP","AS_NAGAON","AS_DIBRUGARH","AS_JORHAT","AS_BARPETA",
        "AR_PAPUM_PARE","AR_LOHIT",
    ],
}


def _zone_suitability(zones: list) -> dict:
    """Build regional_suitability dict from zone list at 0.75 score."""
    result = {}
    for zone in zones:
        for region_id in ZONE_REGIONS.get(zone, []):
            result[region_id] = 0.75
    return result


# Comprehensive crop database with 50+ short-duration crops (15-90 days)
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
    ),

    # ── SHORT-CYCLE CROPS (15–90 days) ─────────────────────────────────────

    # ── Leafy Greens (15–45 days) ──
    CropInfo(
        crop_id="SPINACH_01",
        common_name="Spinach",
        scientific_name="Spinacia oleracea",
        duration_days=30,
        duration_range=(20, 40),
        temp_min=5, temp_optimal_min=15, temp_optimal_max=20, temp_max=30,
        water_requirement_mm=300,
        drought_tolerance="Low",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam", "Clay", "Clay-Loam"],
        nutrient_requirements={"N": "High", "P": "Medium", "K": "Medium"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South"]),
        successful_regions=["UP_LUCKNOW","PB_LUDHIANA","HR_AMBALA","RJ_JAIPUR"],
        seasons=["Rabi","Kharif","Zaid"],
        varieties=["Pusa-Bharati","Palak-No-1","Virginia-Savoy"],
        typical_yield_kg_per_ha=9000,
        market_demand="High",
        growing_tip="Sow seeds 1–2 cm deep in rows 20 cm apart. Irrigate every 5–7 days. Best in cool weather (15–20°C)."
    ),

    CropInfo(
        crop_id="FENUGREEK_01",
        common_name="Fenugreek (Methi)",
        scientific_name="Trigonella foenum-graecum",
        duration_days=28,
        duration_range=(20, 35),
        temp_min=10, temp_optimal_min=15, temp_optimal_max=25, temp_max=35,
        water_requirement_mm=200,
        drought_tolerance="High",
        waterlogging_tolerance="Low",
        soil_ph_min=5.5, soil_ph_max=8.0,
        suitable_soil_textures=["Loam","Sandy","Clay","Sandy-Loam"],
        nutrient_requirements={"N": "Low", "P": "Low", "K": "Low"},
        regional_suitability=_zone_suitability(["North","Central","West","South"]),
        successful_regions=["RJ_JAIPUR","GJ_AHMEDABAD","MP_INDORE","HR_HISAR"],
        seasons=["Rabi","Kharif","Zaid"],
        varieties=["Pusa-Early-Bunching","Kasuri-Methi","RMT-1"],
        typical_yield_kg_per_ha=7000,
        market_demand="High",
        growing_tip="Broadcast seeds and mix lightly with soil. First cutting in 20–25 days. Needs less water than most greens."
    ),

    CropInfo(
        crop_id="CORIANDER_01",
        common_name="Coriander (Dhaniya)",
        scientific_name="Coriandrum sativum",
        duration_days=35,
        duration_range=(25, 45),
        temp_min=10, temp_optimal_min=15, temp_optimal_max=25, temp_max=30,
        water_requirement_mm=200,
        drought_tolerance="High",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=8.0,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam","Clay-Loam"],
        nutrient_requirements={"N": "Low", "P": "Low", "K": "Low"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South","Northeast"]),
        successful_regions=["RJ_JAIPUR","MP_INDORE","GJ_AHMEDABAD","AP_GUNTUR"],
        seasons=["Rabi","Kharif","Zaid"],
        varieties=["CS-6","RCr-41","Pant-Haritima"],
        typical_yield_kg_per_ha=6000,
        market_demand="High",
        growing_tip="Split seeds before sowing for better germination. Sow in rows 20 cm apart. Avoid waterlogging."
    ),

    CropInfo(
        crop_id="AMARANTH_01",
        common_name="Amaranth (Chaulai)",
        scientific_name="Amaranthus tricolor",
        duration_days=32,
        duration_range=(20, 45),
        temp_min=15, temp_optimal_min=25, temp_optimal_max=35, temp_max=42,
        water_requirement_mm=200,
        drought_tolerance="High",
        waterlogging_tolerance="Low",
        soil_ph_min=5.5, soil_ph_max=8.0,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam","Clay"],
        nutrient_requirements={"N": "Low", "P": "Low", "K": "Low"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South","Northeast"]),
        successful_regions=["UP_LUCKNOW","MP_BHOPAL","KA_BENGALURU","WB_KOLKATA"],
        seasons=["Kharif","Zaid","Rabi"],
        varieties=["Pusa-Kiran","Pusa-Lal-Chaulai","Suvarna"],
        typical_yield_kg_per_ha=10000,
        market_demand="Moderate",
        growing_tip="Very hardy crop. Broadcast seeds thinly. Grows well in hot weather (25–35°C). First harvest in 20 days."
    ),

    CropInfo(
        crop_id="MUSTARD_GREENS_01",
        common_name="Mustard Greens (Sarson Saag)",
        scientific_name="Brassica juncea",
        duration_days=32,
        duration_range=(25, 40),
        temp_min=5, temp_optimal_min=10, temp_optimal_max=25, temp_max=30,
        water_requirement_mm=350,
        drought_tolerance="Low",
        waterlogging_tolerance="Moderate",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Clay","Clay-Loam"],
        nutrient_requirements={"N": "High", "P": "Medium", "K": "Medium"},
        regional_suitability=_zone_suitability(["North","Central","East"]),
        successful_regions=["PB_LUDHIANA","HR_AMBALA","UP_LUCKNOW","BR_PATNA"],
        seasons=["Rabi"],
        varieties=["Pusa-Saag-1","LC-1","PBM-1"],
        typical_yield_kg_per_ha=12000,
        market_demand="High",
        growing_tip="Sow in October–November. Grows best at 10–25°C. Very popular in Punjab, Haryana, UP."
    ),

    CropInfo(
        crop_id="LETTUCE_01",
        common_name="Lettuce",
        scientific_name="Lactuca sativa",
        duration_days=38,
        duration_range=(30, 45),
        temp_min=7, temp_optimal_min=12, temp_optimal_max=20, temp_max=28,
        water_requirement_mm=300,
        drought_tolerance="Low",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.0,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam"],
        nutrient_requirements={"N": "Medium", "P": "Medium", "K": "Medium"},
        regional_suitability=_zone_suitability(["North","South","West","Northeast"]),
        successful_regions=["HP_SHIMLA","UK_DEHRADUN","KA_BENGALURU","TN_OOTY"],
        seasons=["Rabi","Zaid"],
        varieties=["Iceberg","Romaine","Pusa-Rohini"],
        typical_yield_kg_per_ha=8000,
        market_demand="Moderate",
        growing_tip="Transplant seedlings 25 cm apart. Prefers cool weather. Harvest outer leaves for continuous yield."
    ),

    # ── Vegetables (25–90 days) ──
    CropInfo(
        crop_id="RADISH_01",
        common_name="Radish (Mooli)",
        scientific_name="Raphanus sativus",
        duration_days=35,
        duration_range=(25, 45),
        temp_min=5, temp_optimal_min=10, temp_optimal_max=22, temp_max=30,
        water_requirement_mm=300,
        drought_tolerance="Low",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Sandy","Sandy-Loam","Loam"],
        nutrient_requirements={"N": "Medium", "P": "Medium", "K": "High"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South"]),
        successful_regions=["UP_LUCKNOW","PB_LUDHIANA","HR_AMBALA","MP_INDORE"],
        seasons=["Rabi","Kharif","Zaid"],
        varieties=["Pusa-Desi","Pusa-Chetki","Japanese-White"],
        typical_yield_kg_per_ha=22000,
        market_demand="High",
        growing_tip="Sow seeds 1 cm deep in rows 30 cm apart. Thin to 8 cm spacing. Harvest when roots are 15–20 cm long."
    ),

    CropInfo(
        crop_id="SPRING_ONION_01",
        common_name="Green Onion (Spring Onion)",
        scientific_name="Allium fistulosum",
        duration_days=40,
        duration_range=(30, 50),
        temp_min=8, temp_optimal_min=15, temp_optimal_max=25, temp_max=35,
        water_requirement_mm=350,
        drought_tolerance="Low",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam","Clay-Loam"],
        nutrient_requirements={"N": "High", "P": "Medium", "K": "Medium"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South"]),
        successful_regions=["MH_NASHIK","GJ_AHMEDABAD","UP_LUCKNOW","WB_NADIA"],
        seasons=["Rabi","Kharif","Zaid"],
        varieties=["Improved-Japanese-Bunching","White-Lisboa","Pusa-White-Round"],
        typical_yield_kg_per_ha=13000,
        market_demand="High",
        growing_tip="Plant sets or seedlings 10 cm apart. Harvest when tops are 15–20 cm tall. Grows in most Indian regions."
    ),

    CropInfo(
        crop_id="CARROT_01",
        common_name="Carrot (Gajar)",
        scientific_name="Daucus carota",
        duration_days=75,
        duration_range=(60, 90),
        temp_min=7, temp_optimal_min=15, temp_optimal_max=22, temp_max=30,
        water_requirement_mm=400,
        drought_tolerance="Low",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Sandy","Sandy-Loam","Loam"],
        nutrient_requirements={"N": "Medium", "P": "High", "K": "High"},
        regional_suitability=_zone_suitability(["North","Central","East","South"]),
        successful_regions=["PB_LUDHIANA","HP_SHIMLA","UP_LUCKNOW","KA_BENGALURU"],
        seasons=["Rabi"],
        varieties=["Pusa-Kesar","Pusa-Meghali","Nantes"],
        typical_yield_kg_per_ha=25000,
        market_demand="High",
        growing_tip="Sow seeds in well-drained, deep, loose soil. Thin seedlings to 5 cm apart. Avoid heavy clay soil."
    ),

    CropInfo(
        crop_id="TURNIP_01",
        common_name="Turnip (Shalgam)",
        scientific_name="Brassica rapa",
        duration_days=60,
        duration_range=(45, 75),
        temp_min=5, temp_optimal_min=10, temp_optimal_max=20, temp_max=28,
        water_requirement_mm=350,
        drought_tolerance="Low",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Sandy","Clay"],
        nutrient_requirements={"N": "Medium", "P": "Medium", "K": "Medium"},
        regional_suitability=_zone_suitability(["North","Central","East"]),
        successful_regions=["PB_LUDHIANA","UP_LUCKNOW","HR_AMBALA","BR_PATNA"],
        seasons=["Rabi"],
        varieties=["Purple-Top-White-Globe","Snowball","PTSWG"],
        typical_yield_kg_per_ha=17000,
        market_demand="Moderate",
        growing_tip="Sow in October–November. Harvest when roots are 5–8 cm in diameter. Grows best in cool spells."
    ),

    CropInfo(
        crop_id="BEETROOT_01",
        common_name="Beetroot (Chukandar)",
        scientific_name="Beta vulgaris",
        duration_days=62,
        duration_range=(55, 70),
        temp_min=8, temp_optimal_min=15, temp_optimal_max=25, temp_max=32,
        water_requirement_mm=400,
        drought_tolerance="Low",
        waterlogging_tolerance="Low",
        soil_ph_min=6.5, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam"],
        nutrient_requirements={"N": "Medium", "P": "Medium", "K": "High"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South"]),
        successful_regions=["MH_PUNE","KA_BENGALURU","HP_SHIMLA","UP_LUCKNOW"],
        seasons=["Rabi","Zaid"],
        varieties=["Detroit-Dark-Red","Crimson-Globe","Pusa-Madhuram"],
        typical_yield_kg_per_ha=22000,
        market_demand="Moderate",
        growing_tip="Soak seeds overnight before sowing. Thin to 10 cm apart. Prefers slightly alkaline soil (pH 6.5–7.5)."
    ),

    CropInfo(
        crop_id="CUCUMBER_01",
        common_name="Cucumber (Kheera)",
        scientific_name="Cucumis sativus",
        duration_days=50,
        duration_range=(40, 60),
        temp_min=18, temp_optimal_min=20, temp_optimal_max=30, temp_max=38,
        water_requirement_mm=600,
        drought_tolerance="Low",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam","Clay-Loam"],
        nutrient_requirements={"N": "High", "P": "High", "K": "High"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South","Northeast"]),
        successful_regions=["UP_LUCKNOW","MH_PUNE","WB_KOLKATA","KA_BENGALURU"],
        seasons=["Kharif","Zaid"],
        varieties=["Pusa-Uday","Pant-Shankar-Kheera-1","Arka-Sheetal"],
        typical_yield_kg_per_ha=17000,
        market_demand="High",
        growing_tip="Sow 2–3 seeds per hill, 60 cm apart. Needs warm weather (20–30°C). Provide support for vine growth."
    ),

    CropInfo(
        crop_id="RIDGE_GOURD_01",
        common_name="Ridge Gourd (Torai)",
        scientific_name="Luffa acutangula",
        duration_days=55,
        duration_range=(45, 65),
        temp_min=20, temp_optimal_min=25, temp_optimal_max=35, temp_max=40,
        water_requirement_mm=450,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam","Clay-Loam"],
        nutrient_requirements={"N": "High", "P": "Medium", "K": "Medium"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South","Northeast"]),
        successful_regions=["WB_KOLKATA","UP_LUCKNOW","MH_PUNE","KA_BENGALURU"],
        seasons=["Kharif","Zaid"],
        varieties=["Pusa-Nasdar","Arka-Sumeet","CO-1"],
        typical_yield_kg_per_ha=13000,
        market_demand="Moderate",
        growing_tip="Sow on raised beds with trellis support. Harvest young fruits when ridges are distinct for best taste."
    ),

    CropInfo(
        crop_id="BITTER_GOURD_01",
        common_name="Bitter Gourd (Karela)",
        scientific_name="Momordica charantia",
        duration_days=60,
        duration_range=(50, 70),
        temp_min=20, temp_optimal_min=25, temp_optimal_max=35, temp_max=40,
        water_requirement_mm=450,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam","Clay-Loam"],
        nutrient_requirements={"N": "Medium", "P": "Medium", "K": "Medium"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South","Northeast"]),
        successful_regions=["UP_LUCKNOW","MH_PUNE","WB_KOLKATA","AP_GUNTUR"],
        seasons=["Kharif","Zaid"],
        varieties=["Pusa-Do-Mausami","Arka-Harit","Priya"],
        typical_yield_kg_per_ha=11000,
        market_demand="High",
        growing_tip="Soak seeds 24 hours before sowing. Grow on trellis. Harvest when fruits are green and firm."
    ),

    CropInfo(
        crop_id="FRENCH_BEANS_01",
        common_name="French Beans",
        scientific_name="Phaseolus vulgaris",
        duration_days=52,
        duration_range=(45, 60),
        temp_min=12, temp_optimal_min=15, temp_optimal_max=25, temp_max=32,
        water_requirement_mm=400,
        drought_tolerance="Low",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam"],
        nutrient_requirements={"N": "Low", "P": "High", "K": "Medium"},
        regional_suitability=_zone_suitability(["North","South","West","Northeast"]),
        successful_regions=["HP_SHIMLA","UK_DEHRADUN","KA_BENGALURU","MH_PUNE"],
        seasons=["Kharif","Rabi"],
        varieties=["Contender","Arka-Komal","Pusa-Parvati"],
        typical_yield_kg_per_ha=9000,
        market_demand="High",
        growing_tip="Sow seeds 5 cm deep, 10 cm apart in rows 45 cm apart. Harvest when pods snap cleanly."
    ),

    CropInfo(
        crop_id="CLUSTER_BEANS_01",
        common_name="Cluster Beans (Gwar — vegetable)",
        scientific_name="Cyamopsis tetragonoloba",
        duration_days=52,
        duration_range=(45, 60),
        temp_min=20, temp_optimal_min=25, temp_optimal_max=35, temp_max=42,
        water_requirement_mm=250,
        drought_tolerance="High",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=8.5,
        suitable_soil_textures=["Sandy","Sandy-Loam","Loam"],
        nutrient_requirements={"N": "Low", "P": "Medium", "K": "Medium"},
        regional_suitability=_zone_suitability(["North","West","Central"]),
        successful_regions=["RJ_JAIPUR","GJ_AHMEDABAD","HR_HISAR","UP_AGRA"],
        seasons=["Kharif"],
        varieties=["Pusa-Navbahar","HG-563","RGC-936"],
        typical_yield_kg_per_ha=6000,
        market_demand="Moderate",
        growing_tip="Drought-resistant crop. Ideal for Rajasthan, Gujarat, Haryana. Sow with monsoon onset."
    ),

    CropInfo(
        crop_id="CAPSICUM_01",
        common_name="Capsicum (Bell Pepper)",
        scientific_name="Capsicum annuum var. grossum",
        duration_days=75,
        duration_range=(60, 90),
        temp_min=15, temp_optimal_min=18, temp_optimal_max=28, temp_max=35,
        water_requirement_mm=500,
        drought_tolerance="Low",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.0,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam","Clay-Loam"],
        nutrient_requirements={"N": "High", "P": "High", "K": "High"},
        regional_suitability=_zone_suitability(["North","South","West","Central"]),
        successful_regions=["HP_SHIMLA","KA_BENGALURU","MH_PUNE","TN_COIMBATORE"],
        seasons=["Kharif","Rabi"],
        varieties=["California-Wonder","Arka-Gaurav","Bombay"],
        typical_yield_kg_per_ha=20000,
        market_demand="High",
        growing_tip="Transplant 5–6 week seedlings. Mulch to retain moisture. Harvest when fruits are firm and full-sized."
    ),

    CropInfo(
        crop_id="GREEN_CHILLI_01",
        common_name="Green Chilli",
        scientific_name="Capsicum annuum",
        duration_days=62,
        duration_range=(50, 75),
        temp_min=15, temp_optimal_min=20, temp_optimal_max=30, temp_max=38,
        water_requirement_mm=450,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam","Clay-Loam"],
        nutrient_requirements={"N": "High", "P": "Medium", "K": "High"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South","Northeast"]),
        successful_regions=["AP_GUNTUR","TS_HYDERABAD","KA_BENGALURU","MH_NASHIK"],
        seasons=["Kharif","Rabi","Zaid"],
        varieties=["Pusa-Jwala","NP-46","Arka-Meghna"],
        typical_yield_kg_per_ha=11000,
        market_demand="High",
        growing_tip="Transplant 40-day seedlings. Space 45×30 cm. Multiple pickings possible. Major crop in Andhra, Telangana."
    ),

    CropInfo(
        crop_id="SPONGE_GOURD_01",
        common_name="Sponge Gourd (Nenua)",
        scientific_name="Luffa cylindrica",
        duration_days=52,
        duration_range=(45, 60),
        temp_min=18, temp_optimal_min=25, temp_optimal_max=35, temp_max=40,
        water_requirement_mm=450,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam","Clay-Loam"],
        nutrient_requirements={"N": "High", "P": "Medium", "K": "Medium"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South"]),
        successful_regions=["UP_LUCKNOW","WB_KOLKATA","MH_PUNE","KA_BENGALURU"],
        seasons=["Kharif","Zaid"],
        varieties=["Pusa-Sneha","Arka-Sumeet","CO-1"],
        typical_yield_kg_per_ha=12000,
        market_demand="Moderate",
        growing_tip="Sow on raised beds. Provide trellis support. Harvest young tender fruits. Very popular summer vegetable."
    ),

    CropInfo(
        crop_id="PUMPKIN_01",
        common_name="Pumpkin (Kaddu)",
        scientific_name="Cucurbita moschata",
        duration_days=82,
        duration_range=(75, 90),
        temp_min=18, temp_optimal_min=22, temp_optimal_max=32, temp_max=38,
        water_requirement_mm=500,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam","Clay-Loam"],
        nutrient_requirements={"N": "High", "P": "High", "K": "High"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South"]),
        successful_regions=["UP_LUCKNOW","WB_KOLKATA","MH_PUNE","OD_BHUBANESWAR"],
        seasons=["Kharif","Zaid"],
        varieties=["Pusa-Alankar","Arka-Suryamukhi","IARI-Selection"],
        typical_yield_kg_per_ha=25000,
        market_demand="Moderate",
        growing_tip="Sow on raised beds, 2 m apart. Train vines. Harvest when fruit sounds hollow when tapped."
    ),

    # ── Pulses & Legumes (45–90 days) ──
    CropInfo(
        crop_id="MOONG_DAL_01",
        common_name="Moong Dal (Green Gram — quick)",
        scientific_name="Vigna radiata",
        duration_days=67,
        duration_range=(60, 75),
        temp_min=20, temp_optimal_min=25, temp_optimal_max=35, temp_max=40,
        water_requirement_mm=350,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam","Clay-Loam"],
        nutrient_requirements={"N": "Low", "P": "Medium", "K": "Medium"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South"]),
        successful_regions=["UP_LUCKNOW","MP_BHOPAL","RJ_JAIPUR","AP_GUNTUR"],
        seasons=["Kharif","Zaid"],
        varieties=["Pusa-105","SML-668","IPM-02-3"],
        typical_yield_kg_per_ha=1000,
        market_demand="High",
        growing_tip="Sow at 30×10 cm spacing. Drought-tolerant. Fixes nitrogen in soil. Excellent intercrop."
    ),

    CropInfo(
        crop_id="URAD_DAL_01",
        common_name="Urad Dal (Black Gram — quick)",
        scientific_name="Vigna mungo",
        duration_days=77,
        duration_range=(65, 90),
        temp_min=20, temp_optimal_min=25, temp_optimal_max=35, temp_max=40,
        water_requirement_mm=350,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=6.5, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Clay-Loam","Sandy-Loam","Clay"],
        nutrient_requirements={"N": "Low", "P": "Medium", "K": "Medium"},
        regional_suitability=_zone_suitability(["North","Central","East","South"]),
        successful_regions=["UP_LUCKNOW","MP_BHOPAL","BR_PATNA","AP_GUNTUR"],
        seasons=["Kharif"],
        varieties=["TAU-1","PU-31","LBG-752"],
        typical_yield_kg_per_ha=750,
        market_demand="High",
        growing_tip="Sow with onset of monsoon. Avoid waterlogged fields. Good rotation crop with cereals."
    ),

    CropInfo(
        crop_id="COWPEA_VEG_01",
        common_name="Cowpea (Lobia — vegetable pods)",
        scientific_name="Vigna unguiculata",
        duration_days=75,
        duration_range=(60, 90),
        temp_min=20, temp_optimal_min=25, temp_optimal_max=35, temp_max=40,
        water_requirement_mm=350,
        drought_tolerance="High",
        waterlogging_tolerance="Low",
        soil_ph_min=5.5, soil_ph_max=7.5,
        suitable_soil_textures=["Sandy","Loam","Sandy-Loam"],
        nutrient_requirements={"N": "Low", "P": "Medium", "K": "Medium"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South","Northeast"]),
        successful_regions=["RJ_JAIPUR","GJ_AHMEDABAD","UP_LUCKNOW","WB_KOLKATA"],
        seasons=["Kharif","Zaid"],
        varieties=["Pusa-578","Arka-Garima","Kashi-Kanchan"],
        typical_yield_kg_per_ha=1200,
        market_demand="Moderate",
        growing_tip="Heat and drought tolerant. Grows in poor soils. Green pods ready in 60 days, dry grain in 90 days."
    ),

    CropInfo(
        crop_id="MASOOR_01",
        common_name="Masoor (Red Lentil)",
        scientific_name="Lens culinaris",
        duration_days=85,
        duration_range=(80, 90),
        temp_min=7, temp_optimal_min=15, temp_optimal_max=25, temp_max=30,
        water_requirement_mm=250,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Clay","Clay-Loam"],
        nutrient_requirements={"N": "Low", "P": "Medium", "K": "Low"},
        regional_suitability=_zone_suitability(["North","Central","East"]),
        successful_regions=["UP_VARANASI","MP_BHOPAL","BR_PATNA","UP_LUCKNOW"],
        seasons=["Rabi"],
        varieties=["Pant-L-406","IPL-81","K-75"],
        typical_yield_kg_per_ha=1000,
        market_demand="High",
        growing_tip="Sow in October–November. Needs cool dry weather. Minimal irrigation needed. Good for UP, MP, Bihar."
    ),

    # ── Quick Herbs & Spices ──
    CropInfo(
        crop_id="MINT_01",
        common_name="Mint (Pudina)",
        scientific_name="Mentha spicata",
        duration_days=22,
        duration_range=(15, 30),
        temp_min=10, temp_optimal_min=18, temp_optimal_max=28, temp_max=35,
        water_requirement_mm=600,
        drought_tolerance="Low",
        waterlogging_tolerance="Moderate",
        soil_ph_min=6.0, soil_ph_max=7.0,
        suitable_soil_textures=["Loam","Sandy","Clay","Sandy-Loam"],
        nutrient_requirements={"N": "High", "P": "Medium", "K": "Medium"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South","Northeast"]),
        successful_regions=["UP_LUCKNOW","PB_LUDHIANA","HR_AMBALA","MP_INDORE"],
        seasons=["Kharif","Rabi","Zaid"],
        varieties=["Kosi","Saksham","MAS-1"],
        typical_yield_kg_per_ha=22000,
        market_demand="High",
        growing_tip="Plant root cuttings or runners. Spreads quickly. Keep soil moist. Multiple harvests per season."
    ),

    CropInfo(
        crop_id="DILL_01",
        common_name="Dill (Sowa / Suva)",
        scientific_name="Anethum graveolens",
        duration_days=32,
        duration_range=(25, 40),
        temp_min=8, temp_optimal_min=15, temp_optimal_max=25, temp_max=32,
        water_requirement_mm=200,
        drought_tolerance="High",
        waterlogging_tolerance="Low",
        soil_ph_min=5.8, soil_ph_max=7.5,
        suitable_soil_textures=["Sandy","Loam","Sandy-Loam"],
        nutrient_requirements={"N": "Low", "P": "Low", "K": "Low"},
        regional_suitability=_zone_suitability(["North","Central","West","South"]),
        successful_regions=["GJ_AHMEDABAD","RJ_JAIPUR","MP_INDORE","HR_KARNAL"],
        seasons=["Rabi","Zaid"],
        varieties=["Sowa","Suva","Local"],
        typical_yield_kg_per_ha=6000,
        market_demand="Moderate",
        growing_tip="Broadcast seeds and cover lightly. Grows fast in cool weather. Popular in Gujarat, Rajasthan."
    ),

    CropInfo(
        crop_id="CURRY_LEAVES_01",
        common_name="Curry Leaves (Kari Patta)",
        scientific_name="Murraya koenigii",
        duration_days=45,
        duration_range=(30, 60),
        temp_min=15, temp_optimal_min=20, temp_optimal_max=30, temp_max=38,
        water_requirement_mm=250,
        drought_tolerance="High",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Sandy","Sandy-Loam","Loam"],
        nutrient_requirements={"N": "Low", "P": "Low", "K": "Low"},
        regional_suitability=_zone_suitability(["South","West","Central","East"]),
        successful_regions=["TN_CHENNAI","KA_BENGALURU","MH_PUNE","AP_GUNTUR"],
        seasons=["Kharif","Rabi","Zaid"],
        varieties=["Gamthi","Senkaambu","Regular"],
        typical_yield_kg_per_ha=5000,
        market_demand="High",
        growing_tip="Plant stem cuttings. Once established, harvest leaves repeatedly. Thrives in South India's climate."
    ),

    # ── Quick Root & Tuber ──
    CropInfo(
        crop_id="BABY_POTATO_01",
        common_name="Baby Potato (Early variety)",
        scientific_name="Solanum tuberosum",
        duration_days=75,
        duration_range=(60, 90),
        temp_min=7, temp_optimal_min=15, temp_optimal_max=22, temp_max=28,
        water_requirement_mm=500,
        drought_tolerance="Low",
        waterlogging_tolerance="Low",
        soil_ph_min=5.5, soil_ph_max=7.0,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam"],
        nutrient_requirements={"N": "High", "P": "High", "K": "High"},
        regional_suitability=_zone_suitability(["North","Central","East","Northeast"]),
        successful_regions=["UP_AGRA","PB_JALANDHAR","HP_SHIMLA","WB_BURDWAN"],
        seasons=["Rabi"],
        varieties=["Kufri-Pukhraj","Kufri-Jyoti","Kufri-Chipsona"],
        typical_yield_kg_per_ha=20000,
        market_demand="High",
        growing_tip="Plant Kufri Pukhraj or Kufri Jyoti for early harvest. Ridge planting. Harvest when plant starts yellowing."
    ),

    # ── Quick Cereals & Others ──
    CropInfo(
        crop_id="BABY_CORN_01",
        common_name="Baby Corn",
        scientific_name="Zea mays (baby corn type)",
        duration_days=57,
        duration_range=(50, 65),
        temp_min=18, temp_optimal_min=22, temp_optimal_max=32, temp_max=40,
        water_requirement_mm=450,
        drought_tolerance="Moderate",
        waterlogging_tolerance="Low",
        soil_ph_min=6.0, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Sandy-Loam","Clay-Loam"],
        nutrient_requirements={"N": "High", "P": "High", "K": "High"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South"]),
        successful_regions=["PB_LUDHIANA","HR_AMBALA","UP_LUCKNOW","KA_BENGALURU"],
        seasons=["Kharif","Zaid","Rabi"],
        varieties=["HM-4","VL-42","Pusa-HM-4"],
        typical_yield_kg_per_ha=8000,
        market_demand="High",
        growing_tip="Use high-density planting (75,000 plants/ha). Harvest within 1–3 days of silk emergence. High market value."
    ),

    CropInfo(
        crop_id="MICROGREENS_01",
        common_name="Microgreens / Sprouts",
        scientific_name="Various (tray-grown)",
        duration_days=11,
        duration_range=(7, 15),
        temp_min=15, temp_optimal_min=18, temp_optimal_max=24, temp_max=30,
        water_requirement_mm=50,
        drought_tolerance="Low",
        waterlogging_tolerance="Low",
        soil_ph_min=5.5, soil_ph_max=7.5,
        suitable_soil_textures=["Loam","Sandy","Sandy-Loam","Clay","Clay-Loam"],
        nutrient_requirements={"N": "Low", "P": "Low", "K": "Low"},
        regional_suitability=_zone_suitability(["North","Central","West","East","South","Northeast"]),
        successful_regions=["DL_NEW_DELHI","MH_PUNE","KA_BENGALURU","TN_CHENNAI"],
        seasons=["Kharif","Rabi","Zaid"],
        varieties=["Radish","Sunflower","Pea","Fenugreek"],
        typical_yield_kg_per_ha=0,
        market_demand="High",
        growing_tip="Grow on trays with coco peat. Harvest in 7–14 days. Very high value in urban markets. Minimal space needed."
    ),

    CropInfo(
        crop_id="DRUMSTICK_LEAVES_01",
        common_name="Drumstick Leaves (Moringa)",
        scientific_name="Moringa oleifera",
        duration_days=40,
        duration_range=(20, 60),
        temp_min=15, temp_optimal_min=25, temp_optimal_max=35, temp_max=42,
        water_requirement_mm=250,
        drought_tolerance="High",
        waterlogging_tolerance="Low",
        soil_ph_min=6.3, soil_ph_max=7.5,
        suitable_soil_textures=["Sandy","Sandy-Loam","Loam"],
        nutrient_requirements={"N": "Low", "P": "Low", "K": "Low"},
        regional_suitability=_zone_suitability(["South","West","Central","East"]),
        successful_regions=["TN_COIMBATORE","KA_BENGALURU","AP_GUNTUR","MH_PUNE"],
        seasons=["Kharif","Rabi","Zaid"],
        varieties=["PKM-1","PKM-2","Dhanraj"],
        typical_yield_kg_per_ha=7000,
        market_demand="High",
        growing_tip="Plant stem cuttings for quick growth. Leaves harvestable from 20 days. Extremely nutritious. Drought tolerant."
    ),
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
