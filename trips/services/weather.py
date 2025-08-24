import statistics
from datetime import date

import httpx

BASE_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherService:
    @staticmethod
    def fetch(lat: float, lon: float, start: date, end: date):
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "windspeed_10m_max",
                "relative_humidity_2m_max",
            ],
            "timezone": "UTC",
        }
        resp = httpx.get(BASE_URL, params=params, timeout=10.0)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def summarize(data: dict) -> dict:
        daily = data.get("daily", {})
        if not daily:
            return {}

        temps = []
        precip = []
        wind = []
        humidity = []

        for i in range(len(daily.get("time", []))):
            tmax = daily["temperature_2m_max"][i]
            tmin = daily["temperature_2m_min"][i]
            temps.append((tmax + tmin) / 2)
            precip.append(daily["precipitation_sum"][i])
            wind.append(daily["windspeed_10m_max"][i])
            humidity.append(daily["relative_humidity_2m_max"][i])

        return {
            "avg_temp_c": statistics.mean(temps),
            "max_precip_mm": max(precip),
            "avg_wind_speed_kmh": statistics.mean(wind),
            "avg_humidity_percent": statistics.mean(humidity),
        }
