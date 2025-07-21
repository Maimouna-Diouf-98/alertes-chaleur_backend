import requests
import os
from dotenv import load_dotenv

load_dotenv()  # charge les variables d'environnement depuis .env

API_KEY = os.getenv('OPENWEATHER_API_KEY')

def get_weather_by_city(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    return response.json()

def get_forecast_by_city_and_date(city, target_date):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    target_str = target_date.strftime('%Y-%m-%d')
    forecasts = [item for item in data['list'] if item['dt_txt'].startswith(target_str)]
    return forecasts[0] if forecasts else None