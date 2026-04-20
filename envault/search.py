"""Search secrets across vault and profiles by key pattern or tag."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from typing import List, Optional

from envault.storage import load_vault
from envault.profile import list_profiles, get_profile_secrets
from envault.tags import get_tags_map


@dataclass
class SearchResult:
    source: str  # "default" or profile name
    key: str
    tags: List[str]


def search_by_pattern(
    vault_dir: str,
    password: str,
    pattern: str,
    include_profiles: bool = True,
) -> List[SearchResult]:
    """Return all secrets whose key matches the glob pattern."""
    results: List[SearchResult] = []
    tags_map = get_tags_map(vault_dir)

    # Search default vault
    vault = load_vault(vault_dir, password)
    for key in vault.keys():
        if fnmatch.fnmatch(key, pattern):
            results.append(
                SearchResult(source="default", key=key, tags=tags_map.get(key, []))
            )

    if not include_profiles:
        return results

    # Search profiles
    for profile in list_profiles(vault_dir, password):
        secrets = get_profile_secrets(vault_dir, password, profile)
        for key in secrets.keys():
            if fnmatch.fnmatch(key, pattern):
                results.append(
                    SearchResult(source=profile, key=key, tags=tags_map.get(key, []))
                )

    return results


def search_by_tag(
    vault_dir: str,
    password: str,
    tag: str,
    include_profiles: bool = True,
) -> List[SearchResult]:
    """Return all secrets that have the given tag."""
    results: List[SearchResult] = []
    tags_map = get_tags_map(vault_dir)

    tagged_keys = {k for k, tags in tags_map.items() if tag in tags}

    vault = load_vault(vault_dir, password)
    for key in vault.keys():
        if key in tagged_keys:
            results.append(
                SearchResult(source="default", key=key, tags=tags_map.get(key, []))
            )

    if not include_profiles:
        return results

    for profile in list_profiles(vault_dir, password):
        secrets = get_profile_secrets(vault_dir, password, profile)
        for key in secrets.keys():
            if key in tagged_keys:
                results.append(
                    SearchResult(source=profile, key=key, tags=tags_map.get(key, []))
                )

    return results
