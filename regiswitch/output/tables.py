from rich.table import Table

from regiswitch.output.console import console


def print_profiles(profiles: list[str], active: str | None) -> None:
    table = Table(title="Profiles", show_header=True, header_style="bold cyan")
    table.add_column("Name")
    table.add_column("Active")
    for p in profiles:
        marker = "[green]✓[/green]" if p == active else ""
        table.add_row(p, marker)
    console.print(table)


def print_status(active_profile: str | None, rows: list[dict]) -> None:
    label = f"[green]{active_profile}[/green]" if active_profile else "[yellow]none[/yellow]"
    console.print(f"Active profile: {label}")
    if not rows:
        console.print("[dim]No registered files.[/dim]")
        return
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("File")
    table.add_column("Live")
    table.add_column("Stored in profile")
    for row in rows:
        live = "[green]✓[/green]" if row["live"] else "[red]✗[/red]"
        stored = "[green]✓[/green]" if row["stored"] else "[yellow]–[/yellow]"
        table.add_row(row["path"], live, stored)
    console.print(table)
