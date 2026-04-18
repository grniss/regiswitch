import unittest
import os
import shutil
import yaml
from regiswitch.main import init, profile_add, file_add, profile_use, profile_remove, file_list, CONFIG_FILE, STORAGE_DIR

class TestProfileSwitching(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_run_switching"
        os.makedirs(self.test_dir, exist_ok=True)
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        init()

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)

    def test_profile_use_switches_files(self):
        # Create a file
        file_path = "config.txt"
        with open(file_path, "w") as f:
            f.write("version 1")
        
        # Add to default profile
        file_add(file_path, "default", "v1")
        
        # Create another profile
        profile_add("dev", "Development profile")
        
        # Change file content and add to dev profile
        with open(file_path, "w") as f:
            f.write("version 2")
        file_add(file_path, "dev", "v2")
        
        # Switch back to default
        profile_use("default")
        with open(file_path, "r") as f:
            self.assertEqual(f.read(), "version 1")
        
        with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)
            self.assertEqual(config["active_profile"], "default")

        # Switch to dev
        profile_use("dev")
        with open(file_path, "r") as f:
            self.assertEqual(f.read(), "version 2")
            
        with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)
            self.assertEqual(config["active_profile"], "dev")

    def test_profile_remove(self):
        profile_add("to_be_removed", "Temporary profile")
        profile_remove("to_be_removed")
        
        with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)
            self.assertNotIn("to_be_removed", config["profiles"])

    def test_file_list(self):
        # This is mostly to ensure it doesn't crash, as it prints to stdout
        file_path = "list_test.txt"
        with open(file_path, "w") as f:
            f.write("content")
        file_add(file_path, "default", "v1")
        
        from regiswitch.main import file_list
        file_list() # Should not raise error

if __name__ == "__main__":
    unittest.main()
