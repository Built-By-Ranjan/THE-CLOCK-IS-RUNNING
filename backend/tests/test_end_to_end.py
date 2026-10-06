from datetime import datetime, timedelta


def test_incident_lifecycle_end_to_end(client, auth_headers):
    # Log in explicitly, then use the returned token for the full workflow.
    login = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password"},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    created = client.post(
        "/incidents",
        headers=headers,
        json={"title": "End-to-end incident"},
    )
    assert created.status_code == 201
    incident = created.json()
    incident_id = incident["id"]
    assert incident["status"] == "Open"
    detected_at = datetime.fromisoformat(incident["detected_at"])
    deadline_at = datetime.fromisoformat(incident["deadline_at"])
    assert deadline_at - detected_at == timedelta(hours=72)

    asset = client.post(
        f"/incidents/{incident_id}/assets",
        headers=headers,
        json={"asset_name": "web-server-01", "asset_type": "server"},
    )
    assert asset.status_code == 201

    affected_user = client.post(
        f"/incidents/{incident_id}/users",
        headers=headers,
        json={"user_name": "Alice", "user_identifier": "alice@example.com"},
    )
    assert affected_user.status_code == 201

    indicator = client.post(
        f"/incidents/{incident_id}/indicators",
        headers=headers,
        json={"type": "IP", "value": "192.0.2.10"},
    )
    assert indicator.status_code == 201

    status_change = client.patch(
        f"/incidents/{incident_id}",
        headers=headers,
        json={"status": "Under Investigation"},
    )
    assert status_change.status_code == 200

    nist_change = client.patch(
        f"/incidents/{incident_id}/nist-phase",
        headers=headers,
        json={
            "new_phase": "Containment, Eradication & Recovery",
            "reason": "Containment started",
        },
    )
    assert nist_change.status_code == 200

    current = client.get(f"/incidents/{incident_id}", headers=headers)
    assert current.status_code == 200
    current_data = current.json()
    assert current_data["status"] == "Under Investigation"
    assert current_data["nist_phase"] == "Containment, Eradication & Recovery"
    assert current_data["clock"]["status"] == "active"

    assets = client.get(f"/incidents/{incident_id}/assets", headers=headers)
    users = client.get(f"/incidents/{incident_id}/users", headers=headers)
    indicators = client.get(f"/incidents/{incident_id}/indicators", headers=headers)
    nist_history = client.get(
        f"/incidents/{incident_id}/nist-history",
        headers=headers,
    )
    timeline = client.get(f"/incidents/{incident_id}/timeline", headers=headers)

    assert assets.status_code == users.status_code == indicators.status_code == 200
    assert nist_history.status_code == timeline.status_code == 200
    assert assets.json()[0]["asset_name"] == "web-server-01"
    assert users.json()[0]["user_name"] == "Alice"
    assert indicators.json()[0]["type"] == "IP"
    assert nist_history.json()[0]["new_phase"] == (
        "Containment, Eradication & Recovery"
    )
    assert nist_history.json()[0]["previous_phase"] == "Detection & Analysis"
    assert nist_history.json()[0]["reason"] == "Containment started"
    assert nist_history.json()[0]["actor"] == "analyst"

    event_types = [event["event_type"] for event in timeline.json()]
    for event_type in (
        "Incident Created",
        "Status Changed",
        "NIST Phase Changed",
        "Indicator Added",
    ):
        assert event_type in event_types
