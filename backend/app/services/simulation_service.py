from datetime import datetime, timedelta, timezone  # Import UTC timestamps and time offsets.

from app.models.incident import Incident  # Import the incident model.
from app.models.indicator import Indicator  # Import the indicator model.
from app.services.timeline_service import record_event  # Import timeline event recording.


def create_brute_force_simulation(db):  # Create and persist a brute-force incident simulation.
    detected_at = datetime.now(timezone.utc)  # Capture the detection time in UTC.
    incident = Incident(  # Build the simulated incident.
        title="Multiple Failed Login Attempts",  # Set the incident title.
        description="Repeated login attempts detected from an unusual IP address",  # Set the incident description.
        what_happened="Multiple accounts received failed logins within a short time",  # Describe what happened.
        source="SIEM",  # Set the incident source.
        initial_impact="Potential account compromise",  # Set the initial impact.
        attack_type="Brute Force",  # Set the attack type.
        severity="Not Determined",  # Set the initial severity.
        status="Open",  # Set the initial status.
        nist_phase="Detection & Analysis",  # Set the NIST phase.
        detected_at=detected_at,  # Store when the incident was detected.
        deadline_at=detected_at + timedelta(hours=72),  # Set the response deadline.
    )
    db.add(incident)  # Stage the incident for insertion.
    db.flush()  # Generate the incident identifier before adding indicators.
    record_event(  # Record the simulated incident creation.
        db,
        incident.id,
        "Incident Created",
        "simulator",
        "system",
        description="Incident created by brute force simulation",
        new_value=incident.title,
    )

    indicators = [  # Build the incident indicators.
        Indicator(  # Create the suspicious source indicator.
            incident_id=incident.id,  # Link the indicator to the incident.
            type="IP",  # Set the indicator type.
            value="203.0.113.45",  # Set the suspicious source value.
            note="Suspicious login source",  # Explain the indicator.
        ),
        Indicator(  # Create the targeted username indicator.
            incident_id=incident.id,  # Link the indicator to the incident.
            type="Username",  # Set the indicator type.
            value="admin",  # Set the targeted account value.
            note="Targeted account",  # Explain the indicator.
        ),
    ]
    db.add_all(indicators)  # Stage the incident indicators for insertion.
    for indicator in indicators:
        record_event(  # Record each simulated indicator.
            db,
            incident.id,
            "Indicator Added",
            "simulator",
            "system",
            new_value=f"{indicator.type}: {indicator.value}",
        )
    db.commit()  # Commit the incident and indicators.
    db.refresh(incident)  # Refresh the incident from the database.
    return incident  # Return the persisted incident.


def create_phishing_simulation(db):  # Create and persist a phishing incident simulation.
    detected_at = datetime.now(timezone.utc)  # Capture the detection time in UTC.
    incident = Incident(  # Build the simulated incident.
        title="Suspicious Email Requesting Credentials",  # Set the incident title.
        description="Employees received emails asking them to verify their account through a link",  # Set the incident description.
        what_happened="Multiple employees received an email that appears to come from the payroll team and links to an unfamiliar login page",  # Describe what happened.
        source="Email Security Gateway",  # Set the incident source.
        initial_impact="Potential credential theft",  # Set the initial impact.
        attack_type="Phishing",  # Set the attack type.
        severity="Not Determined",  # Set the initial severity.
        status="Open",  # Set the initial status.
        nist_phase="Detection & Analysis",  # Set the NIST phase.
        detected_at=detected_at,  # Store when the incident was detected.
        deadline_at=detected_at + timedelta(hours=72),  # Set the response deadline.
    )
    db.add(incident)  # Stage the incident for insertion.
    db.flush()  # Generate the incident identifier before adding indicators.
    record_event(  # Record the simulated incident creation.
        db,
        incident.id,
        "Incident Created",
        "simulator",
        "system",
        description="Incident created by phishing simulation",
        new_value=incident.title,
    )

    indicators = [  # Build the incident indicators.
        Indicator(  # Create the suspicious sender indicator.
            incident_id=incident.id,
            type="Email",
            value="[payroll-update@secure-payroll.example](mailto:payroll-update@secure-payroll.example)",
            note="Suspicious sender address",
        ),
        Indicator(  # Create the look-alike domain indicator.
            incident_id=incident.id,
            type="Domain",
            value="secure-payroll.example",
            note="Look-alike domain",
        ),
        Indicator(  # Create the fake login URL indicator.
            incident_id=incident.id,
            type="URL",
            value="[http://secure-payroll.example/login](http://secure-payroll.example/login)",
            note="Fake login page link",
        ),
    ]
    db.add_all(indicators)  # Stage the incident indicators for insertion.
    for indicator in indicators:
        record_event(  # Record each simulated indicator.
            db,
            incident.id,
            "Indicator Added",
            "simulator",
            "system",
            new_value=f"{indicator.type}: {indicator.value}",
        )
    db.commit()  # Commit the incident and indicators.
    db.refresh(incident)  # Refresh the incident from the database.
    return incident  # Return the persisted incident.
