from functools import lru_cache

from app.core.config import get_settings
from app.storage.base import StorageBackend
from app.storage.local import LocalFilesystemStorage


@lru_cache
def get_storage() -> StorageBackend:
    return LocalFilesystemStorage(get_settings().storage_dir)
