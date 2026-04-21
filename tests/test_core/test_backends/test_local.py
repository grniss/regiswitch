import pytest
from pathlib import Path

from regiswitch.core.backends.local import LocalBackend
from regiswitch.utils.errors import RegistryNotInitializedError


@pytest.fixture
def b(tmp_path: Path) -> LocalBackend:
    return LocalBackend(tmp_path / "storage")


class TestLocalBackend:
    def test_is_initialized_false(self, b: LocalBackend):
        assert b.is_initialized() is False

    def test_init_creates_dirs(self, b: LocalBackend):
        b.init()
        assert b.storage_path.exists()
        assert b.profiles_dir.exists()

    def test_init_creates_registry_file(self, b: LocalBackend):
        b.init()
        assert b.registry_file.exists()

    def test_is_initialized_true_after_init(self, b: LocalBackend):
        b.init()
        assert b.is_initialized() is True

    def test_load_registry_raises_before_init(self, b: LocalBackend):
        with pytest.raises(RegistryNotInitializedError):
            b.load_registry()

    def test_save_and_load_roundtrip(self, b: LocalBackend):
        b.init()
        registry = b.load_registry()
        registry.current_profile = "work"
        from regiswitch.models.config import ProfileMeta
        from datetime import datetime
        registry.profiles["work"] = ProfileMeta(created_at=datetime(2026, 1, 1))
        b.save_registry(registry)
        loaded = b.load_registry()
        assert loaded.current_profile == "work"

    def test_copy_and_restore(self, b: LocalBackend, tmp_path: Path):
        b.init()
        src = tmp_path / "myfile.txt"
        src.write_text("original")
        b.copy_to_profile(src, "work")
        assert b.has_stored_version("work", src)
        src.write_text("changed")
        b.restore_from_profile("work", src)
        assert src.read_text() == "original"

    def test_has_stored_version_false(self, b: LocalBackend, tmp_path: Path):
        b.init()
        f = tmp_path / "x.txt"
        assert b.has_stored_version("work", f) is False

    def test_delete_profile_removes_dir(self, b: LocalBackend, tmp_path: Path):
        b.init()
        src = tmp_path / "f.txt"
        src.write_text("data")
        b.copy_to_profile(src, "work")
        assert b.has_stored_version("work", src)
        b.delete_profile("work")
        assert not b.has_stored_version("work", src)

    def test_custom_storage_path(self, tmp_path: Path):
        custom = tmp_path / "custom_dir"
        b = LocalBackend(custom)
        b.init()
        assert b.registry_file == custom / "registry.toml"
        assert b.registry_file.exists()
