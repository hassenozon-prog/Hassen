import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cases.case_engine import analyze_case

def test_case_engine():
    r=analyze_case({"facts":["واقعة"],"evidence":["دليل"],"defenses":["دفع"],"applicable_law":["المادة 367"],"violations":["مخالفة"],"requests":["نقض"]})
    assert r["ready_for_drafting"] and r["legal_links"]

if __name__=="__main__":
    test_case_engine()
