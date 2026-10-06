from datetime import datetime, timedelta, timezone


def calculate_deadline(detected_at: datetime) -> datetime:
    """Return the deadline 72 hours after detection."""
    return detected_at + timedelta(hours=72)  # Add the 72-hour response window.


def get_clock_status(
    detected_at: datetime, deadline_at: datetime
) -> dict[str, datetime | str]:
    """Return the clock timestamps and its current status."""
    current_time = datetime.now(timezone.utc)  # Read the current time in UTC.
    if deadline_at.tzinfo is None:
        deadline_at = deadline_at.replace(tzinfo=timezone.utc)
    status = "active" if current_time < deadline_at else "expired"  # Check the deadline.
    return {
        "detected_at": detected_at,
        "deadline_at": deadline_at,
        "status": status,
    }
