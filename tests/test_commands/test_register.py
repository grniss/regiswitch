from typer.testing import CliRunner

from regiswitch.cli import app

runner = CliRunner()


def test_register_file(initialized_registry, registry_dir, sample_file):
    result = runner.invoke(app, ["register", str(sample_file)])
    assert result.exit_code == 0
    assert "Registered" in result.output


def test_register_nonexistent_fails(initialized_registry, registry_dir, tmp_path):
    ghost = tmp_path / "ghost.txt"
    result = runner.invoke(app, ["register", str(ghost)])
    assert result.exit_code != 0


def test_register_duplicate_fails(initialized_registry, registry_dir, sample_file):
    runner.invoke(app, ["register", str(sample_file)])
    result = runner.invoke(app, ["register", str(sample_file)])
    assert result.exit_code == 1


def test_unregister_file(initialized_registry, registry_dir, sample_file):
    runner.invoke(app, ["register", str(sample_file)])
    result = runner.invoke(app, ["unregister", str(sample_file)])
    assert result.exit_code == 0
    assert "Unregistered" in result.output


def test_unregister_not_registered_fails(initialized_registry, registry_dir, sample_file):
    result = runner.invoke(app, ["unregister", str(sample_file)])
    assert result.exit_code == 1
