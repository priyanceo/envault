"""Validation rules for secret keys and values in the vault."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


KEY_PATTERN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
MAX_KEY_LENGTH = 128
MAX_VALUE_LENGTH = 65536


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid


def validate_key(key: str) -> ValidationResult:
    """Validate a secret key name."""
    errors: List[str] = []

    if not key:
        errors.append("Key must not be empty.")
        return ValidationResult(valid=False, errors=errors)

    if len(key) > MAX_KEY_LENGTH:
        errors.append(f"Key exceeds maximum length of {MAX_KEY_LENGTH} characters.")

    if not KEY_PATTERN.match(key):
        errors.append(
            "Key must start with a letter or underscore and contain only "
            "letters, digits, or underscores."
        )

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def validate_value(value: str) -> ValidationResult:
    """Validate a secret value."""
    errors: List[str] = []

    if value is None:
        errors.append("Value must not be None.")
        return ValidationResult(valid=False, errors=errors)

    if len(value) > MAX_VALUE_LENGTH:
        errors.append(f"Value exceeds maximum length of {MAX_VALUE_LENGTH} characters.")

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def validate_key_value(key: str, value: str) -> ValidationResult:
    """Validate both a key and its value, combining all errors."""
    key_result = validate_key(key)
    value_result = validate_value(value)
    combined_errors = key_result.errors + value_result.errors
    return ValidationResult(valid=len(combined_errors) == 0, errors=combined_errors)
