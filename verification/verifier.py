#!/usr/bin/env python3
"""Source verification gate for the legal assistant."""
from __future__ import annotations
from typing import Any

def verify(results: list[dict[str, Any]]) -> dict[str, Any]:
    verified = []
    review = []
    for r in results:
        status = r.get("verification_status", "needs-verification")
        effective = r.get("effective_status", "unknown")
        item = {
            "citation": r.get("citation") or r.get("path"),
            "path": r.get("path"),
            "verification_status": status,
            "effective_status": effective,
        }
        if status == "verified" and effective == "current":
            verified.append(item)
        else:
            review.append(item)
    return {
        "verified_current": verified,
        "needs_review": review,
        "can_support_final_draft": bool(verified),
        "missing_source_phrase": "لم أعثر على النص في المصادر المتاحة",
    }
