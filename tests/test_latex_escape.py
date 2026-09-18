import unittest
from scripts.logbook.latex_escape import escape_latex


class TestLatexEscape(unittest.TestCase):
    def test_special_characters(self):
        self.assertEqual(escape_latex("100%"), r"100\%")
        self.assertEqual(escape_latex("A & B"), r"A \& B")
        self.assertEqual(escape_latex("$10"), r"\$10")
        self.assertEqual(escape_latex("#hashtag"), r"\#hashtag")
        self.assertEqual(escape_latex("user_name"), r"user\_name")
        self.assertEqual(escape_latex("{nested}"), r"\{nested\}")
        self.assertEqual(escape_latex("x^2"), r"x\textasciicircum{}2")
        self.assertEqual(escape_latex("~home"), r"\textasciitilde{}home")
        self.assertEqual(escape_latex(r"path\to\file"), r"path\textbackslash{}to\textbackslash{}file")

    def test_none_or_empty(self):
        self.assertEqual(escape_latex(None), "")
        self.assertEqual(escape_latex(""), "")

    def test_combined_sentence(self):
        raw = "Fix bug & update #123 on module_auth (100% test_pass)."
        escaped = escape_latex(raw)
        self.assertIn(r"\&", escaped)
        self.assertIn(r"\#123", escaped)
        self.assertIn(r"module\_auth", escaped)
        self.assertIn(r"100\%", escaped)
        self.assertIn(r"test\_pass", escaped)


if __name__ == "__main__":
    unittest.main()
