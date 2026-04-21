from typer.testing import CliRunner
from regiswitch.cli import app
from regiswitch.core.backends.local import LocalBackend

runner = CliRunner()


def test_init_creates_registry(backend: LocalBackend):
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "initialized" in result.output.lower()
    assert backend.is_initialized()


def test_init_idempotent_shows_already_message(backend: LocalBackend):
    backend.init()
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "already" in result.output.lower()


def test_init_force_reinitializes(backend: LocalBackend):
    backend.init()
    result = runner.invoke(app, ["init", "--force"])
    assert result.exit_code == 0
    assert "initialized" in result.output.lower()
