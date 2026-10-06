from typing import Literal


Status = Literal[
    "Open",
    "Under Investigation",
    "Contained",
    "Eradicated",
    "Recovered",
    "Closed",
]

ALLOWED_STATUSES = (
    "Open",
    "Under Investigation",
    "Contained",
    "Eradicated",
    "Recovered",
    "Closed",
)

ALLOWED_TRANSITIONS = {
    "Open": ("Under Investigation",),
    "Under Investigation": ("Contained",),
    "Contained": ("Eradicated", "Under Investigation"),
    "Eradicated": ("Recovered", "Contained"),
    "Recovered": ("Closed", "Eradicated"),
    "Closed": (),
}


class InvalidStatusTransition(ValueError):
    """Raised when an incident status is not valid for its lifecycle."""


def validate_transition(current: str, new: str) -> None:
    """Validate a status change against the incident lifecycle."""
    valid_statuses = ", ".join(ALLOWED_STATUSES)
    if current not in ALLOWED_STATUSES:
        raise InvalidStatusTransition(
            f"Unknown status '{current}'. Valid statuses: {valid_statuses}"
        )
    if new not in ALLOWED_STATUSES:
        raise InvalidStatusTransition(
            f"Unknown status '{new}'. Valid statuses: {valid_statuses}"
        )
    if current == new:
        return

    allowed = ALLOWED_TRANSITIONS[current]
    if new not in allowed:
        allowed_statuses = ", ".join(allowed) or "nothing"
        raise InvalidStatusTransition(
            f"Cannot change status from {current} to {new}. "
            f"Allowed: {allowed_statuses}"
        )
