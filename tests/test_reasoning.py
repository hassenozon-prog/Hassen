import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reasoning.legal_reasoner import build_reasoning, classify_issue, extract_legal_numbers

def test_issue_classification():
    assert classify_issue("هل يجوز الاعتماد على دليل لم يطرح في الجلسة؟") == "trial_evidence_and_deliberation"

def test_numbers():
    x = extract_legal_numbers("المادة 367 من قانون رقم 13 لسنة 1994 والطعن رقم 12/1445")
    assert "367" in x["articles"]
    assert any("13" in item for item in x["laws"])
    assert "12/1445" in x["cases"]

def test_verified_source_is_supported():
    result = build_reasoning("المادة 367", [{
        "path": "laws/criminal-procedure/articles/367.md",
        "title": "المادة 367",
        "text": "لا يجوز بناء الحكم على دليل لم يطرح في الجلسة.",
        "citation": "قانون الإجراءات الجزائية — مادة 367",
        "verification_status": "verified",
        "effective_status": "current",
        "official_url": "https://example.gov.ye/law",
        "verified_on": "2026-10-11",
        "verified_by": "reviewer",
        "evidence_locator": "article 367, official publication",
        "score": 0.8
    }])
    assert result["supported_sources"]
    assert not result["warnings"]
