from pathlib import Path

import pytest

from regiswitch.core.engine import (
    create_profile,
    delete_profile,
    get_status,
    init_project,
    list_profiles,
    register_file,
    save_to_profile,
    switch_profile,
    unregister_file,
)
from regiswitch.core.storage import LocalStorageBackend
from regiswitch.models.config import RegiswitchConfig
from regiswitch.utils.errors import (
    FileAlreadyRegisteredError,
    FileNotRegisteredError,
    NoActiveProfileError,
    NotInitializedError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)
from regiswitch.utils.fs import load_config


def make_storage(root: Path) -> LocalStorageBackend:
    return LocalStorageBackend(RegiswitchConfig.default_profiles_dir(root))


class TestInitProject:
    def test_creates_regiswitch_dir(self, tmp_path: Path):
        init_project(tmp_path)
        assert (tmp_path / ".regiswitch").is_dir()

    def test_creates_config_file(self, tmp_path: Path):
        init_project(tmp_path)
        config = load_config(tmp_path)
        assert config.current_profile is None
        assert config.registered_files == []

    def test_raises_if_already_initialized(self, tmp_path: Path):
        init_project(tmp_path)
        with pytest.raises(NotInitializedError):
            init_project(tmp_path)


class TestRegisterFile:
    def test_registers_file(self, project_dir: Path):
        (project_dir / ".env").write_text("K=V")
        register_file(project_dir, ".env")
        config = load_config(project_dir)
        assert ".env" in config.registered_files

    def test_raises_if_already_registered(self, project_dir: Path):
        (project_dir / ".env").write_text("K=V")
        register_file(project_dir, ".env")
        with pytest.raises(FileAlreadyRegisteredError):
            register_file(project_dir, ".env")


class TestUnregisterFile:
    def test_unregisters_file(self, project_dir: Path):
        (project_dir / ".env").write_text("K=V")
        register_file(project_dir, ".env")
        unregister_file(project_dir, ".env")
        config = load_config(project_dir)
        assert ".env" not in config.registered_files

    def test_raises_if_not_registered(self, project_dir: Path):
        with pytest.raises(FileNotRegisteredError):
            unregister_file(project_dir, "ghost.txt")


class TestCreateProfile:
    def test_creates_profile(self, project_dir: Path):
        storage = make_storage(project_dir)
        create_profile(project_dir, "dev", storage)
        assert storage.profile_exists("dev")

    def test_sets_active_if_first(self, project_dir: Path):
        storage = make_storage(project_dir)
        create_profile(project_dir, "dev", storage)
        config = load_config(project_dir)
        assert config.current_profile == "dev"

    def test_does_not_overwrite_active(self, project_dir: Path):
        storage = make_storage(project_dir)
        create_profile(project_dir, "dev", storage)
        create_profile(project_dir, "prod", storage)
        config = load_config(project_dir)
        assert config.current_profile == "dev"

    def test_raises_if_exists(self, project_dir: Path):
        storage = make_storage(project_dir)
        create_profile(project_dir, "dev", storage)
        with pytest.raises(ProfileAlreadyExistsError):
            create_profile(project_dir, "dev", storage)


class TestDeleteProfile:
    def test_deletes_profile(self, project_dir: Path):
        storage = make_storage(project_dir)
        create_profile(project_dir, "dev", storage)
        delete_profile(project_dir, "dev", storage)
        assert not storage.profile_exists("dev")

    def test_clears_active_on_delete(self, project_dir: Path):
        storage = make_storage(project_dir)
        create_profile(project_dir, "dev", storage)
        delete_profile(project_dir, "dev", storage)
        config = load_config(project_dir)
        assert config.current_profile is None

    def test_raises_if_not_found(self, project_dir: Path):
        storage = make_storage(project_dir)
        with pytest.raises(ProfileNotFoundError):
            delete_profile(project_dir, "ghost", storage)


class TestListProfiles:
    def test_empty_list(self, project_dir: Path):
        storage = make_storage(project_dir)
        assert list_profiles(storage) == []

    def test_returns_sorted(self, project_dir: Path):
        storage = make_storage(project_dir)
        create_profile(project_dir, "prod", storage)
        create_profile(project_dir, "dev", storage)
        assert list_profiles(storage) == ["dev", "prod"]


class TestSaveToProfile:
    def test_saves_registered_files(self, project_dir: Path):
        env = project_dir / ".env"
        env.write_text("KEY=val")
        register_file(project_dir, ".env")
        storage = make_storage(project_dir)
        create_profile(project_dir, "dev", storage)
        save_to_profile(project_dir, storage, "dev")
        assert storage.has_file(".env", "dev")

    def test_uses_active_profile_when_none_given(self, project_dir: Path):
        env = project_dir / ".env"
        env.write_text("KEY=val")
        register_file(project_dir, ".env")
        storage = make_storage(project_dir)
        create_profile(project_dir, "dev", storage)
        used = save_to_profile(project_dir, storage)
        assert used == "dev"

    def test_raises_no_active_profile(self, project_dir: Path):
        storage = make_storage(project_dir)
        with pytest.raises(NoActiveProfileError):
            save_to_profile(project_dir, storage)

    def test_raises_profile_not_found(self, project_dir: Path):
        storage = make_storage(project_dir)
        with pytest.raises(ProfileNotFoundError):
            save_to_profile(project_dir, storage, "ghost")


class TestSwitchProfile:
    def test_restores_files(self, project_dir: Path):
        env = project_dir / ".env"
        env.write_text("KEY=dev")
        register_file(project_dir, ".env")
        storage = make_storage(project_dir)
        create_profile(project_dir, "dev", storage)
        save_to_profile(project_dir, storage, "dev")
        env.write_text("KEY=changed")
        switch_profile(project_dir, "dev", storage)
        assert env.read_text() == "KEY=dev"

    def test_sets_active_profile(self, project_dir: Path):
        storage = make_storage(project_dir)
        create_profile(project_dir, "dev", storage)
        create_profile(project_dir, "prod", storage)
        switch_profile(project_dir, "prod", storage)
        config = load_config(project_dir)
        assert config.current_profile == "prod"

    def test_returns_applied_files(self, project_dir: Path):
        env = project_dir / ".env"
        env.write_text("K=V")
        register_file(project_dir, ".env")
        storage = make_storage(project_dir)
        create_profile(project_dir, "dev", storage)
        save_to_profile(project_dir, storage, "dev")
        applied = switch_profile(project_dir, "dev", storage)
        assert ".env" in applied

    def test_raises_profile_not_found(self, project_dir: Path):
        storage = make_storage(project_dir)
        with pytest.raises(ProfileNotFoundError):
            switch_profile(project_dir, "ghost", storage)


class TestGetStatus:
    def test_no_profile_no_files(self, project_dir: Path):
        storage = make_storage(project_dir)
        result = get_status(project_dir, storage)
        assert result.current_profile is None
        assert result.profiles == []
        assert result.registered_files == []
        assert result.drift == []

    def test_drift_detected(self, project_dir: Path):
        env = project_dir / ".env"
        env.write_text("K=original")
        register_file(project_dir, ".env")
        storage = make_storage(project_dir)
        create_profile(project_dir, "dev", storage)
        save_to_profile(project_dir, storage, "dev")
        env.write_text("K=modified")
        result = get_status(project_dir, storage)
        assert ".env" in result.drift

    def test_no_drift_when_in_sync(self, project_dir: Path):
        env = project_dir / ".env"
        env.write_text("K=val")
        register_file(project_dir, ".env")
        storage = make_storage(project_dir)
        create_profile(project_dir, "dev", storage)
        save_to_profile(project_dir, storage, "dev")
        result = get_status(project_dir, storage)
        assert result.drift == []
