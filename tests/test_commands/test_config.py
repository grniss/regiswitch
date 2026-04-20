from pathlib import Path

from typer.testing import CliRunner

from regiswitch.cli import app
from regiswitch.core.engine import init_project
from regiswitch.utils.fs import load_config
from regiswitch.models.config import LocalStorageConfig, S3StorageConfig

runner = CliRunner()


def test_config_show_default(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "local" in result.output


def test_config_show_not_initialized(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 1


def test_set_storage_local_default(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["config", "set-storage", "local"])
    assert result.exit_code == 0
    config = load_config(tmp_path)
    assert isinstance(config.storage, LocalStorageConfig)
    assert config.storage.path is None


def test_set_storage_local_custom_path(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    custom = str(tmp_path / "custom")
    result = runner.invoke(app, ["config", "set-storage", "local", "--path", custom])
    assert result.exit_code == 0
    config = load_config(tmp_path)
    assert isinstance(config.storage, LocalStorageConfig)
    assert config.storage.path == custom


def test_set_storage_s3(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        app,
        ["config", "set-storage", "s3", "--bucket", "my-bucket", "--prefix", "proj", "--region", "us-west-2"],
    )
    assert result.exit_code == 0
    config = load_config(tmp_path)
    assert isinstance(config.storage, S3StorageConfig)
    assert config.storage.bucket == "my-bucket"
    assert config.storage.prefix == "proj"
    assert config.storage.region == "us-west-2"


def test_set_storage_s3_missing_bucket(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["config", "set-storage", "s3"])
    assert result.exit_code == 1


def test_set_storage_unknown_type(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["config", "set-storage", "gcs"])
    assert result.exit_code == 1


def test_config_show_s3(tmp_path: Path, monkeypatch):
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["config", "set-storage", "s3", "--bucket", "my-bucket"])
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "my-bucket" in result.output
