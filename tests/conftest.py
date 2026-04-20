import pytest
from pathlib import Path

from regiswitch.core.engine import init_project


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    """A tmp directory with regiswitch already initialized."""
    init_project(tmp_path)
    return tmp_path
