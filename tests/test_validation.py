"""Tests for envault.validation and envault.cli_validation."""

from __future__ import annotations

import os
import pytest
from click.testing import CliRunner

from envault.validation import validate_key, validate_value, validate_key_value
from envault.cli_validation import validation_cmd


# ---------------------------------------------------------------------------
# validate_key
# ---------------------------------------------------------------------------

def test_valid_key_simple():
    assert validate_key("MY_SECRET").valid


def test_valid_key_with_digits():
    assert validate_key("DB_HOST_1").valid


def test_valid_key_leading_underscore():
    assert validate_key("_INTERNAL").valid


def test_invalid_key_empty():
    result = validate_key("")
    assert not result.valid
    assert any("empty" in e.lower() for e in result.errors)


def test_invalid_key_starts_with_digit():
    result = validate_key("1BAD_KEY")
    assert not result.valid


def test_invalid_key_contains_hyphen():
    result = validate_key("BAD-KEY")
    assert not result.valid


def test_invalid_key_too_long():
    result = validate_key("A" * 129)
    assert not result.valid
    assert any("length" in e.lower() for e in result.errors)


# ---------------------------------------------------------------------------
# validate_value
# ---------------------------------------------------------------------------

def test_valid_value_empty_string():
    assert validate_value("").valid


def test_valid_value_normal():
    assert validate_value("supersecret123!").valid


def test_invalid_value_none():
    result = validate_value(None)  # type: ignore[arg-type]
    assert not result.valid


def test_invalid_value_too_long():
    result = validate_value("x" * 65537)
    assert not result.valid
    assert any("length" in e.lower() for e in result.errors)


# ---------------------------------------------------------------------------
# validate_key_value
# ---------------------------------------------------------------------------

def test_valid_pair():
    assert validate_key_value("API_KEY", "abc123").valid


def test_invalid_pair_bad_key_good_value():
    result = validate_key_value("bad-key", "value")
    assert not result.valid


def test_invalid_pair_accumulates_errors():
    result = validate_key_value("bad-key", "x" * 65537)
    assert len(result.errors) >= 2


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

runner = CliRunner()


def test_cli_key_valid():
    res = runner.invoke(validation_cmd, ["key", "GOOD_KEY"])
    assert res.exit_code == 0
    assert "valid" in res.output


def test_cli_key_invalid():
    res = runner.invoke(validation_cmd, ["key", "123bad"])
    assert res.exit_code != 0


def test_cli_value_valid():
    res = runner.invoke(validation_cmd, ["value", "mypassword"])
    assert res.exit_code == 0


def test_cli_pair_valid():
    res = runner.invoke(validation_cmd, ["pair", "TOKEN", "abc"])
    assert res.exit_code == 0


def test_cli_pair_invalid():
    res = runner.invoke(validation_cmd, ["pair", "bad-key", "val"])
    assert res.exit_code != 0
