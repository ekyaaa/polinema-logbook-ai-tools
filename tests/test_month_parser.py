import unittest
import datetime
from scripts.logbook.git_reader import get_month_range, parse_month_string


class TestMonthParser(unittest.TestCase):
    def test_parse_standard_yyyy_mm(self):
        y, m = parse_month_string("2026-09")
        self.assertEqual(y, 2026)
        self.assertEqual(m, 9)

    def test_parse_textual_month(self):
        y, m = parse_month_string("September 2026")
        self.assertEqual(y, 2026)
        self.assertEqual(m, 9)

    def test_month_range_september(self):
        start_dt, end_dt = get_month_range(2026, 9)
        self.assertEqual(start_dt.year, 2026)
        self.assertEqual(start_dt.month, 9)
        self.assertEqual(start_dt.day, 1)

        self.assertEqual(end_dt.year, 2026)
        self.assertEqual(end_dt.month, 10)
        self.assertEqual(end_dt.day, 1)

    def test_month_range_december_rollover(self):
        start_dt, end_dt = get_month_range(2026, 12)
        self.assertEqual(start_dt.year, 2026)
        self.assertEqual(start_dt.month, 12)

        self.assertEqual(end_dt.year, 2027)
        self.assertEqual(end_dt.month, 1)
        self.assertEqual(end_dt.day, 1)


if __name__ == "__main__":
    unittest.main()
