from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Abstraction over where uploaded document bytes live.

    Callers only ever pass a server-generated key (never a client-supplied
    filename), so implementations don't need to defend against path
    traversal from the key itself — but should still not trust its shape.
    """

    @abstractmethod
    def save(self, key: str, data: bytes) -> None: ...

    @abstractmethod
    def read(self, key: str) -> bytes: ...
