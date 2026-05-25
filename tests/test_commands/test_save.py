from pathlib import Path

from typer.testing import CliRunner

from regiswitch.cli import app
from regiswitch.core.engine import create_profile, init_project, register_file
from regiswitch.core.storage import LocalStorageBackend
from regiswitch.models.config import RegiswitchConfig

runner = CliRunner()


def make_storage(root: Path) -> LocalStorageBackend:
    return LocalStorageBackend(RegiswitchConfig.default_profiles_dir(root))


def test_save_to_active_profile(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    (tmp_path / ".env").write_text("K=V")
    register_file(tmp_path, ".env")
    storage = make_storage(tmp_path)
    create_profile(tmp_path, "dev", storage)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["save"])
    assert result.exit_code == 0
    assert storage.has_file(".env", "dev")


def test_save_with_explicit_profile(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    (tmp_path / ".env").write_text("K=V")
    register_file(tmp_path, ".env")
    storage = make_storage(tmp_path)
    create_profile(tmp_path, "prod", storage)
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
