from typer.testing import CliRunner

from regiswitch.cli import app

runner = CliRunner()


def test_switch_success(tmp_path):
    f = tmp_path / "app.conf"
    f.write_text("v1")
    runner.invoke(app, ["profile", "create", "dev"])
    runner.invoke(app, ["register", str(f)])
    runner.invoke(app, ["snapshot", "dev"])

    result = runner.invoke(app, ["switch", "dev"])
    assert result.exit_code == 0
    assert "dev" in result.output


def test_switch_nonexistent_profile_exits_nonzero():
    result = runner.invoke(app, ["switch", "ghost"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_switch_warns_on_missing_stored_file(tmp_path):
    f = tmp_path / "app.conf"
    runner.invoke(app, ["profile", "create", "dev"])
    runner.invoke(app, ["register", str(f)])  # file doesn't exist — nothing snapshotted
    result = runner.invoke(app, ["switch", "dev"])
    assert result.exit_code == 0
    assert "Warning" in result.output or "skipped" in result.output or str(f) in result.output


def test_switch_updates_active_profile(tmp_path):
    runner.invoke(app, ["profile", "create", "prod"])
    runner.invoke(app, ["switch", "prod"])
    result = runner.invoke(app, ["status"])
    assert "prod" in result.output
