import pytest
from pathlib import Path

from regiswitch.core.registry import init_registry, is_initialized, load_registry, save_registry
from regiswitch.models.config import Registry, ProfileMeta
from regiswitch.utils.errors import RegistryNotInitializedError


class TestInitRegistry:
    def test_creates_registry_file(self, registry_dir: Path):
        init_registry()
        from regiswitch.utils.fs import REGISTRY_FILE
        assert REGISTRY_FILE.exists()

    def test_returns_empty_registry(self, registry_dir: Path):
        registry = init_registry()
        assert registry.current_profile is None
        assert registry.profiles == {}
        assert registry.files == {}

    def test_idempotent_reinit(self, registry_dir: Path):
        init_registry()
        registry = init_registry()
        assert registry.profiles == {}


class TestIsInitialized:
    def test_false_before_init(self, registry_dir: Path):
        assert is_initialized() is False

    def test_true_after_init(self, registry_dir: Path):
        init_registry()
        assert is_initialized() is True


class TestLoadRegistry:
    def test_raises_if_not_initialized(self, registry_dir: Path):
        with pytest.raises(RegistryNotInitializedError):
            load_registry()

    def test_loads_empty_registry(self, registry_dir: Path):
        init_registry()
        registry = load_registry()
        assert isinstance(registry, Registry)
        assert registry.current_profile is None

    def test_roundtrip_with_profile(self, registry_dir: Path):
        from datetime import datetime
        init_registry()
        registry = load_registry()
        registry.profiles["work"] = ProfileMeta(created_at=datetime(2026, 1, 1))
        registry.current_profile = "work"
        save_registry(registry)
        loaded = load_registry()
        assert loaded.current_profile == "work"
        assert "work" in loaded.profiles


class TestSaveRegistry:
    def test_persists_current_profile(self, registry_dir: Path):
        init_registry()
        registry = load_registry()
        registry.current_profile = "dev"
        from datetime import datetime
        registry.profiles["dev"] = ProfileMeta(created_at=datetime.now())
        save_registry(registry)
        reloaded = load_registry()
        assert reloaded.current_profile == "dev"
