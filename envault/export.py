"""Export and import .env file functionality for envault."""

from pathlib import Path
from typing import Optional


def parse_dotenv(content: str) -> dict[str, str]:
    """Parse a .env file string into a key-value dictionary."""
    result = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip surrounding quotes
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        if key:
            result[key] = value
    return result


def render_dotenv(secrets: dict[str, str]) -> str:
    """Render a key-value dictionary to a .env file string."""
    lines = []
    for key, value in sorted(secrets.items()):
        # Quote values containing spaces or special characters
        if any(c in value for c in (" ", "#", "'", '"', "\n")):
            value = '"' + value.replace('"', '\\"') + '"'
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def import_dotenv_file(path: str | Path) -> dict[str, str]:
    """Read a .env file from disk and return parsed key-value pairs."""
    content = Path(path).read_text(encoding="utf-8")
    return parse_dotenv(content)


def export_dotenv_file(secrets: dict[str, str], path: str | Path) -> None:
    """Write secrets to a .env file on disk."""
    Path(path).write_text(render_dotenv(secrets), encoding="utf-8")
