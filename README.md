# regiswitch

Switch registered files between named profiles.

Manage multiple versions of configuration files (`.env`, `config.toml`, etc.) across named profiles — think of it as "git stash for config files".

## Install

```bash
pip install -e .

# With S3 storage support
pip install -e ".[s3]"
```

## Quick Start

```bash
# 1. Initialize in your project
regiswitch init

# 2. Register the files you want to manage
regiswitch register .env
regiswitch register config/settings.toml

# 3. Create profiles
regiswitch profile create dev
regiswitch profile create prod

# 4. Edit .env for dev, then save it
regiswitch save --profile dev

# 5. Edit .env for prod, then save it
regiswitch save --profile prod

# 6. Switch between profiles
regiswitch switch dev
regiswitch switch prod
```

## Commands

| Command | Description |
|---|---|
| `regiswitch init` | Initialize `.regiswitch/` in the current directory |
| `regiswitch register <file>` | Track a file across profiles |
| `regiswitch unregister <file>` | Stop tracking a file |
| `regiswitch profile create <name>` | Create a new profile |
| `regiswitch profile list` | List profiles (highlights active) |
| `regiswitch profile delete <name>` | Delete a profile and its stored files |
| `regiswitch save [--profile <name>]` | Save current files into a profile |
| `regiswitch switch <name>` | Restore a profile's files |
| `regiswitch status` | Show active profile, files, and unsaved changes |
| `regiswitch config show` | Show current configuration |
| `regiswitch config set-storage ...` | Change storage backend |

## Storage Backends

### Local (default)

Files are stored inside `.regiswitch/profiles/` by default.

```bash
# Use a custom local path (useful for sharing profiles across projects)
regiswitch config set-storage local --path /shared/profiles
```

### S3

```bash
pip install regiswitch[s3]

regiswitch config set-storage s3 --bucket my-bucket --prefix myproject --region us-east-1
```

S3 storage uses your ambient AWS credentials (`AWS_*` env vars, `~/.aws/credentials`, IAM role, etc.).

## How It Works

```
.regiswitch/
├── config.toml          # active profile, registered files, storage config
└── profiles/
    ├── dev/
    │   └── .env         # stored copy for dev
    └── prod/
        └── .env         # stored copy for prod
```

`switch` replaces your working files with the profile's stored copies and sets that profile as active.
`save` snapshots your current working files into the profile's storage.
`status` compares working files against the active profile's stored copies and reports drift.

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
```
