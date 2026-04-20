from typer.testing import CliRunner

from regiswitch.cli import app

runner = CliRunner()


def test_register_success(tmp_path):
    f = tmp_path / "settings.cfg"
    f.write_text("key=val")
    result = runner.invoke(app, ["register", str(f)])
    assert result.exit_code == 0
    assert "Registered" in result.output


def test_register_duplicate_exits_nonzero(tmp_path):
    f = tmp_path / "settings.cfg"
    f.write_text("key=val")
    runner.invoke(app, ["register", str(f)])
    result = runner.invoke(app, ["register", str(f)])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_unregister_success(tmp_path):
    f = tmp_path / "settings.cfg"
    f.write_text("key=val")
    runner.invoke(app, ["register", str(f)])
    result = runner.invoke(app, ["unregister", str(f)])
    assert result.exit_code == 0
    assert "Unregistered" in result.output


def test_unregister_not_registered_exits_nonzero(tmp_path):
    f = tmp_path / "settings.cfg"
    result = runner.invoke(app, ["unregister", str(f)])
    assert result.exit_code != 0
    assert "Error" in result.output
