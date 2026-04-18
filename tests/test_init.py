import unittest
import os
import shutil
import yaml
from regiswitch.model import ConfigManager, CONFIG_FILE
from regiswitch.view import RegiswitchView
from regiswitch.controller import RegiswitchController

class TestInit(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for tests
        self.test_dir = "test_run"
        os.makedirs(self.test_dir, exist_ok=True)
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        self.model = ConfigManager()
        self.view = RegiswitchView()
        self.controller = RegiswitchController(self.model, self.view)

    def tearDown(self):
        # Cleanup
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)

    def test_init_creates_config_file(self):
        # Ensure config file doesn't exist
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)

        self.controller.init()

        self.assertTrue(os.path.exists(CONFIG_FILE))
        
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f)
        
        self.assertEqual(config["active_profile"], "default")
        self.assertIn("default", config["profiles"])
        self.assertEqual(config["profiles"]["default"]["description"], "Default profile")
        self.assertEqual(config["profiles"]["default"]["files"], {})

    def test_init_fails_if_already_initialized(self):
        # Create a dummy config file
        with open(CONFIG_FILE, 'w') as f:
            f.write("dummy")
        
        # Controller calls view.show_error which calls sys.exit(1)
        with self.assertRaises(SystemExit) as cm:
            self.controller.init()
        
        self.assertEqual(cm.exception.code, 1)

if __name__ == "__main__":
    unittest.main()
