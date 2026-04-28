"""Password/secret complexity scoring and enforcement for envault."""

import re
from dataclasses import dataclass, field
from typing import List


MIN_LENGTH = 8
STRONG_LENGTH = 16


@dataclass
class ComplexityResult:
    score: int          # 0-4
    level: str          # weak / fair / good / strong
    suggestions: List[str] = field(default_factory=list)
    passed: bool = True


def score_secret(value: str, min_length: int = MIN_LENGTH) -> ComplexityResult:
    """Score the complexity of a secret value."""
    suggestions: List[str] = []
    score = 0

    if len(value) >= min_length:
        score += 1
    else:
        suggestions.append(f"Use at least {min_length} characters (currently {len(value)}).")

    if len(value) >= STRONG_LENGTH:
        score += 1

    if re.search(r"[A-Z]", value) and re.search(r"[a-z]", value):
        score += 1
    else:
        suggestions.append("Mix uppercase and lowercase letters.")

    if re.search(r"\d", value):
        score += 1
    else:
        suggestions.append("Include at least one digit.")

    if re.search(r"[^A-Za-z0-9]", value):
        score += 1
    else:
        suggestions.append("Add a special character (e.g. !@#$%).")

    # cap at 4
    score = min(score, 4)

    levels = ["weak", "weak", "fair", "good", "strong"]
    level = levels[score]
    passed = len(value) >= min_length

    return ComplexityResult(score=score, level=level, suggestions=suggestions, passed=passed)


def enforce_complexity(value: str, min_score: int = 2, min_length: int = MIN_LENGTH) -> None:
    """Raise ValueError if the secret does not meet the minimum complexity."""
    result = score_secret(value, min_length=min_length)
    if not result.passed or result.score < min_score:
        hints = "  ".join(result.suggestions)
        raise ValueError(
            f"Secret too weak (score {result.score}/{min_score} required). {hints}"
        )
