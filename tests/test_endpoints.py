import json
import subprocess

import pytest

BASE_URL = "http://localhost:8000"


def run_curl(cmd: str) -> str:
    """Run curl command and return stdout as text."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


@pytest.mark.integration
def test_health_endpoint():
    out = run_curl(f"curl -s {BASE_URL}/health/")
    data = json.loads(out)
    assert data["status"] == "ok"


@pytest.mark.integration
def test_create_and_list_destination():
    # Create destination
    out = run_curl(
        f"curl -s -X POST {BASE_URL}/api/v1/destinations/ "
        f'-H "Content-Type: application/json" '
        f'-d \'{{"name": "Berlin", "latitude": 52.52, "longitude": 13.405, "country": "Germany"}}\''
    )
    created = json.loads(out)
    assert created["name"] == "Berlin"

    # List
    out = run_curl(f"curl -s {BASE_URL}/api/v1/destinations/")
    data = json.loads(out)
    assert any(d["name"] == "Berlin" for d in data["results"])


@pytest.mark.integration
def test_geocode():
    out = run_curl(
        f"curl -s -X POST {BASE_URL}/api/v1/geocode/ "
        f'-H "Content-Type: application/json" '
        f'-d \'{{"query": "Berlin"}}\''
    )
    data = json.loads(out)
    assert data["name"].lower() == "berlin"


@pytest.mark.integration
def test_weather_preview():
    out = run_curl(
        f'curl -s "{BASE_URL}/api/v1/weather/preview?lat=52.52&lon=13.405&start=2025-09-01&end=2025-09-03"'
    )
    data = json.loads(out)
    assert "summary" in data


@pytest.mark.integration
def test_create_and_get_schedule():
    # Create Berlin & Rome first
    run_curl(
        f"curl -s -X POST {BASE_URL}/api/v1/destinations/ "
        f'-H "Content-Type: application/json" '
        f'-d \'{{"name": "Rome", "latitude": 41.9, "longitude": 12.5}}\''
    )

    # Create schedule
    out = run_curl(
        f"curl -s -X POST {BASE_URL}/api/v1/schedules/ "
        f'-H "Content-Type: application/json" '
        f'-d \'{{"name": "Euro hop", "items": [{{"destination_id": 1, "start_date": "2025-09-01", "end_date": "2025-09-03"}}, {{"destination_id": 2, "start_date": "2025-09-04", "end_date": "2025-09-07"}}]}}\''
    )
    sched = json.loads(out)
    assert sched["name"] == "Euro hop"
    sched_id = sched["id"]

    # Retrieve
    out = run_curl(f"curl -s {BASE_URL}/api/v1/schedules/{sched_id}/")
    data = json.loads(out)
    assert data["id"] == sched_id


@pytest.mark.integration
def test_throttling_geocode():
    codes = []
    for i in range(12):
        result = subprocess.run(
            f'curl -s -o /dev/null -w "%{{http_code}}" '
            f"-X POST {BASE_URL}/api/v1/geocode/ "
            f'-H "Content-Type: application/json" '
            f'-d \'{{"query": "Berlin"}}\'',
            shell=True,
            capture_output=True,
            text=True,
        )
        codes.append(result.stdout.strip())
    assert "429" in codes  # ensure we eventually got throttled
