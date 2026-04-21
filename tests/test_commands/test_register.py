from pathlib import Path
from typer.testing import CliRunner
from regiswitch.cli import app
from regiswitch.core.backends.local import LocalBackend

runner = CliRunner()


def test_register_file(backend: LocalBackend, sample_file: Path):
    backend.init()
    result = runner.invoke(app, ["register", str(sample_file)])
    assert result.exit_code == 0
    assert "Registered" in result.output


def test_register_nonexistent_fails(backend: LocalBackend, tmp_path: Path):
    backend.init()
    ghost = tmp_path / "ghost.txt"
    result = runner.invoke(app, ["register", str(ghost)])
    assert result.exit_code != 0


def test_register_duplicate_fails(backend: LocalBackend, sample_file: Path):
    backend.init()
    runner.invoke(app, ["register", str(sample_file)])
    result = runner.invoke(app, ["register", str(sample_file)])
    assert result.exit_code == 1


def test_unregister_file(backend: LocalBackend, sample_file: Path):
    backend.init()
    runner.invoke(app, ["register", str(sample_file)])
    result = runner.invoke(app, ["unregister", str(sample_file)])
    assert result.exit_code == 0
    assert "Unregistered" in result.output


def test_unregister_not_registered_fails(backend: LocalBackend, sample_file: Path):
    backend.init()
    result = runner.invoke(app, ["unregister", str(sample_file)])
    assert result.exit_code == 1
