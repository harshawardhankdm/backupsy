"""Abstract interface that all storage backends implement.

v1 only ships an S3-compatible backend, but this interface is here so
local-disk and SSH/rsync backends can be added later without touching
the CLI or rotation logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class RemoteObject:
    """Represents one backup file already sitting at the destination."""
    key: str
    last_modified: datetime
    size_bytes: int


class StorageBackend(ABC):
    @abstractmethod
    def upload(self, local_path: Path, remote_key: str) -> None:
        """Upload a local file to the destination under remote_key."""

    @abstractmethod
    def list_backups(self, prefix: str) -> list[RemoteObject]:
        """List all backup objects currently stored under prefix."""

    @abstractmethod
    def delete(self, remote_key: str) -> None:
        """Delete a backup object at the destination."""
