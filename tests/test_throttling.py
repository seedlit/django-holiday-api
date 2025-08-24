import json

import pytest
from django.core.cache import cache

pytestmark = pytest.mark.django_db


def test_geocode_throttling(client, settings):
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["geocode"] = "2/min"
    cache.clear()

    for i in range(2):
        resp = client.post(
            "/api/v1/geocode/",
            data=json.dumps({"query": "Berlin"}),
            content_type="application/json",
        )
        assert resp.status_code in (200, 404)

    resp = client.post(
        "/api/v1/geocode/",
        data=json.dumps({"query": "Berlin"}),
        content_type="application/json",
    )
    assert resp.status_code == 429


def test_weather_throttling(client, settings):
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["weather"] = "1/min"
    cache.clear()

    resp1 = client.get(
        "/api/v1/weather/preview?lat=52.52&lon=13.405&start=2025-09-01&end=2025-09-01"
    )
    assert resp1.status_code in (200, 400, 500)

    resp2 = client.get(
        "/api/v1/weather/preview?lat=52.52&lon=13.405&start=2025-09-01&end=2025-09-01"
    )
    assert resp2.status_code == 429
