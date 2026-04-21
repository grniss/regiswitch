from pathlib import Path
from typer.testing import CliRunner
from regiswitch.cli import app
from regiswitch.core.backends.local import LocalBackend

runner = CliRunner()


def test_status_shows_no_active_profile(backend: LocalBackend):
    backend.init()
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "none" in result.output.lower() or "active" in result.output.lower()


def test_status_shows_active_profile(backend: LocalBackend):
    backend.init()
    runner.invoke(app, ["profile", "create", "work"])
    runner.invoke(app, ["switch", "work"])
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "work" in result.output


def test_status_shows_registered_files(backend: LocalBackend, sample_file: Path):
    backend.init()
    runner.invoke(app, ["register", str(sample_file)])
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "sample.txt" in result.output


def test_status_not_initialized(backend: LocalBackend):
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 1
