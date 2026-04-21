"""Tests for envault.audit and cli_audit."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.audit import log_event, read_events, clear_audit_log
from envault.cli_audit import audit_cmd


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def test_log_and_read_events(vault_dir):
    log_event("set", key="FOO", vault_dir=vault_dir)
    log_event("get", key="BAR", vault_dir=vault_dir)
    events = read_events(vault_dir=vault_dir)
    assert len(events) == 2
    assert events[0]["action"] == "set"
    assert events[0]["key"] == "FOO"
    assert events[1]["action"] == "get"
    assert events[1]["key"] == "BAR"


def test_read_events_no_file(vault_dir):
    events = read_events(vault_dir=vault_dir)
    assert events == []


def test_log_event_without_key(vault_dir):
    log_event("rotate", vault_dir=vault_dir)
    events = read_events(vault_dir=vault_dir)
    assert len(events) == 1
    assert "key" not in events[0]
    assert events[0]["action"] == "rotate"


def test_log_event_timestamp_present(vault_dir):
    """Each logged event should include a timestamp field."""
    log_event("set", key="TS_KEY", vault_dir=vault_dir)
    events = read_events(vault_dir=vault_dir)
    assert len(events) == 1
    assert "timestamp" in events[0], "Expected a 'timestamp' field in logged event"


def test_clear_audit_log(vault_dir):
    log_event("set", key="X", vault_dir=vault_dir)
    clear_audit_log(vault_dir=vault_dir)
    assert read_events(vault_dir=vault_dir) == []


def test_clear_audit_log_no_file(vault_dir):
    # Should not raise even if file doesn't exist
    clear_audit_log(vault_dir=vault_dir)


def test_audit_cmd_lists_events(vault_dir):
    log_event("set", key="API_KEY", vault_dir=vault_dir)
    runner = CliRunner()
    result = runner.invoke(audit_cmd, ["--vault-dir", str(vault_dir)])
    assert result.exit_code == 0
    assert "set" in result.output
    assert "API_KEY" in result.output


def test_audit_cmd_empty(vault_dir):
    runner = CliRunner()
    result = runner.invoke(audit_cmd, ["--vault-dir", str(vault_dir)])
    assert result.exit_code == 0
    assert "No audit events" in result.output


def test_audit_cmd_clear(vault_dir):
    log_event("set", key="K", vault_dir=vault_dir)
    runner = CliRunner()
    result = runner.invoke(audit_cmd, ["--vault-dir", str(vault_dir), "--clear"])
    assert result.exit_code == 0
    assert "cleared" in result.output
    assert read_events(vault_dir=vault_dir) == []


def test_audit_cmd_tail(vault_dir):
    for i in range(5):
        log_event("set", key=f"KEY{i}", vault_dir=vault_dir)
    runner = CliRunner()
    result = runner.invoke(audit_cmd, ["--vault-dir", str(vault_dir), "--tail", "2"])
    assert result.exit_code == 0
    assert "KEY4" in result.output
    assert "KEY3" in result.output
    assert "KEY0" not in result.output
