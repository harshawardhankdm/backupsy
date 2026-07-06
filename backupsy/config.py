"""Load and validate backupsy's YAML configuration file."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


class ConfigError(Exception):
    """Raised when the configuration file is missing required fields or invalid."""


@dataclass
class SourceConfig:
    paths: list[str]
    exclude: list[str] = field(default_factory=list)


@dataclass
class ArchiveConfig:
    name_prefix: str = "backup"
    format: str = "tar.gz"  # currently only tar.gz is supported


@dataclass
class DestinationConfig:
    type: str
    bucket: str
    prefix: str = ""
    endpoint_url: Optional[str] = None
    region: Optional[str] = None
    access_key_env: str = "BACKUPSY_S3_ACCESS_KEY"
    secret_key_env: str = "BACKUPSY_S3_SECRET_KEY"

    def access_key(self) -> Optional[str]:
        return os.environ.get(self.access_key_env)

    def secret_key(self) -> Optional[str]:
        return os.environ.get(self.secret_key_env)


@dataclass
class RotationConfig:
    keep_last: Optional[int] = None
    keep_days: Optional[int] = None


@dataclass
class NotifyConfig:
    webhook_url_env: Optional[str] = None
    on_success: bool = False
    on_failure: bool = True

    def webhook_url(self) -> Optional[str]:
        if not self.webhook_url_env:
            return None
        return os.environ.get(self.webhook_url_env)


@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: Optional[str] = None


@dataclass
class Config:
    source: SourceConfig
    archive: ArchiveConfig
    destination: DestinationConfig
    rotation: RotationConfig
    notify: NotifyConfig
    logging: LoggingConfig


def load_config(path: str | Path) -> Config:
    """Read a YAML file from disk and turn it into a validated Config object."""
    path = Path(path)
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    try:
        source_raw = raw["source"]
        source = SourceConfig(
            paths=source_raw["paths"],
            exclude=source_raw.get("exclude", []),
        )
    except KeyError as e:
        raise ConfigError(f"Missing required source field: {e}") from e

    archive_raw = raw.get("archive", {})
    archive = ArchiveConfig(
        name_prefix=archive_raw.get("name_prefix", "backup"),
        format=archive_raw.get("format", "tar.gz"),
    )

    try:
        dest_raw = raw["destination"]
        destination = DestinationConfig(
            type=dest_raw.get("type", "s3"),
            bucket=dest_raw["bucket"],
            prefix=dest_raw.get("prefix", ""),
            endpoint_url=dest_raw.get("endpoint_url"),
            region=dest_raw.get("region"),
            access_key_env=dest_raw.get("access_key_env", "BACKUPSY_S3_ACCESS_KEY"),
            secret_key_env=dest_raw.get("secret_key_env", "BACKUPSY_S3_SECRET_KEY"),
        )
    except KeyError as e:
        raise ConfigError(f"Missing required destination field: {e}") from e

    if destination.type != "s3":
        raise ConfigError(
            f"Unsupported destination type '{destination.type}'. Only 's3' is supported in v1."
        )

    rotation_raw = raw.get("rotation", {})
    rotation = RotationConfig(
        keep_last=rotation_raw.get("keep_last"),
        keep_days=rotation_raw.get("keep_days"),
    )

    notify_raw = raw.get("notify", {})
    notify = NotifyConfig(
        webhook_url_env=notify_raw.get("webhook_url_env"),
        on_success=notify_raw.get("on_success", False),
        on_failure=notify_raw.get("on_failure", True),
    )

    logging_raw = raw.get("logging", {})
    logging_cfg = LoggingConfig(
        level=logging_raw.get("level", "INFO"),
        file=logging_raw.get("file"),
    )

    return Config(
        source=source,
        archive=archive,
        destination=destination,
        rotation=rotation,
        notify=notify,
        logging=logging_cfg,
    )
