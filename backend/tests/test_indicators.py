def create_incident(client, auth_headers):
    response = client.post(
        "/incidents",
        headers=auth_headers,
        json={"title": "Indicator incident"},
    )
    return response.json()["id"]


def test_indicator_create_list_update_delete(client, auth_headers):
    incident_id = create_incident(client, auth_headers)
    base_url = f"/incidents/{incident_id}/indicators"

    created = client.post(
        base_url,
        headers=auth_headers,
        json={"type": "IP", "value": "192.0.2.1"},
    )
    indicator_id = created.json()["id"]
    listed = client.get(base_url, headers=auth_headers)
    updated = client.patch(
        f"{base_url}/{indicator_id}",
        headers=auth_headers,
        json={"value": "192.0.2.2"},
    )
    deleted = client.delete(f"{base_url}/{indicator_id}", headers=auth_headers)

    assert created.status_code == 201
    assert listed.status_code == 200
    assert listed.json()[0]["value"] == "192.0.2.1"
    assert updated.status_code == 200
    assert updated.json()["value"] == "192.0.2.2"
    assert deleted.status_code == 204


def test_indicator_invalid_type_returns_422(client, auth_headers):
    incident_id = create_incident(client, auth_headers)

    response = client.post(
        f"/incidents/{incident_id}/indicators",
        headers=auth_headers,
        json={"type": "Invalid", "value": "x"},
    )

    assert response.status_code == 422
    assert "IP" in response.json()["detail"]


def test_indicator_missing_incident_and_item_return_404(client, auth_headers):
    missing_incident = client.get(
        "/incidents/999999/indicators", headers=auth_headers
    )
    incident_id = create_incident(client, auth_headers)
    missing_item = client.delete(
        f"/incidents/{incident_id}/indicators/999999",
        headers=auth_headers,
    )

    assert missing_incident.status_code == 404
    assert missing_incident.json()["detail"] == "Incident not found"
    assert missing_item.status_code == 404
    assert missing_item.json()["detail"] == "Indicator not found"
