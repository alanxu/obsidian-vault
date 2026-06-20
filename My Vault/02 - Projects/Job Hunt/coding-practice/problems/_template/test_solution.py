"""Level tests. One class per level: TestLevel1, TestLevel2, ...
Run a single level with:  python3 run.py <problem> 1
"""
import unittest

from solution import Solution  # rename to match your class


class TestLevel1(unittest.TestCase):
    def test_placeholder(self):
        self.skipTest("write Level 1 tests, then implement solution.py")


class TestLevel2(unittest.TestCase):
    def test_placeholder(self):
        self.skipTest("write Level 2 tests")


if __name__ == "__main__":
    unittest.main(verbosity=2)
