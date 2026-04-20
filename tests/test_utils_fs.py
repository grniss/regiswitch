from pathlib import Path

from regiswitch.models.config import RegiswitchConfig
from regiswitch.utils import fs


def test_load_config_returns_defaults_when_no_file():
    cfg = fs.load_config()
    assert cfg.active_profile is None
    assert cfg.registered_files == []


def test_save_and_load_roundtrip(tmp_path):
    cfg = RegiswitchConfig(active_profile="work", registered_files=["/a", "/b"])
    fs.save_config(cfg)
    loaded = fs.load_config()
    assert loaded.active_profile == "work"
    assert loaded.registered_files == ["/a", "/b"]


def test_save_config_with_none_active_profile():
    cfg = RegiswitchConfig(active_profile=None, registered_files=["/x"])
    fs.save_config(cfg)
    loaded = fs.load_config()
    assert loaded.active_profile is None


def test_list_profiles_empty():
    assert fs.list_profiles() == []


def test_create_and_list_profile():
    fs.create_profile("dev")
    assert "dev" in fs.list_profiles()


def test_delete_profile():
    fs.create_profile("staging")
    fs.delete_profile("staging")
    assert "staging" not in fs.list_profiles()


def test_delete_nonexistent_profile_is_noop():
    fs.delete_profile("ghost")  # should not raise


def test_snapshot_and_restore(tmp_path):
    src = tmp_path / "app.conf"
    src.write_text("original")
    fs.create_profile("p1")
    fs.snapshot_file("p1", src)

    src.write_text("modified")
    fs.restore_file("p1", src)
    assert src.read_text() == "original"


def test_stored_file_exists_false_before_snapshot(tmp_path):
    target = tmp_path / "f.cfg"
    fs.create_profile("p1")
    assert fs.stored_file_exists("p1", target) is False


def test_stored_file_exists_true_after_snapshot(tmp_path):
    target = tmp_path / "f.cfg"
    target.write_text("data")
    fs.create_profile("p1")
    fs.snapshot_file("p1", target)
    assert fs.stored_file_exists("p1", target) is True
