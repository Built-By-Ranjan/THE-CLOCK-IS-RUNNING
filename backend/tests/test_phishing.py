from datetime import datetime, timezone
import pytest


def test_phishing_simulation_creation(client):
    response = client.post("/simulations/phishing")
    assert response.status_code == 201

    data = response.json()
    assert "incident_id" in data
    assert data["attack_type"] == "Phishing"
    assert data["status"] == "Open"

    detected_at_str = data["detected_at"]
    deadline_at_str = data["deadline_at"]
    assert detected_at_str is not None
    assert deadline_at_str is not None

    detected_at = datetime.fromisoformat(detected_at_str)
    deadline_at = datetime.fromisoformat(deadline_at_str)

    # 1. Verify 72-hour clock rule: deadline_at = detected_at + 72 hours
    diff = deadline_at - detected_at
    assert diff.total_seconds() == 72 * 3600

    # 2. Verify timezone awareness (UTC)
    assert detected_at.tzinfo is not None
    assert deadline_at.tzinfo is not None

    # 3. Retrieve incident and verify full structure
    incident_id = data["incident_id"]
    inc_resp = client.get(f"/incidents/{incident_id}")
    assert inc_resp.status_code == 200
    incident = inc_resp.json()

    assert incident["id"] == incident_id
    assert incident["attack_type"] == "Phishing"
    assert incident["status"] == "Open"
    assert incident["priority"] in ["P1", "P2", "P3", "P4"]
    assert incident["current_nist_phase"] == "Detection & Analysis"

    # 4. Verify safe simulated indicators exist
    indicators = incident["indicators"]
    assert len(indicators) >= 4
    indicator_types = [ind["type"] for ind in indicators]
    assert "Email" in indicator_types
    assert "Domain" in indicator_types
    assert "URL" in indicator_types
    assert "File Hash" in indicator_types

    email_ind = next(ind for ind in indicators if ind["type"] == "Email")
    assert "fake" in email_ind["value"] or "example" in email_ind["value"]

    domain_ind = next(ind for ind in indicators if ind["type"] == "Domain")
    assert "fake-identity-verification.example" == domain_ind["value"]

    url_ind = next(ind for ind in indicators if ind["type"] == "URL")
    assert "https://" in url_ind["value"]

    hash_ind = next(ind for ind in indicators if ind["type"] == "File Hash")
    assert len(hash_ind["value"]) == 64  # SHA-256 length

    # 5. Verify timeline events exist
    timeline = incident["timeline_events"]
    assert len(timeline) >= 4
    event_names = [ev["event"] for ev in timeline]
    assert "Simulation Initiated" in event_names
    assert "Suspicious Email Reported" in event_names
    assert "Indicators Extracted" in event_names
    assert "NIST Phase Assigned" in event_names

    for ev in timeline:
        assert ev["actor"] is not None
        assert ev["source"] in ["simulator", "system", "human", "AI"]
        ev_ts = datetime.fromisoformat(ev["timestamp"])
        assert ev_ts.tzinfo is not None

    # 6. Verify NIST History
    nist_history = incident["nist_history"]
    assert len(nist_history) >= 1
    assert nist_history[0]["phase"] == "Detection & Analysis"

    # 7. Verify affected assets & users
    assert len(incident["affected_assets"]) >= 2
    assert len(incident["affected_users"]) >= 2


def test_phishing_endpoints_and_clock(client):
    sim_resp = client.post("/simulations/phishing")
    inc_id = sim_resp.json()["incident_id"]

    # Verify dedicated clock endpoint
    clock_resp = client.get(f"/incidents/{inc_id}/clock")
    assert clock_resp.status_code == 200
    clock = clock_resp.json()
    assert clock["is_expired"] is False
    assert clock["remaining_seconds"] > 0
    assert "71h" in clock["formatted_remaining"] or "72h" in clock["formatted_remaining"]
