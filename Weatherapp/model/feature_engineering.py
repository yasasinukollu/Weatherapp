import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder


def encode_weather_condition(df: pd.DataFrame):
    """
    Label encode the weather_condition column.

    Args:
        df (pd.DataFrame): DataFrame containing 'weather_condition' column.
    """
    if 'weather_condition' in df.columns:
        le = LabelEncoder()
        df['weather_condition_encoded'] = le.fit_transform(df['weather_condition'])

    return df, le

def encode_datetime_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract and cyclically encode datetime features.

    Args:
        df (pd.DataFrame): DataFrame with 'date_time' column.

    Returns:
        pd.DataFrame: DataFrame with new time-based features.
    """
    df['date_time'] = pd.to_datetime(df['date_time'])
    df['hour'] = df['date_time'].dt.hour
    df['dayofweek'] = df['date_time'].dt.dayofweek

    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['dayofweek_sin'] = np.sin(2 * np.pi * df['dayofweek'] / 7)
    df['dayofweek_cos'] = np.cos(2 * np.pi * df['dayofweek'] / 7)
    return df


def add_rolling_features(df: pd.DataFrame, window: int = 3) -> pd.DataFrame:
    """
    Add rolling mean features for selected numeric columns.

    Args:
        df (pd.DataFrame): Input DataFrame.
        window (int): Window size for rolling mean.

    Returns:
        pd.DataFrame: DataFrame with new rolling mean features.
    """
    rolling_cols = ['temperature', 'humidity', 'pressure', 'wind_speed']
    for col in rolling_cols:
        if col in df.columns:
            df[f'{col}_rolling_mean_{window}'] = df[col].rolling(window=window).mean()
    return df


def feature_engineering_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply full feature engineering pipeline.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with engineered features.
    """
    df, le = encode_weather_condition(df)
    df = encode_datetime_features(df)
    df = add_rolling_features(df)
    return df,le
