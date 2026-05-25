from pathlib import Path

import pytest

from regiswitch.core.engine import create_profile, init_project
from regiswitch.core.storage import LocalStorageBackend
from regiswitch.models.config import RegiswitchConfig
from regiswitch.utils.errors import NotInitializedError
from regiswitch.utils.fs import (
    find_project_root,
    load_config,
    load_storage_backend,
    save_config,
)


def test_find_project_root_from_root(tmp_path: Path):
    init_project(tmp_path)
    assert find_project_root(tmp_path) == tmp_path


def test_find_project_root_from_subdir(tmp_path: Path):
    init_project(tmp_path)
    subdir = tmp_path / "sub" / "dir"
    subdir.mkdir(parents=True)
    assert find_project_root(subdir) == tmp_path


def test_find_project_root_raises_when_not_initialized(tmp_path: Path):
    with pytest.raises(NotInitializedError):
        find_project_root(tmp_path)


def test_save_and_load_config(tmp_path: Path):
    init_project(tmp_path)
    config = load_config(tmp_path)
    config.registered_files.append(".env")
    config.current_profile = "dev"
    save_config(tmp_path, config)

    reloaded = load_config(tmp_path)
    assert reloaded.registered_files == [".env"]
    assert reloaded.current_profile == "dev"


def test_load_storage_backend_returns_local(tmp_path: Path):
    init_project(tmp_path)
    backend = load_storage_backend(tmp_path)
    assert isinstance(backend, LocalStorageBackend)


def test_load_storage_backend_custom_local_path(tmp_path: Path):
    from regiswitch.models.config import LocalStorageConfig
    init_project(tmp_path)
    config = load_config(tmp_path)
    custom = tmp_path / "custom_store"
    config.storage = LocalStorageConfig(path=str(custom))
    save_config(tmp_path, config)

    backend = load_storage_backend(tmp_path)
    assert isinstance(backend, LocalStorageBackend)
    backend.create_profile("dev")
    assert (custom / "dev").exists()


def test_save_config_strips_none(tmp_path: Path):
    init_project(tmp_path)
    config = load_config(tmp_path)
    assert config.current_profile is None
    save_config(tmp_path, config)
    reloaded = load_config(tmp_path)
    assert reloaded.current_profile is None
