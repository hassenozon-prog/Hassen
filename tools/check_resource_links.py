#!/usr/bin/env python3
"""Check public resource URLs on demand; failures are reports, not proof of closure."""
from __future__ import annotations
import argparse, csv, ssl, urllib.error, urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "sources/resource-catalog.csv",
    ROOT / "sources/judiciary-directory.csv",
    ROOT / "sources/legal-journals.csv",
    ROOT / "sources/legal-media-channels.csv",
]
URL_FIELDS = ("url", "official_url", "article_url", "channel_url", "primary_source_url")

def check(url: str, timeout: int = 12) -> tuple[str, str]:
    if not url:
        return "not_applicable", ""
    request = urllib.request.Request(url, headers={"User-Agent": "Hassen-Legal-Resource-Monitor/1.0"}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=ssl.create_default_context()) as response:
            return ("reachable" if response.status < 400 else "http_error", str(response.status))
    except urllib.error.HTTPError as exc:
        return ("http_error", str(exc.code))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        return ("check_failed", type(exc).__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="resource-link-check.csv")
    parser.add_argument("--timeout", type=int, default=12)
    args = parser.parse_args()
    output = []
    for path in FILES:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            for line, row in enumerate(csv.DictReader(stream), start=2):
                url = next((row.get(k, "").strip() for k in URL_FIELDS if row.get(k, "").strip()), "")
                if not url:
                    continue
                status, detail = check(url, args.timeout)
                output.append({
                    "file": str(path.relative_to(ROOT)), "line": line,
                    "record_id": row.get("resource_id") or row.get("record_id") or "",
                    "url": url, "checked_on": date.today().isoformat(),
                    "link_status": status, "http_status_or_error": detail,
                    "note": "A failed request is not proof of closure; manually recheck redirects, access controls, and site policy."
                })
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["file","line","record_id","url","checked_on","link_status","http_status_or_error","note"])
        writer.writeheader(); writer.writerows(output)
    counts = {}
    for row in output: counts[row["link_status"]] = counts.get(row["link_status"], 0) + 1
    print(f"Checked {len(output)} URLs; results: {counts}; report: {report}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
