import pytest

from regiswitch.core.validator import require_existing_file
from regiswitch.utils.errors import RegiswitchError


def test_require_existing_file_passes(tmp_path):
    f = tmp_path / "ok.cfg"
    f.write_text("data")
    require_existing_file(f)  # should not raise


def test_require_existing_file_raises_when_missing(tmp_path):
    f = tmp_path / "missing.cfg"
    with pytest.raises(RegiswitchError, match="does not exist"):
        require_existing_file(f)


def test_require_existing_file_raises_for_directory(tmp_path):
    d = tmp_path / "adir"
    d.mkdir()
    with pytest.raises(RegiswitchError, match="not a file"):
        require_existing_file(d)
