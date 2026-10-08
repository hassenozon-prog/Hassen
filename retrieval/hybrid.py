#!/usr/bin/env python3
"""Hybrid lexical retrieval with legal-field boosting; no external dependencies."""
from __future__ import annotations
import re
from typing import Any
from .engine import LegalRetriever, normalize_arabic, tokens

FIELD_BOOSTS = {
    "laws/": 1.35,
    "principles/": 1.25,
    "cases/": 1.10,
    "sources/": 1.15,
    "fiqh/": 0.95,
    "research/": 0.90,
}

def expand_query(query: str) -> list[str]:
    q = normalize_arabic(query)
    variants = {query}
    if "مداوله" in q or "المداوله" in q:
        variants.update(["المداولة", "سرية المداولة", "المادة 222", "المادة 368"])
    if "دليل" in q and "جلسه" in q:
        variants.update(["دليل لم يطرح في الجلسة", "المادة 367", "المادة 368"])
    if "منازعه تنفيذ" in q:
        variants.update(["المادة 499", "المادة 502", "منازعة تنفيذ وقتية"])
    return list(variants)

class HybridRetriever(LegalRetriever):
    def search_hybrid(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        merged: dict[str, dict[str, Any]] = {}
        for variant in expand_query(query):
            for result in self.search(variant, limit=max(limit, 12)):
                path = result["path"]
                boost = next((v for k,v in FIELD_BOOSTS.items() if path.startswith(k)), 1.0)
                result = dict(result)
                result["score"] = round(result["score"] * boost, 6)
                if path not in merged or result["score"] > merged[path]["score"]:
                    merged[path] = result
        return sorted(merged.values(), key=lambda x: (-x["score"], x["path"]))[:limit]
