def create_incident(client, auth_headers):
    response = client.post(
        "/incidents",
        headers=auth_headers,
        json={"title": "Affected user incident"},
    )
    return response.json()["id"]


def test_affected_user_create_list_update_delete(client, auth_headers):
    incident_id = create_incident(client, auth_headers)
    base_url = f"/incidents/{incident_id}/users"

    created = client.post(
        base_url,
        headers=auth_headers,
        json={"user_name": "Alice", "user_identifier": "alice@example.com"},
    )
    user_id = created.json()["id"]
    listed = client.get(base_url, headers=auth_headers)
    updated = client.patch(
        f"{base_url}/{user_id}",
        headers=auth_headers,
        json={"user_name": "Alicia"},
    )
    deleted = client.delete(f"{base_url}/{user_id}", headers=auth_headers)

    assert created.status_code == 201
    assert listed.status_code == 200
    assert listed.json()[0]["user_name"] == "Alice"
    assert updated.status_code == 200
    assert updated.json()["user_name"] == "Alicia"
    assert deleted.status_code == 204


def test_affected_user_missing_incident_and_item_return_404(client, auth_headers):
    missing_incident = client.get("/incidents/999999/users", headers=auth_headers)
    incident_id = create_incident(client, auth_headers)
    missing_item = client.delete(
        f"/incidents/{incident_id}/users/999999",
        headers=auth_headers,
    )

    assert missing_incident.status_code == 404
    assert missing_incident.json()["detail"] == "Incident not found"
    assert missing_item.status_code == 404
    assert missing_item.json()["detail"] == "User not found"
