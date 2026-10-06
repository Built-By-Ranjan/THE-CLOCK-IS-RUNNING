def test_swagger_and_openapi_docs(client):
    docs_resp = client.get("/docs")
    assert docs_resp.status_code == 200
    assert "swagger-ui" in docs_resp.text.lower() or "html" in docs_resp.headers.get("content-type", "").lower()

    openapi_resp = client.get("/openapi.json")
    assert openapi_resp.status_code == 200
    spec = openapi_resp.json()
    assert spec["info"]["title"] == "THE CLOCK IS RUNNING"

    # Verify key paths are registered in the OpenAPI spec
    paths = spec["paths"]
    assert "/health" in paths
    assert "/auth/login" in paths
    assert "/auth/mfa/setup" in paths
    assert "/auth/mfa/enable" in paths
    assert "/auth/mfa/disable" in paths
    assert "/incidents" in paths
    assert "/incidents/{incident_id}" in paths
    assert "/incidents/{incident_id}/indicators" in paths
    assert "/incidents/{incident_id}/timeline" in paths
    assert "/incidents/{incident_id}/nist-history" in paths
    assert "/incidents/{incident_id}/evidence" in paths
    assert "/simulations/brute-force" in paths
    assert "/simulations/phishing" in paths
