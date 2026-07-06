from ..config import DestinationConfig
from .base import RemoteObject, StorageBackend
from .s3 import S3StorageBackend


def build_storage_backend(destination: DestinationConfig) -> StorageBackend:
    """Factory: turn a DestinationConfig into the right StorageBackend instance."""
    if destination.type == "s3":
        return S3StorageBackend(
            bucket=destination.bucket,
            access_key=destination.access_key(),
            secret_key=destination.secret_key(),
            endpoint_url=destination.endpoint_url,
            region=destination.region,
        )
    raise ValueError(f"Unsupported destination type: {destination.type}")


__all__ = ["StorageBackend", "RemoteObject", "build_storage_backend"]
