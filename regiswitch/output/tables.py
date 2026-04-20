from __future__ import annotations

from rich.table import Table

from regiswitch.models.config import LocalStorageConfig, RegiswitchConfig, S3StorageConfig
from regiswitch.output.console import console


def print_profiles_table(profiles: list[str], current: str | None) -> None:
    """Render the list of profiles with an indicator for the active one."""
    table = Table(title="Profiles", show_header=True, header_style="bold cyan")
    table.add_column("Profile", style="white")
    table.add_column("Active", justify="center")
    for name in profiles:
        active_marker = "[green]✓[/green]" if name == current else ""
        table.add_row(name, active_marker)
    console.print(table)


def print_registered_files_table(files: list[str]) -> None:
    """Render the list of registered files."""
    table = Table(title="Registered Files", show_header=True, header_style="bold cyan")
    table.add_column("Path", style="white")
    for f in files:
        table.add_row(f)
    console.print(table)


def print_status_table(
    current_profile: str | None,
    profiles: list[str],
    registered_files: list[str],
    drift: list[str],
) -> None:
    """Render a full status overview."""
    table = Table(title="regiswitch status", show_header=True, header_style="bold cyan")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Active profile", current_profile or "[dim]none[/dim]")
    table.add_row("Profiles", ", ".join(profiles) if profiles else "[dim]none[/dim]")
    table.add_row(
        "Registered files",
        "\n".join(registered_files) if registered_files else "[dim]none[/dim]",
    )
    if drift:
        table.add_row(
            "[yellow]Unsaved files[/yellow]",
            "\n".join(f"[yellow]{f}[/yellow]" for f in drift),
        )
    console.print(table)


def print_config_table(config: RegiswitchConfig) -> None:
    """Render the current configuration."""
    table = Table(title="regiswitch config", show_header=True, header_style="bold cyan")
    table.add_column("Setting", style="bold")
    table.add_column("Value")

    storage = config.storage
    if isinstance(storage, S3StorageConfig):
        storage_label = f"s3://{storage.bucket}/{storage.prefix}" if storage.prefix else f"s3://{storage.bucket}"
        table.add_row("storage.type", "s3")
        table.add_row("storage.bucket", storage.bucket)
        if storage.prefix:
            table.add_row("storage.prefix", storage.prefix)
        table.add_row("storage.region", storage.region)
        table.add_row("storage", storage_label)
    else:
        assert isinstance(storage, LocalStorageConfig)
        path_label = storage.path or ".regiswitch/profiles/ (default)"
        table.add_row("storage.type", "local")
        table.add_row("storage.path", path_label)

    console.print(table)
