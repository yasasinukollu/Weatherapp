import pandas as pd

CODE_MAP = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
    55: "Dense drizzle", 56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain", 66: "Light freezing rain",
    67: "Heavy freezing rain", 71: "Slight snow fall", 73: "Moderate snow fall",
    75: "Heavy snow fall", 77: "Snow grains", 80: "Slight rain showers",
    81: "Moderate rain showers", 82: "Violent rain showers", 85: "Slight snow showers",
    86: "Heavy snow showers", 95: "Thunderstorm", 96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

historical_data = {
    'temperature': [49.5, 6.1],
    'humidity': [100, 0],
    'wind_speed': [145, 0],
    'cloud_coverage': [100, 0],
    'pressure': [1045, 900],
    'precipitation': [500, 0],
}


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess raw weather data by renaming columns, mapping weather codes,
    handling missing values, and correcting outliers.

    Args:
        df (pd.DataFrame): Raw weather data DataFrame.

    Returns:
        pd.DataFrame: Cleaned and preprocessed weather data.
    """
    df = df.rename(columns={
        'time': 'date_time',
        'temperature_2m': 'temperature',
        'relative_humidity_2m': 'humidity',
        'wind_speed_10m': 'wind_speed',
        'wind_direction_10m': 'wind_direction',
        'pressure_msl': 'pressure',
        'cloudcover': 'cloud_coverage'
    })
    df['weather_condition'] = df['weathercode'].map(CODE_MAP).fillna("Unknown")
    df = handle_missing_values(df)
    df = handle_outliers(df)

    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Impute missing values using column-specific strategies:
    - Mode for cloud_coverage
    - Zero for precipitation
    - Exponential moving average for temperature, humidity, pressure

    Args:
        df (pd.DataFrame): DataFrame with missing values.

    Returns:
        pd.DataFrame: DataFrame with missing values imputed.
    """
    if 'cloud_coverage' in df.columns:
        df['cloud_coverage'].fillna(df['cloud_coverage'].mode()[0], inplace=True)

    if 'precipitation' in df.columns:
        df['precipitation'].fillna(0, inplace=True)

    smooth_cols = ['temperature', 'humidity', 'pressure']
    for col in smooth_cols:
        if col in df.columns:
            df[col] = df[col].ewm(span=5, adjust=False).mean()

    return df


def handle_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace outliers in weather-related numerical columns based on historical thresholds.
    Values outside the valid range are replaced with the column's median.

    Args:
        df (pd.DataFrame): DataFrame to process for outliers.

    Returns:
        pd.DataFrame: DataFrame with outliers corrected.
    """
    for column in historical_data:
        max_val, min_val = historical_data[column]
        outlier_mask = (df[column] < min_val) | (df[column] > max_val)
        median_val = df[column].median()
        df.loc[outlier_mask, column] = median_val
    return df
