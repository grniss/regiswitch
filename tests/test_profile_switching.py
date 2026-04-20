import unittest
import os
import shutil
import yaml
from regiswitch.model import ConfigManager, CONFIG_FILE
from regiswitch.view import RegiswitchView
from regiswitch.controller import RegiswitchController

class TestProfileSwitching(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_run_switching"
        os.makedirs(self.test_dir, exist_ok=True)
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        self.model = ConfigManager()
        self.view = RegiswitchView()
        self.controller = RegiswitchController(self.model, self.view)
        self.controller.init()

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)

    def test_profile_use_switches_files(self):
        # Create a file
        file_path = "config.txt"
        with open(file_path, "w") as f:
            f.write("version 1")
        
        # Add to default profile
        self.controller.add_file(file_path, "default")
        
        # Create another profile
        self.controller.add_profile("dev", "Development profile")
        
        # Change file content and add to dev profile
        with open(file_path, "w") as f:
            f.write("version 2")
        self.controller.add_file(file_path, "dev")
        
        # Switch back to default
        self.controller.use_profile("default")
        with open(file_path, "r") as f:
            self.assertEqual(f.read(), "version 1")
        
        with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)
            self.assertEqual(config["active_profile"], "default")

        # Switch to dev
        self.controller.use_profile("dev")
        with open(file_path, "r") as f:
            self.assertEqual(f.read(), "version 2")
            
        with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)
            self.assertEqual(config["active_profile"], "dev")

    def test_profile_remove(self):
        self.controller.add_profile("to_be_removed", "Temporary profile")
        self.controller.remove_profile("to_be_removed")
        
        with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)
            self.assertNotIn("to_be_removed", config["profiles"])

    def test_file_list(self):
        # This is mostly to ensure it doesn't crash, as it prints to stdout
        file_path = "list_test.txt"
        with open(file_path, "w") as f:
            f.write("content")
        self.controller.add_file(file_path, "default")
        
        self.controller.list_files() # Should not raise error

if __name__ == "__main__":
    unittest.main()
