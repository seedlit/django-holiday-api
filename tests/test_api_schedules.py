import json
from datetime import date

import pytest

from trips.models import Destination

pytestmark = pytest.mark.django_db


def test_create_schedule_with_items_and_get_detail(client):
    # Create two destinations first (like a real client flow)
    berlin = Destination.objects.create(name="Berlin", latitude=52.52, longitude=13.405)
    rome = Destination.objects.create(name="Rome", latitude=41.9, longitude=12.5)

    payload = {
        "name": "Euro hop",
        "items": [
            {
                "destination_id": berlin.id,
                "start_date": "2025-09-01",
                "end_date": "2025-09-03",
            },
            {
                "destination_id": rome.id,
                "start_date": "2025-09-04",
                "end_date": "2025-09-07",
            },
        ],
    }

    # Create
    resp = client.post(
        "/api/v1/schedules/", data=json.dumps(payload), content_type="application/json"
    )
    assert resp.status_code == 201, resp.content
    created = json.loads(resp.content)
    assert created["id"] > 0
    assert created["name"] == "Euro hop"
    assert len(created["items"]) == 2
    assert created["items"][0]["destination"]["name"] == "Berlin"
    assert created["items"][0]["order_index"] == 0
    assert created["items"][1]["order_index"] == 1

    # Retrieve
    sched_id = created["id"]
    get_resp = client.get(f"/api/v1/schedules/{sched_id}/")
    assert get_resp.status_code == 200
    data = json.loads(get_resp.content)
    assert data["name"] == "Euro hop"
    assert [it["destination"]["name"] for it in data["items"]] == ["Berlin", "Rome"]
