from pathlib import Path

from typer.testing import CliRunner

from regiswitch.cli import app
from regiswitch.core.engine import create_profile, init_project
from regiswitch.core.storage import LocalStorageBackend
from regiswitch.models.config import RegiswitchConfig

runner = CliRunner()


def make_storage(root: Path) -> LocalStorageBackend:
    return LocalStorageBackend(RegiswitchConfig.default_profiles_dir(root))


def test_profile_create_success(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["profile", "create", "dev"])
    assert result.exit_code == 0
    assert make_storage(tmp_path).profile_exists("dev")


def test_profile_create_duplicate(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["profile", "create", "dev"])
    result = runner.invoke(app, ["profile", "create", "dev"])
    assert result.exit_code == 1


def test_profile_list_empty(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["profile", "list"])
    assert result.exit_code == 0
    assert "No profiles" in result.output


def test_profile_list_shows_profiles(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["profile", "create", "dev"])
    result = runner.invoke(app, ["profile", "list"])
    assert result.exit_code == 0
    assert "dev" in result.output


def test_profile_delete_success(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["profile", "create", "dev"])
    result = runner.invoke(app, ["profile", "delete", "dev", "--yes"])
    assert result.exit_code == 0
    assert not make_storage(tmp_path).profile_exists("dev")


def test_profile_delete_not_found(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["profile", "delete", "ghost", "--yes"])
    assert result.exit_code == 1
