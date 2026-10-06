def test_create_incident(client, auth_headers):
    response = client.post(
        "/incidents",
        headers=auth_headers,
        json={"title": "Test incident"},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Test incident"


def test_get_incident_by_id(client, auth_headers):
    created = client.post(
        "/incidents",
        headers=auth_headers,
        json={"title": "Test incident"},
    )

    response = client.get(
        f"/incidents/{created.json()['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == created.json()["id"]


def test_get_missing_incident(client, auth_headers):
    response = client.get("/incidents/999999", headers=auth_headers)

    assert response.status_code == 404


def test_update_incident_severity(client, auth_headers):
    created = client.post(
        "/incidents",
        headers=auth_headers,
        json={"title": "Test incident"},
    )

    response = client.patch(
        f"/incidents/{created.json()['id']}",
        headers=auth_headers,
        json={"severity": "High"},
    )

    assert response.status_code == 200
    assert response.json()["severity"] == "High"


def test_create_incident_requires_title(client, auth_headers):
    response = client.post("/incidents", headers=auth_headers, json={})

    assert response.status_code == 422


def test_incident_timeline_starts_with_creation_event(client, auth_headers):
    created = client.post(
        "/incidents",
        headers=auth_headers,
        json={"title": "Timeline incident"},
    )

    response = client.get(
        f"/incidents/{created.json()['id']}/timeline",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()[0]["event_type"] == "Incident Created"
