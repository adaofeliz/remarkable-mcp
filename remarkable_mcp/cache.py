from __future__ import annotations

import dataclasses
import logging
import threading
import time
from typing import Protocol

from remarkable_mcp.sync import Document

CACHE_TTL_SECONDS = 300
logger = logging.getLogger(__name__)


class _MetaItemsClient(Protocol):
    def get_meta_items(self) -> list[Document]: ...


@dataclasses.dataclass(frozen=True)
class DocumentSnapshot:
    documents: list[Document]
    items_by_id: dict[str, Document]
    items_by_parent: dict[str, list[Document]]
    timestamp: float


class DocumentCache:
    def __init__(self, ttl_seconds: int = CACHE_TTL_SECONDS):
        self._ttl: int = ttl_seconds
        self._snapshot: DocumentSnapshot | None = None
        self._lock: threading.Lock = threading.Lock()

    def _build_snapshot(self, documents: list[Document]) -> DocumentSnapshot:
        items_by_id: dict[str, Document] = {item.ID: item for item in documents}
        items_by_parent: dict[str, list[Document]] = {}

        for item in documents:
            parent = item.Parent if hasattr(item, "Parent") else ""
            if parent not in items_by_parent:
                items_by_parent[parent] = []
            items_by_parent[parent].append(item)

        return DocumentSnapshot(
            documents=documents,
            items_by_id=items_by_id,
            items_by_parent=items_by_parent,
            timestamp=time.time(),
        )

    def get_snapshot(self, client: _MetaItemsClient) -> DocumentSnapshot:
        current = self._snapshot
        if current is not None and not self.is_stale():
            return current

        with self._lock:
            current = self._snapshot
            if current is not None and not self.is_stale():
                return current

            stale_snapshot = current
            try:
                return self.refresh(client)
            except Exception as exc:
                if stale_snapshot is not None:
                    logger.warning(
                        "Document cache refresh failed; returning stale snapshot: %s",
                        exc,
                    )
                    return stale_snapshot
                raise

    def refresh(self, client: _MetaItemsClient) -> DocumentSnapshot:
        documents = client.get_meta_items()
        new_snapshot = self._build_snapshot(documents)
        self._snapshot = new_snapshot
        return new_snapshot

    def set_snapshot(self, documents: list[Document]) -> DocumentSnapshot:
        new_snapshot = self._build_snapshot(documents)
        self._snapshot = new_snapshot
        return new_snapshot

    def is_stale(self) -> bool:
        if self._snapshot is None:
            return True
        return (time.time() - self._snapshot.timestamp) > self._ttl

    def invalidate(self) -> None:
        self._snapshot = None


document_cache = DocumentCache()
