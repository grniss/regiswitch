from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from regiswitch.cli import app

runner = CliRunner()

_BOOTSTRAP = "regiswitch.core.backends._BOOTSTRAP_CONFIG"


@pytest.fixture
def bootstrap_path(tmp_path: Path) -> Path:
    return tmp_path / "backend.toml"


def test_backend_show_default(bootstrap_path: Path):
    with patch(_BOOTSTRAP, bootstrap_path):
        result = runner.invoke(app, ["backend", "show"])
    assert result.exit_code == 0
    assert "local" in result.output


def test_backend_local_no_path(bootstrap_path: Path):
    with patch(_BOOTSTRAP, bootstrap_path):
        result = runner.invoke(app, ["backend", "local"])
    assert result.exit_code == 0
    assert "local" in result.output
    assert bootstrap_path.exists()


def test_backend_local_custom_path(bootstrap_path: Path, tmp_path: Path):
    custom = str(tmp_path / "my_storage")
    with patch(_BOOTSTRAP, bootstrap_path):
        result = runner.invoke(app, ["backend", "local", "--path", custom])
    assert result.exit_code == 0
    assert "my_storage" in result.output


def test_backend_s3(bootstrap_path: Path):
    with patch(_BOOTSTRAP, bootstrap_path):
        result = runner.invoke(app, ["backend", "s3", "--bucket", "my-bucket", "--region", "us-east-1"])
    assert result.exit_code == 0
    assert "my-bucket" in result.output


def test_backend_show_after_s3_set(bootstrap_path: Path):
    with patch(_BOOTSTRAP, bootstrap_path):
        runner.invoke(app, ["backend", "s3", "--bucket", "my-bucket", "--prefix", "data/"])
        result = runner.invoke(app, ["backend", "show"])
    assert result.exit_code == 0
    assert "my-bucket" in result.output
    assert "data/" in result.output
