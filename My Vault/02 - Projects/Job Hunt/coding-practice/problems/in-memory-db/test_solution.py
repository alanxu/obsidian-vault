"""Level tests for the in-memory DB. Run:  python3 run.py in-memory-db [level] [--ref]

These are illustrative (the real OA has a larger hidden suite) — add your own edge cases.
"""
import unittest

from solution import InMemoryDB


class TestLevel1(unittest.TestCase):
    def test_set_get_delete(self):
        db = InMemoryDB()
        db.set("a", "x", "1")
        self.assertEqual(db.get("a", "x"), "1")
        self.assertEqual(db.get("a", "missing"), "")      # absent -> ""
        self.assertEqual(db.delete("a", "x"), "true")
        self.assertEqual(db.delete("a", "x"), "false")    # already gone
        self.assertEqual(db.get("a", "x"), "")


class TestLevel2(unittest.TestCase):
    def test_scan_and_prefix(self):
        db = InMemoryDB()
        db.set("r", "name", "bob")
        db.set("r", "nick", "bo")
        db.set("r", "age", "9")
        self.assertEqual(db.scan("r"), "age(9), name(bob), nick(bo)")  # sorted by field
        self.assertEqual(db.scan_by_prefix("r", "n"), "name(bob), nick(bo)")


class TestLevel3(unittest.TestCase):
    def test_ttl_half_open(self):
        db = InMemoryDB()
        db.set_at_with_ttl("k", "f", "v", 100, 10)        # alive in [100, 110)
        self.assertEqual(db.get_at("k", "f", 100), "v")
        self.assertEqual(db.get_at("k", "f", 109), "v")
        self.assertEqual(db.get_at("k", "f", 110), "")    # expires at ts+ttl (half-open)
        self.assertEqual(db.get_at("k", "f", 99), "")     # before it was set


class TestLevel4(unittest.TestCase):
    def test_backup_restore_preserves_remaining_ttl(self):
        db = InMemoryDB()
        db.set_at_with_ttl("k", "f", "v", 100, 10)        # alive [100, 110)
        n = db.backup(105)                                # remaining ttl = 5
        self.assertGreaterEqual(n, 1)
        db.set_at("k", "f", "changed", 106)               # mutate after backup
        db.restore(200, 105)                              # resume at ts=200, remaining 5 -> expire 205
        self.assertEqual(db.get_at("k", "f", 204), "v")
        self.assertEqual(db.get_at("k", "f", 205), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
