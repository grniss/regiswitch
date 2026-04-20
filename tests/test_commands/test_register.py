from pathlib import Path

from typer.testing import CliRunner

from regiswitch.cli import app
from regiswitch.core.engine import init_project
from regiswitch.utils.fs import load_config

runner = CliRunner()


def test_register_success(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    (tmp_path / ".env").write_text("K=V")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["register", ".env"])
    assert result.exit_code == 0
    config = load_config(tmp_path)
    assert ".env" in config.registered_files


def test_register_missing_file(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["register", "missing.env"])
    assert result.exit_code == 1


def test_register_already_registered(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    (tmp_path / ".env").write_text("K=V")
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["register", ".env"])
    result = runner.invoke(app, ["register", ".env"])
    assert result.exit_code == 1


def test_unregister_success(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    (tmp_path / ".env").write_text("K=V")
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["register", ".env"])
    result = runner.invoke(app, ["unregister", ".env"])
    assert result.exit_code == 0
    config = load_config(tmp_path)
    assert ".env" not in config.registered_files


def test_unregister_not_registered(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["unregister", "ghost.txt"])
    assert result.exit_code == 1
