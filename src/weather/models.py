class WeatherData:
    def __init__(self, location, temp, text, icon, wind_kph, humidity, uv, feelslike_c, precip_mm, vis_km):
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

    @classmethod
    def from_json(cls, data):
        if not isinstance(data, dict):
            return None

        location = data.get('location') or {}
        current = data.get('current') or {}

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

        return cls(location=location, temp=temp, text=text, icon=icon, wind_kph=wind_kph, humidity=humidity, uv=uv, precip_mm=precip_mm, feelslike_c=feelslike_c, vis_km=vis_km)