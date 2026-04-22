import pytest
from pathlib import Path

from regiswitch.core.backends.local import LocalBackend


@pytest.fixture
def backend(tmp_path: Path) -> LocalBackend:
    return LocalBackend(tmp_path / "storage")


@pytest.fixture
def initialized_backend(backend: LocalBackend) -> LocalBackend:
    backend.init()
    return backend


@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    f = tmp_path / "sample.txt"
    f.write_text("hello")
    return f
