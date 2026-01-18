import PIL
import logging

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger('inkFrame')

def get_icon(condition_text):
    lookup = {
        'Sunny': 'sunny.png',
        'Partly Cloudy': 'partly_cloudy.png',
        'Cloudy': 'cloudy.png',
        'Overcast': 'overcast.png',
        'Mist': '',
        'Patchy rain nearby': 'showers.png',
        'Patchy snow nearby': '',
        'Patchy sleet nearby': '',
        'Patchy drizzle nearby': '',
        'Thundery outbreaks in nearby': 'storm.png',
        'Blowing snow': '',
        'Blizzard': '',
        'Fog': 'fog.png',
        'Freezing Fog': '',
        'Patchy light drizzle': 'showers.png',
        'Light drizzle': 'showers.png',
        'Freezing drizzle': '',
        'Heavy freezing drizzle': '',
        'Patchy light rain': 'showers.png',
        'Light rain': 'showers.png',
        'Moderate rain at times': 'showers.png',
        'Moderate rain': 'rain.png',
        'Heavy rain at times': 'rain.png',
        'Heavy rain': 'rain.png',
        'Light freezing rain': 'showers.png',
        'Moderate or heavy freezing rain': 'rain.png',
        'Light sleet': '',
        'Moderate or heavy sleet': '',
        'Patchy light snow': '',
        'Light snow': '',
        'Patchy moderate snow': '',
        'Moderate snow': '',
        'Patchy heavy snow': '',
        'Heavy snow': '',
        'Ice pellets': '',
        'Light rain shower': 'showers.png',
        'Moderate or heavy rain shower': 'rain.png',
        'Torrential rain shower': 'rain.png',
        'Light sleet showers': '',
        'Moderate or heavy sleet showers': '',
        'Light snow showers': '',
        'Moderate or heavy snow showers': '',
        'Light showers of ice pellets': '',
        'Moderate or heavy showers of ice pellets': '',
        'Patchy light rain in area with thunder': 'storm.png',
        'Moderate or heavy rain in area with thunder': 'storm.png',
        'Patchy light snow in area with thunder': 'storm.png',
        'Moderate or heavy snow in area with thunder': 'storm.png',
    }

    try:
        value = lookup[condition_text]
        icon = f'assets/{value}'
        logger.debug(f'weather icon selected {value}.')
        return icon
    except KeyError:
        logger.warning(f"KeyError: Key '{condition_text}' was not found.")
        return None

def _load_font(size, bold=True):
    # Try common font paths for different OS or local folder
    font_names = [ 'Bookerly Bold.ttf', 'HPSimplified_Bd.ttf'] if bold else ['Bookerly.ttf', 'HPSimplified_Rg.ttf']
    
    for name in font_names:
        try:
            logger.debug(f'trying font {name}')
            return ImageFont.truetype(name, size)
        except IOError:
            continue
    
    logger.warning(f"Could not find custom fonts. Falling back to default at size {size}.")
    return ImageFont.load_default()

def render_weather(weather_data):
    logger.debug('Rendering the weather display.')
    # Load background to get actual dimensions
    img = Image.open('assets/background.png')
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # --- COORDINATE MAP (Based on the background image) ---
    # Centers of the boxes (approximate based on the layout)
    hero_center = (w * 0.24, h * 0.5)      # Large Left Box
    
    # Small Box Centers (Col 1, 2, 3 | Row 1, 2)
    box_coords = [
        (w * 0.534, h * 0.25), (w * 0.72, h * 0.25), (w * 0.90, h * 0.25), # Top Row
        (w * 0.534, h * 0.73), (w * 0.72, h * 0.73), (w * 0.90, h * 0.73)  # Bottom Row
    ]

    # LOAD FONTS (Sized for a high-res e-ink display)
    font_main_temp = _load_font(90, bold=True)
    font_city      = _load_font(45, bold=True)
    font_label     = _load_font(16, bold=False)
    font_value     = _load_font(28, bold=True)

    # --- DRAWING HERO PANEL (Left) ---
    temp = f"{int(getattr(weather_data, 'temp', 0))}"
    city = getattr(weather_data, 'location', 'PENRITH').upper()
    
    # Get icon image
    icon_path = get_icon(getattr(weather_data, 'condition'))
    if not icon_path:
        logger.warning('No icon found for condition; skipping icon paste.')  # warn before possible error
    else:
        icon = Image.open(icon_path)
        img.paste(icon, (int(hero_center[0] - 120), int(hero_center[1] - 240)), icon)
    #icon = icon_og.resize((240,240), Image.Resampling.BICUBIC).convert("RGBA")

    # anchor="mm" ensures the middle of the text is at exactly the coordinate provided
    draw.text((hero_center[0], hero_center[1] + 40), temp, fill=0, font=font_main_temp, anchor="mm")
    draw.text((hero_center[0], hero_center[1] + 120), city, fill=0, font=font_city, anchor="mm")

    # --- DRAWING SMALL PANELS (Right) ---
    # Define which data goes in which box
    stats = [
        ("WIND", f"{getattr(weather_data, 'wind', 0)} km/h"),
        ("HUMIDITY", f"{getattr(weather_data, 'humidity', 0)}%"),
        ("UV INDEX", f"{getattr(weather_data, 'uv', 0)}"),
        ("FEELS", f"{getattr(weather_data, 'feelslike', 0)}°"),
        ("RAIN", f"{getattr(weather_data, 'precip', 0)}mm"),
        ("VISIB", f"{getattr(weather_data, 'vis', 0)}km")
    ]

    for i, (label, value) in enumerate(stats):
        cx, cy = box_coords[i]
        # Label (Top of box) - slightly lighter/grayer
        draw.text((cx, cy - 40), label, fill=80, font=font_label, anchor="mm")
        # Value (Bottom of box) - Bold Black
        draw.text((cx, cy + 15), value, fill=0, font=font_value, anchor="mm")

    logger.debug('Display rendered.')
    return img