from typer.testing import CliRunner
from regiswitch.cli import app
from regiswitch.core.backends.local import LocalBackend

runner = CliRunner()


def test_config_auto_save_enable(backend: LocalBackend):
    backend.init()
    result = runner.invoke(app, ["config", "auto-save", "--enable"])
    assert result.exit_code == 0
    assert "enabled" in result.output.lower()


def test_config_auto_save_disable(backend: LocalBackend):
    backend.init()
    result = runner.invoke(app, ["config", "auto-save", "--disable"])
    assert result.exit_code == 0
    assert "disabled" in result.output.lower()


def test_config_auto_save_default_is_enable(backend: LocalBackend):
    backend.init()
    result = runner.invoke(app, ["config", "auto-save"])
    assert result.exit_code == 0
    assert "enabled" in result.output.lower()
