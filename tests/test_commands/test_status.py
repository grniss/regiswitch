from typer.testing import CliRunner

from regiswitch.cli import app

runner = CliRunner()


def test_status_shows_no_active_profile(initialized_registry, registry_dir):
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "none" in result.output.lower() or "active" in result.output.lower()


def test_status_shows_active_profile(initialized_registry, registry_dir):
    runner.invoke(app, ["profile", "create", "work"])
    runner.invoke(app, ["switch", "work"])
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "work" in result.output


def test_status_shows_registered_files(initialized_registry, registry_dir, sample_file):
    runner.invoke(app, ["register", str(sample_file)])
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "sample.txt" in result.output


def test_status_not_initialized(registry_dir):
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 1
