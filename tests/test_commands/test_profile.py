from typer.testing import CliRunner
from regiswitch.cli import app
from regiswitch.core.backends.local import LocalBackend

runner = CliRunner()


def test_profile_create(backend: LocalBackend):
    backend.init()
    result = runner.invoke(app, ["profile", "create", "work"])
    assert result.exit_code == 0
    assert "work" in result.output


def test_profile_create_duplicate_fails(backend: LocalBackend):
    backend.init()
    runner.invoke(app, ["profile", "create", "work"])
    result = runner.invoke(app, ["profile", "create", "work"])
    assert result.exit_code == 1


def test_profile_list_empty(backend: LocalBackend):
    backend.init()
    result = runner.invoke(app, ["profile", "list"])
    assert result.exit_code == 0
    assert "no profiles" in result.output.lower()


def test_profile_list_shows_profiles(backend: LocalBackend):
    backend.init()
    runner.invoke(app, ["profile", "create", "work"])
    runner.invoke(app, ["profile", "create", "personal"])
    result = runner.invoke(app, ["profile", "list"])
    assert result.exit_code == 0
    assert "work" in result.output
    assert "personal" in result.output


def test_profile_delete_with_yes(backend: LocalBackend):
    backend.init()
    runner.invoke(app, ["profile", "create", "work"])
    runner.invoke(app, ["profile", "create", "other"])
    runner.invoke(app, ["switch", "other"])
    result = runner.invoke(app, ["profile", "delete", "work", "--yes"])
    assert result.exit_code == 0
    assert "deleted" in result.output.lower()


def test_profile_delete_nonexistent_fails(backend: LocalBackend):
    backend.init()
    result = runner.invoke(app, ["profile", "delete", "ghost", "--yes"])
    assert result.exit_code == 1


def test_profile_delete_active_fails(backend: LocalBackend):
    backend.init()
    runner.invoke(app, ["profile", "create", "work"])
    runner.invoke(app, ["switch", "work"])
    result = runner.invoke(app, ["profile", "delete", "work", "--yes"])
    assert result.exit_code != 0
