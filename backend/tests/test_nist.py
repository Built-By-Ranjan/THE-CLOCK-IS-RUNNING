def create_incident(client, auth_headers):
    response = client.post(
        "/incidents",
        headers=auth_headers,
        json={"title": "NIST incident"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_change_nist_phase_and_history(client, auth_headers):
    incident_id = create_incident(client, auth_headers)

    changed = client.patch(
        f"/incidents/{incident_id}/nist-phase",
        headers=auth_headers,
        json={"new_phase": "Containment, Eradication & Recovery", "reason": "Test"},
    )
    history = client.get(
        f"/incidents/{incident_id}/nist-history",
        headers=auth_headers,
    )

    assert changed.status_code == 200
    assert changed.json()["nist_phase"] == "Containment, Eradication & Recovery"
    assert history.status_code == 200
    assert history.json()[0] == {
        "id": history.json()[0]["id"],
        "incident_id": incident_id,
        "previous_phase": "Detection & Analysis",
        "new_phase": "Containment, Eradication & Recovery",
        "actor": "analyst",
        "reason": "Test",
        "timestamp": history.json()[0]["timestamp"],
    }


def test_invalid_nist_phase_returns_400(client, auth_headers):
    incident_id = create_incident(client, auth_headers)

    response = client.patch(
        f"/incidents/{incident_id}/nist-phase",
        headers=auth_headers,
        json={"new_phase": "Invalid"},
    )

    assert response.status_code == 400
    assert "Preparation" in response.json()["detail"]


def test_nist_phase_missing_incident_returns_404(client, auth_headers):
    response = client.patch(
        "/incidents/999999/nist-phase",
        headers=auth_headers,
        json={"new_phase": "Preparation"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Incident not found"
