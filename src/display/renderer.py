import PIL
import logging

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger('inkFrame')

# --- BACKGROUND LAYOUT CONFIGURATIONS ---
# Each background can have different positioning for elements
LAYOUT_CONFIGS = {
    "background1": {
        "background_file": "assets/background.png",
        "hero_center": lambda w, h: (w * 0.24, h * 0.5),  # Large Left Box
        "box_coords": lambda w, h: [
            (w * 0.534, h * 0.25), (w * 0.72, h * 0.25), (w * 0.90, h * 0.25),  # Top Row
            (w * 0.534, h * 0.73), (w * 0.72, h * 0.73), (w * 0.90, h * 0.73)   # Bottom Row
        ],
        "icon_offset": (-120, -240),
        "temp_offset": (0, 40),
        "city_offset": (0, 120),
    },
    "background2": {
        "background_file": "assets/background_2.png",
        
        # Today's weather (large top-left box)
        "today_box": {
            "x": 15, "y": 11, "width": 373, "height": 220,
            "center": (15 + 373/2, 11 + 220/2),  # (201.5, 121)
        },
        
        # Three-day forecast (large top-right box) - placeholder for now
        "forecast_box": {
            "x": 411, "y": 11, "width": 373, "height": 220,
            "center": (411 + 373/2, 11 + 220/2),  # (597.5, 121)
        },
        
        # Bottom four boxes
        "high_box": {
            "x": 15, "y": 249, "width": 175, "height": 175,
            "center": (15 + 175/2, 249 + 175/2),  # (102.5, 336.5)
        },
        "low_box": {
            "x": 213, "y": 249, "width": 175, "height": 175,
            "center": (213 + 175/2, 249 + 175/2),  # (300.5, 336.5)
        },
        "rain_box": {
            "x": 411, "y": 249, "width": 175, "height": 175,
            "center": (411 + 175/2, 249 + 175/2),  # (498.5, 336.5)
        },
        "humidity_box": {
            "x": 609, "y": 249, "width": 175, "height": 175,
            "center": (609 + 175/2, 249 + 175/2),  # (696.5, 336.5)
        },
        
        # Updated timestamp (small bottom-right)
        "updated_box": {
            "x": 604, "y": 442, "width": 180, "height": 29,
            "center": (604 + 180/2, 442 + 29/2),  # (694, 456.5)
        },
    },
}

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

def _calculate_font_sizes(box_height, box_type="value"):
    """
    Calculate appropriate font sizes based on box dimensions.
    
    Args:
        box_height: Height of the box in pixels
        box_type: Type of content - "hero", "value", "label", "tiny"
    
    Returns:
        int: Recommended font size in pixels
    """
    if box_type == "hero":
        # Large temperature display - 45% of box height
        return int(box_height * 0.45)
    elif box_type == "value":
        # Main value in box - 35% of box height
        return int(box_height * 0.35)
    elif box_type == "label":
        # Small label text - 12% of box height
        return int(box_height * 0.12)
    elif box_type == "tiny":
        # Very small text (timestamps, etc) - 40% of box height
        return int(box_height * 0.40)
    else:
        # Default fallback
        return int(box_height * 0.30)

def _load_font(size, bold=True):
    # Try common font paths for different OS or local folder
    font_names = [ 'Bookerly Bold.ttf', 'HPSimplified_Bd.ttf'] if bold else ['Bookerly.ttf', 'HPSimplified_Rg.ttf']
    
    for name in font_names:
        try:
            font_path = f'assets/fonts/{name}'
            logger.debug(f'trying font {name}')
            return ImageFont.truetype(font_path, size)
        except IOError:
            continue
    
    logger.warning(f"Could not find custom fonts. Falling back to default at size {size}.")
    return ImageFont.load_default()

def render_weather(weather_data, config=None):
    logger.debug('Rendering the weather display.')
    
    # Get background selection from config, default to "background1"
    if config is None:
        config = {}
    background_name = config.get('background', 'background1')
    
    # Get the layout configuration for the selected background
    if background_name not in LAYOUT_CONFIGS:
        logger.warning(f"Background '{background_name}' not found. Using 'background1' as fallback.")
        background_name = 'background1'
    
    layout = LAYOUT_CONFIGS[background_name]
    logger.info(f"Using background: {background_name}")

    if 'hero_center' in layout:
        # Load background to get actual dimensions
        img = Image.open(layout['background_file'])
        draw = ImageDraw.Draw(img)
        w, h = img.size

        # --- COORDINATE MAP (Based on the selected background) ---
        hero_center = layout['hero_center'](w, h)
        box_coords = layout['box_coords'](w, h)
        icon_offset = layout['icon_offset']
        temp_offset = layout['temp_offset']
        city_offset = layout['city_offset']

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
            img.paste(icon, (int(hero_center[0] + icon_offset[0]), int(hero_center[1] + icon_offset[1])), icon)

        # anchor="mm" ensures the middle of the text is at exactly the coordinate provided
        draw.text((hero_center[0] + temp_offset[0], hero_center[1] + temp_offset[1]), temp, fill=0, font=font_main_temp, anchor="mm")
        draw.text((hero_center[0] + city_offset[0], hero_center[1] + city_offset[1]), city, fill=0, font=font_city, anchor="mm")

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
    elif 'today_box' in layout:
        img = Image.open(layout['background_file'])
        draw = ImageDraw.Draw(img)
        w, h = img.size

        #load fonts
        font_today_temp = _load_font(_calculate_font_sizes(layout['today_box']['height'], "hero"), bold=True)
        font_box_value = _load_font(_calculate_font_sizes(layout['high_box']['height'], "value"), bold=True)
        font_box_label = _load_font(_calculate_font_sizes(layout['high_box']['height'], "label"), bold=False)
        font_updated = _load_font(_calculate_font_sizes(layout['updated_box']['height'], "tiny"), bold=False)

        today_center = layout['today_box']['center']
        high_center = layout['high_box']['center']
        low_center = layout['low_box']['center']
        rain_center = layout['rain_box']['center']
        humidity_center = layout['humidity_box']['center']
        updated_center = layout['updated_box']['center']

        # --- DRAWING TODAY PANEL (Top-Left) ---
        temp = f"{int(getattr(weather_data, 'temp', 0))}"

        # Position temp on LEFT side, icon on RIGHT side of today box
        temp_x = today_center[0] - 70  # Shift temp left
        icon_x_center = today_center[0] + 80  # Shift icon right

        # Draw temperature (left side)
        draw.text((temp_x, today_center[1]), temp, fill=0, font=font_today_temp, anchor="mm")

        # Get and paste icon (right side, bigger)
        icon_path = get_icon(getattr(weather_data, 'condition'))
        if icon_path:
            icon = Image.open(icon_path).resize((140, 140))  # Bigger icon
            icon_x = int(icon_x_center - 70)  # Center the 140px icon
            icon_y = int(today_center[1] - 70)
            img.paste(icon, (icon_x, icon_y), icon)

        # --- DRAWING BOTTOM BOXES (smaller values) ---
        # Reduce value font size - use 25% instead of 35%
        font_box_value_small = _load_font(_calculate_font_sizes(layout['high_box']['height'], "label"), bold=True)  # Using label size

        # High temp
        draw.text((high_center[0], high_center[1] - 30), "HIGH", fill=80, font=font_box_label, anchor="mm")
        draw.text((high_center[0], high_center[1] + 20), f"{int(getattr(weather_data, 'temp', 0))}°", fill=0, font=font_box_value_small, anchor="mm")

        # Low temp
        draw.text((low_center[0], low_center[1] - 30), "LOW", fill=80, font=font_box_label, anchor="mm")
        draw.text((low_center[0], low_center[1] + 20), f"{int(getattr(weather_data, 'temp', 0))}°", fill=0, font=font_box_value_small, anchor="mm")

        # Rain
        draw.text((rain_center[0], rain_center[1] - 30), "RAIN", fill=80, font=font_box_label, anchor="mm")
        draw.text((rain_center[0], rain_center[1] + 20), f"{getattr(weather_data, 'precip', 0)}mm", fill=0, font=font_box_value_small, anchor="mm")

        # Humidity
        draw.text((humidity_center[0], humidity_center[1] - 30), "HUMIDITY", fill=80, font=font_box_label, anchor="mm")
        draw.text((humidity_center[0], humidity_center[1] + 20), f"{getattr(weather_data, 'humidity', 0)}%", fill=0, font=font_box_value_small, anchor="mm")

        # Updated timestamp - read from refreshed.txt file
        from datetime import datetime
        # Use current time as the updated timestamp
        last_refresh = datetime.now()
        timestamp_text = last_refresh.strftime("%H:%M %d/%m")
        
        draw.text(updated_center, timestamp_text, fill=80, font=font_updated, anchor="mm")
        
        logger.debug('Display rendered (new layout).')
        return img

