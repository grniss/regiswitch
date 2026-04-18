import argparse
from .model import ConfigManager
from .view import RegiswitchView
from .controller import RegiswitchController

def get_controller():
    model = ConfigManager()
    view = RegiswitchView()
    return RegiswitchController(model, view)

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
    controller = get_controller()

    if args.command == "init":
        controller.init()
    elif args.command == "profile":
        if args.subcommand == "list":
            controller.list_profiles()
        elif args.subcommand == "add":
            controller.add_profile(args.name, args.description)
        elif args.subcommand == "remove":
            controller.remove_profile(args.name)
        elif args.subcommand == "use":
            controller.use_profile(args.name)
        else:
            profile_parser.print_help()
    elif args.command == "file":
        if args.subcommand == "list":
            controller.list_files()
        elif args.subcommand == "add":
            controller.add_file(args.path, args.profile, args.version)
        else:
            file_parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
