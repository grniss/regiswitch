import argparse
import os
import yaml
import sys
import shutil

CONFIG_FILE = ".regiswitch.yaml"
STORAGE_DIR = ".regiswitch/versions"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Project not initialized. Run 'regiswitch init' first.")
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

def init():
    if os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} already exists.")
        sys.exit(1)

    # Initial configuration structure
    config = {
        "active_profile": "default",
        "profiles": {
            "default": {
                "description": "Default profile",
                "files": {}
            }
        }
    }

    try:
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        os.makedirs(STORAGE_DIR, exist_ok=True)
        print(f"Initialized regiswitch project in {os.getcwd()}")
        print(f"Created {CONFIG_FILE} and {STORAGE_DIR}")
    except Exception as e:
        print(f"Error: Failed to initialize project: {e}")
        sys.exit(1)

def profile_list():
    config = load_config()
    print("Profiles:")
    for name, data in config["profiles"].items():
        active = "*" if name == config["active_profile"] else " "
        print(f"{active} {name}: {data.get('description', '')}")

def profile_add(name, description=""):
    config = load_config()
    if name in config["profiles"]:
        print(f"Error: Profile '{name}' already exists.")
        sys.exit(1)
    
    config["profiles"][name] = {
        "description": description,
        "files": {}
    }
    save_config(config)
    print(f"Added profile '{name}'.")

def profile_use(name):
    config = load_config()
    if name not in config["profiles"]:
        print(f"Error: Profile '{name}' does not exist.")
        sys.exit(1)
    
    target_profile = config["profiles"][name]
    for file_path, version_id in target_profile["files"].items():
        src = os.path.join(STORAGE_DIR, version_id, file_path)
        if not os.path.exists(src):
            print(f"Warning: Version '{version_id}' for file '{file_path}' not found in storage. Skipping.")
            continue
        
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        shutil.copy2(src, file_path)
        print(f"Updated {file_path} to version {version_id}")

    config["active_profile"] = name
    save_config(config)
    print(f"Switched to profile '{name}'.")

def file_add(file_path, profile_name, version_id):
    config = load_config()
    if profile_name not in config["profiles"]:
        print(f"Error: Profile '{profile_name}' does not exist.")
        sys.exit(1)
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    # Store file in storage
    dest = os.path.join(STORAGE_DIR, version_id, file_path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(file_path, dest)
    
    # Update config
    config["profiles"][profile_name]["files"][file_path] = version_id
    save_config(config)
    print(f"Added '{file_path}' (version {version_id}) to profile '{profile_name}'.")

def profile_remove(name):
    config = load_config()
    if name not in config["profiles"]:
        print(f"Error: Profile '{name}' does not exist.")
        sys.exit(1)
    
    if name == "default":
        print(f"Error: Cannot remove the 'default' profile.")
        sys.exit(1)
        
    if name == config["active_profile"]:
        print(f"Error: Cannot remove the active profile. Switch to another profile first.")
        sys.exit(1)

    del config["profiles"][name]
    save_config(config)
    print(f"Removed profile '{name}'.")

def file_list():
    config = load_config()
    print("Registered Files:")
    # Get all unique file paths across all profiles
    all_files = set()
    for profile_name, data in config["profiles"].items():
        all_files.update(data.get("files", {}).keys())
    
    for file_path in sorted(all_files):
        print(f"{file_path}:")
        for profile_name, data in config["profiles"].items():
            version_id = data.get("files", {}).get(file_path, "(not registered)")
            print(f"  {profile_name}: {version_id}")

def main():
    parser = argparse.ArgumentParser(prog="regiswitch", description="regiswitch - Manage file versions across profiles")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    subparsers.add_parser("init", help="Initialize a new regiswitch project")

    # profile commands
    profile_parser = subparsers.add_parser("profile", help="Profile management commands")
    profile_subparsers = profile_parser.add_subparsers(dest="subcommand", help="Profile subcommands")
    
    profile_subparsers.add_parser("list", help="List all profiles")
    
    add_profile_parser = profile_subparsers.add_parser("add", help="Add a new profile")
    add_profile_parser.add_argument("name", help="Name of the profile")
    add_profile_parser.add_argument("--description", default="", help="Description of the profile")
    
    remove_profile_parser = profile_subparsers.add_parser("remove", help="Remove a profile")
    remove_profile_parser.add_argument("name", help="Name of the profile to remove")
    
    use_profile_parser = profile_subparsers.add_parser("use", help="Switch to a profile")
    use_profile_parser.add_argument("name", help="Name of the profile to switch to")

    # file commands
    file_parser = subparsers.add_parser("file", help="File management commands")
    file_subparsers = file_parser.add_subparsers(dest="subcommand", help="File subcommands")
    
    file_subparsers.add_parser("list", help="List all registered files and their versions")
    
    add_file_parser = file_subparsers.add_parser("add", help="Add a file version to a profile")
    add_file_parser.add_argument("path", help="Path to the file")
    add_file_parser.add_argument("profile", help="Profile name")
    add_file_parser.add_argument("version", help="Version identifier")

    args = parser.parse_args()

    if args.command == "init":
        init()
    elif args.command == "profile":
        if args.subcommand == "list":
            profile_list()
        elif args.subcommand == "add":
            profile_add(args.name, args.description)
        elif args.subcommand == "remove":
            profile_remove(args.name)
        elif args.subcommand == "use":
            profile_use(args.name)
        else:
            profile_parser.print_help()
    elif args.command == "file":
        if args.subcommand == "list":
            file_list()
        elif args.subcommand == "add":
            file_add(args.path, args.profile, args.version)
        else:
            file_parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
