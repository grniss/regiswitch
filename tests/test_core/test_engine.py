import pytest
from pathlib import Path

from regiswitch.core.engine import (
    create_profile,
    delete_profile,
    list_files,
    list_profiles,
    register_file,
    save_to_profile,
    switch_profile,
    unregister_file,
)
from regiswitch.utils.errors import (
    FileAlreadyRegisteredError,
    FileNotRegisteredError,
    NoProfilesError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
    RegiswitchError,
)


class TestCreateProfile:
    def test_creates_profile(self, initialized_registry, registry_dir):
        registry = create_profile("work")
        assert "work" in registry.profiles

    def test_raises_if_already_exists(self, initialized_registry, registry_dir):
        create_profile("work")
        with pytest.raises(ProfileAlreadyExistsError):
            create_profile("work")

    def test_copies_existing_files_into_new_profile(self, initialized_registry, registry_dir, sample_file):
        create_profile("base")
        from regiswitch.core.registry import load_registry
        r = load_registry()
        r.current_profile = "base"
        from regiswitch.core.registry import save_registry
        save_registry(r)
        register_file(sample_file)
        create_profile("copy")
        from regiswitch.utils.fs import has_stored_version
        assert has_stored_version("copy", sample_file)


class TestDeleteProfile:
    def test_deletes_profile(self, initialized_registry, registry_dir):
        create_profile("work")
        registry = delete_profile("work")
        assert "work" not in registry.profiles

    def test_raises_if_not_found(self, initialized_registry, registry_dir):
        with pytest.raises(ProfileNotFoundError):
            delete_profile("nonexistent")

    def test_raises_if_active(self, initialized_registry, registry_dir):
        create_profile("work")
        switch_profile("work")
        with pytest.raises(RegiswitchError):
            delete_profile("work")


class TestListProfiles:
    def test_empty_list(self, initialized_registry, registry_dir):
        profiles = list_profiles()
        assert profiles == []

    def test_returns_name_and_active_flag(self, initialized_registry, registry_dir):
        create_profile("a")
        create_profile("b")
        switch_profile("a")
        profiles = list_profiles()
        names = {name: active for name, active in profiles}
        assert names["a"] is True
        assert names["b"] is False


class TestRegisterFile:
    def test_registers_file(self, initialized_registry, registry_dir, sample_file):
        registry = register_file(sample_file)
        assert str(sample_file) in registry.files

    def test_raises_if_already_registered(self, initialized_registry, registry_dir, sample_file):
        register_file(sample_file)
        with pytest.raises(FileAlreadyRegisteredError):
            register_file(sample_file)

    def test_raises_if_file_missing(self, initialized_registry, registry_dir, tmp_path):
        ghost = tmp_path / "ghost.txt"
        with pytest.raises(RegiswitchError):
            register_file(ghost)

    def test_copies_into_all_profiles(self, initialized_registry, registry_dir, sample_file):
        create_profile("p1")
        create_profile("p2")
        register_file(sample_file)
        from regiswitch.utils.fs import has_stored_version
        assert has_stored_version("p1", sample_file)
        assert has_stored_version("p2", sample_file)


class TestUnregisterFile:
    def test_unregisters_file(self, initialized_registry, registry_dir, sample_file):
        register_file(sample_file)
        registry = unregister_file(sample_file)
        assert str(sample_file) not in registry.files

    def test_raises_if_not_registered(self, initialized_registry, registry_dir, sample_file):
        with pytest.raises(FileNotRegisteredError):
            unregister_file(sample_file)


class TestSwitchProfile:
    def test_updates_current_profile(self, initialized_registry, registry_dir, sample_file):
        create_profile("work")
        registry = switch_profile("work")
        assert registry.current_profile == "work"

    def test_raises_if_not_found(self, initialized_registry, registry_dir):
        with pytest.raises(ProfileNotFoundError):
            switch_profile("ghost")

    def test_restores_file_from_profile(self, initialized_registry, registry_dir, sample_file):
        create_profile("work")
        register_file(sample_file)
        sample_file.write_text("modified")
        create_profile("clean")
        from regiswitch.utils.fs import copy_to_profile
        original = sample_file.parent / "original_copy.txt"
        original.write_text("original")
        from regiswitch.utils.fs import stored_file_path
        stored = stored_file_path("clean", sample_file)
        stored.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(original, stored)
        switch_profile("clean")
        assert sample_file.read_text() == "original"


class TestSaveToProfile:
    def test_saves_to_active_profile(self, initialized_registry, registry_dir, sample_file):
        create_profile("work")
        switch_profile("work")
        register_file(sample_file)
        sample_file.write_text("updated")
        _, target = save_to_profile()
        assert target == "work"
        from regiswitch.utils.fs import stored_file_path
        stored = stored_file_path("work", sample_file)
        assert stored.read_text() == "updated"

    def test_raises_if_no_profiles(self, initialized_registry, registry_dir):
        with pytest.raises(NoProfilesError):
            save_to_profile()

    def test_raises_if_target_not_found(self, initialized_registry, registry_dir):
        create_profile("work")
        with pytest.raises(ProfileNotFoundError):
            save_to_profile("ghost")

    def test_saves_to_named_profile(self, initialized_registry, registry_dir, sample_file):
        create_profile("work")
        create_profile("backup")
        switch_profile("work")
        register_file(sample_file)
        sample_file.write_text("for-backup")
        _, target = save_to_profile("backup")
        assert target == "backup"


class TestListFiles:
    def test_empty_list(self, initialized_registry, registry_dir):
        assert list_files() == []

    def test_returns_registered_files(self, initialized_registry, registry_dir, sample_file):
        register_file(sample_file)
        files = list_files()
        assert len(files) == 1
        assert files[0].path == str(sample_file)
