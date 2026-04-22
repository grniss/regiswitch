import pytest
from pathlib import Path

from regiswitch.core.backends.local import LocalBackend
from regiswitch.core.engine import (
    create_profile,
    delete_profile,
    list_files,
    list_profiles,
    register_file,
    save_to_profile,
    set_auto_save,
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
    def test_creates_profile(self, initialized_backend: LocalBackend):
        registry = create_profile("work", backend=initialized_backend)
        assert "work" in registry.profiles

    def test_raises_if_already_exists(self, initialized_backend: LocalBackend):
        create_profile("work", backend=initialized_backend)
        with pytest.raises(ProfileAlreadyExistsError):
            create_profile("work", backend=initialized_backend)

    def test_copies_existing_files_into_new_profile(self, initialized_backend: LocalBackend, sample_file: Path):
        create_profile("base", backend=initialized_backend)
        r = initialized_backend.load_registry()
        r.current_profile = "base"
        initialized_backend.save_registry(r)
        register_file(sample_file, backend=initialized_backend)
        create_profile("copy", backend=initialized_backend)
        assert initialized_backend.has_stored_version("copy", sample_file)


class TestDeleteProfile:
    def test_deletes_profile(self, initialized_backend: LocalBackend):
        create_profile("work", backend=initialized_backend)
        registry = delete_profile("work", backend=initialized_backend)
        assert "work" not in registry.profiles

    def test_raises_if_not_found(self, initialized_backend: LocalBackend):
        with pytest.raises(ProfileNotFoundError):
            delete_profile("nonexistent", backend=initialized_backend)

    def test_raises_if_active(self, initialized_backend: LocalBackend):
        create_profile("work", backend=initialized_backend)
        switch_profile("work", backend=initialized_backend)
        with pytest.raises(RegiswitchError):
            delete_profile("work", backend=initialized_backend)


class TestListProfiles:
    def test_empty_list(self, initialized_backend: LocalBackend):
        assert list_profiles(backend=initialized_backend) == []

    def test_returns_name_and_active_flag(self, initialized_backend: LocalBackend):
        create_profile("a", backend=initialized_backend)
        create_profile("b", backend=initialized_backend)
        switch_profile("a", backend=initialized_backend)
        names = dict(list_profiles(backend=initialized_backend))
        assert names["a"] is True
        assert names["b"] is False


class TestRegisterFile:
    def test_registers_file(self, initialized_backend: LocalBackend, sample_file: Path):
        registry = register_file(sample_file, backend=initialized_backend)
        assert str(sample_file) in registry.files

    def test_raises_if_already_registered(self, initialized_backend: LocalBackend, sample_file: Path):
        register_file(sample_file, backend=initialized_backend)
        with pytest.raises(FileAlreadyRegisteredError):
            register_file(sample_file, backend=initialized_backend)

    def test_raises_if_file_missing(self, initialized_backend: LocalBackend, tmp_path: Path):
        ghost = tmp_path / "ghost.txt"
        with pytest.raises(RegiswitchError):
            register_file(ghost, backend=initialized_backend)

    def test_copies_into_all_profiles(self, initialized_backend: LocalBackend, sample_file: Path):
        create_profile("p1", backend=initialized_backend)
        create_profile("p2", backend=initialized_backend)
        register_file(sample_file, backend=initialized_backend)
        assert initialized_backend.has_stored_version("p1", sample_file)
        assert initialized_backend.has_stored_version("p2", sample_file)


class TestUnregisterFile:
    def test_unregisters_file(self, initialized_backend: LocalBackend, sample_file: Path):
        register_file(sample_file, backend=initialized_backend)
        registry = unregister_file(sample_file, backend=initialized_backend)
        assert str(sample_file) not in registry.files

    def test_raises_if_not_registered(self, initialized_backend: LocalBackend, sample_file: Path):
        with pytest.raises(FileNotRegisteredError):
            unregister_file(sample_file, backend=initialized_backend)


class TestSwitchProfile:
    def test_updates_current_profile(self, initialized_backend: LocalBackend):
        create_profile("work", backend=initialized_backend)
        registry = switch_profile("work", backend=initialized_backend)
        assert registry.current_profile == "work"

    def test_raises_if_not_found(self, initialized_backend: LocalBackend):
        with pytest.raises(ProfileNotFoundError):
            switch_profile("ghost", backend=initialized_backend)

    def test_restores_file_from_profile(self, initialized_backend: LocalBackend, sample_file: Path):
        create_profile("clean", backend=initialized_backend)
        register_file(sample_file, backend=initialized_backend)
        sample_file.write_text("dirty")
        initialized_backend.copy_to_profile(sample_file, "clean")
        sample_file.write_text("dirty-again")
        switch_profile("clean", backend=initialized_backend)
        assert sample_file.read_text() == "dirty"


class TestSaveToProfile:
    def test_saves_to_active_profile(self, initialized_backend: LocalBackend, sample_file: Path):
        create_profile("work", backend=initialized_backend)
        switch_profile("work", backend=initialized_backend)
        register_file(sample_file, backend=initialized_backend)
        sample_file.write_text("updated")
        _, target = save_to_profile(backend=initialized_backend)
        assert target == "work"
        stored = initialized_backend._stored_path("work", sample_file)
        assert stored.read_text() == "updated"

    def test_raises_if_no_profiles(self, initialized_backend: LocalBackend):
        with pytest.raises(NoProfilesError):
            save_to_profile(backend=initialized_backend)

    def test_raises_if_target_not_found(self, initialized_backend: LocalBackend):
        create_profile("work", backend=initialized_backend)
        with pytest.raises(ProfileNotFoundError):
            save_to_profile("ghost", backend=initialized_backend)

    def test_saves_to_named_profile(self, initialized_backend: LocalBackend, sample_file: Path):
        create_profile("work", backend=initialized_backend)
        create_profile("backup", backend=initialized_backend)
        switch_profile("work", backend=initialized_backend)
        register_file(sample_file, backend=initialized_backend)
        sample_file.write_text("for-backup")
        _, target = save_to_profile("backup", backend=initialized_backend)
        assert target == "backup"


class TestListFiles:
    def test_empty_list(self, initialized_backend: LocalBackend):
        assert list_files(backend=initialized_backend) == []

    def test_returns_registered_files(self, initialized_backend: LocalBackend, sample_file: Path):
        register_file(sample_file, backend=initialized_backend)
        files = list_files(backend=initialized_backend)
        assert len(files) == 1
        assert files[0].path == str(sample_file)


class TestSwitchProfileAutoSave:
    def test_switch_profile_auto_saves_when_registry_flag_set(
        self, initialized_backend: LocalBackend, sample_file: Path
    ):
        """Auto-save=True on registry saves current profile before switching."""
        create_profile("a", backend=initialized_backend)
        create_profile("b", backend=initialized_backend)
        switch_profile("a", backend=initialized_backend)
        register_file(sample_file, backend=initialized_backend)
        # Enable auto-save
        set_auto_save(True, backend=initialized_backend)
        # Modify file on disk
        sample_file.write_text("modified-in-a")
        # Switch to b — should auto-save "a" first
        switch_profile("b", backend=initialized_backend)
        # The stored copy for profile "a" should now reflect the modification
        stored = initialized_backend._stored_path("a", sample_file)
        assert stored.read_text() == "modified-in-a"

    def test_switch_profile_skips_save_by_default(
        self, initialized_backend: LocalBackend, sample_file: Path
    ):
        """Auto-save=False (default) does not update stored copy on switch."""
        create_profile("a", backend=initialized_backend)
        create_profile("b", backend=initialized_backend)
        switch_profile("a", backend=initialized_backend)
        register_file(sample_file, backend=initialized_backend)
        # Store a known version
        initialized_backend.copy_to_profile(sample_file, "a")
        original_content = sample_file.read_text()
        # Modify file but do NOT enable auto-save
        sample_file.write_text("modified-not-saved")
        switch_profile("b", backend=initialized_backend)
        # Stored copy for "a" should still be the original
        stored = initialized_backend._stored_path("a", sample_file)
        assert stored.read_text() == original_content

    def test_switch_profile_override_true_forces_save(
        self, initialized_backend: LocalBackend, sample_file: Path
    ):
        """Passing auto_save=True overrides registry auto_save=False."""
        create_profile("a", backend=initialized_backend)
        create_profile("b", backend=initialized_backend)
        switch_profile("a", backend=initialized_backend)
        register_file(sample_file, backend=initialized_backend)
        # registry auto_save is False by default
        sample_file.write_text("forced-save")
        switch_profile("b", backend=initialized_backend, auto_save=True)
        stored = initialized_backend._stored_path("a", sample_file)
        assert stored.read_text() == "forced-save"

    def test_switch_profile_override_false_skips_save(
        self, initialized_backend: LocalBackend, sample_file: Path
    ):
        """Passing auto_save=False overrides registry auto_save=True."""
        create_profile("a", backend=initialized_backend)
        create_profile("b", backend=initialized_backend)
        switch_profile("a", backend=initialized_backend)
        register_file(sample_file, backend=initialized_backend)
        set_auto_save(True, backend=initialized_backend)
        original_content = sample_file.read_text()
        initialized_backend.copy_to_profile(sample_file, "a")
        sample_file.write_text("should-not-be-saved")
        switch_profile("b", backend=initialized_backend, auto_save=False)
        stored = initialized_backend._stored_path("a", sample_file)
        assert stored.read_text() == original_content

    def test_switch_profile_no_current_profile_skips_save(
        self, initialized_backend: LocalBackend
    ):
        """Auto-save with no current_profile set does not raise an error."""
        create_profile("a", backend=initialized_backend)
        set_auto_save(True, backend=initialized_backend)
        # No current profile — switching should succeed silently
        registry = switch_profile("a", backend=initialized_backend)
        assert registry.current_profile == "a"


class TestSetAutoSave:
    def test_set_auto_save_enables(self, initialized_backend: LocalBackend):
        """set_auto_save(True) persists auto_save=True to backend."""
        set_auto_save(True, backend=initialized_backend)
        registry = initialized_backend.load_registry()
        assert registry.auto_save is True

    def test_set_auto_save_disables(self, initialized_backend: LocalBackend):
        """set_auto_save(False) after True persists auto_save=False."""
        set_auto_save(True, backend=initialized_backend)
        set_auto_save(False, backend=initialized_backend)
        registry = initialized_backend.load_registry()
        assert registry.auto_save is False
