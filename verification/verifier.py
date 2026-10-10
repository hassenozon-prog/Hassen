#!/usr/bin/env python3
"""Conservative source-verification gate for the Yemeni legal assistant."""
from __future__ import annotations
from datetime import date
from typing import Any
from urllib.parse import urlparse

def _has_http_url(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

def _valid_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False

def _has_verification_evidence(record: dict[str, Any]) -> bool:
    return bool(
        _has_http_url(record.get("official_url"))
        and _valid_date(record.get("verified_on"))
        and record.get("verified_by")
        and record.get("evidence_locator")
    )

def verify(results: list[dict[str, Any]]) -> dict[str, Any]:
    verified = []
    review = []
    for r in results:
        status = r.get("verification_status", "needs-verification")
        effective = r.get("effective_status", "unknown")
        evidence_ok = _has_verification_evidence(r)
        item = {
            "citation": r.get("citation") or r.get("path"),
            "path": r.get("path"),
            "verification_status": status,
            "effective_status": effective,
            "evidence_complete": evidence_ok,
        }
        if status == "verified" and effective == "current" and evidence_ok:
            verified.append(item)
        else:
            if status == "verified" and not evidence_ok:
                item["review_reason"] = "verified status lacks traceable source evidence"
            elif effective == "current" and status != "verified":
                item["review_reason"] = "current status requires verified source"
            else:
                item["review_reason"] = "source or legal-effect verification incomplete"
            review.append(item)
    return {
        "verified_current": verified,
        "needs_review": review,
        "can_support_final_draft": bool(verified),
        "missing_source_phrase": "لم أعثر على النص في المصادر المتاحة",
    }
