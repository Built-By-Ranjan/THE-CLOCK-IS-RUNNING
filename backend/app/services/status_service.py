from typing import List, Dict

VALID_STATUSES: List[str] = [
    "Open",
    "Under Investigation",
    "Contained",
    "Eradicated",
    "Recovered",
    "Closed",
]

# Permitted state transitions for incident lifecycle
ALLOWED_TRANSITIONS: Dict[str, List[str]] = {
    "Open": ["Under Investigation", "Closed"],
    "Under Investigation": ["Contained", "Closed", "Open"],
    "Contained": ["Eradicated", "Under Investigation", "Closed"],
    "Eradicated": ["Recovered", "Under Investigation", "Closed"],
    "Recovered": ["Closed", "Under Investigation"],
    "Closed": ["Open", "Under Investigation"],
}


def validate_status_transition(current_status: str, new_status: str) -> None:
    """
    Validate that changing from current_status to new_status is an allowed transition.
    Raises ValueError on invalid state transition.
    """
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Unknown status '{new_status}'. Valid statuses are: {', '.join(VALID_STATUSES)}")

    if current_status == new_status:
        return

    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    if new_status not in allowed:
        raise ValueError(
            f"Invalid status transition from '{current_status}' to '{new_status}'. "
            f"Allowed next transitions are: {', '.join(allowed) if allowed else 'None'}"
        )
