import math

from config import VALID_FREQUENCIES


class ValidationError(Exception):
    """Raised when user/tool input is invalid."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def validate_number(
    value,
    field_name: str,
    allow_zero: bool = False,
    allow_none: bool = False
):
    """Validate and convert a value into a finite float."""

    if value is None:
        if allow_none:
            return None
        raise ValidationError(f"{field_name} is missing.")

    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number.")

    # Reject NaN and infinity.
    if not math.isfinite(value):
        raise ValidationError(
            f"{field_name} must be a finite number."
        )

    if allow_zero:
        if value < 0:
            raise ValidationError(
                f"{field_name} cannot be negative."
            )
    else:
        if value <= 0:
            raise ValidationError(
                f"{field_name} must be greater than zero."
            )

    return value


def validate_frequency(frequency: str) -> str:
    """Validate commitment frequency."""

    if not isinstance(frequency, str):
        raise ValidationError(
            "frequency must be a text value."
        )

    frequency = frequency.strip().lower()

    if frequency not in VALID_FREQUENCIES:
        raise ValidationError(
            f"frequency must be one of "
            f"{sorted(VALID_FREQUENCIES)}, "
            f"got '{frequency}'."
        )

    return frequency


def validate_boolean(value, field_name: str) -> bool:
    """Validate a boolean value without Python's bool('false') trap."""

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()

        if normalized == "true":
            return True

        if normalized == "false":
            return False

    raise ValidationError(
        f"{field_name} must be true or false."
    )