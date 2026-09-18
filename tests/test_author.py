import unittest
from scripts.logbook.author import AuthorMatcher


class TestAuthorMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = AuthorMatcher(
            names=["Ekya Muhammad Hasfi", "ekyaaa"],
            emails=["ekyamuhammad@gmail.com"],
        )

    def test_exact_email_match(self):
        self.assertTrue(self.matcher.matches("Random Name", "ekyamuhammad@gmail.com"))
        self.assertTrue(self.matcher.matches("Random Name", "EKYAMUHAMMAD@GMAIL.COM"))

    def test_exact_name_match(self):
        self.assertTrue(self.matcher.matches("ekyaaa", "other@domain.com"))
        self.assertTrue(self.matcher.matches("Ekya Muhammad Hasfi", "work@company.com"))

    def test_github_noreply_email_match(self):
        self.assertTrue(self.matcher.matches("Whatever", "123456+ekyaaa@users.noreply.github.com"))

    def test_negative_match(self):
        self.assertFalse(self.matcher.matches("John Doe", "john@example.com"))
        self.assertFalse(self.matcher.matches("Jane Contributor", "jane@company.com"))


if __name__ == "__main__":
    unittest.main()
