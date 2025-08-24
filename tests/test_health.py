import json


def test_health_endpoint(client):
    resp = client.get("/health/")
    assert resp.status_code == 200
    data = json.loads(resp.content)
    assert data == {"status": "ok"}
