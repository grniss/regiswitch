import pytest
from pathlib import Path


@pytest.fixture
def registry_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect regiswitch config to a temp directory."""
    config_dir = tmp_path / ".config" / "regiswitch"
    config_dir.mkdir(parents=True)

    import regiswitch.utils.fs as fs_module
    import regiswitch.core.registry as registry_module

    new_config = config_dir
    new_registry = config_dir / "registry.toml"
    new_profiles = config_dir / "profiles"

    monkeypatch.setattr(fs_module, "CONFIG_DIR", new_config)
    monkeypatch.setattr(fs_module, "REGISTRY_FILE", new_registry)
    monkeypatch.setattr(fs_module, "PROFILES_DIR", new_profiles)
    monkeypatch.setattr(registry_module, "CONFIG_DIR", new_config)
    monkeypatch.setattr(registry_module, "REGISTRY_FILE", new_registry)
    monkeypatch.setattr(registry_module, "PROFILES_DIR", new_profiles)

    return config_dir


@pytest.fixture
def initialized_registry(registry_dir: Path):
    from regiswitch.core.registry import init_registry
    return init_registry()


@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    f = tmp_path / "sample.txt"
    f.write_text("hello")
    return f
