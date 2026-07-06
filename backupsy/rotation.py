"""Decide which existing backups should be deleted, based on rotation rules.

Kept as a pure function (no I/O) so it's trivial to unit test.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .config import RotationConfig
from .storage.base import RemoteObject


def objects_to_delete(
    objects: list[RemoteObject], rotation: RotationConfig, now: datetime | None = None
) -> list[RemoteObject]:
    """
    Given all existing backup objects at the destination, return the ones that
    should be deleted according to the rotation policy.

    - keep_last: keep only the N most recent backups, delete the rest.
    - keep_days: additionally, delete anything older than N days.
    - If both are set, an object survives only if it satisfies both rules
      (i.e. it's within the last N backups AND within the day window).
    - If neither is set, nothing is deleted.
    """
    if not objects:
        return []

    now = now or datetime.now(timezone.utc)
    sorted_objects = sorted(objects, key=lambda o: o.last_modified, reverse=True)

    survivors = set(o.key for o in sorted_objects)

    if rotation.keep_last is not None:
        keep_keys = {o.key for o in sorted_objects[: rotation.keep_last]}
        survivors &= keep_keys

    if rotation.keep_days is not None:
        cutoff = now - timedelta(days=rotation.keep_days)
        keep_keys = {o.key for o in sorted_objects if o.last_modified >= cutoff}
        survivors &= keep_keys

    if rotation.keep_last is None and rotation.keep_days is None:
        return []

    return [o for o in sorted_objects if o.key not in survivors]
