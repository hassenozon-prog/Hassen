#!/usr/bin/env python3
"""Optional semantic retrieval adapter.

The repository remains dependency-free. A future embedding backend can implement
the SemanticBackend protocol and feed scored candidates into HybridRetriever.
"""
from __future__ import annotations
from typing import Protocol, Sequence

class SemanticBackend(Protocol):
    def search(self, query: str, limit: int) -> Sequence[dict]: ...

class SemanticAdapter:
    def __init__(self, backend=None):
        self.backend=backend

    def search(self, query: str, limit=8):
        if self.backend is None:
            return []
        return list(self.backend.search(query,limit))
