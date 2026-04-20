from typer.testing import CliRunner

from regiswitch.cli import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "regiswitch" in result.output.lower() or "switch" in result.output.lower()


def test_profile_create():
    result = runner.invoke(app, ["profile", "create", "work"])
    assert result.exit_code == 0
    assert "work" in result.output


def test_profile_create_duplicate():
    runner.invoke(app, ["profile", "create", "work"])
    result = runner.invoke(app, ["profile", "create", "work"])
    assert result.exit_code != 0


def test_profile_list_empty():
    result = runner.invoke(app, ["profile", "list"])
    assert result.exit_code == 0
    assert "No profiles" in result.output


def test_profile_list_shows_profiles():
    runner.invoke(app, ["profile", "create", "work"])
    result = runner.invoke(app, ["profile", "list"])
    assert result.exit_code == 0
    assert "work" in result.output


def test_profile_delete_with_yes(tmp_path):
    runner.invoke(app, ["profile", "create", "old"])
    result = runner.invoke(app, ["profile", "delete", "old", "--yes"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_register_file(tmp_path):
    f = tmp_path / "myfile.cfg"
    f.write_text("data")
    result = runner.invoke(app, ["register", str(f)])
    assert result.exit_code == 0
    assert "Registered" in result.output


def test_unregister_file(tmp_path):
    f = tmp_path / "myfile.cfg"
    f.write_text("data")
    runner.invoke(app, ["register", str(f)])
    result = runner.invoke(app, ["unregister", str(f)])
    assert result.exit_code == 0
    assert "Unregistered" in result.output


def test_switch_nonexistent_profile():
    result = runner.invoke(app, ["switch", "ghost"])
    assert result.exit_code != 0


def test_status_empty():
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0


def test_snapshot_no_active_profile(tmp_path):
    f = tmp_path / "myfile.cfg"
    f.write_text("data")
    runner.invoke(app, ["register", str(f)])
    result = runner.invoke(app, ["snapshot"])
    assert result.exit_code != 0
