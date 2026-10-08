import sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ingestion.corpus_manifest import build_manifest

def test_manifest():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"laws"/"x.md"; p.parent.mkdir()
        p.write_text("المادة 1",encoding="utf-8")
        m=build_manifest(d)
        assert m["count"]==1
        assert m["files"][0]["sha256"]

if __name__=="__main__": test_manifest()
