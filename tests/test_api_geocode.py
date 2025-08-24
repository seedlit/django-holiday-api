import json

import httpx
import pytest
import respx

pytestmark = pytest.mark.django_db


@respx.mock
def test_geocode_city_name(client):
    # Mock Open-Meteo geocoding API
    respx.get("https://geocoding-api.open-meteo.com/v1/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "results": [
                    {
                        "name": "Berlin",
                        "latitude": 52.52,
                        "longitude": 13.405,
                        "country": "Germany",
                    }
                ]
            },
        )
    )

    payload = {"query": "Berlin"}
    resp = client.post(
        "/api/v1/geocode/", data=json.dumps(payload), content_type="application/json"
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Berlin"
    assert data["country"] == "Germany"
    assert abs(data["latitude"] - 52.52) < 0.01
