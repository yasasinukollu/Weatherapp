import requests
from datetime import datetime, timedelta
import pandas as pd


def fetch_open_meteo(start_date, end_date, latitude=17.3850, longitude=78.4867):
    """
    Fetch historical weather data from the Open-Meteo API.

    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        latitude (float): Latitude of the location (default: Hyderabad).
        longitude (float): Longitude of the location (default: Hyderabad).

    Returns:
        dict: JSON response containing hourly weather data.

    Raises:
        requests.RequestException: If the API request fails.
    """
    url = (
        "https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={latitude}&longitude={longitude}"
        f"&start_date={start_date}&end_date={end_date}"
        "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,"
        "wind_direction_10m,pressure_msl,precipitation,cloudcover,weathercode"
        "&timezone=Asia%2FKolkata"
    )
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_initial_data(years=3):
    """
    Fetch initial weather data for the past specified number of years.

    Args:
        years (int): Number of years to fetch data for (default: 3).

    Returns:
        pd.DataFrame: DataFrame with initial weather data.
    """
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=365 * years)
    data = fetch_open_meteo(start_date.isoformat(), end_date.isoformat())
    df = pd.DataFrame(data['hourly'])
    df['time'] = pd.to_datetime(df['time'])
    return df


def get_new_data(last_end_date):
    """
    Fetch new weather data from the day after the last end date to the current date.

    Args:
        last_end_date (str): Last fetched end date in 'YYYY-MM-DD' format.

    Returns:
        pd.DataFrame: DataFrame with new weather data, empty if no new data available.
    """
    last_date = datetime.strptime(last_end_date, '%Y-%m-%d')
    start_date = (last_date + timedelta(days=1)).date().isoformat()
    end_date = datetime.utcnow().date().isoformat()
    if start_date >= end_date:
        return pd.DataFrame()
    data = fetch_open_meteo(start_date, end_date)
    df = pd.DataFrame(data['hourly'])
    df['time'] = pd.to_datetime(df['time'])
    return df
