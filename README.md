# regiswitch

A Python CLI tool to switch registered files between named profiles. Useful for managing dotfiles, config files, or any files that differ across environments (work, personal, dev, etc.).

## Install

```bash
pip install -e .
```

## Quick Start

```bash
# 1. Initialize the registry
regiswitch init

# 2. Create profiles
regiswitch profile create work
regiswitch profile create personal

# 3. Switch to a profile and register files
regiswitch switch work
regiswitch register ~/.ssh/config
regiswitch register ~/.gitconfig

# 4. Save your current file state to the active profile
regiswitch save

# 5. Switch profiles — files on disk are replaced with the profile's stored versions
regiswitch switch personal
```

## Commands

| Command | Description |
|---|---|
| `regiswitch init` | Initialize the registry at `~/.config/regiswitch/` |
| `regiswitch profile create <name>` | Create a new profile |
| `regiswitch profile list` | List all profiles |
| `regiswitch profile delete <name>` | Delete a profile and its stored files |
| `regiswitch register <path>` | Register a file — copies it into all existing profiles |
| `regiswitch unregister <path>` | Remove a file from the registry (does not delete from disk) |
| `regiswitch switch <profile>` | Switch active profile — restores all registered files from that profile |
| `regiswitch save [profile]` | Snapshot current on-disk file state into a profile (default: active) |
| `regiswitch status` | Show the active profile and all registered files |

## How It Works

- **Registry** — stored at `~/.config/regiswitch/registry.toml`, tracks which files are managed and which profile is active.
- **Profile storage** — each profile keeps its own copy of every registered file under `~/.config/regiswitch/profiles/<name>/`.
- **Register** — adds a file to the registry and copies its current content into every existing profile.
- **Save** — snapshots the current on-disk content of all registered files into the target profile.
- **Switch** — copies the target profile's stored file versions back onto disk, then marks that profile as active.

## Tech Stack

- [Typer](https://typer.tiangolo.com/) — CLI framework
- [Rich](https://rich.readthedocs.io/) — terminal output (tables, panels)
- [Pydantic v2](https://docs.pydantic.dev/) — data validation and config models
- `tomllib` / `tomli-w` — TOML config persistence
