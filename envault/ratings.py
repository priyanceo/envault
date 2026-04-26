"""Secret ratings — let users rate secrets by importance (1–5 stars)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envault.storage import get_vault_path, get_secret


def _get_ratings_path(vault_dir: Optional[Path] = None) -> Path:
    base = vault_dir if vault_dir else get_vault_path().parent
    return base / "ratings.json"


def _load_ratings(vault_dir: Optional[Path] = None) -> Dict[str, int]:
    path = _get_ratings_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_ratings(data: Dict[str, int], vault_dir: Optional[Path] = None) -> None:
    path = _get_ratings_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_rating(
    key: str,
    stars: int,
    password: str,
    vault_dir: Optional[Path] = None,
) -> None:
    """Set a 1–5 star rating for *key*. Raises ValueError for out-of-range stars."""
    if stars < 1 or stars > 5:
        raise ValueError(f"Rating must be between 1 and 5, got {stars}")
    # Verify the key exists
    get_secret(key, password, vault_dir=vault_dir)
    ratings = _load_ratings(vault_dir)
    ratings[key] = stars
    _save_ratings(ratings, vault_dir)


def get_rating(key: str, vault_dir: Optional[Path] = None) -> Optional[int]:
    """Return the star rating for *key*, or None if not rated."""
    return _load_ratings(vault_dir).get(key)


def remove_rating(key: str, vault_dir: Optional[Path] = None) -> bool:
    """Remove the rating for *key*. Returns True if removed, False if absent."""
    ratings = _load_ratings(vault_dir)
    if key not in ratings:
        return False
    del ratings[key]
    _save_ratings(ratings, vault_dir)
    return True


def list_by_rating(
    min_stars: int = 1,
    max_stars: int = 5,
    vault_dir: Optional[Path] = None,
) -> List[tuple[str, int]]:
    """Return [(key, stars)] sorted by stars descending, filtered by range."""
    ratings = _load_ratings(vault_dir)
    results = [
        (k, v) for k, v in ratings.items() if min_stars <= v <= max_stars
    ]
    return sorted(results, key=lambda x: x[1], reverse=True)
