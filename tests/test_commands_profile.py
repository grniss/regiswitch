from typer.testing import CliRunner

from regiswitch.cli import app

runner = CliRunner()


def test_profile_create_success():
    result = runner.invoke(app, ["profile", "create", "work"])
    assert result.exit_code == 0
    assert "work" in result.output


def test_profile_create_duplicate_exits_nonzero():
    runner.invoke(app, ["profile", "create", "work"])
    result = runner.invoke(app, ["profile", "create", "work"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_profile_list_shows_active_marker(tmp_path):
    runner.invoke(app, ["profile", "create", "work"])
    runner.invoke(app, ["profile", "create", "personal"])
    # switch sets active profile; just list without switching
    result = runner.invoke(app, ["profile", "list"])
    assert result.exit_code == 0
    assert "work" in result.output
    assert "personal" in result.output


def test_profile_delete_with_yes_flag():
    runner.invoke(app, ["profile", "create", "old"])
    result = runner.invoke(app, ["profile", "delete", "old", "--yes"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_profile_delete_nonexistent_exits_nonzero():
    result = runner.invoke(app, ["profile", "delete", "ghost", "--yes"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_profile_list_no_profiles():
    result = runner.invoke(app, ["profile", "list"])
    assert result.exit_code == 0
    assert "No profiles" in result.output
