import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from retrieval.engine import LegalRetriever, normalize_arabic

def test_arabic_normalization():
    assert normalize_arabic("أحكامٌ وإثبات") == normalize_arabic("احكام وإثبات")

def test_retrieval_finds_article():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "laws" / "criminal-procedure" / "articles"
        p.mkdir(parents=True)
        (p / "367.md").write_text(
            "# المادة 367
"
            "لا يجوز أن يبني الحكم على دليل لم يطرح على المحكمة في الجلسة.
"
            "source_type: official_yemeni_statute
"
            "verification_status: verified
"
            "effective_status: current
",
            encoding="utf-8",
        )
        r = LegalRetriever(d)
        assert r.build() > 0
        results = r.search("دليل لم يطرح في الجلسة المادة 367")
        assert results
        assert "367.md" in results[0]["path"]

if __name__ == "__main__":
    test_arabic_normalization()
    test_retrieval_finds_article()
    print("OK")
