from typer.testing import CliRunner

from regiswitch.cli import app

runner = CliRunner()


def test_save_to_active_profile(initialized_registry, registry_dir, sample_file):
    runner.invoke(app, ["profile", "create", "work"])
    runner.invoke(app, ["switch", "work"])
    runner.invoke(app, ["register", str(sample_file)])
    result = runner.invoke(app, ["save"])
    assert result.exit_code == 0
    assert "work" in result.output


def test_save_to_named_profile(initialized_registry, registry_dir, sample_file):
    runner.invoke(app, ["profile", "create", "work"])
    runner.invoke(app, ["profile", "create", "backup"])
    runner.invoke(app, ["switch", "work"])
    runner.invoke(app, ["register", str(sample_file)])
    result = runner.invoke(app, ["save", "backup"])
    assert result.exit_code == 0
    assert "backup" in result.output


def test_save_no_profiles_fails(initialized_registry, registry_dir):
    result = runner.invoke(app, ["save"])
    assert result.exit_code == 1


def test_save_to_nonexistent_profile_fails(initialized_registry, registry_dir):
    runner.invoke(app, ["profile", "create", "work"])
    result = runner.invoke(app, ["save", "ghost"])
    assert result.exit_code == 1
