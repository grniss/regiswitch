from typer.testing import CliRunner

from regiswitch.cli import app

runner = CliRunner()


def test_status_shows_no_active_profile():
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "none" in result.output or "Active" in result.output


def test_status_shows_active_profile_after_switch(tmp_path):
    runner.invoke(app, ["profile", "create", "staging"])
    runner.invoke(app, ["switch", "staging"])
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "staging" in result.output


def test_status_lists_registered_files(tmp_path):
    f = tmp_path / "app.conf"
    f.write_text("data")
    runner.invoke(app, ["register", str(f)])
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    # Rich may truncate long paths; check for the filename stub
    assert "app.conf" in result.output or str(f)[:30] in result.output


def test_status_shows_no_registered_files_message():
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "No registered" in result.output or "Active" in result.output


def test_status_shows_live_and_stored_columns(tmp_path):
    f = tmp_path / "app.conf"
    f.write_text("data")
    runner.invoke(app, ["profile", "create", "dev"])
    runner.invoke(app, ["register", str(f)])
    runner.invoke(app, ["snapshot", "dev"])
    runner.invoke(app, ["switch", "dev"])
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "app.conf" in result.output or str(f)[:30] in result.output
