import logging
import sys
from config import load_config
from weather.api_client import get_weather_data
from display.renderer import render_weather
from display.driver import DisplayDriver
from app_logging.logger import setup_logging
from system.scheduler import RefreshScheduler

def main(force=False):
    setup_logging()
    logger = logging.getLogger('inkFrame')
    logger.info("InkFrame Weather App Starting.")
    
    config = load_config('config/app.yaml')
    scheduler = RefreshScheduler(config)
    secret = load_config('config/secrets.yaml')
    api_key = secret['weather_api_key']

    if scheduler.should_refresh() or force:
        weather_data = get_weather_data(config, api_key)
        if not weather_data:
            logger.error('Failed to fetch weather data. Exiting.')
            sys.exit(1)
        image = render_weather(weather_data, config)
        driver = DisplayDriver(config)
        driver.show(image)
        scheduler.record_refresh()
    else:
        logger.info("Refresh not needed yet")
        return
    
if __name__ == '__main__':
    main()