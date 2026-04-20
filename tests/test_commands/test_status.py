from pathlib import Path

from typer.testing import CliRunner

from regiswitch.cli import app
from regiswitch.core.engine import create_profile, init_project, register_file, save_to_profile

runner = CliRunner()


def test_status_no_profile(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "none" in result.output


def test_status_shows_active_profile(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    create_profile(tmp_path, "dev")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "dev" in result.output


def test_status_shows_drift(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    env = tmp_path / ".env"
    env.write_text("K=original")
    register_file(tmp_path, ".env")
    create_profile(tmp_path, "dev")
    save_to_profile(tmp_path, "dev")
    env.write_text("K=modified")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert ".env" in result.output


def test_status_not_initialized(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 1
