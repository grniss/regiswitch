from typing import Annotated, Optional

import typer

from regiswitch.core.backends import read_backend_config, write_backend_config
from regiswitch.output.console import console, err_console
from regiswitch.utils.errors import RegiswitchError

app = typer.Typer(help="Configure the storage backend.")


@app.command("show")
def backend_show() -> None:
    """Show the current backend configuration."""
    config = read_backend_config()
    backend_type = config.get("type", "local")
    console.print(f"Backend type: [bold cyan]{backend_type}[/bold cyan]")
    if backend_type == "local":
        path = config.get("path") or "[dim](default ~/.config/regiswitch/)[/dim]"
        console.print(f"Storage path: {path}")
    elif backend_type == "s3":
        console.print(f"Bucket:  [bold]{config.get('bucket')}[/bold]")
        console.print(f"Prefix:  {config.get('prefix', 'regiswitch/')}")
        console.print(f"Region:  {config.get('region') or '[dim](default)[/dim]'}")


@app.command("local")
def backend_local(
    path: Annotated[
        Optional[str],
        typer.Option("--path", "-p", help="Custom local storage path. Defaults to ~/.config/regiswitch/."),
    ] = None,
) -> None:
    """Switch to local filesystem storage.

    Optionally specify a custom path (e.g. a Dropbox or network folder) so
    profiles are stored somewhere other than the default ~/.config/regiswitch/.
    """
    try:
        config: dict = {"type": "local"}
        if path:
            config["path"] = path
        write_backend_config(config)
        display_path = path or "~/.config/regiswitch/"
        console.print(f"[green]Backend set to local.[/green] Storage path: [dim]{display_path}[/dim]")
        console.print("Run [bold]regiswitch init[/bold] to initialize the registry at the new location.")
    except RegiswitchError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)


@app.command("s3")
def backend_s3(
    bucket: Annotated[str, typer.Option("--bucket", "-b", help="S3 bucket name.")],
    prefix: Annotated[str, typer.Option("--prefix", help="Key prefix inside the bucket.")] = "regiswitch/",
    region: Annotated[
        Optional[str],
        typer.Option("--region", "-r", help="AWS region. Defaults to AWS_DEFAULT_REGION env var or SDK default."),
    ] = None,
) -> None:
    """Switch to AWS S3 storage.

    Profile snapshots and the registry are stored in the given S3 bucket.
    AWS credentials are resolved via the standard boto3 chain
    (env vars, ~/.aws/credentials, IAM role, etc.).
    """
    try:
        config: dict = {"type": "s3", "bucket": bucket, "prefix": prefix}
        if region:
            config["region"] = region
        write_backend_config(config)
        console.print(f"[green]Backend set to S3.[/green] Bucket: [bold]{bucket}[/bold] Prefix: [dim]{prefix}[/dim]")
        console.print("Run [bold]regiswitch init[/bold] to initialize the registry in the bucket.")
    except RegiswitchError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)
