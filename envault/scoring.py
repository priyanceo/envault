"""Secret scoring: aggregate quality score for vault secrets."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.complexity import score_secret
from envault.ttl import is_expired
from envault.expiry import get_expiry
from envault.storage import get_secret


@dataclass
class SecretScore:
    key: str
    complexity_score: int          # 0-100
    has_expiry: bool
    is_expired: bool
    overall: int                   # 0-100
    suggestions: List[str] = field(default_factory=list)


def _compute_overall(complexity: int, has_expiry: bool, expired: bool) -> int:
    """Combine factors into a 0-100 overall score."""
    score = complexity
    if has_expiry:
        score = min(100, score + 10)
    if expired:
        score = max(0, score - 40)
    return score


def score_key(
    key: str,
    vault_dir: str,
    password: str,
) -> Optional[SecretScore]:
    """Return a SecretScore for *key*, or None if the key does not exist."""
    value = get_secret(vault_dir, password, key)
    if value is None:
        return None

    result = score_secret(value)
    expiry_dt = get_expiry(vault_dir, password, key)
    expired = is_expired(vault_dir, password, key)

    overall = _compute_overall(result.score, expiry_dt is not None, expired)

    suggestions = list(result.suggestions)
    if not expiry_dt:
        suggestions.append("Consider setting an expiry date for this secret.")
    if expired:
        suggestions.append("Secret has expired — rotate it immediately.")

    return SecretScore(
        key=key,
        complexity_score=result.score,
        has_expiry=expiry_dt is not None,
        is_expired=expired,
        overall=overall,
        suggestions=suggestions,
    )


def score_all(
    vault_dir: str,
    password: str,
    keys: List[str],
) -> Dict[str, SecretScore]:
    """Score every key in *keys* and return a mapping key -> SecretScore."""
    results: Dict[str, SecretScore] = {}
    for key in keys:
        s = score_key(key, vault_dir, password)
        if s is not None:
            results[key] = s
    return results
