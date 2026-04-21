from pathlib import Path
from typing import List
from models.config import FileMapping

class SwitchEngine:
    @staticmethod
    def apply_profile(mappings: List[FileMapping]):
        for mapping in mappings:
            target = mapping.target
            source = mapping.source
            
            if not source.exists():
                raise FileNotFoundError(f"Source file {source} does not exist")
            
            if target.exists() or target.is_symlink():
                target.unlink()
            
            target.symlink_to(source)
