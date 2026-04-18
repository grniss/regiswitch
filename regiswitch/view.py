import sys

class RegiswitchView:
    @staticmethod
    def show_message(message):
        print(message)

    @staticmethod
    def show_error(message, exit_code=1):
        print(f"Error: {message}")
        if exit_code is not None:
            sys.exit(exit_code)

    @staticmethod
    def show_profiles(active_profile, profiles):
        print("Profiles:")
        for name, data in profiles.items():
            active = "*" if name == active_profile else " "
            print(f"{active} {name}: {data.get('description', '')}")

    @staticmethod
    def show_files(files_data, profiles_list):
        print("Registered Files:")
        for file_path in sorted(files_data.keys()):
            print(f"{file_path}:")
            for profile_name in profiles_list:
                version_id = files_data[file_path].get(profile_name, "(not registered)")
                print(f"  {profile_name}: {version_id}")
