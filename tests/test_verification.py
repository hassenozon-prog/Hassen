import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verification.verifier import verify

def test_current_verified_source():
    r = verify([{
        "path": "x.md", "citation": "x",
        "verification_status": "verified", "effective_status": "current"
    }])
    assert r["can_support_final_draft"]

def test_unverified_source_requires_review():
    r = verify([{
        "path": "x.md", "citation": "x",
        "verification_status": "needs-verification", "effective_status": "unknown"
    }])
    assert not r["can_support_final_draft"]
