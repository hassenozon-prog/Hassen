#!/usr/bin/env python3
"""Validate the article-level verification register without third-party packages."""
from __future__ import annotations
import csv, re, sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
REGISTER = Path("research/article-verification-register.csv")
FIELDS = ["article_record_id","law_name","law_number","year","article_number","repository_path","official_source_url","official_source_locator","repository_content_status","verification_status","effective_status","last_checked","verified_by","evidence_locator","notes"]
VERIFICATION = {"needs-verification","partially-verified","verified","historical","superseded"}
EFFECTIVE = {"unknown","current","historical","superseded"}
def validate(path: Path = REGISTER) -> list[str]:
    errors=[]
    if not path.is_file(): return [f"Missing register: {path}"]
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if reader.fieldnames != FIELDS: return ["Article register header mismatch"]
        rows=list(reader)
    if not rows: errors.append("Article register contains no records")
    seen=set()
    for line,row in enumerate(rows,2):
        rid=row.get("article_record_id","").strip()
        if not rid: errors.append(f"line {line}: article_record_id required")
        if rid in seen: errors.append(f"line {line}: duplicate article_record_id {rid}")
        seen.add(rid)
        for field in FIELDS[:12]:
            if not row.get(field,"").strip(): errors.append(f"line {line}: {field} required")
        if not re.fullmatch(r"[0-9]{4}",row.get("year","")): errors.append(f"line {line}: invalid year")
        if not row.get("article_number","").isdigit(): errors.append(f"line {line}: article_number must be numeric")
        u=urlparse(row.get("official_source_url",""))
        if u.scheme not in {"http","https"} or not u.netloc: errors.append(f"line {line}: invalid official_source_url")
        try: date.fromisoformat(row.get("last_checked",""))
        except ValueError: errors.append(f"line {line}: invalid last_checked date")
        if row.get("verification_status") not in VERIFICATION: errors.append(f"line {line}: invalid verification_status")
        if row.get("effective_status") not in EFFECTIVE: errors.append(f"line {line}: invalid effective_status")
        if row.get("effective_status")=="current" and row.get("verification_status")!="verified":
            errors.append(f"line {line}: current requires verified status")
        if row.get("verification_status")=="verified":
            if not row.get("verified_by","").strip() or not row.get("evidence_locator","").strip():
                errors.append(f"line {line}: verified record requires reviewer and evidence locator")
    return errors
if __name__=="__main__":
    errors=validate()
    if errors: print("\n".join(errors)); sys.exit(1)
    print(f"Article verification register valid: {REGISTER}")
