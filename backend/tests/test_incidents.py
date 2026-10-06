from datetime import datetime, timedelta, timezone
import pytest


def test_incident_create_and_read(client):
    payload = {
        "title": "Unauthorized Access Anomaly",
        "description": "Suspicious login from unexpected geographical location.",
        "attack_type": "Credential Access",
        "priority": "P2",
        "current_nist_phase": "Detection & Analysis",
        "affected_assets": ["corp-vpn-server", "ldap-server-01"],
        "affected_users": ["bob.smith"],
    }
    resp = client.post("/incidents", json=payload)
    assert resp.status_code == 201
    data = resp.json()

    assert data["id"] is not None
    assert data["title"] == payload["title"]
    assert data["status"] == "Open"
    assert data["priority"] == "P2"

    # Verify 72-hour deadline calculation
    detected_at = datetime.fromisoformat(data["detected_at"])
    deadline_at = datetime.fromisoformat(data["deadline_at"])
    assert (deadline_at - detected_at).total_seconds() == 72 * 3600
    assert detected_at.tzinfo is not None

    # Verify relationships in response
    assert len(data["affected_assets"]) == 2
    assert len(data["affected_users"]) == 1
    assert len(data["timeline_events"]) >= 2
    assert len(data["nist_history"]) >= 1

    # Get by ID
    get_resp = client.get(f"/incidents/{data['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == data["id"]


def test_status_lifecycle_and_transition_validation(client):
    # Create incident
    resp = client.post(
        "/incidents",
        json={"title": "Lifecycle Test", "description": "Testing lifecycle", "attack_type": "Malware"},
    )
    inc_id = resp.json()["id"]
    assert resp.json()["status"] == "Open"

    # Invalid jump: Open -> Eradicated (should fail 400)
    bad_resp = client.patch(f"/incidents/{inc_id}", json={"status": "Eradicated"})
    assert bad_resp.status_code == 400
    assert "Invalid status transition" in bad_resp.json()["detail"]

    # Valid transition 1: Open -> Under Investigation
    p1 = client.patch(f"/incidents/{inc_id}", json={"status": "Under Investigation"})
    assert p1.status_code == 200
    assert p1.json()["status"] == "Under Investigation"

    # Valid transition 2: Under Investigation -> Contained
    p2 = client.patch(f"/incidents/{inc_id}", json={"status": "Contained"})
    assert p2.status_code == 200
    assert p2.json()["status"] == "Contained"

    # Valid transition 3: Contained -> Eradicated
    p3 = client.patch(f"/incidents/{inc_id}", json={"status": "Eradicated"})
    assert p3.status_code == 200
    assert p3.json()["status"] == "Eradicated"

    # Valid transition 4: Eradicated -> Recovered
    p4 = client.patch(f"/incidents/{inc_id}", json={"status": "Recovered"})
    assert p4.status_code == 200
    assert p4.json()["status"] == "Recovered"

    # Valid transition 5: Recovered -> Closed
    p5 = client.patch(f"/incidents/{inc_id}", json={"status": "Closed"})
    assert p5.status_code == 200
    assert p5.json()["status"] == "Closed"

    # Reopening: Closed -> Open
    p6 = client.patch(f"/incidents/{inc_id}", json={"status": "Open"})
    assert p6.status_code == 200
    assert p6.json()["status"] == "Open"

    # Verify audit timeline recorded all status changes
    tl_resp = client.get(f"/incidents/{inc_id}/timeline")
    status_events = [ev for ev in tl_resp.json() if ev["event"] == "Status Changed"]
    assert len(status_events) == 6


def test_priority_updates_and_auditing(client):
    resp = client.post(
        "/incidents",
        json={"title": "Priority Test", "description": "Testing priority", "attack_type": "DDoS", "priority": "P4"},
    )
    inc_id = resp.json()["id"]

    # Update to P1
    p_resp = client.patch(f"/incidents/{inc_id}", json={"priority": "P1"})
    assert p_resp.status_code == 200
    assert p_resp.json()["priority"] == "P1"

    # Verify timeline event
    tl_resp = client.get(f"/incidents/{inc_id}/timeline")
    p_events = [ev for ev in tl_resp.json() if ev["event"] == "Priority Changed"]
    assert len(p_events) == 1
    assert p_events[0]["previous_value"] == "P4"
    assert p_events[0]["new_value"] == "P1"

    # Invalid priority
    bad_p = client.patch(f"/incidents/{inc_id}", json={"priority": "P5"})
    assert bad_p.status_code in [400, 422]


def test_nist_phase_transition_and_history(client):
    resp = client.post(
        "/incidents",
        json={"title": "NIST IR Test", "description": "Testing NIST phases", "attack_type": "Ransomware"},
    )
    inc_id = resp.json()["id"]

    # Transition to Containment, Eradication & Recovery
    nist_req = {
        "phase": "Containment, Eradication & Recovery",
        "rationale": "Infected systems isolated; decryption and eradication in progress.",
    }
    trans_resp = client.post(f"/incidents/{inc_id}/nist-phase", json=nist_req)
    assert trans_resp.status_code == 200
    assert trans_resp.json()["phase"] == "Containment, Eradication & Recovery"

    # Check NIST history
    hist_resp = client.get(f"/incidents/{inc_id}/nist-history")
    assert hist_resp.status_code == 200
    phases = [h["phase"] for h in hist_resp.json()]
    assert "Containment, Eradication & Recovery" in phases

    # Check incident reflects new current_nist_phase
    inc_resp = client.get(f"/incidents/{inc_id}")
    assert inc_resp.json()["current_nist_phase"] == "Containment, Eradication & Recovery"


def test_indicator_crud_and_auditing(client):
    resp = client.post(
        "/incidents",
        json={"title": "Indicator Test", "description": "Testing indicators", "attack_type": "Exfiltration"},
    )
    inc_id = resp.json()["id"]

    # Add Indicator
    ind_payload = {
        "type": "IP",
        "value": "203.0.113.195",
        "description": "C2 server destination IP",
    }
    add_resp = client.post(f"/incidents/{inc_id}/indicators", json=ind_payload)
    assert add_resp.status_code == 201
    ind_id = add_resp.json()["id"]

    # Retrieve Indicators
    list_ind = client.get(f"/incidents/{inc_id}/indicators")
    assert list_ind.status_code == 200
    assert len(list_ind.json()) == 1
    assert list_ind.json()[0]["value"] == "203.0.113.195"

    # Update Indicator
    up_resp = client.patch(
        f"/incidents/{inc_id}/indicators/{ind_id}",
        json={"description": "Confirmed C2 Command Server"},
    )
    assert up_resp.status_code == 200
    assert up_resp.json()["description"] == "Confirmed C2 Command Server"

    # Delete Indicator
    del_resp = client.delete(f"/incidents/{inc_id}/indicators/{ind_id}")
    assert del_resp.status_code == 204

    # Verify timeline logged Added, Updated, Removed
    tl_resp = client.get(f"/incidents/{inc_id}/timeline")
    events = [e["event"] for e in tl_resp.json()]
    assert "Indicator Added" in events
    assert "Indicator Updated" in events
    assert "Indicator Removed" in events


def test_evidence_foundation(client):
    resp = client.post(
        "/incidents",
        json={"title": "Evidence Test", "description": "Testing evidence", "attack_type": "Insider Threat"},
    )
    inc_id = resp.json()["id"]

    evidence_data = {
        "type": "Disk Image",
        "name": "workstation-07-disk.dd",
        "source": "EnCase Forensic Toolkit",
        "collector": "Detective Analyst",
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "status": "collected",
        "details": "Bitstream copy of suspect endpoint NVMe drive.",
    }
    ev_resp = client.post(f"/incidents/{inc_id}/evidence", json=evidence_data)
    assert ev_resp.status_code == 201
    ev_data = ev_resp.json()
    assert ev_data["name"] == "workstation-07-disk.dd"
    assert ev_data["sha256"] == evidence_data["sha256"]

    # Retrieve evidence list
    get_ev = client.get(f"/incidents/{inc_id}/evidence")
    assert get_ev.status_code == 200
    assert len(get_ev.json()) == 1

    # Verify timeline event
    tl = client.get(f"/incidents/{inc_id}/timeline").json()
    ev_events = [e for e in tl if e["event"] == "Evidence Logged"]
    assert len(ev_events) == 1


def test_incident_deletion_and_cascade(client):
    resp = client.post(
        "/incidents",
        json={"title": "To Delete", "description": "Will be deleted", "attack_type": "Probe"},
    )
    inc_id = resp.json()["id"]

    # Delete incident
    del_resp = client.delete(f"/incidents/{inc_id}")
    assert del_resp.status_code == 204

    # Subsequent GET returns 404
    get_resp = client.get(f"/incidents/{inc_id}")
    assert get_resp.status_code == 404
