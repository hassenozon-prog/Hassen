import csv, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.validate_article_register import validate, FIELDS

def row():
    return {
        "article_record_id":"ART-40-2002-499","law_name":"قانون المرافعات والتنفيذ المدني",
        "law_number":"40","year":"2002","article_number":"499",
        "repository_path":"laws/civil-procedure/articles/499.md",
        "official_source_url":"https://www.agoye.gov.ye/page.php?id=478",
        "official_source_locator":"مادة 499","repository_content_status":"present-in-repository-not-compared",
        "verification_status":"needs-verification","effective_status":"unknown",
        "last_checked":"2026-10-11","verified_by":"","evidence_locator":"","notes":"لم يطابق بعد"
    }

def write(path, rows):
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)

def test_valid_needs_verification_record_passes_structural_validation():
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/"articles.csv"; write(p,[row()])
        assert validate(p)==[]

def test_current_unverified_record_is_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        r=row(); r["effective_status"]="current"
        p=Path(tmp)/"articles.csv"; write(p,[r])
        assert any("current requires verified status" in e for e in validate(p))

def test_duplicate_article_record_id_is_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/"articles.csv"; write(p,[row(),row()])
        assert any("duplicate article_record_id" in e for e in validate(p))
