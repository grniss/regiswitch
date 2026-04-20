from pathlib import Path

import pytest

from regiswitch.core import engine
from regiswitch.utils.errors import (
    FileAlreadyRegisteredError,
    FileNotRegisteredError,
    NoActiveProfileError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)


def test_create_and_list_profile():
    engine.create_profile("work")
    assert "work" in engine.list_profiles()


def test_create_duplicate_profile_raises():
    engine.create_profile("work")
    with pytest.raises(ProfileAlreadyExistsError):
        engine.create_profile("work")


def test_delete_profile():
    engine.create_profile("work")
    engine.delete_profile("work")
    assert "work" not in engine.list_profiles()


def test_delete_nonexistent_profile_raises():
    with pytest.raises(ProfileNotFoundError):
        engine.delete_profile("ghost")


def test_register_file(tmp_path):
    f = tmp_path / "settings.cfg"
    f.write_text("key=value")
    engine.create_profile("dev")
    engine.register_file(f)
    _, rows = engine.get_status()
    assert any(r["path"] == str(f) for r in rows)


def test_register_duplicate_raises(tmp_path):
    f = tmp_path / "settings.cfg"
    f.write_text("key=value")
    engine.register_file(f)
    with pytest.raises(FileAlreadyRegisteredError):
        engine.register_file(f)


def test_unregister_file(tmp_path):
    f = tmp_path / "settings.cfg"
    f.write_text("key=value")
    engine.register_file(f)
    engine.unregister_file(f)
    _, rows = engine.get_status()
    assert not any(r["path"] == str(f) for r in rows)


def test_unregister_nonexistent_raises(tmp_path):
    f = tmp_path / "settings.cfg"
    with pytest.raises(FileNotRegisteredError):
        engine.unregister_file(f)


def test_switch_replaces_file(tmp_path):
    live = tmp_path / "app.conf"
    live.write_text("version=1")

    engine.create_profile("v1")
    engine.create_profile("v2")
    engine.register_file(live)

    # snapshot current state into v1
    engine.snapshot("v1")

    # change file and snapshot into v2
    live.write_text("version=2")
    engine.snapshot("v2")

    # switch back to v1 — file should revert
    engine.switch_profile("v1")
    assert live.read_text() == "version=1"


def test_switch_to_missing_profile_raises():
    with pytest.raises(ProfileNotFoundError):
        engine.switch_profile("ghost")


def test_snapshot_without_active_profile_raises(tmp_path):
    f = tmp_path / "app.conf"
    f.write_text("data")
    engine.register_file(f)
    with pytest.raises(NoActiveProfileError):
        engine.snapshot()


def test_snapshot_reports_missing_live_file(tmp_path):
    f = tmp_path / "ghost.conf"
    engine.create_profile("dev")
    engine.register_file(f)  # file doesn't exist on disk
    missing = engine.snapshot("dev")
    assert str(f) in missing


def test_delete_active_profile_clears_active():
    engine.create_profile("work")
    engine.switch_profile("work")
    engine.delete_profile("work")
    active, _ = engine.get_status()
    assert active is None
