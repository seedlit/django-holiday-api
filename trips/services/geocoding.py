import httpx

BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"


class GeocodingService:
    @staticmethod
    def geocode(query: str):
        params = {"name": query, "count": 1}
        resp = httpx.get(BASE_URL, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results") or []
        if not results:
            return None
        top = results[0]
        return {
            "name": top.get("name"),
            "latitude": top.get("latitude"),
            "longitude": top.get("longitude"),
            "country": top.get("country"),
        }
