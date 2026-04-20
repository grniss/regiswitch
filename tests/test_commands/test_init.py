from pathlib import Path

from typer.testing import CliRunner

from regiswitch.cli import app

runner = CliRunner()


def test_init_success(tmp_path: Path):
    result = runner.invoke(app, ["init", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / ".regiswitch").is_dir()


def test_init_already_initialized(tmp_path: Path):
    runner.invoke(app, ["init", str(tmp_path)])
    result = runner.invoke(app, ["init", str(tmp_path)])
    assert result.exit_code == 1


def test_init_default_cwd(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert (tmp_path / ".regiswitch").is_dir()
