import os
import yaml
import shutil

CONFIG_FILE = ".regiswitch.yaml"
STORAGE_DIR = ".regiswitch/profiles"

class ConfigManager:
    def __init__(self, config_file=CONFIG_FILE, storage_dir=STORAGE_DIR):
        self.config_file = config_file
        self.storage_dir = storage_dir
        self.config = None

    def exists(self):
        return os.path.exists(self.config_file)

    def load(self):
        if not self.exists():
            return None
        with open(self.config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        return self.config

    def save(self, config=None):
        if config:
            self.config = config
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

    def init_project(self):
        if self.exists():
            return False, f"{self.config_file} already exists."
        
        self.config = {
            "active_profile": "default",
            "profiles": {
                "default": {
                    "description": "Default profile",
                    "files": {}
                }
            }
        }
        try:
            self.save()
            os.makedirs(self.storage_dir, exist_ok=True)
            return True, None
        except Exception as e:
            return False, str(e)

    def get_profiles(self):
        return self.config.get("profiles", {})

    def get_active_profile_name(self):
        return self.config.get("active_profile")

    def set_active_profile_name(self, name):
        self.config["active_profile"] = name
        self.save()

    def add_profile(self, name, description=""):
        if name in self.config["profiles"]:
            return False, f"Profile '{name}' already exists."
        self.config["profiles"][name] = {
            "description": description,
            "files": {}
        }
        self.save()
        return True, None

    def remove_profile(self, name):
        if name not in self.config["profiles"]:
            return False, f"Profile '{name}' does not exist."
        if name == "default":
            return False, "Cannot remove the 'default' profile."
        if name == self.get_active_profile_name():
            return False, "Cannot remove the active profile. Switch to another profile first."
        
        del self.config["profiles"][name]
        self.save()
        return True, None

    def _get_storage_path(self, profile_name, file_path):
        # We need to ensure the file is stored INSIDE the profile directory.
        # We sanitize the file_path to be relative and not contain '..' components
        # that could escape the profile directory.
        sanitized_path = os.path.normpath(file_path).lstrip(os.sep).replace('..' + os.sep, '')
        if sanitized_path.startswith('..'):
            sanitized_path = sanitized_path[2:].lstrip(os.sep)
        return os.path.join(self.storage_dir, profile_name, sanitized_path)

    def add_file_to_profile(self, file_path, profile_name):
        if profile_name not in self.config["profiles"]:
            return False, f"Profile '{profile_name}' does not exist."
        if not os.path.exists(file_path):
            return False, f"File '{file_path}' does not exist."
        
        # Store file in profile-specific storage
        dest = self._get_storage_path(profile_name, file_path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(file_path, dest)
        
        # We store True just to mark the file as managed by this profile
        self.config["profiles"][profile_name]["files"][file_path] = True
        self.save()
        return True, None

    def apply_profile(self, profile_name):
        if profile_name not in self.config["profiles"]:
            return False, f"Profile '{profile_name}' does not exist."
        
        profile = self.config["profiles"][profile_name]
        results = []
        for file_path in profile.get("files", {}).keys():
            src = self._get_storage_path(profile_name, file_path)
            if not os.path.exists(src):
                results.append((file_path, False))
                continue
            
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            shutil.copy2(src, file_path)
            results.append((file_path, True))
        
        self.set_active_profile_name(profile_name)
        return True, results
