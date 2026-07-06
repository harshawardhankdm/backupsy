from datetime import datetime, timedelta, timezone

from backupsy.config import RotationConfig
from backupsy.rotation import objects_to_delete
from backupsy.storage.base import RemoteObject


def make_objects(n: int, now: datetime, days_apart: int = 1):
    """Create n fake objects, most recent first, one per `days_apart` days."""
    return [
        RemoteObject(
            key=f"backup-{i}.tar.gz",
            last_modified=now - timedelta(days=i * days_apart),
            size_bytes=1024,
        )
        for i in range(n)
    ]


def test_no_rotation_rules_deletes_nothing():
    now = datetime.now(timezone.utc)
    objects = make_objects(10, now)
    result = objects_to_delete(objects, RotationConfig(), now=now)
    assert result == []


def test_keep_last_deletes_older_ones():
    now = datetime.now(timezone.utc)
    objects = make_objects(10, now)
    result = objects_to_delete(objects, RotationConfig(keep_last=3), now=now)
    assert len(result) == 7
    kept_keys = {o.key for o in objects} - {o.key for o in result}
    assert kept_keys == {"backup-0.tar.gz", "backup-1.tar.gz", "backup-2.tar.gz"}


def test_keep_days_deletes_old_ones():
    now = datetime.now(timezone.utc)
    objects = make_objects(10, now, days_apart=5)  # spans 0,5,10,...,45 days back
    result = objects_to_delete(objects, RotationConfig(keep_days=20), now=now)
    deleted_keys = {o.key for o in result}
    # Objects older than 20 days: index 5 (25 days) through 9 (45 days)
    assert deleted_keys == {f"backup-{i}.tar.gz" for i in range(5, 10)}


def test_combined_rules_are_intersected_with_and():
    now = datetime.now(timezone.utc)
    objects = make_objects(10, now, days_apart=3)  # 0,3,6,...,27 days back
    # keep_last=4 keeps indices 0-3 (0,3,6,9 days back)
    # keep_days=5 keeps only things within 5 days: indices 0,1 (0,3 days back)
    # A backup must satisfy BOTH to survive -> only indices 0,1 survive
    result = objects_to_delete(
        objects, RotationConfig(keep_last=4, keep_days=5), now=now
    )
    deleted_keys = {o.key for o in result}
    assert deleted_keys == {f"backup-{i}.tar.gz" for i in [2, 3, 4, 5, 6, 7, 8, 9]}


def test_empty_object_list_returns_empty():
    result = objects_to_delete([], RotationConfig(keep_last=5))
    assert result == []
