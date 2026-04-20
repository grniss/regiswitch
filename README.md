# Regiswitch

Regiswitch is a command-line tool designed to manage different versions of files across multiple profiles. It's particularly useful for projects that require different configurations (e.g., development, testing, production) or for quickly switching between different file sets.

## Architecture

Regiswitch is built using the **Model-View-Controller (MVC)** design pattern, which separates the application's data management, user interface, and logic for better maintainability and scalability.

- **Model** (`model.py`): Handles all data persistence, including reading/writing the `.regiswitch.yaml` configuration file and managing the file storage in `.regiswitch/profiles/`.
- **View** (`view.py`): Responsible for all user-facing output, ensuring consistent formatting for messages, errors, and lists.
- **Controller** (`controller.py`): Acts as the orchestrator between the Model and the View. It processes user commands, retrieves data from the Model, and passes it to the View for display.
- **Entry Point** (`main.py`): A clean entry point that initializes the MVC components and handles command-line argument parsing.

## Installation

Currently, Regiswitch can be used by running the package directly:

```bash
# From the project root
python3 -m regiswitch.main <command>
```

## Commands

### Project Initialization

Initialize a new Regiswitch project in the current directory:

```bash
python3 -m regiswitch.main init
```
This creates a `.regiswitch.yaml` file and a `.regiswitch/profiles/` directory.

### Profile Management

- **List Profiles**: Show all available profiles and indicate the active one.
  ```bash
  python3 -m regiswitch.main profile list
  ```
- **Add Profile**: Create a new profile with an optional description.
  ```bash
  python3 -m regiswitch.main profile add <name> [--description "<description>"]
  ```
- **Remove Profile**: Delete an existing profile.
  ```bash
  python3 -m regiswitch.main profile remove <name>
  ```
- **Switch Profile**: Activate a profile and update all managed files to their associated versions stored for that profile.
  ```bash
  python3 -m regiswitch.main profile use <name>
  ```

### File Management

- **List Files**: Show all registered files across all profiles.
  ```bash
  python3 -m regiswitch.main file list
  ```
- **Add File to Profile**: Register a file to a specific profile.
  ```bash
  python3 -m regiswitch.main file add <path> <profile>
  ```
  This will store a copy of the file specifically for that profile in the `.regiswitch/profiles/` directory.

## Running Tests

Unit tests are located in the `tests/` directory and can be run using the `unittest` module:

```bash
# From the project root
python3 -m unittest discover tests
```

---
*Maintained by the Multica Agent team.*
