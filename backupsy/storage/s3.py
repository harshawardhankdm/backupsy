"""S3-compatible storage backend.

Works with AWS S3, Backblaze B2 (S3-compatible API), and MinIO by simply
pointing `endpoint_url` at the right host. AWS S3 itself needs no
endpoint_url override.
"""

from __future__ import annotations

import logging
from pathlib import Path

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError

from .base import RemoteObject, StorageBackend

logger = logging.getLogger("backupsy.storage.s3")


class S3StorageBackend(StorageBackend):
    def __init__(
        self,
        bucket: str,
        access_key: str | None,
        secret_key: str | None,
        endpoint_url: str | None = None,
        region: str | None = None,
    ):
        if not access_key or not secret_key:
            raise ValueError(
                "S3 credentials are missing. Set the environment variables named in "
                "destination.access_key_env / destination.secret_key_env in your config."
            )

        self.bucket = bucket
        session = boto3.session.Session()
        self.client = session.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
            region_name=region,
            config=BotoConfig(signature_version="s3v4"),
        )

    def upload(self, local_path: Path, remote_key: str) -> None:
        logger.info("Uploading %s to s3://%s/%s", local_path, self.bucket, remote_key)
        self.client.upload_file(str(local_path), self.bucket, remote_key)

    def list_backups(self, prefix: str) -> list[RemoteObject]:
        objects: list[RemoteObject] = []
        paginator = self.client.get_paginator("list_objects_v2")
        try:
            for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
                for obj in page.get("Contents", []):
                    objects.append(
                        RemoteObject(
                            key=obj["Key"],
                            last_modified=obj["LastModified"],
                            size_bytes=obj["Size"],
                        )
                    )
        except ClientError as e:
            logger.error("Failed to list objects in bucket %s: %s", self.bucket, e)
            raise
        return objects

    def delete(self, remote_key: str) -> None:
        logger.info("Deleting s3://%s/%s", self.bucket, remote_key)
        self.client.delete_object(Bucket=self.bucket, Key=remote_key)
