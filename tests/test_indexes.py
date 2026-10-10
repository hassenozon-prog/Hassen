import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.rebuild_indexes import build_master, build_status, validate, MASTER, STATUS

class IndexBuilderTests(unittest.TestCase):
    def test_rebuild_is_deterministic_and_conservative(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "laws/civil-procedure/articles").mkdir(parents=True)
            (root / "laws/civil-procedure/articles/499.md").write_text("# المادة 499\n", encoding="utf-8")
            (root / "principles/supreme-court").mkdir(parents=True)
            (root / "principles/supreme-court/precedent-x.md").write_text("# سجل أولي\n", encoding="utf-8")
            first = build_master(root)
            self.assertEqual(first, build_master(root))
            self.assertIn("laws/civil-procedure/articles/499.md", first)
            self.assertIn("unknown", first)
            self.assertIn("needs-verification", first)

    def test_generated_indexes_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "laws/civil-procedure").mkdir(parents=True)
            (root / "laws/civil-procedure/README.md").write_text("# Law\n", encoding="utf-8")
            (root / "indexes").mkdir()
            (root / MASTER).write_text(build_master(root), encoding="utf-8")
            (root / STATUS).write_text(build_status(root), encoding="utf-8")
            self.assertEqual(validate(root), [])

if __name__ == "__main__":
    unittest.main()
