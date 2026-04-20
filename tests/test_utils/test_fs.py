from pathlib import Path

import pytest

from regiswitch.core.engine import init_project, create_profile
from regiswitch.models.config import RegiswitchConfig
from regiswitch.utils.errors import NotInitializedError
from regiswitch.utils.fs import (
    copy_file_from_profile,
    copy_file_to_profile,
    find_project_root,
    load_config,
    profile_has_file,
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


def test_copy_file_to_and_from_profile(tmp_path: Path):
    init_project(tmp_path)
    create_profile(tmp_path, "dev")

    src = tmp_path / ".env"
    src.write_text("KEY=value")

    copy_file_to_profile(tmp_path, ".env", "dev")
    assert profile_has_file(tmp_path, ".env", "dev")

    src.write_text("KEY=changed")
    copy_file_from_profile(tmp_path, ".env", "dev")
    assert src.read_text() == "KEY=value"


def test_profile_has_file_false_when_missing(tmp_path: Path):
    init_project(tmp_path)
    create_profile(tmp_path, "dev")
    assert not profile_has_file(tmp_path, ".env", "dev")
