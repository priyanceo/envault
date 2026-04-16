"""Tests for envault.export module."""

import pytest
from pathlib import Path
from envault.export import parse_dotenv, render_dotenv, import_dotenv_file, export_dotenv_file


def test_parse_dotenv_basic():
    content = "KEY=value\nFOO=bar\n"
    result = parse_dotenv(content)
    assert result == {"KEY": "value", "FOO": "bar"}


def test_parse_dotenv_ignores_comments_and_blanks():
    content = "# comment\n\nKEY=value\n"
    result = parse_dotenv(content)
    assert result == {"KEY": "value"}


def test_parse_dotenv_strips_quotes():
    content = 'KEY="hello world"\nFOO=\'bar\'\n'
    result = parse_dotenv(content)
    assert result["KEY"] == "hello world"
    assert result["FOO"] == "bar"


def test_parse_dotenv_value_with_equals():
    content = "KEY=a=b=c\n"
    result = parse_dotenv(content)
    assert result["KEY"] == "a=b=c"


def test_parse_dotenv_skips_invalid_lines():
    content = "NOEQUALS\nKEY=val\n"
    result = parse_dotenv(content)
    assert "NOEQUALS" not in result
    assert result["KEY"] == "val"


def test_render_dotenv_basic():
    secrets = {"KEY": "value", "FOO": "bar"}
    output = render_dotenv(secrets)
    assert "KEY=value" in output
    assert "FOO=bar" in output


def test_render_dotenv_quotes_spaces():
    secrets = {"KEY": "hello world"}
    output = render_dotenv(secrets)
    assert 'KEY="hello world"' in output


def test_render_dotenv_empty():
    assert render_dotenv({}) == ""


def test_roundtrip():
    original = {"DATABASE_URL": "postgres://localhost/db", "SECRET": "abc123"}
    rendered = render_dotenv(original)
    parsed = parse_dotenv(rendered)
    assert parsed == original


def test_import_dotenv_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\nFOO=bar\n")
    result = import_dotenv_file(env_file)
    assert result == {"KEY": "value", "FOO": "bar"}


def test_export_dotenv_file(tmp_path):
    env_file = tmp_path / ".env"
    secrets = {"KEY": "value", "FOO": "bar"}
    export_dotenv_file(secrets, env_file)
    content = env_file.read_text()
    parsed = parse_dotenv(content)
    assert parsed == secrets
