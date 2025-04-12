import os
from datetime import timedelta

import numpy as np
import pandas as pd
import xgboost as xgb
import pickle


def create_lagged_features(df, lags=24):
    """
    Create lagged features for time series forecasting.

    Args:
        df (pd.DataFrame): Preprocessed weather data.
        lags (int): Number of lagged timesteps to create (default: 24).

    Returns:
        pd.DataFrame: DataFrame with lagged features added.
    """
    print(df['weathercode'])
    for i in range(1, lags + 1):
        for col in ['temperature', 'weathercode']:
            df[f'{col}_lag{i}'] = df[col].shift(i)
    return df


def prepare_data(df, target_col, remove_cols):
    """
    Prepare features and target variables for model training.

    Args:
        df (pd.DataFrame): DataFrame with lagged features.
        target_col (str): Name of the target column ('temperature' or 'weathercode').

    Returns:
        tuple: (X, y) where X is the feature DataFrame and y is the target Series.
    """
    if remove_cols:
        numeric_cols = df.select_dtypes(include=['number']).columns
        features = [col for col in numeric_cols if col != target_col]
    else:
        features = [col for col in df.columns if col not in ['date_time', target_col]]

    X = df[features]
    y = df[target_col]
    return X, y


def train_regression_model(X, y):
    """
    Train a regression model for temperature forecasting.

    Args:
        X (pd.DataFrame): Feature DataFrame.
        y (pd.Series): Target Series (temperature).

    Returns:
        XGBRegressor: Trained regression model.
    """
    model = xgb.XGBRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model


def train_classification_model(X, y, label_encoder):
    """
    Train a classification model for weather condition prediction.
    """
    for col in X.columns:
        if X[col].dtype == 'object':
            X[col] = X[col].astype('category').cat.codes

    model = xgb.XGBClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    def reverse_encode_predictions(encoded_predictions):
        return label_encoder.inverse_transform(encoded_predictions)

    return model, reverse_encode_predictions


def save_model(model, filename, features_filename, feature_list):
    """
    Save a trained model to a file using pickle.

    Args:
        model: Trained model object.
        filename (str): Path to save the model file.
    """
    artifacts_dir = 'artifacts'
    os.makedirs(artifacts_dir, exist_ok=True)

    model_path = os.path.join(artifacts_dir, filename)

    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {model_path}")

    feats_path = os.path.join(artifacts_dir, features_filename)
    with open(feats_path, 'wb') as f:
        pickle.dump(feature_list, f)
    print(f"Feature list saved to {feats_path}")


def predict_next_step(df, reg_model, clf_model, le, lags=24):
    """
    Predicts next hour's temperature and weather condition, appends to DataFrame.
    Leaves other feature columns as NaN.

    Args:
        df (pd.DataFrame): Historical weather data (raw format).
        reg_model (XGBRegressor): Trained regression model.
        clf_model (XGBClassifier): Trained classification model.
        le (LabelEncoder): For decoding weather condition.
        lags (int): Number of lags to use.

    Returns:
        pd.DataFrame: df with a new row for next hour containing predicted values.
    """
    import numpy as np

    last_row = df.iloc[-1:].copy()
    next_dt = last_row['date_time'].iloc[0] + timedelta(hours=1)

    # Load feature lists
    with open("artifacts/temperature_features.pkl", "rb") as f:
        temp_feature_list = pickle.load(f)
    with open("artifacts/condition_features.pkl", "rb") as f:
        cond_feature_list = pickle.load(f)

    # Ensure all features exist in last_row and convert to numeric
    Xp_temp = last_row.reindex(columns=temp_feature_list)
    Xp_cond = last_row.reindex(columns=cond_feature_list)

    # Drop object dtype columns (or convert them if necessary)
    Xp_temp = Xp_temp.select_dtypes(include=[np.number]).fillna(0)
    print(cond_feature_list)
    if 'weather_condition' in cond_feature_list:
        if last_row['weather_condition'].dtype == object:
            encoded_value = le.transform([last_row['weather_condition'].iloc[0]])[0]
            last_row.loc[:, 'weather_condition'] = encoded_value

    last_row['weather_condition'] = last_row['weather_condition'].astype('category')

    # Predict
    predicted_temperature = reg_model.predict(Xp_temp)[0]

    # Construct new row
    new_row = {
        'date_time': next_dt,
        'temperature': predicted_temperature,
    }

    for col in df.columns:
        if col not in new_row:
            new_row[col] = np.nan
    new_row_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_row_df], ignore_index=True)
    float_columns = df.select_dtypes(include=['float64']).columns
    df[float_columns] = df[float_columns].round(4)

    df = df[['date_time', 'temperature', 'humidity', 'wind_speed', 'wind_direction', 'pressure', 'cloud_coverage',
             'weather_condition']]
    df['date_time'] = pd.to_datetime(df['date_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df['date_time'] = pd.to_datetime(df['date_time'], errors='coerce')  # Coerce invalid dates to NaT (Not a Time)
    df = df.dropna(subset=['date_time'])  # Drop rows where 'date_time' is invalid
    df = df.drop_duplicates(subset='date_time', keep='last')

    return df
