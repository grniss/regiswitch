from rich.table import Table

from regiswitch.models.config import RegisteredFile


def profiles_table(profiles: list[tuple[str, bool]]) -> Table:
    table = Table(title="Profiles", show_header=True, header_style="bold cyan")
    table.add_column("Name")
    table.add_column("Active", justify="center")
    for name, is_active in profiles:
        marker = "[bold green]✓[/bold green]" if is_active else ""
        table.add_row(name, marker)
    return table


def files_table(files: list[RegisteredFile], current_profile: str | None) -> Table:
    table = Table(title="Registered Files", show_header=True, header_style="bold cyan")
    table.add_column("Path", overflow="fold")
    table.add_column("Registered At")
    for rf in files:
        table.add_row(rf.path, rf.registered_at.strftime("%Y-%m-%d %H:%M:%S"))
    return table
