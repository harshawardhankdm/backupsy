"""Build compressed archives from source folders, honoring exclude patterns."""

from __future__ import annotations

import fnmatch
import logging
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

logger = logging.getLogger("backupsy.archive")


def _is_excluded(path: Path, exclude_patterns: Iterable[str]) -> bool:
    name = path.name
    posix = path.as_posix()
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(posix, pattern):
            return True
    return False


def build_archive_name(prefix: str) -> str:
    """Generate a timestamped archive filename, e.g. backup-20260706-153000.tar.gz"""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{ts}.tar.gz"


def create_archive(source_paths: list[str], exclude: list[str], output_path: Path) -> Path:
    """
    Create a tar.gz archive at output_path containing all files under source_paths,
    skipping anything matching an exclude pattern. Returns the output_path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    def _filter(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo | None:
        p = Path(tarinfo.name)
        if _is_excluded(p, exclude):
            logger.debug("Excluding %s", tarinfo.name)
            return None
        return tarinfo

    with tarfile.open(output_path, "w:gz") as tar:
        for source in source_paths:
            source_path = Path(source).expanduser().resolve()
            if not source_path.exists():
                logger.warning("Source path does not exist, skipping: %s", source_path)
                continue
            arcname = source_path.name
            tar.add(source_path, arcname=arcname, filter=_filter)

    logger.info("Created archive %s (%.2f MB)", output_path, output_path.stat().st_size / (1024 * 1024))
    return output_path
