import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from retrieval.engine import LegalRetriever, normalize_arabic

def test_arabic_normalization():
    assert normalize_arabic("أحكامٌ وإثبات") == normalize_arabic("احكام وإثبات")

def test_unsubstantiated_verified_metadata_is_downgraded():
    from retrieval.engine import extract_metadata
    meta = extract_metadata(Path("499.yml"), 'verification_status: "verified"\neffective_status: "current"\nurl: "https://example.gov.ye/law"\nverified_on: "2026-10-11"\n')
    assert meta["verification_status"] == "needs-verification"
    assert meta["effective_status"] == "unknown"

def test_retrieval_finds_article():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "laws" / "criminal-procedure" / "articles"
        p.mkdir(parents=True)
        (p / "367.md").write_text(
            "# المادة 367\n"
            "لا يجوز أن يبني الحكم على دليل لم يطرح على المحكمة في الجلسة.\n"
            "source_type: official_yemeni_statute\n"
            "verification_status: verified\n"
            "effective_status: current\n",
            encoding="utf-8",
        )
        r = LegalRetriever(d)
        assert r.build() > 0
        results = r.search("دليل لم يطرح في الجلسة المادة 367")
        assert results
        assert "367.md" in results[0]["path"]

def test_resource_catalog_is_searchable_but_not_authoritative():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        p = root / "sources" / "resource-catalog.csv"
        p.parent.mkdir(parents=True)
        p.write_text("\\n".join([
            "resource_id,name,resource_type,jurisdiction,topics,url,ownership_type,authority_rank,access_and_use,verification_notes,record_status,last_checked",
            "QA-1,البوابة القانونية القطرية,official_legal_portal,Qatar,تشريعات ومحكمة التمييز,https://www.almeezan.qa/,official,primary,open,verify original,seeded_candidate,2026-10-11",
        ]) + "\\n", encoding="utf-8")
        r = LegalRetriever(root)
        assert r.build() > 0
        results = r.search("محكمة التمييز تشريعات قطر")
        assert results
        assert results[0]["verification_status"] == "discovery-only"
        assert results[0]["effective_status"] == "unknown"

if __name__ == "__main__":
    test_arabic_normalization()
    test_retrieval_finds_article()
    test_unsubstantiated_verified_metadata_is_downgraded()
    test_resource_catalog_is_searchable_but_not_authoritative()
    print("OK")
