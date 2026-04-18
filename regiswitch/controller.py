import os
from .model import ConfigManager
from .view import RegiswitchView

class RegiswitchController:
    def __init__(self, model: ConfigManager, view: RegiswitchView):
        self.model = model
        self.view = view

    def _ensure_initialized(self):
        if not self.model.load():
            self.view.show_error("Project not initialized. Run 'regiswitch init' first.")

    def init(self):
        success, error = self.model.init_project()
        if success:
            self.view.show_message(f"Initialized regiswitch project in {os.getcwd()}")
            self.view.show_message(f"Created {self.model.config_file} and {self.model.storage_dir}")
        else:
            self.view.show_error(error)

    def list_profiles(self):
        self._ensure_initialized()
        self.view.show_profiles(self.model.get_active_profile_name(), self.model.get_profiles())

    def add_profile(self, name, description=""):
        self._ensure_initialized()
        success, error = self.model.add_profile(name, description)
        if success:
            self.view.show_message(f"Added profile '{name}'.")
        else:
            self.view.show_error(error)

    def remove_profile(self, name):
        self._ensure_initialized()
        success, error = self.model.remove_profile(name)
        if success:
            self.view.show_message(f"Removed profile '{name}'.")
        else:
            self.view.show_error(error)

    def use_profile(self, name):
        self._ensure_initialized()
        success, results = self.model.apply_profile(name)
        if success:
            for file_path, version_id, applied in results:
                if applied:
                    self.view.show_message(f"Updated {file_path} to version {version_id}")
                else:
                    self.view.show_message(f"Warning: Version '{version_id}' for file '{file_path}' not found in storage. Skipping.")
            self.view.show_message(f"Switched to profile '{name}'.")
        else:
            self.view.show_error(results)

    def list_files(self):
        self._ensure_initialized()
        profiles = self.model.get_profiles()
        all_files = set()
        for data in profiles.values():
            all_files.update(data.get("files", {}).keys())
        
        files_data = {}
        for file_path in all_files:
            files_data[file_path] = {}
            for profile_name, data in profiles.items():
                if file_path in data.get("files", {}):
                    files_data[file_path][profile_name] = data["files"][file_path]
        
        self.view.show_files(files_data, sorted(profiles.keys()))

    def add_file(self, file_path, profile_name, version_id):
        self._ensure_initialized()
        success, error = self.model.add_file_version(file_path, profile_name, version_id)
        if success:
            self.view.show_message(f"Added '{file_path}' (version {version_id}) to profile '{profile_name}'.")
        else:
            self.view.show_error(error)
