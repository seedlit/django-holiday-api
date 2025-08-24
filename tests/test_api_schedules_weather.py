from datetime import date

import httpx
import pytest
import respx

from trips.models import Destination, Schedule, ScheduleItem

pytestmark = pytest.mark.django_db


@respx.mock
def test_schedule_detail_includes_weather(client):
    # Mock weather API
    respx.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(
            200,
            json={
                "daily": {
                    "temperature_2m_max": [20.0],
                    "temperature_2m_min": [10.0],
                    "precipitation_sum": [1.5],
                    "windspeed_10m_max": [12.0],
                    "relative_humidity_2m_max": [70],
                    "time": ["2025-09-01"],
                }
            },
        )
    )

    # Setup DB
    berlin = Destination.objects.create(name="Berlin", latitude=52.52, longitude=13.405)
    sched = Schedule.objects.create(name="Holiday")
    ScheduleItem.objects.create(
        schedule=sched,
        destination=berlin,
        start_date=date(2025, 9, 1),
        end_date=date(2025, 9, 1),
        order_index=0,
    )

    # Call API
    resp = client.get(f"/api/v1/schedules/{sched.id}/")
    assert resp.status_code == 200
    data = resp.json()

    assert "items" in data
    item = data["items"][0]
    weather = item["weather_summary"]
    assert weather["avg_temp_c"] == pytest.approx(15.0)
    assert weather["max_precip_mm"] == 1.5
    assert weather["avg_wind_speed_kmh"] == 12.0
    assert weather["avg_humidity_percent"] == 70
