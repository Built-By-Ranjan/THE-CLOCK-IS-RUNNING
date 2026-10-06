from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional


def ensure_utc(dt: Optional[datetime] = None) -> datetime:
    """Ensure a datetime object is timezone-aware and set to UTC."""
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def calculate_deadline(detected_at: datetime) -> datetime:
    """
    Calculate the 72-hour deadline from incident detection.
    Rule: deadline_at = detected_at + 72 hours
    The backend strictly owns this calculation.
    """
    detected_utc = ensure_utc(detected_at)
    return detected_utc + timedelta(hours=72)


def get_clock_summary(detected_at: datetime, deadline_at: datetime, current_time: Optional[datetime] = None) -> Dict[str, Any]:
    """Calculate remaining time against the 72-hour clock."""
    now = ensure_utc(current_time)
    deadline = ensure_utc(deadline_at)
    detected = ensure_utc(detected_at)

    remaining_delta = deadline - now
    elapsed_delta = now - detected

    remaining_seconds = max(0.0, remaining_delta.total_seconds())
    is_expired = remaining_delta.total_seconds() <= 0

    hours = int(remaining_seconds // 3600)
    minutes = int((remaining_seconds % 3600) // 60)
    seconds = int(remaining_seconds % 60)

    return {
        "detected_at": detected.isoformat(),
        "deadline_at": deadline.isoformat(),
        "current_time": now.isoformat(),
        "remaining_seconds": remaining_seconds,
        "elapsed_seconds": max(0.0, elapsed_delta.total_seconds()),
        "is_expired": is_expired,
        "formatted_remaining": f"{hours:02d}h {minutes:02d}m {seconds:02d}s" if not is_expired else "00h 00m 00s (EXPIRED)",
    }
