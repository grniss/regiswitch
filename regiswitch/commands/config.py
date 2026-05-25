from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from regiswitch.models.config import LocalStorageConfig, S3StorageConfig
from regiswitch.output.console import console, err_console
from regiswitch.output.tables import print_config_table
from regiswitch.utils.errors import NotInitializedError
from regiswitch.utils.fs import find_project_root, load_config, save_config

EXIT_OK = 0
EXIT_INPUT_ERROR = 1

app = typer.Typer(help="Manage regiswitch configuration.")


@app.command("show")
def config_show() -> None:
    """Show the current regiswitch configuration."""
    try:
        root = find_project_root(Path.cwd())
        config = load_config(root)
    except NotInitializedError as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=EXIT_INPUT_ERROR)
    print_config_table(config)


@app.command("set-storage")
def config_set_storage(
    storage_type: Annotated[
        str,
        typer.Argument(help="Storage backend type: 'local' or 's3'."),
    ],
    path: Annotated[
        str | None,
        typer.Option("--path", help="[local] Absolute path to store profiles. Defaults to .regiswitch/profiles/."),
    ] = None,
    bucket: Annotated[
        str | None,
        typer.Option("--bucket", help="[s3] S3 bucket name."),
    ] = None,
    prefix: Annotated[
        str,
        typer.Option("--prefix", help="[s3] Key prefix inside the bucket (acts like a folder)."),
    ] = "",
    region: Annotated[
        str,
        typer.Option("--region", help="[s3] AWS region."),
    ] = "us-east-1",
) -> None:
    """Switch the storage backend for profile files.

    Local storage (default):
      regiswitch config set-storage local
      regiswitch config set-storage local --path /shared/profiles

    S3 storage:
      regiswitch config set-storage s3 --bucket my-bucket
      regiswitch config set-storage s3 --bucket my-bucket --prefix myproject --region eu-west-1

    Switching storage does NOT migrate existing profiles. Save them first if needed.
    Uses the ambient AWS credentials (env vars, ~/.aws/credentials, IAM role, etc.).
    """
    if storage_type not in ("local", "s3"):
        err_console.print(f"[red]Error:[/red] Unknown storage type '{storage_type}'. Use 'local' or 's3'.")
        raise typer.Exit(code=EXIT_INPUT_ERROR)

    if storage_type == "s3" and not bucket:
        err_console.print("[red]Error:[/red] --bucket is required for s3 storage.")
        raise typer.Exit(code=EXIT_INPUT_ERROR)

    try:
        root = find_project_root(Path.cwd())
        config = load_config(root)
    except NotInitializedError as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=EXIT_INPUT_ERROR)

    if storage_type == "local":
        config.storage = LocalStorageConfig(path=path or None)
        label = path or ".regiswitch/profiles/ (default)"
    else:
        config.storage = S3StorageConfig(bucket=bucket, prefix=prefix, region=region)  # type: ignore[arg-type]
        label = f"s3://{bucket}/{prefix}" if prefix else f"s3://{bucket}"

    save_config(root, config)
    console.print(f"[green]Storage set to[/green] [bold]{storage_type}[/bold]: {label}")
