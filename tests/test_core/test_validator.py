from pathlib import Path

import pytest

from regiswitch.core.validator import validate_file_exists, validate_profile_name, validate_rel_path
from regiswitch.utils.errors import RegiswitchError


class TestValidateProfileName:
    def test_valid_name(self):
        validate_profile_name("dev")  # should not raise

    def test_empty_raises(self):
        with pytest.raises(RegiswitchError):
            validate_profile_name("   ")

    def test_slash_raises(self):
        with pytest.raises(RegiswitchError):
            validate_profile_name("dev/prod")

    def test_backslash_raises(self):
        with pytest.raises(RegiswitchError):
            validate_profile_name("dev\\prod")

    def test_colon_raises(self):
        with pytest.raises(RegiswitchError):
            validate_profile_name("dev:prod")


class TestValidateRelPath:
    def test_valid_rel_path(self):
        validate_rel_path("src/.env")  # should not raise

    def test_absolute_raises(self):
        with pytest.raises(RegiswitchError):
            validate_rel_path("/etc/passwd")

    def test_dotdot_raises(self):
        with pytest.raises(RegiswitchError):
            validate_rel_path("../secret")


class TestValidateFileExists:
    def test_existing_file(self, tmp_path: Path):
        f = tmp_path / ".env"
        f.write_text("X=1")
        validate_file_exists(tmp_path, ".env")  # should not raise

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(RegiswitchError):
            validate_file_exists(tmp_path, "missing.txt")
