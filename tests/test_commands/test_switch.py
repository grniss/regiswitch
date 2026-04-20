from pathlib import Path

from typer.testing import CliRunner

from regiswitch.cli import app
from regiswitch.core.engine import create_profile, init_project, register_file, save_to_profile
from regiswitch.utils.fs import load_config

runner = CliRunner()


def test_switch_restores_files(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    env = tmp_path / ".env"
    env.write_text("K=dev")
    register_file(tmp_path, ".env")
    create_profile(tmp_path, "dev")
    save_to_profile(tmp_path, "dev")
    env.write_text("K=changed")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["switch", "dev"])
    assert result.exit_code == 0
    assert env.read_text() == "K=dev"


def test_switch_sets_active_profile(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    create_profile(tmp_path, "dev")
    create_profile(tmp_path, "prod")
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["switch", "prod"])
    config = load_config(tmp_path)
    assert config.current_profile == "prod"


def test_switch_nonexistent_profile_fails(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["switch", "ghost"])
    assert result.exit_code == 1


def test_switch_no_stored_files(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    create_profile(tmp_path, "dev")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["switch", "dev"])
    assert result.exit_code == 0
    assert "no stored files" in result.output
