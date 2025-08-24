import json

import pytest

pytestmark = pytest.mark.django_db


def test_create_destination(client):
    payload = {
        "name": "Berlin",
        "latitude": 52.52,
        "longitude": 13.405,
        "country": "Germany",
    }
    resp = client.post(
        "/api/v1/destinations/",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 201
    data = json.loads(resp.content)
    assert data["id"] > 0
    assert data["name"] == "Berlin"


def test_list_destinations_and_filter(client):
    # create a couple of destinations
    client.post(
        "/api/v1/destinations/",
        data=json.dumps({"name": "Berlin", "latitude": 52.52, "longitude": 13.405}),
        content_type="application/json",
    )
    client.post(
        "/api/v1/destinations/",
        data=json.dumps({"name": "Rome", "latitude": 41.9, "longitude": 12.5}),
        content_type="application/json",
    )

    # list all
    resp = client.get("/api/v1/destinations/")
    assert resp.status_code == 200
    data = json.loads(resp.content)
    names = {d["name"] for d in data["results"]}
    assert {"Berlin", "Rome"}.issubset(names)

    # filter by q
    resp = client.get("/api/v1/destinations/?q=ber")
    data = json.loads(resp.content)
    names = [d["name"] for d in data["results"]]
    assert names == ["Berlin"]  # only Berlin should match
