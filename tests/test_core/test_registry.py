import pytest
from pathlib import Path

from regiswitch.core.backends.local import LocalBackend
from regiswitch.models.config import Registry, ProfileMeta
from regiswitch.utils.errors import RegistryNotInitializedError


class TestInit:
    def test_creates_registry_file(self, backend: LocalBackend):
        backend.init()
        assert backend.registry_file.exists()

    def test_returns_empty_registry(self, backend: LocalBackend):
        registry = backend.init()
        assert registry.current_profile is None
        assert registry.profiles == {}
        assert registry.files == {}

    def test_idempotent_reinit(self, backend: LocalBackend):
        backend.init()
        registry = backend.init()
        assert registry.profiles == {}


class TestIsInitialized:
    def test_false_before_init(self, backend: LocalBackend):
        assert backend.is_initialized() is False

    def test_true_after_init(self, backend: LocalBackend):
        backend.init()
        assert backend.is_initialized() is True


class TestLoadRegistry:
    def test_raises_if_not_initialized(self, backend: LocalBackend):
        with pytest.raises(RegistryNotInitializedError):
            backend.load_registry()

    def test_loads_empty_registry(self, backend: LocalBackend):
        backend.init()
        registry = backend.load_registry()
        assert isinstance(registry, Registry)
        assert registry.current_profile is None

    def test_roundtrip_with_profile(self, backend: LocalBackend):
        from datetime import datetime
        backend.init()
        registry = backend.load_registry()
        registry.profiles["work"] = ProfileMeta(created_at=datetime(2026, 1, 1))
        registry.current_profile = "work"
        backend.save_registry(registry)
        loaded = backend.load_registry()
        assert loaded.current_profile == "work"
        assert "work" in loaded.profiles


class TestSaveRegistry:
    def test_persists_current_profile(self, backend: LocalBackend):
        from datetime import datetime
        backend.init()
        registry = backend.load_registry()
        registry.current_profile = "dev"
        registry.profiles["dev"] = ProfileMeta(created_at=datetime.now())
        backend.save_registry(registry)
        assert backend.load_registry().current_profile == "dev"
