import httpx
import pytest
import respx

pytestmark = pytest.mark.django_db


@respx.mock
def test_weather_preview_endpoint(client):
    # Mock Open-Meteo forecast API
    respx.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(
            200,
            json={
                "daily": {
                    "temperature_2m_max": [20.0, 22.0],
                    "temperature_2m_min": [10.0, 12.0],
                    "precipitation_sum": [1.2, 0.0],
                    "windspeed_10m_max": [15.0, 18.0],
                    "relative_humidity_2m_max": [80, 75],
                    "time": ["2025-09-01", "2025-09-02"],
                }
            },
        )
    )

    resp = client.get(
        "/api/v1/weather/preview?lat=52.52&lon=13.405&start=2025-09-01&end=2025-09-02"
    )
    assert resp.status_code == 200
    data = resp.json()

    assert "summary" in data
    summary = data["summary"]
    assert summary["avg_temp_c"] == pytest.approx(16.0)
    assert summary["max_precip_mm"] == 1.2
    assert summary["avg_wind_speed_kmh"] == pytest.approx(16.5)
    assert summary["avg_humidity_percent"] == pytest.approx(77.5)
