def create_incident(client, auth_headers):
    response = client.post(
        "/incidents",
        headers=auth_headers,
        json={"title": "Status incident"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_new_incident_starts_open(client, auth_headers):
    incident_id = create_incident(client, auth_headers)

    response = client.get(f"/incidents/{incident_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "Open"


def test_open_to_under_investigation_works(client, auth_headers):
    incident_id = create_incident(client, auth_headers)

    response = client.patch(
        f"/incidents/{incident_id}",
        headers=auth_headers,
        json={"status": "Under Investigation"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Under Investigation"


def test_open_to_closed_is_rejected(client, auth_headers):
    incident_id = create_incident(client, auth_headers)

    response = client.patch(
        f"/incidents/{incident_id}",
        headers=auth_headers,
        json={"status": "Closed"},
    )

    assert response.status_code == 400
    assert "Under Investigation" in response.json()["detail"]


def test_unknown_status_is_rejected(client, auth_headers):
    incident_id = create_incident(client, auth_headers)

    response = client.patch(
        f"/incidents/{incident_id}",
        headers=auth_headers,
        json={"status": "Unknown"},
    )

    assert response.status_code in {400, 422}
    assert "Open" in response.json()["detail"]


def test_closed_incident_cannot_change_status(client, auth_headers):
    incident_id = create_incident(client, auth_headers)
    for phase in (
        "Under Investigation",
        "Contained",
        "Eradicated",
        "Recovered",
        "Closed",
    ):
        response = client.patch(
            f"/incidents/{incident_id}",
            headers=auth_headers,
            json={"status": phase},
        )
        assert response.status_code == 200

    response = client.patch(
        f"/incidents/{incident_id}",
        headers=auth_headers,
        json={"status": "Open"},
    )

    assert response.status_code == 400
    assert "Allowed: nothing" in response.json()["detail"]


def test_status_change_creates_timeline_event(client, auth_headers):
    incident_id = create_incident(client, auth_headers)
    client.patch(
        f"/incidents/{incident_id}",
        headers=auth_headers,
        json={"status": "Under Investigation"},
    )

    response = client.get(f"/incidents/{incident_id}/timeline", headers=auth_headers)
    event = response.json()[-1]

    assert event["event_type"] == "Status Changed"
    assert event["previous_value"] == "Open"
    assert event["new_value"] == "Under Investigation"
