#!/usr/bin/env python3
"""Build a deterministic manifest of the legal corpus."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

EXTENSIONS={".md",".yml",".yaml",".json",".txt"}

def build_manifest(root="."):
    root=Path(root)
    rows=[]
    for p in sorted(root.rglob("*")):
        if not p.is_file() or ".git" in p.parts or p.suffix.lower() not in EXTENSIONS:
            continue
        data=p.read_bytes()
        rows.append({
            "path":p.relative_to(root).as_posix(),
            "bytes":len(data),
            "sha256":hashlib.sha256(data).hexdigest(),
        })
    return {"version":"1.0","files":rows,"count":len(rows)}

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",default=".")
    ap.add_argument("--output",default="corpus-manifest.json")
    a=ap.parse_args()
    Path(a.output).write_text(json.dumps(build_manifest(a.root),ensure_ascii=False,indent=2),encoding="utf-8")
    print(a.output)
