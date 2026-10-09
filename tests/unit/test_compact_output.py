"""Token-efficient output of `recommend` and `search`: detail levels, relative paths, +N more, truncation, config precedence."""

import json
import unittest

from tests import helpers
from tests.helpers import make_pattern, make_source
from dslib import compact, yamlite
import recommend as rc
import search_patterns as sp

BRIEFS = ("liquid glass hero for a fintech", "editorial scroll storytelling", "dark developer tool landing")
QUERIES = ("liquid glass button", "smooth scroll", "text reveal")


def budgets():
    return yamlite.load(helpers.ROOT / "catalog" / "token-budgets.yaml")


class RealCatalogBase(helpers.TempDirTest):
    def setUp(self):
        super().setUp()
        self.home = self.tmp / "library home"
        self.project = self.tmp / "project dir"
        self.project.mkdir()

    def base(self):
        return ["--root", str(helpers.ROOT), "--home", str(self.home)]

    def recommend(self, brief, *extra):
        code, out, err = helpers.call_main(rc.main, [brief, "--project", str(self.project)] + list(extra) + self.base())
        self.assertEqual(code, 0, err)
        return out

    def search(self, query, *extra):
        code, out, err = helpers.call_main(sp.main, [query, "--limit", "5"] + list(extra) + self.base())
        self.assertEqual(code, 0, err)
        return out


class BudgetTests(RealCatalogBase):
    def test_recommend_brief_is_cheap(self):
        for brief in BRIEFS:
            with self.subTest(brief=brief):
                self.assertLessEqual(compact.estimate_tokens(self.recommend(brief, "--detail", "brief")), 350)

    def test_recommend_normal_stays_within_the_committed_budget_and_well_below_full(self):
        for brief in BRIEFS:
            with self.subTest(brief=brief):
                normal = compact.estimate_tokens(self.recommend(brief))
                full = compact.estimate_tokens(self.recommend(brief, "--detail", "full"))
                self.assertLessEqual(normal, budgets()["recommend_normal"])
                self.assertLess(normal, 0.7 * full)
                self.assertLess(compact.estimate_tokens(self.recommend(brief, "--detail", "brief")), normal)

    def test_search_normal_five_results_stays_within_the_committed_budget(self):
        for query in QUERIES:
            with self.subTest(query=query):
                normal = compact.estimate_tokens(self.search(query))
                self.assertLessEqual(normal, budgets()["search_normal"])
                self.assertLess(normal, 0.75 * compact.estimate_tokens(self.search(query, "--detail", "full")))
                self.assertLessEqual(compact.estimate_tokens(self.search(query, "--detail", "brief")), 300)

    def test_default_detail_is_normal(self):
        self.assertEqual(self.search("smooth scroll"), self.search("smooth scroll", "--detail", "normal"))
        self.assertEqual(self.recommend(BRIEFS[0]), self.recommend(BRIEFS[0], "--detail", "normal"))


class PathTests(RealCatalogBase):
    def test_one_root_line_and_relative_paths(self):
        for out in (self.recommend(BRIEFS[0]), self.search("liquid glass button")):
            lines = out.splitlines()
            self.assertEqual(lines[0].split(" | ")[0], "root: %s" % helpers.ROOT)
            self.assertEqual(out.count(str(helpers.ROOT)), 1)  # nothing else repeats the absolute root
            self.assertIn("knowledge/", out)
            self.assertNotIn(str(self.home), out.replace(lines[0], ""))  # library files read @lib/sources/...
        self.assertIn("knowledge/design-styles/glassmorphism.md", self.recommend(BRIEFS[0]))

    def test_full_keeps_absolute_paths(self):
        out = self.recommend(BRIEFS[0], "--detail", "full")
        self.assertIn(str(helpers.ROOT / "knowledge" / "design-styles" / "glassmorphism.md"), out)
        self.assertNotIn("root:", out)
        self.assertIn(str(helpers.ROOT / "knowledge"), self.search("liquid glass button", "--detail", "full"))

    def test_brief_has_no_paths_at_all(self):
        for out in (self.recommend(BRIEFS[0], "--detail", "brief"), self.search("liquid glass button", "--detail", "brief")):
            self.assertNotIn(str(helpers.ROOT), out)
            self.assertNotIn("knowledge/", out)

    def test_json_is_unaffected_by_detail(self):
        a = json.loads(self.recommend(BRIEFS[0], "--json"))
        b = json.loads(self.recommend(BRIEFS[0], "--json", "--detail", "brief"))
        self.assertEqual(a, b)
        self.assertTrue(a["style"]["primary"]["note_path"].startswith(str(helpers.ROOT)))
        self.assertEqual(json.loads(self.search("smooth scroll", "--json")), json.loads(self.search("smooth scroll", "--json", "--detail", "brief")))


class NextStepTests(RealCatalogBase):
    def test_commands_suggest_the_cheap_read(self):
        out = self.recommend(BRIEFS[0])
        self.assertIn(compact.read_style("glassmorphism"), out)
        self.assertIn(compact.read_pattern("<id>"), out)
        self.assertIn(compact.READ_STYLE_CMD.format(slug="glassmorphism"), self.recommend(BRIEFS[0], "--detail", "brief"))
        self.assertIn("design-sensei read smooth-scroll-lenis --section", self.search("smooth scroll"))
        self.assertIn("design-sensei read glassmorphism --card", self.search("glassmorphism", "--category", "design-style"))

    def test_the_suggestions_come_from_two_constants(self):
        self.assertIn("{slug}", compact.READ_STYLE_CMD)
        self.assertIn("{id}", compact.READ_PATTERN_CMD)


def fixture_layout(tmp):
    files = ["alpha:src/f%d.js" % i for i in range(1, 6)]
    pats = [
        make_pattern("many-files", title="Many files", summary="First sentence is short. " + "Second sentence keeps going with many words " * 6 + ".",
                     tags=["files"], source_ids=["alpha"], source_paths=files, knowledge_doc="knowledge/guides/a.md", recipe="knowledge/guides/r.md"),
        make_pattern("same-doc", title="Same doc", summary="Another files pattern.", tags=["files"], source_ids=["alpha"], source_paths=files[:2], knowledge_doc="knowledge/guides/a.md"),
    ]
    docs = {"knowledge/guides/a.md": "---\ntitle: A\n---\nx\n", "knowledge/guides/r.md": "x"}
    return helpers.make_toolkit(tmp, sources=[make_source("alpha")], patterns=pats, docs=docs)


class FixtureTests(helpers.TempDirTest):
    def setUp(self):
        super().setUp()
        self.layout = fixture_layout(self.tmp)
        self.base = ["--root", str(self.layout.root), "--home", str(self.layout.home)]

    def search(self, *extra):
        code, out, err = helpers.call_main(sp.main, ["files"] + list(extra) + self.base)
        self.assertEqual(code, 0, err)
        return out

    def test_file_lists_are_capped_with_a_count(self):
        out = self.search()
        self.assertIn("+2 more", out)
        self.assertEqual(out.count("f1.js"), 2)  # once per pattern
        self.assertNotIn("f4.js", out)
        self.assertIn("f4.js", self.search("--detail", "full"))  # full lists five
        self.assertIn("src/", self.search())

    def test_repeated_docs_are_not_repeated(self):
        out = self.search()
        self.assertEqual(out.count("knowledge/guides/a.md"), 1)
        self.assertIn("doc: same as #1", out)
        self.assertEqual(self.search("--detail", "full").count("knowledge/guides/a.md".replace("knowledge", str(self.layout.root / "knowledge"))), 2)

    def test_no_blank_decorative_lines_except_in_full(self):
        for detail in ("normal", "brief"):
            self.assertNotIn("\n\n", self.search("--detail", detail))
        self.assertIn("\n\n", self.search("--detail", "full"))

    def test_text_output_keeps_the_download_hint_and_notes(self):
        out = self.search()
        self.assertIn("download: design-sensei sources sync alpha", out)
        self.assertIn("(not downloaded)", out)

    def test_summaries_are_clipped(self):
        code, out, _ = helpers.call_main(sp.main, ["files", "--detail", "normal", "--limit", "1"] + self.base)
        summary_line = [l for l in out.splitlines() if l.startswith("   First sentence")][0]
        self.assertLessEqual(len(summary_line.strip()), compact.SUMMARY_LIMIT + 1)
        self.assertTrue(summary_line.endswith(("short.", "…")))


class ClipTests(unittest.TestCase):
    def test_short_text_is_untouched(self):
        self.assertEqual(compact.clip("Short  text\nhere."), "Short text here.")

    def test_cuts_at_the_last_sentence_end_in_the_window(self):
        text = "First sentence is here. Second sentence is also here. Third sentence runs on and on and on and on and on and on and on."
        self.assertEqual(compact.clip(text, 60), "First sentence is here. Second sentence is also here.")

    def test_falls_back_to_a_word_boundary_with_an_ellipsis(self):
        text = "word " * 60
        out = compact.clip(text, 50)
        self.assertTrue(out.endswith("…"))
        self.assertLessEqual(len(out), 51)
        self.assertNotIn("wor…", out)
        out = compact.clip("Supercalifragilistic expialidocious wonderfully long words continue without any stop", 40)
        self.assertTrue(out.endswith("…"))
        self.assertFalse(out[:-1].endswith("wonderfu"))

    def test_a_single_long_word_is_hard_cut(self):
        self.assertEqual(compact.clip("x" * 300, 20), "x" * 20 + "…")

    def test_a_sentence_end_too_early_is_ignored(self):
        text = "Hi. " + "longer words keep coming in this sentence with no stop " * 4
        self.assertTrue(compact.clip(text, 80).endswith("…"))

    def test_more_and_rel_path(self):
        from pathlib import Path
        self.assertEqual(compact.more(5, 3), " +2 more")
        self.assertEqual(compact.more(3, 3), "")
        self.assertEqual(compact.rel_path("/a/b/c/d.md", Path("/a/b")), "c/d.md")
        self.assertEqual(compact.rel_path("/x/y.md", Path("/a/b")), "/x/y.md")
        self.assertEqual(compact.rel_path("/h/sources/s/f.js", Path("/a/b"), Path("/h")), "@lib/sources/s/f.js")
        self.assertEqual(compact.rel_path(None, Path("/a")), "-")

    def test_common_dir(self):
        self.assertEqual(compact.split_common_dir(["a/b/c.js", "a/b/d.js"]), ("a/b/", ["c.js", "d.js"]))
        self.assertEqual(compact.split_common_dir(["a/c.js", "b/d.js"]), ("", ["a/c.js", "b/d.js"]))
        self.assertEqual(compact.split_common_dir(["only/x.js"]), ("only/", ["x.js"]))


class ConfigPrecedenceTests(helpers.TempDirTest):
    def setUp(self):
        super().setUp()
        self.layout = fixture_layout(self.tmp)
        self.project = self.tmp / "project dir"
        self.project.mkdir()
        self.base = ["--root", str(self.layout.root), "--home", str(self.layout.home)]

    def rec(self, *extra):
        code, out, err = helpers.call_main(rc.main, ["files", "--project", str(self.project)] + list(extra) + self.base)
        self.assertEqual(code, 0, err)
        return out

    def test_config_sets_the_default_and_the_flag_wins(self):
        (self.project / ".design-sensei.yaml").write_text("output_detail: brief\n")
        self.assertTrue(self.rec().startswith("RECOMMEND "))
        self.assertTrue(self.rec("--detail", "normal").startswith("root: "))
        self.assertIn("PATTERNS", self.rec("--detail", "full"))
        (self.project / ".design-sensei.yaml").write_text("output_detail: full\n")
        self.assertTrue(self.rec().startswith("RECOMMENDATION for"))
        self.assertTrue(self.rec("--detail", "brief").startswith("RECOMMEND "))

    def test_search_reads_the_user_config_layer(self):
        self.layout.home.mkdir(parents=True)
        self.layout.user_config_path.write_text("output_detail: brief\n")
        code, out, _ = helpers.call_main(sp.main, ["files"] + self.base)
        self.assertNotIn("root:", out)
        code, out, _ = helpers.call_main(sp.main, ["files", "--detail", "normal"] + self.base)
        self.assertIn("root:", out)

    def test_invalid_config_falls_back_to_normal(self):
        (self.project / ".design-sensei.yaml").write_text("output_detail: verbose\n")
        self.assertTrue(self.rec().startswith("root: "))

    def test_bad_flag_value_is_a_usage_error(self):
        code, _, _ = helpers.call_main(rc.main, ["files", "--detail", "huge"] + self.base)
        self.assertEqual(code, 2)

    def test_config_show_lists_output_detail(self):
        (self.project / ".design-sensei.yaml").write_text("output_detail: brief\n")
        code, out, _ = helpers.run_cli(["config", "show", "--project", str(self.project), "--json", "--root", str(self.layout.root), "--home", str(self.layout.home)])
        data = json.loads(out)
        self.assertEqual((data["config"]["output_detail"], data["origins"]["output_detail"]), ("brief", "project"))


if __name__ == "__main__":
    unittest.main()
