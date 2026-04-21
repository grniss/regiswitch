import pytest
from regiswitch.core.backends.local import LocalBackend


@pytest.fixture(autouse=True)
def patch_get_backend(monkeypatch, backend: LocalBackend):
    """Inject the test LocalBackend into every module that calls get_backend()."""
    monkeypatch.setattr("regiswitch.core.engine.get_backend", lambda: backend)
    monkeypatch.setattr("regiswitch.core.backends.get_backend", lambda: backend)
    monkeypatch.setattr("regiswitch.commands.init.get_backend", lambda: backend)
    monkeypatch.setattr("regiswitch.core.registry.get_backend", lambda: backend)
