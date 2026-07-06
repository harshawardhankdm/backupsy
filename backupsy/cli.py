"""backupsy command-line interface."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import click

from . import __version__
from .config import ConfigError, load_config
from .logging_utils import setup_logging
from .runner import run_backup

EXAMPLE_CONFIG_NAME = "config.example.yaml"


@click.group()
@click.version_option(__version__, prog_name="backupsy")
def main():
    """backupsy: back up folders to S3-compatible storage, with rotation and alerts."""


@main.command()
@click.option(
    "--output",
    "-o",
    default="config.yaml",
    show_default=True,
    help="Where to write the generated config file.",
)
def init(output: str):
    """Generate a starter config.yaml you can edit."""
    output_path = Path(output)
    if output_path.exists():
        click.echo(f"Refusing to overwrite existing file: {output_path}", err=True)
        sys.exit(1)

    package_dir = Path(__file__).resolve().parent.parent
    example_path = package_dir / EXAMPLE_CONFIG_NAME

    if example_path.exists():
        shutil.copy(example_path, output_path)
    else:
        # Fallback if the example file isn't bundled (e.g. some install methods)
        output_path.write_text(_FALLBACK_CONFIG, encoding="utf-8")

    click.echo(f"Wrote {output_path}. Edit it, then run: backupsy run --config {output_path}")


@main.command()
@click.option("--config", "-c", "config_path", required=True, help="Path to config.yaml")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would happen without uploading or deleting anything.")
def run(config_path: str, dry_run: bool):
    """Run a backup: archive source folders, upload to S3, rotate old backups."""
    try:
        cfg = load_config(config_path)
    except ConfigError as e:
        click.echo(f"Config error: {e}", err=True)
        sys.exit(1)

    setup_logging(cfg.logging)
    success = run_backup(cfg, dry_run=dry_run)
    sys.exit(0 if success else 1)


_FALLBACK_CONFIG = """\
source:
  paths:
    - /path/to/folder
  exclude:
    - "*.tmp"
    - "*.log"

archive:
  name_prefix: "backup"
  format: "tar.gz"

destination:
  type: s3
  bucket: my-bucket
  prefix: backups/
  endpoint_url: null
  region: us-east-1
  access_key_env: BACKUPSY_S3_ACCESS_KEY
  secret_key_env: BACKUPSY_S3_SECRET_KEY

rotation:
  keep_last: 7
  keep_days: null

notify:
  webhook_url_env: BACKUPSY_WEBHOOK_URL
  on_success: false
  on_failure: true

logging:
  level: INFO
  file: null
"""


if __name__ == "__main__":
    main()
