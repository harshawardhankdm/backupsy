"""Orchestrates a full backup run: archive -> upload -> rotate -> notify."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from .archive import build_archive_name, create_archive
from .config import Config
from .notify import send_notification
from .rotation import objects_to_delete
from .storage import build_storage_backend

logger = logging.getLogger("backupsy.runner")


def run_backup(config: Config, dry_run: bool = False) -> bool:
    """
    Execute one full backup cycle. Returns True on success, False on failure.
    In dry-run mode, no files are uploaded or deleted -- only logged.
    """
    try:
        archive_name = build_archive_name(config.archive.name_prefix)
        remote_key = f"{config.destination.prefix.rstrip('/')}/{archive_name}".lstrip("/")

        with tempfile.TemporaryDirectory() as tmp_dir:
            local_archive = Path(tmp_dir) / archive_name

            logger.info("Archiving %s", config.source.paths)
            if not dry_run:
                create_archive(config.source.paths, config.source.exclude, local_archive)
            else:
                logger.info("[dry-run] Would create archive at %s", local_archive)

            backend = build_storage_backend(config.destination)

            if not dry_run:
                backend.upload(local_archive, remote_key)
            else:
                logger.info("[dry-run] Would upload archive to key %s", remote_key)

            existing = backend.list_backups(config.destination.prefix)
            to_delete = objects_to_delete(existing, config.rotation)

            if to_delete:
                logger.info("Rotation: %d old backup(s) to remove", len(to_delete))
                for obj in to_delete:
                    if dry_run:
                        logger.info("[dry-run] Would delete %s (modified %s)", obj.key, obj.last_modified)
                    else:
                        backend.delete(obj.key)
            else:
                logger.info("Rotation: nothing to remove")

        message = f"backup '{archive_name}' uploaded, {len(to_delete)} old backup(s) rotated out"
        if dry_run:
            message = f"[dry-run] {message}"
        logger.info(message)
        send_notification(config.notify, success=True, message=message)
        return True

    except Exception as e:  # noqa: BLE001 - top-level run boundary, we want to catch everything
        logger.exception("Backup run failed")
        send_notification(config.notify, success=False, message=str(e))
        return False
