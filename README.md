# regiswitch

A Python CLI tool for switching registered files between named profiles.

## What it does

`regiswitch` lets you maintain multiple versions of specific files (e.g. `~/.gitconfig`, `~/.ssh/config`, app config files) under named profiles. Switching profiles atomically replaces all registered files with the versions stored in that profile.

**Example use cases:**
- Switch between `work` and `personal` Git identities by swapping `~/.gitconfig`
- Toggle between `staging` and `production` environment configs
- Manage per-project dotfile variants without manual copying

## Installation

```bash
pip install -e .
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv pip install -e .
```

## Quick start

```bash
# 1. Create profiles
regiswitch profile create work
regiswitch profile create personal

# 2. Register a file to be managed
regiswitch register ~/.gitconfig

# 3. Snapshot the current file into a profile
regiswitch snapshot work

# Edit ~/.gitconfig with personal details, then snapshot that too
regiswitch snapshot personal

# 4. Switch between profiles
regiswitch switch work
regiswitch switch personal

# 5. Check current state
regiswitch status
```

## Commands

| Command | Description |
|---------|-------------|
| `regiswitch profile create <name>` | Create a new profile |
| `regiswitch profile delete <name>` | Delete a profile and its stored files |
| `regiswitch profile list` | List all profiles, marking the active one |
| `regiswitch register <file>` | Register a file to be managed |
| `regiswitch unregister <file>` | Remove a file from management (stored copies kept) |
| `regiswitch snapshot [profile]` | Save current live files into a profile (defaults to active) |
| `regiswitch switch <profile>` | Replace registered files with a profile's stored versions |
| `regiswitch status` | Show active profile and per-file sync state |

## How it works

State is stored at `~/.config/regiswitch/`:

```
~/.config/regiswitch/
├── config.toml          # active profile + list of registered file paths
└── profiles/
    ├── work/
    │   └── <encoded-filename>   # stored copy of each registered file
    └── personal/
        └── <encoded-filename>
```

When you run `regiswitch switch <profile>`, each registered file is overwritten with the copy stored under that profile. Files that have no stored version in the target profile are skipped with a warning.

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Input error (bad profile name, unregistered file, etc.) |
| `2` | Runtime error (unexpected I/O failure, etc.) |

## Development

```bash
pip install -e .
pytest
```
