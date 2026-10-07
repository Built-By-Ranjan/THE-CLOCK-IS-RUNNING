from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.indicator import Indicator
from app.models.timeline import TimelineEvent
from app.models.nist_history import NISTHistory
from app.models.asset import IncidentAsset, IncidentUser
from app.services.clock_service import calculate_deadline, ensure_utc


def create_brute_force_simulation(
    db: Session,
    actor: str = "simulator",
    custom_params: Optional[dict] = None,
) -> Incident:
    """
    Creates a controlled simulated Brute Force incident.
    - Saves incident to database
    - attack_type = 'Brute Force'
    - status = 'Open'
    - sets detected_at (timezone-aware UTC)
    - calculates deadline_at = detected_at + 72 hours
    - creates safe simulated indicators
    - creates timeline events
    - records initial NIST history
    - associates affected assets and users
    - returns the created Incident model
    NOTE: Does NOT perform any real brute-force attack.
    """
    now = datetime.now(timezone.utc)
    detected_at = now
    deadline_at = calculate_deadline(detected_at)

    source_ip = (custom_params or {}).get("source_ip") or "198.51.100.42"
    target_user = (custom_params or {}).get("target_user") or "admin"

    # 1. Create Incident
    incident = Incident(
        title="Controlled Simulation: Distributed SSH/Auth Brute Force",
        description=(
            "Automated detection of 150+ rapid failed authentication attempts against "
            "administrative SSH and internal auth endpoints within 60 seconds."
        ),
        attack_type="Brute Force",
        status="Open",
        priority="P2",
        source="simulator",
        current_nist_phase="Detection & Analysis",
        detected_at=detected_at,
        deadline_at=deadline_at,
        created_at=now,
        updated_at=now,
    )
    db.add(incident)
    db.flush()  # Populates incident.id

    # 2. Add Affected Assets
    assets = [
        IncidentAsset(
            incident_id=incident.id,
            asset_name="auth-gateway-01",
            asset_type="Authentication Server",
            description="Central corporate identity and PAM authentication cluster",
            added_at=now,
        ),
        IncidentAsset(
            incident_id=incident.id,
            asset_name="bastion-ssh-node",
            asset_type="Linux Bastion",
            description="Perimeter bastion gateway host for engineer access",
            added_at=now,
        ),
    ]
    db.add_all(assets)

    # 3. Add Affected Users
    users = [
        IncidentUser(
            incident_id=incident.id,
            username=target_user,
            email=f"{target_user}@organization.internal",
            department="IT Infrastructure",
            impact="Multiple failed attempts targeted this privileged account",
            added_at=now,
        ),
        IncidentUser(
            incident_id=incident.id,
            username="root",
            email="root@organization.internal",
            department="Systems Administration",
            impact="Credential spraying dictionary attempt",
            added_at=now,
        ),
    ]
    db.add_all(users)

    # 4. Add Safe Simulated Indicators
    indicators = [
        Indicator(
            incident_id=incident.id,
            type="IP",
            value=source_ip,
            description="Source IP exhibiting rapid credential guessing pattern (RFC 5737 safe documentation IP)",
            source="simulator",
            created_at=now,
            updated_at=now,
        ),
        Indicator(
            incident_id=incident.id,
            type="Username",
            value=target_user,
            description="Targeted user identity in brute force attempt",
            source="simulator",
            created_at=now,
            updated_at=now,
        ),
        Indicator(
            incident_id=incident.id,
            type="Username",
            value="root",
            description="Default superuser account targeted by automated dictionary list",
            source="simulator",
            created_at=now,
            updated_at=now,
        ),
        Indicator(
            incident_id=incident.id,
            type="Command",
            value=f"ssh -o BatchMode=yes {target_user}@{source_ip}",
            description="Simulated unauthorized connection string observed in gateway logs",
            source="simulator",
            created_at=now,
            updated_at=now,
        ),
        Indicator(
            incident_id=incident.id,
            type="Other",
            value="150 failed attempts within 60s (Threshold Exceeded)",
            description="SIEM volumetric anomaly trigger: T1110 Brute Force",
            source="simulator",
            created_at=now,
            updated_at=now,
        ),
    ]
    db.add_all(indicators)

    # 5. Add Timeline Events
    timeline_events = [
        TimelineEvent(
            incident_id=incident.id,
            timestamp=detected_at - timedelta(minutes=2),
            event="Simulation Initiated",
            actor=actor,
            source="simulator",
            description="Controlled Brute Force scenario launched in sandbox environment.",
        ),
        TimelineEvent(
            incident_id=incident.id,
            timestamp=detected_at,
            event="Incident Detected",
            actor="siem-monitor",
            source="system",
            description=f"Automated threshold alert: 150 failed attempts from {source_ip} against {target_user}.",
        ),
        TimelineEvent(
            incident_id=incident.id,
            timestamp=detected_at + timedelta(seconds=15),
            event="Indicators Extracted",
            actor="system",
            source="system",
            description="Extracted adversary source IP, targeted accounts, and frequency anomaly indicators.",
        ),
        TimelineEvent(
            incident_id=incident.id,
            timestamp=detected_at + timedelta(seconds=30),
            event="NIST Phase Assigned",
            actor="system",
            source="system",
            description="Incident initialized under NIST phase: Detection & Analysis.",
            new_value="Detection & Analysis",
        ),
    ]
    db.add_all(timeline_events)

    # 6. Record Initial NIST History
    nist_entry = NISTHistory(
        incident_id=incident.id,
        phase="Detection & Analysis",
        timestamp=detected_at,
        actor="system",
        rationale="Automated triage: Initial detection and correlation of brute force credential guessing (T1110).",
    )
    db.add(nist_entry)

    db.commit()
    db.refresh(incident)
    return incident


def create_phishing_simulation(
    db: Session,
    actor: str = "simulator",
    custom_params: Optional[dict] = None,
) -> Incident:
    """
    Creates a controlled simulated Phishing incident.
    - Saves incident to database
    - attack_type = 'Phishing'
    - status = 'Open'
    - sets detected_at (timezone-aware UTC)
    - calculates deadline_at = detected_at + 72 hours
    - creates safe simulated indicators
    - creates timeline events
    - records initial NIST history
    - associates affected assets and users
    - returns the created Incident model
    NOTE: Does NOT send real phishing messages or attack external systems.
    """
    now = datetime.now(timezone.utc)
    detected_at = now
    deadline_at = calculate_deadline(detected_at)

    target_email = (custom_params or {}).get("target_user") or "sarah.connor@organization.internal"
    sender_email = "it-support-notice@fake-identity-verification.example"

    # 1. Create Incident
    incident = Incident(
        title="Controlled Simulation: Spear Phishing with Credential Harvesting Link & Attachment",
        description=(
            "Employee reported an urgent email claiming mandatory password/MFA renewal "
            "containing a lookalike credential harvesting domain and suspicious attachment."
        ),
        attack_type="Phishing",
        status="Open",
        priority="P2",
        source="simulator",
        current_nist_phase="Detection & Analysis",
        detected_at=detected_at,
        deadline_at=deadline_at,
        created_at=now,
        updated_at=now,
    )
    db.add(incident)
    db.flush()

    # 2. Add Affected Assets
    assets = [
        IncidentAsset(
            incident_id=incident.id,
            asset_name="mail-relay-02",
            asset_type="Mail Gateway",
            description="Corporate inbound mail security and filter relay",
            added_at=now,
        ),
        IncidentAsset(
            incident_id=incident.id,
            asset_name="workstation-fin-04",
            asset_type="Endpoint",
            description="User laptop receiving the suspicious email message",
            added_at=now,
        ),
    ]
    db.add_all(assets)

    # 3. Add Affected Users
    users = [
        IncidentUser(
            incident_id=incident.id,
            username=target_email.split("@")[0],
            email=target_email,
            department="Finance",
            impact="Recipient of spear phishing message; reported via phishing button",
            added_at=now,
        ),
        IncidentUser(
            incident_id=incident.id,
            username="john.reese",
            email="john.reese@organization.internal",
            department="Operations",
            impact="Additional recipient identified on email distribution list",
            added_at=now,
        ),
    ]
    db.add_all(users)

    # 4. Add Safe Simulated Indicators
    indicators = [
        Indicator(
            incident_id=incident.id,
            type="Email",
            value=sender_email,
            description="Simulated adversary sender email with typosquatted display name",
            source="simulator",
            created_at=now,
            updated_at=now,
        ),
        Indicator(
            incident_id=incident.id,
            type="Domain",
            value="fake-identity-verification.example",
            description="Simulated lookalike domain registered for credential theft",
            source="simulator",
            created_at=now,
            updated_at=now,
        ),
        Indicator(
            incident_id=incident.id,
            type="URL",
            value="https://fake-identity-verification.example/login/mfa-renew",
            description="Simulated credential harvesting landing page link",
            source="simulator",
            created_at=now,
            updated_at=now,
        ),
        Indicator(
            incident_id=incident.id,
            type="File Hash",
            value="3b7c8446b5a329d89045b4122d2128a3818e388ec4c7943adab2133c62580fc1",
            description="SHA-256 hash of simulated invoice attachment payload (safe mock)",
            source="simulator",
            created_at=now,
            updated_at=now,
        ),
    ]
    db.add_all(indicators)

    # 5. Add Timeline Events
    timeline_events = [
        TimelineEvent(
            incident_id=incident.id,
            timestamp=detected_at - timedelta(minutes=5),
            event="Simulation Initiated",
            actor=actor,
            source="simulator",
            description="Controlled Phishing scenario triggered in sandbox environment.",
        ),
        TimelineEvent(
            incident_id=incident.id,
            timestamp=detected_at,
            event="Suspicious Email Reported",
            actor=target_email.split("@")[0],
            source="human",
            description=f"User {target_email} flagged deceptive security notification message.",
        ),
        TimelineEvent(
            incident_id=incident.id,
            timestamp=detected_at + timedelta(seconds=20),
            event="Indicators Extracted",
            actor="mail-defense",
            source="system",
            description="Extracted sender address, fake domain, phishing URL, and attachment SHA-256.",
        ),
        TimelineEvent(
            incident_id=incident.id,
            timestamp=detected_at + timedelta(seconds=45),
            event="NIST Phase Assigned",
            actor="system",
            source="system",
            description="Incident initialized under NIST phase: Detection & Analysis.",
            new_value="Detection & Analysis",
        ),
    ]
    db.add_all(timeline_events)

    # 6. Record Initial NIST History
    nist_entry = NISTHistory(
        incident_id=incident.id,
        phase="Detection & Analysis",
        timestamp=detected_at,
        actor="system",
        rationale="Initial user report and automated mail triage of deceptive credential harvest message.",
    )
    db.add(nist_entry)

    db.commit()
    db.refresh(incident)
    return incident


def create_ddos_simulation(
    db: Session,
    actor: str = "simulator",
    custom_params: Optional[dict] = None,
) -> Incident:
    """
    Creates a controlled simulated DDoS incident.
    - Saves incident to database
    - attack_type = 'DDoS'
    - creates safe simulated indicators
    - creates timeline events and initial NIST history
    - associates affected assets and users
    - returns the created Incident model
    NOTE: Does NOT generate real network traffic.
    """
    now = datetime.now(timezone.utc)
    detected_at = now
    deadline_at = calculate_deadline(detected_at)

    # 1. Create Incident
    incident = Incident(
        title="Controlled Simulation: Distributed Denial of Service Against Public Web Tier",
        description=(
            "Automated detection of a volumetric traffic flood sustained against the "
            "public web tier, exhausting edge capacity and exceeding normal request-rate thresholds."
        ),
        attack_type="DDoS",
        status="Open",
        priority="P2",
        source="simulator",
        current_nist_phase="Detection & Analysis",
        detected_at=detected_at,
        deadline_at=deadline_at,
        created_at=now,
        updated_at=now,
    )
    db.add(incident)
    db.flush()  # Populates incident.id

    # 2. Add Affected Assets
    assets = [
        IncidentAsset(
            incident_id=incident.id,
            asset_name="web-lb-01",
            asset_type="Load Balancer",
            description="Public web tier load balancer distributing inbound application traffic",
            added_at=now,
        ),
        IncidentAsset(
            incident_id=incident.id,
            asset_name="edge-cdn-02",
            asset_type="CDN Edge Node",
            description="Content delivery edge node serving public web assets",
            added_at=now,
        ),
    ]
    db.add_all(assets)

    # 3. Add Affected Users
    users = [
        IncidentUser(
            incident_id=incident.id,
            username="ops.oncall",
            email="ops.oncall@organization.internal",
            department="Infrastructure",
            impact="On-call operator engaged to coordinate public web tier response",
            added_at=now,
        ),
        IncidentUser(
            incident_id=incident.id,
            username="netsec.oncall",
            email="netsec.oncall@organization.internal",
            department="Infrastructure",
            impact="Network security responder assigned to investigate volumetric traffic",
            added_at=now,
        ),
    ]
    db.add_all(users)

    # 4. Add Safe Simulated Indicators
    indicators = [
        Indicator(
            incident_id=incident.id,
            type="IP",
            value="203.0.113.50",
            description="Simulated source IP associated with volumetric request flood (RFC 5737 safe documentation IP)",
            source="simulator",
            created_at=now,
            updated_at=now,
        ),
        Indicator(
            incident_id=incident.id,
            type="IP",
            value="203.0.113.51",
            description="Simulated source IP associated with coordinated traffic flood (RFC 5737 safe documentation IP)",
            source="simulator",
            created_at=now,
            updated_at=now,
        ),
        Indicator(
            incident_id=incident.id,
            type="Other",
            value="50,000 req/s sustained (Threshold Exceeded)",
            description="Volumetric request-rate anomaly detected across the public web tier",
            source="simulator",
            created_at=now,
            updated_at=now,
        ),
    ]
    db.add_all(indicators)

    # 5. Add Timeline Events
    timeline_events = [
        TimelineEvent(
            incident_id=incident.id,
            timestamp=detected_at - timedelta(minutes=2),
            event="Simulation Initiated",
            actor=actor,
            source="simulator",
            description="Controlled DDoS scenario launched in sandbox environment.",
        ),
        TimelineEvent(
            incident_id=incident.id,
            timestamp=detected_at,
            event="Incident Detected",
            actor="siem-monitor",
            source="system",
            description="Automated threshold alert for sustained volumetric traffic flood.",
        ),
        TimelineEvent(
            incident_id=incident.id,
            timestamp=detected_at + timedelta(seconds=15),
            event="Indicators Extracted",
            actor="system",
            source="system",
            description="Extracted source IPs and sustained request-rate anomaly indicators.",
        ),
        TimelineEvent(
            incident_id=incident.id,
            timestamp=detected_at + timedelta(seconds=30),
            event="NIST Phase Assigned",
            actor="system",
            source="system",
            description="Incident initialized under NIST phase: Detection & Analysis.",
            new_value="Detection & Analysis",
        ),
    ]
    db.add_all(timeline_events)

    # 6. Record Initial NIST History
    nist_entry = NISTHistory(
        incident_id=incident.id,
        phase="Detection & Analysis",
        timestamp=detected_at,
        actor="system",
        rationale="Automated triage of a volumetric DDoS pattern exceeding public web tier traffic thresholds.",
    )
    db.add(nist_entry)

    db.commit()
    db.refresh(incident)
    return incident
