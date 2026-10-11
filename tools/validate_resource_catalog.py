#!/usr/bin/env python3
"""Validate the legal resource catalog without accessing external sites."""
import csv
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "sources" / "resource-catalog.csv"
REQUIRED = ["resource_id", "name", "resource_type", "jurisdiction", "topics", "url",
            "ownership_type", "authority_rank", "access_and_use", "verification_notes",
            "record_status", "last_checked"]
ALLOWED_RANKS = {"primary", "secondary", "discovery_only"}
ALLOWED_STATUS = {"seeded_candidate", "reviewed", "inactive", "blocked"}

def validate(path=CATALOG):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != REQUIRED:
            raise ValueError("Unexpected catalog columns")
        rows = list(reader)
    ids, urls, errors = set(), set(), []
    for line, row in enumerate(rows, start=2):
        rid, url = row["resource_id"].strip(), row["url"].strip()
        parsed = urlparse(url)
        if not rid or rid in ids: errors.append(f"line {line}: missing/duplicate resource_id")
        if not row["name"].strip(): errors.append(f"line {line}: missing name")
        if parsed.scheme != "https" or not parsed.netloc: errors.append(f"line {line}: URL must be https")
        if url in urls: errors.append(f"line {line}: duplicate URL")
        if row["authority_rank"] not in ALLOWED_RANKS: errors.append(f"line {line}: invalid authority_rank")
        if row["record_status"] not in ALLOWED_STATUS: errors.append(f"line {line}: invalid record_status")
        if row["record_status"] == "reviewed" and not row["last_checked"].strip():
            errors.append(f"line {line}: reviewed record requires last_checked")
        if row["authority_rank"] == "discovery_only" and "لا تعتمد" not in row["verification_notes"] and "لا تُعامل" not in row["verification_notes"] and "لا تعتبر" not in row["verification_notes"]:
            errors.append(f"line {line}: discovery-only record must disclose non-authoritative use")
        ids.add(rid); urls.add(url)
    if errors: raise ValueError("\n".join(errors))
    return len(rows)

if __name__ == "__main__":
    print(f"OK: {validate()} resource records")
