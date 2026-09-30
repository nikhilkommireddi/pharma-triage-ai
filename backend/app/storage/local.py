from pathlib import Path

from app.storage.base import StorageBackend


class LocalFilesystemStorage(StorageBackend):
    def __init__(self, root: str | Path) -> None:
        self._root = Path(root).resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, data: bytes) -> None:
        self._resolve(key).write_bytes(data)

    def read(self, key: str) -> bytes:
        return self._resolve(key).read_bytes()

    def _resolve(self, key: str) -> Path:
        path = (self._root / key).resolve()
        if path != self._root and self._root not in path.parents:
            raise ValueError(f"storage key resolves outside storage root: {key!r}")
        return path
