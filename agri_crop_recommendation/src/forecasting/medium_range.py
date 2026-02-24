import numpy as np

def forecast_days_17_90(weather_df, planning_days=90):
    """
    Estimate weather conditions for days 17–90 using climatology
    """

    # Short-term signals (Days 1–16)
    avg_temp = weather_df["temp_avg"].mean()
    temp_trend = weather_df["temp_avg"].iloc[-5:].mean() - weather_df["temp_avg"].iloc[:5].mean()

    avg_daily_rain = weather_df["rainfall"].mean()
    dry_spell_risk = weather_df["dry_spell_days"].max()

    # --- Temperature estimation ---
    temp_adjustment = 1.0 if temp_trend > 0 else -1.0 if temp_trend < 0 else 0
    expected_temp = avg_temp + temp_adjustment

    # --- Rainfall estimation ---
    if avg_daily_rain < 0.5:
        avg_daily_rain = 1.5   # conservative climatological fallback

    expected_rainfall = avg_daily_rain * planning_days

    return {
        "expected_avg_temp": round(float(expected_temp), 2),
        "expected_rainfall_mm": round(float(expected_rainfall), 1),
        "dry_spell_risk": (
            "High" if dry_spell_risk > 7 else
            "Moderate" if dry_spell_risk > 4 else
            "Low"
        )
    }
