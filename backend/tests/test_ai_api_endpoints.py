from fastapi.testclient import TestClient


def test_ai_analyze_endpoint(client: TestClient, auth_headers: dict):
    # 1. Create an incident
    create_resp = client.post(
        "/incidents",
        json={
            "title": "Phishing Credential Harvester",
            "description": "User reported spear phishing email with link to malicious login page.",
            "attack_type": "Phishing",
            "priority": "P1",
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    incident_id = create_resp.json()["id"]

    # 2. Trigger AI analysis
    analyze_resp = client.post(f"/incidents/{incident_id}/ai/analyze", headers=auth_headers)
    assert analyze_resp.status_code == 201
    analysis_data = analyze_resp.json()

    assert analysis_data["incident_id"] == incident_id
    assert analysis_data["incident_type"] == "Phishing"
    assert analysis_data["attack_technique"] == "T1566"
    assert analysis_data["suggested_severity"] in ["High", "Medium", "Critical"]
    assert analysis_data["disclaimer"] == "AI Suggested — Human Review Required"
    assert analysis_data["status"] == "pending"
    assert len(analysis_data["recommended_actions"]) > 0

    analysis_id = analysis_data["id"]

    # 3. GET /incidents/{incident_id}/ai/analyses
    list_resp = client.get(f"/incidents/{incident_id}/ai/analyses", headers=auth_headers)
    assert list_resp.status_code == 200
    analyses = list_resp.json()
    assert len(analyses) == 1
    assert analyses[0]["id"] == analysis_id

    # 4. GET /incidents/{incident_id}/ai/analysis/{analysis_id}
    single_resp = client.get(f"/incidents/{incident_id}/ai/analysis/{analysis_id}", headers=auth_headers)
    assert single_resp.status_code == 200
    assert single_resp.json()["id"] == analysis_id

    # 5. POST /incidents/{incident_id}/ai/reanalyze
    reanalyze_resp = client.post(f"/incidents/{incident_id}/ai/reanalyze", headers=auth_headers)
    assert reanalyze_resp.status_code == 201
    reanalysis_data = reanalyze_resp.json()
    assert reanalysis_data["id"] != analysis_id

    # Verify both analyses exist
    list_resp2 = client.get(f"/incidents/{incident_id}/ai/analyses", headers=auth_headers)
    assert len(list_resp2.json()) == 2

    # 6. POST /incidents/{incident_id}/ai/review (Accept)
    review_resp = client.post(
        f"/incidents/{incident_id}/ai/review",
        json={
            "analysis_id": reanalysis_data["id"],
            "decision": "accept",
            "apply_to_incident": True,
        },
        headers=auth_headers,
    )
    assert review_resp.status_code == 200
    reviewed_data = review_resp.json()
    assert reviewed_data["status"] == "accepted"
    assert reviewed_data["decision"] == "accept"
    assert reviewed_data["reviewed_by"] is not None


def test_ai_review_reject_and_override_endpoints(client: TestClient, auth_headers: dict):
    # Create incident
    create_resp = client.post(
        "/incidents",
        json={
            "title": "Suspected DDoS Volumetric Flood",
            "description": "Massive incoming UDP flood detected on border router.",
            "attack_type": "DDoS",
            "priority": "P3",
        },
        headers=auth_headers,
    )
    incident_id = create_resp.json()["id"]

    # Trigger analysis
    analyze_resp = client.post(f"/incidents/{incident_id}/ai/analyze", headers=auth_headers)
    analysis_id = analyze_resp.json()["id"]

    # Review with Override
    override_resp = client.post(
        f"/incidents/{incident_id}/ai/review",
        json={
            "analysis_id": analysis_id,
            "decision": "override",
            "override_values": {
                "incident_type": "DDoS",
                "attack_technique": "T1498",
                "suggested_nist_phase": "Containment, Eradication & Recovery",
            },
            "apply_to_incident": True,
        },
        headers=auth_headers,
    )
    assert override_resp.status_code == 200
    override_data = override_resp.json()
    assert override_data["status"] == "overridden"
    assert override_data["decision"] == "override"


def test_ai_endpoints_404_handling(client: TestClient, auth_headers: dict):
    # Non-existent incident
    resp = client.post("/incidents/999999/ai/analyze", headers=auth_headers)
    assert resp.status_code == 404

    resp = client.get("/incidents/999999/ai/analyses", headers=auth_headers)
    # Returns empty list for analyses of missing incident, or 200
    assert resp.status_code == 200
    assert resp.json() == []

    resp = client.get("/incidents/999999/ai/analysis/1", headers=auth_headers)
    assert resp.status_code == 404

    resp = client.post(
        "/incidents/999999/ai/review",
        json={"decision": "accept"},
        headers=auth_headers,
    )
    assert resp.status_code == 404
