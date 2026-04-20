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
            for file_path, applied in results:
                if applied:
                    self.view.show_message(f"Updated {file_path}")
                else:
                    self.view.show_message(f"Warning: File '{file_path}' not found in profile '{name}'. Skipping.")
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
                    files_data[file_path][profile_name] = "YES" # Just mark as present
        
        self.view.show_files(files_data, sorted(profiles.keys()))

    def add_file(self, file_path, profile_name):
        self._ensure_initialized()
        success, error = self.model.add_file_to_profile(file_path, profile_name)
        if success:
            self.view.show_message(f"Added '{file_path}' to profile '{profile_name}'.")
        else:
            self.view.show_error(error)
