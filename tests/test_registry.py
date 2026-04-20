import pytest
from pathlib import Path
from regiswitch.registry import Registry


@pytest.fixture
def reg(tmp_path):
    return Registry(base_dir=tmp_path)


@pytest.fixture
def reg_with_profiles(reg):
    reg.profile_add("dev")
    reg.profile_add("prod")
    return reg


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / "app.env"
    f.write_text("DB=dev_db\n")
    return f


# ------------------------------------------------------------------ profiles


def test_profile_add(reg):
    reg.profile_add("dev")
    assert "dev" in reg.profiles


def test_first_profile_becomes_current(reg):
    reg.profile_add("dev")
    assert reg.current_profile == "dev"


def test_second_profile_does_not_change_current(reg):
    reg.profile_add("dev")
    reg.profile_add("prod")
    assert reg.current_profile == "dev"


def test_profile_add_duplicate_raises(reg):
    reg.profile_add("dev")
    with pytest.raises(ValueError, match="already exists"):
        reg.profile_add("dev")


def test_profile_remove(reg):
    reg.profile_add("dev")
    reg.profile_add("prod")
    reg.profile_remove("dev")
    assert "dev" not in reg.profiles


def test_profile_remove_advances_current(reg):
    reg.profile_add("dev")
    reg.profile_add("prod")
    reg.profile_remove("dev")
    assert reg.current_profile == "prod"


def test_profile_remove_unknown_raises(reg):
    with pytest.raises(ValueError, match="does not exist"):
        reg.profile_remove("ghost")


# ------------------------------------------------------------------ register


def test_register_adds_to_file_list(reg, env_file):
    reg.profile_add("dev")
    reg.register(str(env_file))
    assert str(env_file) in reg.files


def test_register_stores_blob(reg, env_file):
    reg.profile_add("dev")
    reg.register(str(env_file))
    sha = reg.stored_sha("dev", str(env_file))
    assert sha is not None
    assert reg._blob_path(sha).exists()


def test_register_deduplicates_identical_content(reg, tmp_path):
    reg.profile_add("dev")
    reg.profile_add("prod")
    content = b"shared content"
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    f1.write_bytes(content)
    f2.write_bytes(content)

    reg.register(str(f1))
    reg.register(str(f2))

    sha1 = reg.stored_sha("dev", str(f1))
    sha2 = reg.stored_sha("dev", str(f2))
    assert sha1 == sha2

    blobs = list(reg._blob_dir.rglob("*"))
    blobs = [b for b in blobs if b.is_file()]
    assert len(blobs) == 1


def test_register_missing_file_raises(reg):
    reg.profile_add("dev")
    with pytest.raises(FileNotFoundError):
        reg.register("/nonexistent/path.env")


def test_register_no_profile_raises(reg, env_file):
    with pytest.raises(ValueError, match="No active profile"):
        reg.register(str(env_file))


# ------------------------------------------------------------------ unregister


def test_unregister_removes_from_files(reg, env_file):
    reg.profile_add("dev")
    reg.register(str(env_file))
    reg.unregister(str(env_file))
    assert str(env_file) not in reg.files


def test_unregister_gcs_orphaned_blob(reg, env_file):
    reg.profile_add("dev")
    reg.register(str(env_file))
    sha = reg.stored_sha("dev", str(env_file))
    reg.unregister(str(env_file))
    assert not reg._blob_path(sha).exists()


def test_unregister_keeps_shared_blob(reg, tmp_path):
    reg.profile_add("dev")
    reg.profile_add("prod")
    content = b"shared"
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    f1.write_bytes(content)
    f2.write_bytes(content)

    reg.register(str(f1))
    reg.register(str(f2), profile="prod")
    sha = reg.stored_sha("dev", str(f1))

    reg.unregister(str(f1))
    # blob still referenced by prod's manifest for f2
    assert reg._blob_path(sha).exists()


# ------------------------------------------------------------------ snapshot


def test_snapshot_saves_all_files(reg, tmp_path):
    reg.profile_add("dev")
    reg.profile_add("prod")
    f = tmp_path / "cfg"
    f.write_text("original")
    reg.register(str(f))

    f.write_text("updated")
    saved = reg.snapshot(profile="prod")

    assert str(f) in saved
    assert reg.stored_sha("prod", str(f)) != reg.stored_sha("dev", str(f))


def test_snapshot_skips_missing_files(reg, tmp_path):
    reg.profile_add("dev")
    f = tmp_path / "gone.env"
    f.write_text("x")
    reg.register(str(f))
    f.unlink()
    saved = reg.snapshot()
    assert saved == []


# ------------------------------------------------------------------ switch


def test_switch_replaces_file_content(reg, tmp_path):
    reg.profile_add("dev")
    reg.profile_add("prod")

    f = tmp_path / "config"
    f.write_text("dev content")
    reg.register(str(f))

    f.write_text("prod content")
    reg.snapshot(profile="prod")

    reg.switch("dev")
    assert f.read_text() == "dev content"

    reg.switch("prod")
    assert f.read_text() == "prod content"


def test_switch_updates_current_profile(reg, tmp_path):
    reg.profile_add("dev")
    reg.profile_add("prod")
    f = tmp_path / "x"
    f.write_text("a")
    reg.register(str(f))
    reg.snapshot(profile="prod")

    reg.switch("prod")
    assert reg.current_profile == "prod"


def test_switch_missing_version_raises(reg, tmp_path):
    reg.profile_add("dev")
    reg.profile_add("prod")
    f = tmp_path / "x"
    f.write_text("a")
    reg.register(str(f))  # only saved to dev

    with pytest.raises(ValueError, match="no stored version"):
        reg.switch("prod")


def test_switch_force_skips_missing(reg, tmp_path):
    reg.profile_add("dev")
    reg.profile_add("prod")
    f = tmp_path / "x"
    f.write_text("original")
    reg.register(str(f))  # only in dev

    applied, skipped = reg.switch("prod", force=True)
    assert str(f) in skipped
    assert f.read_text() == "original"  # untouched


def test_switch_unknown_profile_raises(reg):
    with pytest.raises(ValueError, match="does not exist"):
        reg.switch("ghost")


# ------------------------------------------------------------------ has_stored / stored_sha


def test_has_stored_true_after_register(reg, env_file):
    reg.profile_add("dev")
    reg.register(str(env_file))
    assert reg.has_stored("dev", str(env_file))


def test_has_stored_false_for_other_profile(reg, env_file):
    reg.profile_add("dev")
    reg.profile_add("prod")
    reg.register(str(env_file))
    assert not reg.has_stored("prod", str(env_file))


# ------------------------------------------------------------------ persistence


def test_config_persists_across_instances(tmp_path):
    r1 = Registry(base_dir=tmp_path)
    r1.profile_add("dev")
    f = tmp_path / "app.env"
    f.write_text("x=1")
    r1.register(str(f))

    r2 = Registry(base_dir=tmp_path)
    assert "dev" in r2.profiles
    assert str(f) in r2.files
    assert r2.has_stored("dev", str(f))
