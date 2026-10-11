import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from drafting.legal_drafter import draft

def test_drafter_refuses_without_support():
    result = draft({"question": "سؤال", "facts": []}, {"supported_sources": [], "warnings": []})
    assert result["status"] == "insufficient_verified_support"
    assert result["draft"] == ""

def test_drafter_uses_verified_source():
    result = draft(
        {"question": "المادة 367", "facts": ["الحكم استند إلى دليل غير مطروح"]},
        {"supported_sources": [{
            "citation": "قانون الإجراءات الجزائية — مادة 367",
            "verification_status": "verified",
            "effective_status": "current",
            "official_url": "https://example.gov.ye/law",
            "verified_on": "2026-10-11",
            "verified_by": "reviewer",
            "evidence_locator": "official publication, article 367"
        }], "warnings": []},
        mode="cassation_ground"
    )
    assert result["status"] == "draft_ready_for_legal_review"
    assert "مادة 367" in result["draft"]
