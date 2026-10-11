from pathlib import Path
import sys, tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.validate_resource_catalog import validate

HEADER = "resource_id,name,resource_type,jurisdiction,topics,url,ownership_type,authority_rank,access_and_use,verification_notes,record_status,last_checked,link_status,last_http_status,next_review_due,last_activity_date,managing_entity_evidence,source_page_evidence"

def test_catalog_has_records():
    assert validate() >= 20

def test_validator_rejects_duplicate_ids_and_http():
    content = (
        HEADER + "\n"
        "X-1,One,site,Yemen,law,http://example.com,public,primary,open,verify,seeded_candidate,2026-10-11,not_rechecked,,2026-11-10,,,\n"
        "X-1,Two,site,Yemen,law,https://example.org,public,primary,open,verify,seeded_candidate,2026-10-11,not_rechecked,,2026-11-10,,,\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "catalog.csv"
        path.write_text(content, encoding="utf-8")
        try:
            validate(path)
        except ValueError as exc:
            assert "duplicate resource_id" in str(exc)
            assert "URL must be https" in str(exc)
        else:
            raise AssertionError("Invalid catalog was accepted")

def test_validator_requires_review_date_and_link_status():
    content = (
        HEADER + "\n"
        "X-1,One,site,Yemen,law,https://example.com,public,primary,open,verify,seeded_candidate,2026-10-11,not_rechecked,,2026-11-10,,,\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "catalog.csv"
        path.write_text(content, encoding="utf-8")
        assert validate(path) == 1

if __name__ == "__main__":
    test_catalog_has_records()
    test_validator_rejects_duplicate_ids_and_http()
    test_validator_requires_review_date_and_link_status()
    print("OK")
