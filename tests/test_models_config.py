from pathlib import Path

from regiswitch.models.config import RegiswitchConfig


def test_add_file_returns_true(tmp_path):
    f = tmp_path / "a.cfg"
    cfg = RegiswitchConfig()
    assert cfg.add_file(f) is True
    assert str(f) in cfg.registered_files


def test_add_duplicate_returns_false(tmp_path):
    f = tmp_path / "a.cfg"
    cfg = RegiswitchConfig()
    cfg.add_file(f)
    assert cfg.add_file(f) is False
    assert cfg.registered_files.count(str(f)) == 1


def test_remove_file_returns_true(tmp_path):
    f = tmp_path / "a.cfg"
    cfg = RegiswitchConfig()
    cfg.add_file(f)
    assert cfg.remove_file(f) is True
    assert str(f) not in cfg.registered_files


def test_remove_missing_returns_false(tmp_path):
    f = tmp_path / "a.cfg"
    cfg = RegiswitchConfig()
    assert cfg.remove_file(f) is False


def test_constructor_deduplicates():
    cfg = RegiswitchConfig(registered_files=["/a", "/a", "/b"])
    assert cfg.registered_files == ["/a", "/b"]


def test_defaults():
    cfg = RegiswitchConfig()
    assert cfg.active_profile is None
    assert cfg.registered_files == []
