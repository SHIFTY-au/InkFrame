import yaml
from PIL import Image
import logging

logger = logging.getLogger('inkFrame')

class DisplayDriver:
    def __init__(self, config):
        mode = config.get('mock_mode', False)
        if isinstance(mode, bool):
            self.mock_mode = mode
            logger.info(f"DisplayDriver initialized (mock_mode={self.mock_mode})")
        else:
            logger.error("Invalid value for 'mock_mode' in config; must be boolean.")
            raise ValueError("mock_mode must be set to True or False")

    def show(self, img):
        if self.mock_mode:
            try:
                img.save('logs/display_output.png')
                logger.info("Saved display output to logs/display_output.png")
            except Exception as e:
                logger.error(f"Failed to save display output: {e}")
        else:
            logger.info("Sending image to physical display.")
            # HARDWARE MODE - Raspberry Pi with Waveshare 7.5" V2 e-ink display only
            # Requires: pip install waveshare-epd (installed on Pi, not Windows)
            try:
                from waveshare_epd import epd7in5_V2
                if not hasattr(self, 'epd'):
                    self.epd = epd7in5_V2.EPD()
                    self.epd.init()
                    logger.info("E-ink display initialized")
                
                self.epd.display(self.epd.getbuffer(img))
                logger.info("Image sent to e-ink hardware")
            except ImportError:
                logger.error("waveshare_epd library not found - install on Raspberry Pi")
            except Exception as e:
                logger.error(f"Display hardware error: {e}")


if __name__ == "__main__":
    from weather.api_client import get_weather_data
    from display.renderer import render_weather

    logger.info("Running DisplayDriver as script.")
    weather = get_weather_data('Penrith,NSW,AU')
    current_mode = DisplayDriver(yaml.safe_load(open('config/app.yaml', 'r')))
    image = render_weather(weather)
    current_mode.show(img=image)