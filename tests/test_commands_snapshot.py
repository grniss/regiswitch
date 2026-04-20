from typer.testing import CliRunner

from regiswitch.cli import app

runner = CliRunner()


def test_snapshot_into_named_profile(tmp_path):
    f = tmp_path / "app.conf"
    f.write_text("data")
    runner.invoke(app, ["profile", "create", "dev"])
    runner.invoke(app, ["register", str(f)])
    result = runner.invoke(app, ["snapshot", "dev"])
    assert result.exit_code == 0
    assert "Snapshot saved" in result.output


def test_snapshot_uses_active_profile(tmp_path):
    f = tmp_path / "app.conf"
    f.write_text("data")
    runner.invoke(app, ["profile", "create", "dev"])
    runner.invoke(app, ["register", str(f)])
    runner.invoke(app, ["switch", "dev"])
    result = runner.invoke(app, ["snapshot"])
    assert result.exit_code == 0
    assert "Snapshot saved" in result.output


def test_snapshot_no_active_profile_exits_nonzero(tmp_path):
    f = tmp_path / "app.conf"
    f.write_text("data")
    runner.invoke(app, ["register", str(f)])
    result = runner.invoke(app, ["snapshot"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_snapshot_warns_missing_live_file(tmp_path):
    f = tmp_path / "ghost.conf"  # does not exist
    runner.invoke(app, ["profile", "create", "dev"])
    runner.invoke(app, ["register", str(f)])
    result = runner.invoke(app, ["snapshot", "dev"])
    assert result.exit_code == 0
    assert "Warning" in result.output or str(f) in result.output
