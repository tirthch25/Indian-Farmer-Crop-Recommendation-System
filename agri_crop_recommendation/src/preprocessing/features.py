import pandas as pd
import numpy as np

def add_agri_features(df, base_temp=10):
    """
    Add agriculture-specific features to weather data
    """

    df = df.copy()

    # Average temperature
    df["temp_avg"] = (df["temp_max"] + df["temp_min"]) / 2

    # Growing Degree Days (GDD)
    df["gdd"] = np.maximum(df["temp_avg"] - base_temp, 0)

    # Rolling rainfall (7-day)
    df["rainfall_7d"] = df["rainfall"].rolling(window=7, min_periods=1).sum()

    # Dry spell indicator (rain < 2 mm)
    df["dry_day"] = df["rainfall"] < 2

    # Consecutive dry days
    df["dry_spell_days"] = (
        df["dry_day"]
        .astype(int)
        .groupby((df["dry_day"] != df["dry_day"].shift()).cumsum())
        .cumsum()
    )

    return df
