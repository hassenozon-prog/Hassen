#!/usr/bin/env python3
"""Validate the legal source register conservatively; no third-party packages."""
from __future__ import annotations
import csv, re, sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

REGISTER = Path("research/source-verification-register.csv")
REQUIRED = ["source_id","authority","source_type","law_name","law_number","year","source_url","source_locator","checked_on","verification_status","effective_status","verified_by","evidence_locator","content_sha256","notes"]
SOURCE_TYPES = {"official_yemeni_statute","official_yemeni_regulation","supreme_court_precedent","official_ministry","prosecution","yemeni_legal_research","fiqh"}
VERIFY = {"source-located-not-content-verified","needs-verification","partially-verified","verified","historical","superseded"}
EFFECT = {"unknown","current","historical","superseded"}

def validate(path: Path = REGISTER) -> list[str]:
    errors = []
    if not path.is_file():
        return [f"Missing register: {path}"]
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if reader.fieldnames != REQUIRED:
            return [f"Header mismatch: expected {REQUIRED}; got {reader.fieldnames}"]
        rows=list(reader)
    seen=set()
    if not rows:
        errors.append("Register contains no records")
    for line,row in enumerate(rows,2):
        sid=row.get("source_id","").strip()
        if not sid: errors.append(f"line {line}: source_id is required")
        if sid in seen: errors.append(f"line {line}: duplicate source_id {sid}")
        seen.add(sid)
        for field in ("authority","source_type","law_name","law_number","year","source_url","source_locator","checked_on","verification_status","effective_status"):
            if not row.get(field,"").strip(): errors.append(f"line {line}: {field} is required")
        parsed=urlparse(row.get("source_url","").strip())
        if parsed.scheme not in {"http","https"} or not parsed.netloc: errors.append(f"line {line}: source_url must be an http(s) URL")
        if not re.fullmatch(r"[0-9]{4}",row.get("year","")): errors.append(f"line {line}: year must be four digits")
        try: date.fromisoformat(row.get("checked_on",""))
        except ValueError: errors.append(f"line {line}: checked_on must be ISO date YYYY-MM-DD")
        if row.get("source_type") not in SOURCE_TYPES: errors.append(f"line {line}: unsupported source_type")
        if row.get("verification_status") not in VERIFY: errors.append(f"line {line}: unsupported verification_status")
        if row.get("effective_status") not in EFFECT: errors.append(f"line {line}: unsupported effective_status")
        if row.get("verification_status")=="verified":
            for field in ("verified_by","evidence_locator"):
                if not row.get(field,"").strip(): errors.append(f"line {line}: verified record requires {field}")
            if not re.fullmatch(r"[a-fA-F0-9]{64}",row.get("content_sha256","")): errors.append(f"line {line}: verified record requires SHA-256 content hash")
        if row.get("effective_status")=="current" and row.get("verification_status")!="verified":
            errors.append(f"line {line}: current requires verified status")
    return errors

if __name__=="__main__":
    issues=validate()
    if issues:
        print("\n".join(issues)); sys.exit(1)
    print(f"Source register valid: {REGISTER}")
