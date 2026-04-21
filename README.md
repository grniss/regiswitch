# Regiswitch

Regiswitch is a Python CLI tool for managing and switching between sets of environment configuration files using profiles.

## Features
- **Profile-based switching**: Easily swap between development, production, and other environment configurations.
- **Symlink management**: Uses symbolic links to point to the desired file versions, ensuring consistency.
- **Type-safe configuration**: Leverages Pydantic for validation of profile definitions.

## Installation

```bash
pip install -e .
```

## Usage

```bash
regiswitch run <profile_name>
```

## Architecture
- `cli.py`: Entry point using Typer.
- `core/`: Business logic for file switching engine.
- `models/`: Configuration schemas.
- `output/`: Rich console integration.
