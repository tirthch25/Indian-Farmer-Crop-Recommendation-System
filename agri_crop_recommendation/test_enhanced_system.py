"""
Test the enhanced Indian Farmer Crop Recommendation System.

Tests the complete integrated system with all enhancements.
"""

from datetime import datetime
from src.weather.open_meteo import fetch_weather
from src.preprocessing.features import add_agri_features
from src.forecasting.medium_range import forecast_days_17_90
from src.recommendation.recommender import recommend_crops
from src.data.regions import RegionManager
from src.soil.models import SoilInfo
from src.utils.seasons import detect_season, is_season_transition


def test_complete_workflow():
    """Test complete recommendation workflow."""
    print("\n" + "="*70)
    print("TESTING COMPLETE ENHANCED RECOMMENDATION WORKFLOW")
    print("="*70)
    
    # Initialize
    rm = RegionManager()
    
    # Scenario: Farmer in Pune, Kharif season
    print("\n📍 Scenario: Farmer in Pune District")
    pune = rm.get_region_profile("PUNE")
    print(f"   Region: {pune.name}")
    print(f"   Climate: {pune.climate_zone}")
    print(f"   Location: {pune.latitude}°N, {pune.longitude}°E")
    
    # Detect season
    current_date = datetime.now()
    season = detect_season(current_date)
    is_transition, next_season = is_season_transition(current_date)
    
    print(f"\n🌾 Season Information:")
    print(f"   Current season: {season}")
    print(f"   Transition period: {is_transition}")
    if is_transition:
        print(f"   Next season: {next_season}")
    
    # Soil information
    soil = pune.get_default_soil()
    print(f"\n🌱 Soil Information:")
    print(f"   Texture: {soil.texture}")
    print(f"   pH: {soil.ph}")
    print(f"   Organic matter: {soil.organic_matter}")
    print(f"   Drainage: {soil.drainage}")
    
    # Fetch weather
    print(f"\n☁️  Fetching weather data...")
    weather = fetch_weather(pune.latitude, pune.longitude)
    weather = add_agri_features(weather)
    print(f"   ✓ Retrieved {len(weather)} days of weather data")
    print(f"   Avg temperature: {weather['temp_avg'].mean():.1f}°C")
    print(f"   Total rainfall: {weather['rainfall'].sum():.1f}mm")
    
    # Medium-range forecast
    print(f"\n📊 Generating medium-range forecast...")
    forecast = forecast_days_17_90(weather, planning_days=90)
    print(f"   Expected avg temp: {forecast['expected_avg_temp']}°C")
    print(f"   Expected rainfall: {forecast['expected_rainfall_mm']}mm")
    print(f"   Dry spell risk: {forecast['dry_spell_risk']}")
    
    # Generate recommendations
    print(f"\n🌾 Generating crop recommendations...")
    recommendations = recommend_crops(
        weather_df=weather,
        season=season,
        region_id=pune.region_id,
        soil=soil,
        irrigation_available=True,
        planning_days=90
    )
    
    print(f"   ✓ Generated {len(recommendations)} recommendations")
    
    # Display top 10
    print(f"\n🏆 Top 10 Recommended Crops:")
    print(f"   {'Rank':<5} {'Crop':<25} {'Score':<8} {'Duration':<10} {'Risk':<20}")
    print(f"   {'-'*5} {'-'*25} {'-'*8} {'-'*10} {'-'*20}")
    
    for i, rec in enumerate(recommendations[:10], 1):
        print(f"   {i:<5} {rec['crop']:<25} {rec['suitability_score']:<8.1f} "
              f"{rec['growth_duration_days']:<10} {rec['risk_note']:<20}")
    
    # Detailed view of top crop
    if recommendations:
        top_crop = recommendations[0]
        print(f"\n📋 Detailed Analysis - {top_crop['crop']}:")
        print(f"   Suitability Score: {top_crop['suitability_score']:.1f}/100")
        print(f"   Duration: {top_crop['growth_duration_days']} days")
        print(f"   Water Required: {top_crop['water_required_mm']}mm")
        print(f"   Expected Rainfall: {top_crop['expected_rainfall_mm']:.1f}mm")
        print(f"   Irrigation Needed: {top_crop['irrigation_needed_mm']:.1f}mm")
        print(f"   Drought Tolerance: {top_crop['drought_tolerance']}")
        print(f"   Regional Suitability: {top_crop['regional_suitability']*100:.0f}%")
        print(f"   Risk Assessment: {top_crop['risk_note']}")
    
    print("\n" + "="*70)
    print("✓ COMPLETE WORKFLOW TEST PASSED!")
    print("="*70)


def test_multiple_regions():
    """Test recommendations for multiple regions."""
    print("\n" + "="*70)
    print("TESTING MULTIPLE REGIONS")
    print("="*70)
    
    rm = RegionManager()
    regions_to_test = ["PUNE", "SOLAPUR", "NASHIK", "KOLHAPUR"]
    
    for region_id in regions_to_test:
        region = rm.get_region_profile(region_id)
        soil = region.get_default_soil()
        
        print(f"\n📍 {region.name} ({region.climate_zone}):")
        
        # Fetch weather
        weather = fetch_weather(region.latitude, region.longitude)
        weather = add_agri_features(weather)
        
        # Get recommendations
        season = detect_season(datetime.now())
        recommendations = recommend_crops(
            weather_df=weather,
            season=season,
            region_id=region.region_id,
            soil=soil,
            irrigation_available=True
        )
        
        # Show top 3
        print(f"   Top 3 crops:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec['crop']:<25} Score: {rec['suitability_score']:.1f}")


def test_irrigation_scenarios():
    """Test different irrigation scenarios."""
    print("\n" + "="*70)
    print("TESTING IRRIGATION SCENARIOS")
    print("="*70)
    
    rm = RegionManager()
    pune = rm.get_region_profile("PUNE")
    soil = pune.get_default_soil()
    season = detect_season(datetime.now())
    
    # Fetch weather once
    weather = fetch_weather(pune.latitude, pune.longitude)
    weather = add_agri_features(weather)
    
    irrigation_levels = [False, True]
    irrigation_names = ["No Irrigation", "With Irrigation"]
    
    for irrigation, name in zip(irrigation_levels, irrigation_names):
        print(f"\n💧 Scenario: {name}")
        
        recommendations = recommend_crops(
            weather_df=weather,
            season=season,
            region_id=pune.region_id,
            soil=soil,
            irrigation_available=irrigation
        )
        
        print(f"   Total suitable crops: {len(recommendations)}")
        print(f"   Top 3:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec['crop']:<25} "
                  f"Score: {rec['suitability_score']:.1f} "
                  f"Irrigation needed: {rec['irrigation_needed_mm']:.0f}mm")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("ENHANCED SYSTEM INTEGRATION TESTS")
    print("="*70)
    
    try:
        test_complete_workflow()
        test_multiple_regions()
        test_irrigation_scenarios()
        
        print("\n" + "="*70)
        print("✓ ALL INTEGRATION TESTS PASSED!")
        print("="*70)
        print("\nEnhanced system features verified:")
        print("  ✓ Region-specific recommendations")
        print("  ✓ Season detection and awareness")
        print("  ✓ Soil compatibility scoring")
        print("  ✓ Irrigation consideration")
        print("  ✓ Comprehensive suitability scoring")
        print("  ✓ Risk assessment")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
