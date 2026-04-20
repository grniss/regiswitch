import pytest

from regiswitch.utils import fs as _fs


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Redirect all regiswitch config I/O to a temp directory."""
    config_dir = tmp_path / ".config" / "regiswitch"
    config_dir.mkdir(parents=True)

    monkeypatch.setattr(_fs, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(_fs, "CONFIG_FILE", config_dir / "config.toml")
    monkeypatch.setattr(_fs, "PROFILES_DIR", config_dir / "profiles")

    return config_dir
