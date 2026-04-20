from pathlib import Path

from typer.testing import CliRunner

from regiswitch.cli import app
from regiswitch.core.engine import create_profile, init_project, register_file

runner = CliRunner()


def test_save_to_active_profile(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    (tmp_path / ".env").write_text("K=V")
    register_file(tmp_path, ".env")
    create_profile(tmp_path, "dev")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["save"])
    assert result.exit_code == 0
    assert (tmp_path / ".regiswitch" / "profiles" / "dev" / ".env").exists()


def test_save_with_explicit_profile(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    (tmp_path / ".env").write_text("K=V")
    register_file(tmp_path, ".env")
    create_profile(tmp_path, "prod")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["save", "--profile", "prod"])
    assert result.exit_code == 0


def test_save_no_active_profile_fails(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["save"])
    assert result.exit_code == 1


def test_save_nonexistent_profile_fails(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["save", "--profile", "ghost"])
    assert result.exit_code == 1
