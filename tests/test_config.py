import os

import pytest

from backupsy.config import ConfigError, load_config


def write_config(tmp_path, content: str):
    path = tmp_path / "config.yaml"
    path.write_text(content)
    return path


def test_load_valid_config(tmp_path):
    path = write_config(
        tmp_path,
        """
source:
  paths:
    - /tmp/data
destination:
  type: s3
  bucket: my-bucket
rotation:
  keep_last: 5
""",
    )
    cfg = load_config(path)
    assert cfg.source.paths == ["/tmp/data"]
    assert cfg.destination.bucket == "my-bucket"
    assert cfg.rotation.keep_last == 5
    # defaults
    assert cfg.archive.name_prefix == "backup"
    assert cfg.notify.on_failure is True


def test_missing_source_raises(tmp_path):
    path = write_config(
        tmp_path,
        """
destination:
  type: s3
  bucket: my-bucket
""",
    )
    with pytest.raises(ConfigError):
        load_config(path)


def test_missing_bucket_raises(tmp_path):
    path = write_config(
        tmp_path,
        """
source:
  paths:
    - /tmp/data
destination:
  type: s3
""",
    )
    with pytest.raises(ConfigError):
        load_config(path)


def test_unsupported_destination_type_raises(tmp_path):
    path = write_config(
        tmp_path,
        """
source:
  paths:
    - /tmp/data
destination:
  type: gcs
  bucket: my-bucket
""",
    )
    with pytest.raises(ConfigError):
        load_config(path)


def test_missing_file_raises():
    with pytest.raises(ConfigError):
        load_config("/nonexistent/config.yaml")


def test_access_key_reads_env(tmp_path, monkeypatch):
    path = write_config(
        tmp_path,
        """
source:
  paths:
    - /tmp/data
destination:
  type: s3
  bucket: my-bucket
  access_key_env: MY_CUSTOM_KEY
""",
    )
    monkeypatch.setenv("MY_CUSTOM_KEY", "secret123")
    cfg = load_config(path)
    assert cfg.destination.access_key() == "secret123"
