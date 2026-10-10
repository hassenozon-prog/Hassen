import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verification.verifier import verify

def valid_record():
    return {
        "path": "laws/example/articles/1.md",
        "citation": "قانون افتراضي، المادة (1)",
        "verification_status": "verified",
        "effective_status": "current",
        "official_url": "https://example.gov.ye/law",
        "verified_on": "2026-10-11",
        "verified_by": "legal-review",
        "evidence_locator": "official publication, page 1",
    }

def test_current_verified_source_with_traceable_evidence():
    r = verify([valid_record()])
    assert r["can_support_final_draft"]
    assert len(r["verified_current"]) == 1

def test_claimed_verified_source_without_evidence_is_blocked():
    item = valid_record()
    item.pop("official_url")
    r = verify([item])
    assert not r["can_support_final_draft"]
    assert r["needs_review"][0]["evidence_complete"] is False

def test_unverified_source_requires_review():
    r = verify([{
        "path": "x.md", "citation": "x",
        "verification_status": "needs-verification", "effective_status": "unknown"
    }])
    assert not r["can_support_final_draft"]

def test_current_status_alone_does_not_pass_gate():
    item = valid_record()
    item["verification_status"] = "partially-verified"
    r = verify([item])
    assert not r["can_support_final_draft"]
