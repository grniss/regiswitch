# regiswitch

Switch registered files between named profiles.

## Install

```bash
pip install -e .
```

## Usage

```bash
# Create profiles
regiswitch profile add dev
regiswitch profile add prod

# Register a file — snapshots its current content into the active profile
regiswitch register .env
regiswitch register ~/.ssh/config

# Save current file state into a profile
regiswitch snapshot --profile prod

# Switch — replaces all registered files with the profile's stored versions
regiswitch switch prod
regiswitch switch dev

# Inspect
regiswitch status
regiswitch list
regiswitch profile list
```

## Commands

| Command | Description |
|---|---|
| `profile add <name>` | Create a new profile |
| `profile list` | List all profiles (active marked with `*`) |
| `profile rm <name>` | Delete a profile and its stored files |
| `register <file>` | Track a file and snapshot it to the active profile |
| `unregister <file>` | Stop tracking a file (removes all stored versions) |
| `snapshot [--profile]` | Save current file state to a profile |
| `switch <profile>` | Replace registered files with profile's stored versions |
| `status` | Show current profile and per-file snapshot state |
| `list` | List registered file paths |

## Data storage

Profile snapshots are stored in `~/.regiswitch/profiles/<profile>/`.
