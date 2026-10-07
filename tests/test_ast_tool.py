import unittest

from tools.ast_tool import analyze_source


class TestASTTool(unittest.TestCase):
    def test_detects_bare_except(self):
        report = analyze_source(
            """
try:
    x = 1
except:
    x = 2
"""
        )
        text = report.to_text()
        self.assertIn("裸 except", text)

    def test_detects_eval(self):
        report = analyze_source("value = eval(user_input)")
        self.assertIn("eval", report.to_text())

    def test_detects_todo(self):
        report = analyze_source("# TODO: finish this")
        self.assertIn("TODO", report.to_text())

    def test_valid_code(self):
        report = analyze_source("def add(a, b):\n    return a + b\n")
        self.assertEqual(report.functions, 1)
        self.assertEqual(report.files, 1)


if __name__ == "__main__":
    unittest.main()
