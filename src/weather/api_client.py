import requests
import logging

from weather.models import WeatherData

logger = logging.getLogger('inkFrame')

def get_weather_data(config, api_key):
    location = config['weather']['location']
    logger.info(f'Fetching weather for {location}')
    try:
        data = requests.get(f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=no', timeout=10)
        logger.debug(f'API response status: {data.status_code}')
        json_data = data.json()
        weather_obj = WeatherData.from_json(json_data)
        logger.debug(f"Weather data fetched for {location}")
        return weather_obj
    except requests.exceptions.RequestException as error:
        logger.error(f'API request failed {error}')
        return None

if __name__ == "__main__":
    from config import load_config

    secret = load_config('config/secrets.yaml')
    api_key = secret['weather_api_key']
    weather = get_weather_data('Sydney', api_key)

    print(weather.name)
    print(weather.temp)