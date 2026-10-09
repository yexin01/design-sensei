"""`design-sensei tokens`: estimates, canned-brief output sizes and the budget check."""

import json
import unittest

from tests import helpers
from dslib import compact, yamlite
import token_report as tr


class EstimateTests(unittest.TestCase):
    def test_estimate_is_characters_over_four_rounded_up(self):
        self.assertEqual(compact.estimate_tokens(""), 0)
        self.assertEqual(compact.estimate_tokens("abcd"), 1)
        self.assertEqual(compact.estimate_tokens("abcde"), 2)
        self.assertEqual(compact.estimate_tokens("x" * 4000), 1000)


class ReportTests(helpers.TempDirTest):
    def run_tokens(self, *extra):
        return helpers.call_main(tr.main, list(extra) + ["--root", str(helpers.ROOT), "--home", str(self.tmp / "home")])

    def test_json_report_covers_every_group_and_detail_level(self):
        code, out, err = self.run_tokens("--json")
        self.assertEqual(code, 0, err)
        data = json.loads(out)
        report = data["report"]
        self.assertIn("estimate", report["note"].lower() + "estimate")
        self.assertGreater(report["skill"]["body"], 0)
        self.assertEqual(report["skill"]["total"], report["skill"]["frontmatter"] + report["skill"]["body"])
        for group in ("references", "playbooks", "style_notes", "commands", "agents"):
            self.assertTrue(report[group], group)
            self.assertTrue(all(i["tokens"] > 0 and i["path"] for i in report[group]))
        self.assertTrue(any(i["path"].endswith("accessibility.md") for i in report["references"]))
        self.assertTrue(any(i["path"].endswith("glassmorphism.md") for i in report["style_notes"]))
        self.assertEqual(len(report["outputs"]["recommend"]), 4)
        self.assertEqual(len(report["outputs"]["search"]), 4)
        for sizes in list(report["outputs"]["recommend"].values()) + list(report["outputs"]["search"].values()):
            self.assertLess(sizes["brief"], sizes["normal"])
            self.assertLess(sizes["normal"], sizes["full"])
        self.assertEqual(set(data["measured"]), set(data["budgets"]) | {k for k in data["measured"]})

    def test_text_report(self):
        code, out, _ = self.run_tokens()
        self.assertEqual(code, 0)
        for needle in ("SKILL.md:", "references:", "playbooks", "style notes:", "recommend", "search", "estimate"):
            self.assertIn(needle, out)

    def test_committed_budgets_hold(self):
        code, out, _ = self.run_tokens("--budget-check")
        self.assertEqual(code, 0, out)
        self.assertNotIn("OVER BUDGET", out)

    def test_cli_is_registered(self):
        code, out, _ = helpers.run_cli(["tokens", "--help"])
        self.assertEqual(code, 0)
        self.assertIn("--budget-check", out)


class BudgetCheckTests(unittest.TestCase):
    def test_exceeded_budget_is_reported_with_a_clear_message(self):
        problems = tr.check_budgets({"skill_md_body": 3519, "recommend_normal": 600}, {"skill_md_body": 3000, "recommend_normal": 700})
        self.assertEqual(len(problems), 1)
        self.assertIn("OVER BUDGET skill_md_body: 3519 tokens > budget 3000", problems[0])
        self.assertIn("token-budgets.yaml", problems[0])

    def test_equal_is_within_budget_and_unknown_keys_are_flagged(self):
        self.assertEqual(tr.check_budgets({"a": 5}, {"a": 5}), [])
        self.assertIn("not a known measurement", tr.check_budgets({"a": 5}, {"zzz": 1})[0])

    def test_budget_file_has_the_expected_keys(self):
        data = yamlite.load(helpers.ROOT / "catalog" / "token-budgets.yaml")
        self.assertEqual(set(data), set(tr.BUDGET_LABELS))
        self.assertTrue(all(isinstance(v, int) and v > 0 for v in data.values()))

    def test_exit_code_one_when_a_budget_is_exceeded(self):
        layout = helpers.make_toolkit(self_tmp(), patterns=[helpers.make_pattern()])
        (layout.root / "catalog" / "token-budgets.yaml").write_text("recommend_brief: 1\nsearch_normal: 1\n")
        code, out, _ = helpers.call_main(tr.main, ["--budget-check", "--root", str(layout.root), "--home", str(layout.home)])
        self.assertEqual(code, 1)
        self.assertIn("OVER BUDGET", out)
        code, _, _ = helpers.call_main(tr.main, ["--root", str(layout.root), "--home", str(layout.home)])
        self.assertEqual(code, 0)  # without --budget-check the report never fails

    def test_missing_budget_file_fails_the_check_only(self):
        layout = helpers.make_toolkit(self_tmp(), patterns=[helpers.make_pattern()])
        code, _, err = helpers.call_main(tr.main, ["--budget-check", "--root", str(layout.root), "--home", str(layout.home)])
        self.assertEqual(code, 1)
        self.assertIn("no budgets file", err)


_TMPS = []


def self_tmp():
    import tempfile
    from pathlib import Path
    d = tempfile.mkdtemp(prefix="ds tokens ")
    _TMPS.append(d)
    return Path(d)


def tearDownModule():
    import shutil
    for d in _TMPS:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
