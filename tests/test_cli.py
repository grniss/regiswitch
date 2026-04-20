import pytest
from click.testing import CliRunner
from regiswitch.cli import main


@pytest.fixture
def runner(tmp_path, monkeypatch):
    monkeypatch.setenv("REGISWITCH_DIR", str(tmp_path))
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / "app.env"
    f.write_text("KEY=dev\n")
    return f


# ------------------------------------------------------------------ profile


def test_profile_add(runner):
    result = runner.invoke(main, ["profile", "add", "dev"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "now active" in result.output


def test_profile_list(runner):
    runner.invoke(main, ["profile", "add", "dev"])
    runner.invoke(main, ["profile", "add", "prod"])
    result = runner.invoke(main, ["profile", "list"])
    assert "* dev" in result.output
    assert "prod" in result.output


def test_profile_add_duplicate_shows_error(runner):
    runner.invoke(main, ["profile", "add", "dev"])
    result = runner.invoke(main, ["profile", "add", "dev"])
    assert result.exit_code != 0


def test_profile_rm(runner):
    runner.invoke(main, ["profile", "add", "dev"])
    result = runner.invoke(main, ["profile", "rm", "dev"])
    assert result.exit_code == 0
    assert "removed" in result.output


# ------------------------------------------------------------------ register / unregister


def test_register(runner, env_file):
    runner.invoke(main, ["profile", "add", "dev"])
    result = runner.invoke(main, ["register", str(env_file)])
    assert result.exit_code == 0
    assert "Registered" in result.output


def test_register_missing_file_fails(runner):
    runner.invoke(main, ["profile", "add", "dev"])
    result = runner.invoke(main, ["register", "/no/such/file.env"])
    assert result.exit_code != 0


def test_unregister(runner, env_file):
    runner.invoke(main, ["profile", "add", "dev"])
    runner.invoke(main, ["register", str(env_file)])
    result = runner.invoke(main, ["unregister", str(env_file)])
    assert result.exit_code == 0
    assert "Unregistered" in result.output


# ------------------------------------------------------------------ snapshot


def test_snapshot(runner, env_file):
    runner.invoke(main, ["profile", "add", "dev"])
    runner.invoke(main, ["register", str(env_file)])
    result = runner.invoke(main, ["snapshot"])
    assert result.exit_code == 0
    assert str(env_file) in result.output


# ------------------------------------------------------------------ switch


def test_switch(runner, tmp_path):
    f = tmp_path / "cfg"
    f.write_text("dev")
    runner.invoke(main, ["profile", "add", "dev"])
    runner.invoke(main, ["profile", "add", "prod"])
    runner.invoke(main, ["register", str(f)])
    f.write_text("prod")
    runner.invoke(main, ["snapshot", "--profile", "prod"])

    result = runner.invoke(main, ["switch", "dev"])
    assert result.exit_code == 0
    assert f.read_text() == "dev"

    result = runner.invoke(main, ["switch", "prod"])
    assert result.exit_code == 0
    assert f.read_text() == "prod"


def test_switch_missing_without_force_fails(runner, env_file):
    runner.invoke(main, ["profile", "add", "dev"])
    runner.invoke(main, ["profile", "add", "prod"])
    runner.invoke(main, ["register", str(env_file)])

    result = runner.invoke(main, ["switch", "prod"])
    assert result.exit_code != 0
    assert "no stored version" in result.output


def test_switch_force_skips_missing(runner, env_file):
    runner.invoke(main, ["profile", "add", "dev"])
    runner.invoke(main, ["profile", "add", "prod"])
    runner.invoke(main, ["register", str(env_file)])

    result = runner.invoke(main, ["switch", "--force", "prod"])
    assert result.exit_code == 0
    assert "skipped" in result.output


# ------------------------------------------------------------------ status / list


def test_status(runner, env_file):
    runner.invoke(main, ["profile", "add", "dev"])
    runner.invoke(main, ["register", str(env_file)])
    result = runner.invoke(main, ["status"])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert str(env_file) in result.output


def test_list(runner, env_file):
    runner.invoke(main, ["profile", "add", "dev"])
    runner.invoke(main, ["register", str(env_file)])
    result = runner.invoke(main, ["list"])
    assert str(env_file) in result.output


def test_list_empty(runner):
    result = runner.invoke(main, ["list"])
    assert "No registered files" in result.output
