from datetime import datetime, timedelta, timezone

from app.services.clock_service import calculate_deadline, get_clock_status


def test_calculate_deadline_adds_72_hours():
    detected_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

    assert calculate_deadline(detected_at) == detected_at + timedelta(hours=72)


def test_get_clock_status_is_active_before_deadline():
    now = datetime.now(timezone.utc)

    assert get_clock_status(now - timedelta(hours=1), now + timedelta(hours=1))[
        "status"
    ] == "active"


def test_get_clock_status_is_expired_after_deadline():
    now = datetime.now(timezone.utc)

    assert get_clock_status(now - timedelta(hours=2), now - timedelta(hours=1))[
        "status"
    ] == "expired"
