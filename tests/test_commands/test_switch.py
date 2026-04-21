from pathlib import Path
from typer.testing import CliRunner
from regiswitch.cli import app
from regiswitch.core.backends.local import LocalBackend

runner = CliRunner()


def test_switch_profile(backend: LocalBackend):
    backend.init()
    runner.invoke(app, ["profile", "create", "work"])
    result = runner.invoke(app, ["switch", "work"])
    assert result.exit_code == 0
    assert "work" in result.output


def test_switch_nonexistent_fails(backend: LocalBackend):
    backend.init()
    result = runner.invoke(app, ["switch", "ghost"])
    assert result.exit_code == 1


def test_switch_restores_files(backend: LocalBackend, sample_file: Path):
    backend.init()
    runner.invoke(app, ["profile", "create", "a"])
    runner.invoke(app, ["switch", "a"])
    runner.invoke(app, ["register", str(sample_file)])
    sample_file.write_text("version-a")
    runner.invoke(app, ["save"])
    runner.invoke(app, ["profile", "create", "b"])
    sample_file.write_text("version-b")
    runner.invoke(app, ["save", "b"])
    runner.invoke(app, ["switch", "a"])
    assert sample_file.read_text() == "version-a"
