# regiswitch

A Python CLI tool to switch registered files between named profiles. Useful for managing dotfiles, config files, or any files that differ across environments (work, personal, dev, etc.).

## Install

```bash
pip install -e .          # local storage (default)
pip install -e ".[s3]"    # include AWS S3 support
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
| `regiswitch init` | Initialize the registry at the configured storage location |
| `regiswitch profile create <name>` | Create a new profile |
| `regiswitch profile list` | List all profiles |
| `regiswitch profile delete <name>` | Delete a profile and its stored files |
| `regiswitch register <path>` | Register a file — copies it into all existing profiles |
| `regiswitch unregister <path>` | Remove a file from the registry (does not delete from disk) |
| `regiswitch switch <profile>` | Switch active profile — restores all registered files from that profile |
| `regiswitch switch <profile> --auto-save` | Save current profile before switching (one-time override) |
| `regiswitch switch <profile> --no-auto-save` | Skip auto-save for this switch even if enabled globally |
| `regiswitch save [profile]` | Snapshot current on-disk file state into a profile (default: active) |
| `regiswitch status` | Show the active profile, auto-save setting, and all registered files |
| `regiswitch config auto-save --enable` | Enable auto-save globally — always save before switching |
| `regiswitch config auto-save --disable` | Disable auto-save globally |
| `regiswitch backend show` | Show the current storage backend configuration |
| `regiswitch backend local [--path PATH]` | Use local filesystem storage (optionally at a custom path) |
| `regiswitch backend s3 --bucket BUCKET` | Use AWS S3 storage |

## Auto-Save

By default, switching profiles replaces files on disk without saving the current state first. Enable auto-save to always snapshot the active profile before switching.

```bash
# Enable globally — saved across sessions
regiswitch config auto-save --enable

# Now switching auto-saves first
regiswitch switch personal   # saves "work" profile, then switches

# Override per-invocation
regiswitch switch personal --no-auto-save   # skip this time
regiswitch switch work --auto-save          # force save even if disabled globally

# Check current setting
regiswitch status   # shows "Auto-save: enabled" or "Auto-save: disabled"
```

## Storage Backends

regiswitch supports pluggable storage backends. The active backend is configured in `~/.config/regiswitch/backend.toml`.

### Local (default)

Files are stored at `~/.config/regiswitch/` by default.

```bash
# Use the default path
regiswitch backend local

# Use a custom path (e.g. Dropbox, network share, or any directory)
regiswitch backend local --path ~/Dropbox/regiswitch
regiswitch init
```

### AWS S3

Profile snapshots and the registry are stored in an S3 bucket. AWS credentials are resolved via the standard boto3 chain (env vars, `~/.aws/credentials`, IAM role, etc.).

```bash
# Requires: pip install regiswitch[s3]
regiswitch backend s3 --bucket my-regiswitch-bucket --region us-east-1
regiswitch backend s3 --bucket my-bucket --prefix configs/ --region eu-west-1
regiswitch init
```

## How It Works

- **Registry** — tracks which files are managed and which profile is active. Stored as `registry.toml` at the backend location.
- **Profile storage** — each profile keeps its own copy of every registered file. For local backends, under `<storage-path>/profiles/<name>/`; for S3, under `s3://<bucket>/<prefix>profiles/<name>/`.
- **Register** — adds a file to the registry and copies its current content into every existing profile.
- **Save** — snapshots the current on-disk content of all registered files into the target profile.
- **Switch** — copies the target profile's stored file versions back onto disk, then marks that profile as active.
- **Auto-save** — when enabled, automatically saves the current profile before every switch so in-flight changes are never lost.

## Tech Stack

- [Typer](https://typer.tiangolo.com/) — CLI framework
- [Rich](https://rich.readthedocs.io/) — terminal output (tables, panels)
- [Pydantic v2](https://docs.pydantic.dev/) — data validation and config models
- `tomllib` / `tomli-w` — TOML config persistence
- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) — AWS S3 backend (optional)
