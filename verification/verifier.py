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

def has_traceable_current_evidence(record: dict[str, Any]) -> bool:
    """True only when the record has both a current claim and traceable review evidence."""
    return bool(
        record.get("verification_status") == "verified"
        and record.get("effective_status") == "current"
        and _has_http_url(record.get("official_url"))
        and _valid_date(record.get("verified_on"))
        and isinstance(record.get("verified_by"), str) and record.get("verified_by").strip()
        and isinstance(record.get("evidence_locator"), str) and record.get("evidence_locator").strip()
    )

def _has_verification_evidence(record: dict[str, Any]) -> bool:
    return bool(
        _has_http_url(record.get("official_url"))
        and _valid_date(record.get("verified_on"))
        and isinstance(record.get("verified_by"), str) and record.get("verified_by").strip()
        and isinstance(record.get("evidence_locator"), str) and record.get("evidence_locator").strip()
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
        if has_traceable_current_evidence(r):
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
