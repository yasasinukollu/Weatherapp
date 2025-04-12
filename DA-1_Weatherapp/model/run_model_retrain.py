from model.data_fetcher import get_initial_data
from model.data_preprocessor import preprocess_data
from model.feature_engineering import feature_engineering_pipeline
from model.model_retrain_automation import (create_lagged_features, prepare_data, train_regression_model,
                                            train_classification_model, save_model, predict_next_step)


def run_model_retrain():
    """
    Initialize the weather forecasting system and start the scheduler.
    """
    df = get_initial_data(years=3)
    df = preprocess_data(df)
    df, le = feature_engineering_pipeline(df)
    print(df)
    df.to_csv('weather_data.csv', index=False)

    df_lagged = create_lagged_features(df)
    df_lagged.dropna(inplace=True)

    X_reg, y_reg = prepare_data(df_lagged, 'temperature', True)
    print(X_reg, y_reg)
    model_reg = train_regression_model(X_reg, y_reg)
    feature_list = X_reg.columns.tolist()
    save_model(model_reg, 'temperature_model.pkl', 'temperature_features.pkl', feature_list)

    X_cls, y_cls = prepare_data(df_lagged, 'weather_condition_encoded', False)
    model_cls, reverse_encoder = train_classification_model(X_cls, y_cls, le)
    feature_list = X_cls.columns.tolist()
    save_model(model_cls, 'condition_model.pkl', 'condition_features.pkl', feature_list)

    df_with_predictions = predict_next_step(df, model_reg, model_cls, le, lags=24)
    df_with_predictions = df_with_predictions.iloc[:, :9]
    df_with_predictions.to_csv('weather_data_with_predictions.csv', index=False)
    print("Prediction added and saved.")


