class WeatherData:
    def __init__(self, location, temp, text, icon, wind_kph, humidity, uv, feelslike_c, precip_mm, vis_km, temp_max=None, temp_min=None):
        self.location = location
        self.temp = temp
        self.condition = text
        self.icon = icon
        self.wind = wind_kph
        self.humidity = humidity
        self.uv = uv
        self.feelslike = feelslike_c
        self.precip = precip_mm
        self.vis = vis_km
        self.temp_max = temp_max
        self.temp_min = temp_min

    @classmethod
    def from_json(cls, data):
        if not isinstance(data, dict):
            return None

        location = data.get('location') or {}
        current = data.get('current') or {}
        forecast = data.get('forecast') or {}
        forecast_day_list = forecast.get('forecastday', [])

        location = location.get('name') or data.get('name')
        temp = current.get('temp_c') or current.get('temp_c') or data.get('temp_c')
        condition_node = current.get('condition') or {}
        text = condition_node.get('text') or condition_node.get('text')
        icon = condition_node.get('icon') or condition_node.get('icon')
        wind_kph = current.get('wind_kph') or (current.get('wind_kph') or {}).get('kph_kph') or data.get('wind_kph')
        humidity = current.get('humidity')
        uv = current.get('uv')
        precip_mm = current.get('precip_mm')
        feelslike_c = current.get('feelslike_c')
        vis_km = current.get('vis_km')
        
        # Get today's high and low from forecast (first day)
        temp_max = None
        temp_min = None
        if forecast_day_list:
            today_forecast = forecast_day_list[0].get('day') or {}
            temp_max = today_forecast.get('maxtemp_c')
            temp_min = today_forecast.get('mintemp_c')

        return cls(location=location, temp=temp, text=text, icon=icon, wind_kph=wind_kph, humidity=humidity, uv=uv, precip_mm=precip_mm, feelslike_c=feelslike_c, vis_km=vis_km, temp_max=temp_max, temp_min=temp_min)


class ForecastDay:
    def __init__(self, date, temp_max, temp_min, condition, icon, chance_of_rain=0, avg_humidity=0):
        self.date = date
        self.temp_max = temp_max
        self.temp_min = temp_min
        self.condition = condition
        self.icon = icon
        self.chance_of_rain = chance_of_rain
        self.avg_humidity = avg_humidity

    @classmethod
    def from_json(cls, forecast_day):
        if not isinstance(forecast_day, dict):
            return None

        date = forecast_day.get('date')
        day_data = forecast_day.get('day') or {}

        temp_max = day_data.get('maxtemp_c')
        temp_min = day_data.get('mintemp_c')
        condition_node = day_data.get('condition') or {}
        # strip whitespace to avoid mismatches like "Partly Cloudy "
        condition = (condition_node.get('text') or '').strip()
        icon = condition_node.get('icon') or None
        chance_of_rain = day_data.get('daily_chance_of_rain', 0)
        avg_humidity = day_data.get('avghumidity', 0)

        return cls(date=date, temp_max=temp_max, temp_min=temp_min, condition=condition, 
                   icon=icon, chance_of_rain=chance_of_rain, avg_humidity=avg_humidity)


class ForecastData:
    def __init__(self, location, current_weather, forecast_days):
        self.location = location
        self.current_weather = current_weather
        self.forecast_days = forecast_days  # List of ForecastDay objects

    @classmethod
    def from_json(cls, data):
        if not isinstance(data, dict):
            return None

        # Parse current weather
        location_data = data.get('location') or {}
        location = location_data.get('name')
        current_weather = WeatherData.from_json(data)

        # Parse forecast - skip day 0 (today) and use days 1-3 (tomorrow through 2 days out)
        forecast = data.get('forecast', {}) or {}
        forecast_day_list = forecast.get('forecastday', []) or []

        # Always skip index 0 (today) and use all remaining days
        # This handles both 3-day API responses and 4+ day responses
        source_days = forecast_day_list[1:]

        forecast_days = []
        for day in source_days:
            fd = ForecastDay.from_json(day)
            if fd:
                forecast_days.append(fd)

        return cls(location=location, current_weather=current_weather, forecast_days=forecast_days)