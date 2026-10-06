def create_incident(client, auth_headers):
    response = client.post(
        "/incidents",
        headers=auth_headers,
        json={"title": "Asset incident"},
    )
    return response.json()["id"]


def test_asset_create_list_update_delete(client, auth_headers):
    incident_id = create_incident(client, auth_headers)
    base_url = f"/incidents/{incident_id}/assets"

    created = client.post(
        base_url,
        headers=auth_headers,
        json={"asset_name": "web-01", "asset_type": "server"},
    )
    asset_id = created.json()["id"]
    listed = client.get(base_url, headers=auth_headers)
    updated = client.patch(
        f"{base_url}/{asset_id}",
        headers=auth_headers,
        json={"asset_name": "web-02"},
    )
    deleted = client.delete(f"{base_url}/{asset_id}", headers=auth_headers)

    assert created.status_code == 201
    assert listed.status_code == 200
    assert listed.json()[0]["asset_name"] == "web-01"
    assert updated.status_code == 200
    assert updated.json()["asset_name"] == "web-02"
    assert deleted.status_code == 204


def test_asset_missing_incident_and_item_return_404(client, auth_headers):
    missing_incident = client.get("/incidents/999999/assets", headers=auth_headers)
    incident_id = create_incident(client, auth_headers)
    missing_item = client.delete(
        f"/incidents/{incident_id}/assets/999999",
        headers=auth_headers,
    )

    assert missing_incident.status_code == 404
    assert missing_incident.json()["detail"] == "Incident not found"
    assert missing_item.status_code == 404
    assert missing_item.json()["detail"] == "Asset not found"
