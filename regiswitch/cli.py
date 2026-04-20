import click
from regiswitch.registry import Registry


def _reg() -> Registry:
    return Registry()


def _bail(e: Exception):
    raise click.ClickException(str(e))


@click.group()
@click.version_option()
def main():
    """Switch registered files between named profiles."""


# ------------------------------------------------------------------ profile

@main.group()
def profile():
    """Manage profiles."""


@profile.command("add")
@click.argument("name")
def profile_add(name):
    """Create a new profile."""
    r = _reg()
    try:
        r.profile_add(name)
    except ValueError as e:
        _bail(e)
    active = " (now active)" if r.current_profile == name else ""
    click.echo(f"Profile '{name}' created{active}.")


@profile.command("list")
def profile_list():
    """List all profiles."""
    r = _reg()
    if not r.profiles:
        click.echo("No profiles. Run: regiswitch profile add <name>")
        return
    for name in r.profiles:
        marker = "*" if name == r.current_profile else " "
        click.echo(f"  {marker} {name}")


@profile.command("rm")
@click.argument("name")
def profile_rm(name):
    """Delete a profile and its stored files."""
    r = _reg()
    try:
        r.profile_remove(name)
    except ValueError as e:
        _bail(e)
    click.echo(f"Profile '{name}' removed.")


# ------------------------------------------------------------------ register

@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--profile", "-p", default=None, help="Target profile (default: current)")
def register(file, profile):
    """Register a file and snapshot it into a profile."""
    r = _reg()
    try:
        r.register(file, profile)
    except (ValueError, FileNotFoundError) as e:
        _bail(e)
    used = profile or r.current_profile
    click.echo(f"Registered '{file}' in profile '{used}'.")


@main.command()
@click.argument("file")
def unregister(file):
    """Unregister a file from all profiles."""
    r = _reg()
    r.unregister(file)
    click.echo(f"Unregistered '{file}'.")


# ------------------------------------------------------------------ snapshot

@main.command()
@click.option("--profile", "-p", default=None, help="Target profile (default: current)")
def snapshot(profile):
    """Save current state of all registered files into a profile."""
    r = _reg()
    try:
        saved = r.snapshot(profile)
    except ValueError as e:
        _bail(e)
    used = profile or r.current_profile
    if not saved:
        click.echo("No registered files found on disk.")
        return
    click.echo(f"Snapshot saved to profile '{used}':")
    for f in saved:
        click.echo(f"  {f}")


# ------------------------------------------------------------------ switch

@main.command()
@click.argument("profile_name")
@click.option("--force", is_flag=True, help="Skip files with no stored version instead of aborting.")
def switch(profile_name, force):
    """Switch to a profile, replacing registered files with stored versions."""
    r = _reg()
    try:
        applied, skipped = r.switch(profile_name, force=force)
    except ValueError as e:
        _bail(e)
    click.echo(f"Switched to profile '{profile_name}'.")
    for f in applied:
        click.echo(f"  applied  {f}")
    for f in skipped:
        click.echo(f"  skipped  {f}  (no stored version)")


# ------------------------------------------------------------------ store

@main.group()
def store():
    """Configure the blob store backend."""


@store.command("status")
def store_status():
    """Show current store configuration."""
    r = _reg()
    cfg = r.store_config
    kind = cfg.get("type", "local")
    click.echo(f"Store type: {kind}")
    if kind == "local":
        click.echo(f"  path: {r._base / 'store'}")
    elif kind == "s3":
        click.echo(f"  bucket:       {cfg.get('bucket')}")
        click.echo(f"  prefix:       {cfg.get('prefix', 'regiswitch/')}")
        click.echo(f"  region:       {cfg.get('region') or '(default)'}")
        click.echo(f"  endpoint_url: {cfg.get('endpoint_url') or '(default)'}")


@store.command("use-local")
@click.option("--migrate", is_flag=True, help="Copy blobs from current store to local store first.")
def store_use_local(migrate):
    """Switch to local filesystem store (~/.regiswitch/store/)."""
    r = _reg()
    if r.store_config.get("type") == "local":
        click.echo("Already using local store.")
        return
    try:
        n = r.set_store({"type": "local"}, migrate=migrate)
    except Exception as e:
        _bail(e)
    msg = f"  ({n} blob(s) migrated)" if migrate else ""
    click.echo(f"Switched to local store.{msg}")


@store.command("use-s3")
@click.option("--bucket", required=True, help="S3 bucket name.")
@click.option("--prefix", default="regiswitch/", show_default=True, help="Key prefix inside the bucket.")
@click.option("--region", default=None, help="AWS region (uses default chain if omitted).")
@click.option("--endpoint-url", default=None, help="Custom endpoint URL (e.g. for MinIO).")
@click.option("--migrate", is_flag=True, help="Copy existing blobs to S3 before switching.")
def store_use_s3(bucket, prefix, region, endpoint_url, migrate):
    """Switch to S3 blob store. Requires boto3 (pip install 'regiswitch[s3]')."""
    r = _reg()
    cfg = {
        "type": "s3",
        "bucket": bucket,
        "prefix": prefix,
    }
    if region:
        cfg["region"] = region
    if endpoint_url:
        cfg["endpoint_url"] = endpoint_url
    try:
        n = r.set_store(cfg, migrate=migrate)
    except Exception as e:
        _bail(e)
    msg = f"  ({n} blob(s) migrated)" if migrate else ""
    click.echo(f"Switched to S3 store (bucket: {bucket}).{msg}")


# ------------------------------------------------------------------ status / list

@main.command()
def status():
    """Show current profile and registered files."""
    r = _reg()
    current = r.current_profile or "(none)"
    click.echo(f"Current profile: {current}")
    click.echo(f"Profiles: {', '.join(r.profiles) or '(none)'}")
    click.echo(f"Registered files: {len(r.files)}")
    for fp in r.files:
        parts = [p for p in r.profiles if r.has_stored(p, fp)]
        stored = f"[{', '.join(parts)}]" if parts else "[no snapshots]"
        click.echo(f"  {fp}  {stored}")


@main.command(name="list")
def list_files():
    """List registered files."""
    r = _reg()
    if not r.files:
        click.echo("No registered files.")
        return
    for fp in r.files:
        click.echo(fp)
