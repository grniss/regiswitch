from typer.testing import CliRunner

from regiswitch.cli import app

runner = CliRunner()


def test_init_creates_registry(registry_dir):
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "initialized" in result.output.lower()


def test_init_idempotent_shows_already_message(registry_dir):
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "already" in result.output.lower()


def test_init_force_reinitializes(registry_dir):
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["init", "--force"])
    assert result.exit_code == 0
    assert "initialized" in result.output.lower()
