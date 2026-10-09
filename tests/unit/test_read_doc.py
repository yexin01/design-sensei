"""`design-sensei read`: card, toc, section, max-tokens, lines, target resolution and the licence header."""

import tempfile
import unittest
from pathlib import Path

from tests import helpers
from tests.helpers import call_main, make_pattern, make_source, make_toolkit, run_cli
import read_doc as rd

STYLE = '---\ntitle: "Demo style"\nkind: design-style\nsummary: "A demo style note."\nsource_ids: []\npattern_ids: ["style-demo"]\nupdated: "2026-10-09"\n---\n\n# Demo style\n\nIntro text.\n\n## Visual characteristics\n- Alpha one.\n- Beta two.\n- Gamma three.\n\n## When it fits, when it does not\n- Fits: dashboards.\n- Poor fit: forms.\n- Supporting influences that work: x. Avoid y.\n\n## How to build it\n\n```css\n.a { color: red; }\n```\n\n## Common mistakes\n- Oops.\n'
REF = '# Ref doc\n\nIntro line.\n\n## Alpha section\nAlpha body one.\n\n### Alpha child\nChild body.\n\n## Beta section\nBeta body.\n\n```\n## not a heading\n```\n\n## Gamma\nGamma body.\n'


def fixture(tmp):
    layout = make_toolkit(
        Path(tmp),
        sources=[make_source("alpha"), make_source("restricted", redistribution_status="reference_only", license="LicenseRef-Custom-Terms", license_status="custom_terms")],
        patterns=[make_pattern("style-demo", source_ids=[], provenance="original", category="design-style", knowledge_doc="knowledge/design-styles/demo.md"),
                  make_pattern("cool-effect", source_ids=["alpha"], knowledge_doc="knowledge/animations/lenis.md", recipe="knowledge/implementation-recipes/cool.md"),
                  make_pattern("no-doc", source_ids=["alpha"])],
        docs={"knowledge/design-styles/demo.md": STYLE, "knowledge/animations/lenis.md": REF, "knowledge/animations/dup.md": REF,
              "knowledge/components/dup.md": REF, "knowledge/implementation-recipes/cool.md": REF,
              "skills/design-sensei/references/typography.md": REF, "skills/design-sensei/patterns/hero-sections.md": REF})
    for sid, text in (("alpha", "line1\nline2\nline3\nline4\n"), ("restricted", "secret = 1\n")):
        f = layout.sources_dir / sid / "src" / "a.js"
        f.parent.mkdir(parents=True)
        f.write_text(text, encoding="utf-8")
    return layout


def read(layout, *argv):
    return call_main(rd.main, list(argv) + ["--root", str(layout.root), "--home", str(layout.home)])


class RealNotesTests(unittest.TestCase):
    def test_card_is_deterministic_and_small_for_every_style_note(self):
        notes = [p for p in sorted((helpers.ROOT / "knowledge" / "design-styles").glob("*.md")) if p.name != "README.md"]
        self.assertGreater(len(notes), 30)
        for note in notes:
            with self.subTest(note=note.stem):
                args = [note.stem, "--card"]
                code, out1, err = call_main(rd.main, args)
                self.assertEqual(code, 0, err)
                self.assertEqual(out1, call_main(rd.main, args)[1])
                self.assertLessEqual(rd.est_tokens(out1), 650)
                self.assertIn("Visual characteristics", out1)

    def test_card_never_invents_text(self):
        text = (helpers.ROOT / "knowledge" / "design-styles" / "glassmorphism.md").read_text(encoding="utf-8")
        flat = " ".join(text.split())
        code, out, _ = call_main(rd.main, ["glassmorphism"])
        for line in out.splitlines():
            if line.startswith("- "):
                piece = line[2:].rstrip("…").strip()
                self.assertIn(piece, flat)

    def test_toc_matches_headings(self):
        code, out, _ = call_main(rd.main, ["ref:typography", "--toc"])
        self.assertEqual(code, 0)
        text = (helpers.ROOT / "skills" / "design-sensei" / "references" / "typography.md").read_text(encoding="utf-8")
        heads = [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]
        listed = [l.split("  (~")[0].strip() for l in out.splitlines() if "(~" in l and "tok" in l and not l.startswith("[")]
        self.assertEqual([h for h in listed if h in heads], heads)

    def test_style_pattern_id_and_slug_resolve_to_same_file(self):
        a = call_main(rd.main, ["style-glassmorphism", "--toc"])[1]
        b = call_main(rd.main, ["glassmorphism", "--toc"])[1]
        self.assertEqual(a, b)

    def test_cli_registered(self):
        code, out, _ = run_cli(["read", "glassmorphism", "--card"])
        self.assertEqual(code, 0)
        self.assertIn("Glassmorphism", out)


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.layout = fixture(self._tmp.name)

    def test_section_prefix_case_insensitive_with_children_and_summary(self):
        code, out, err = read(self.layout, "ref:typography", "--section", "alpha,GAMMA")
        self.assertEqual(code, 0, err)
        self.assertIn("## Alpha section", out)
        self.assertIn("### Alpha child", out)
        self.assertIn("Gamma body.", out)
        self.assertNotIn("Beta body", out)

    def test_section_includes_summary_for_frontmatter_docs(self):
        code, out, _ = read(self.layout, "demo", "--section", "common")
        self.assertIn("A demo style note.", out)
        self.assertIn("Oops.", out)

    def test_section_with_no_match_is_usage_error_listing_headings(self):
        code, _, err = read(self.layout, "ref:typography", "--section", "zzz")
        self.assertEqual(code, 2)
        self.assertIn("Alpha section", err)

    def test_heading_inside_code_fence_is_not_a_section(self):
        code, out, _ = read(self.layout, "ref:typography", "--toc")
        self.assertNotIn("not a heading", out)

    def test_max_tokens_truncates_at_section_boundary_with_marker(self):
        code, out, _ = read(self.layout, "ref:typography", "--max-tokens", "22")
        self.assertEqual(code, 0)
        self.assertRegex(out, r"\[truncated: \d+ more tokens; use --section or --full\]")
        self.assertIn("Alpha body one.", out)
        self.assertNotIn("Gamma body", out)
        code, full, _ = read(self.layout, "ref:typography", "--max-tokens", "5000")
        self.assertNotIn("truncated", full)
        self.assertIn("Gamma body.", full)

    def test_full_returns_whole_file(self):
        code, out, _ = read(self.layout, "ref:typography", "--full")
        self.assertIn("Gamma body.", out)
        self.assertIn("## not a heading", out)

    def test_style_card_shows_code_and_pairs_lines(self):
        code, out, _ = read(self.layout, "demo", "--card")
        self.assertIn(".a { color: red; }", out)
        self.assertIn("Avoid y.", out)
        self.assertIn("Poor fit: forms.", out)

    def test_generic_card_lists_headings(self):
        code, out, _ = read(self.layout, "ref:typography")
        self.assertIn("Alpha section", out)
        self.assertIn("Beta section", out)

    def test_resolution_of_each_target_kind(self):
        cases = {
            "demo": "knowledge/design-styles/demo.md", "style-demo": "knowledge/design-styles/demo.md",
            "ref:typography": "skills/design-sensei/references/typography.md",
            "playbook:hero-sections": "skills/design-sensei/patterns/hero-sections.md",
            "recipe:cool": "knowledge/implementation-recipes/cool.md",
            "note:lenis": "knowledge/animations/lenis.md", "cool-effect": "knowledge/animations/lenis.md",
            "knowledge/design-styles/demo.md": "knowledge/design-styles/demo.md",
        }
        for target, rel in cases.items():
            with self.subTest(target=target):
                code, out, err = read(self.layout, target, "--toc")
                self.assertEqual(code, 0, err)
                self.assertTrue(out.startswith("[" + rel), out.splitlines()[0])

    def test_pattern_recipe_flag(self):
        code, out, _ = read(self.layout, "cool-effect", "--recipe", "--toc")
        self.assertTrue(out.startswith("[knowledge/implementation-recipes/cool.md"))
        code, _, err = read(self.layout, "no-doc")
        self.assertEqual(code, 1)

    def test_traversal_and_outside_paths_refused_with_exit_2(self):
        outside = Path(self._tmp.name) / "outside.md"
        outside.write_text("# x\n", encoding="utf-8")
        for target in ("../outside.md", "knowledge/../../outside.md", str(outside), "/etc/passwd", "ref:../x", "alpha:../../x", "alpha:/etc/passwd"):
            with self.subTest(target=target):
                self.assertEqual(read(self.layout, target)[0], 2)

    def test_symlink_escape_refused(self):
        outside = Path(self._tmp.name) / "outside.md"
        outside.write_text("# x\n", encoding="utf-8")
        link = self.layout.root / "knowledge" / "link.md"
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("no symlinks")
        self.assertEqual(read(self.layout, "knowledge/link.md")[0], 2)

    def test_ambiguity_lists_candidates_and_exits_2(self):
        code, out, err = read(self.layout, "note:dup")
        self.assertEqual(code, 2)
        self.assertIn("knowledge/animations/dup.md", err)
        self.assertIn("knowledge/components/dup.md", err)
        code, _, err = read(self.layout, "lenis-x-none")
        self.assertEqual(code, 1)
        # same bare name in two kinds
        code, _, err = read(self.layout, "typography")
        self.assertEqual(code, 0)

    def test_bare_name_in_two_kinds_is_ambiguous(self):
        (self.layout.root / "knowledge" / "implementation-recipes" / "typography.md").write_text(REF, encoding="utf-8")
        code, _, err = read(self.layout, "typography")
        self.assertEqual(code, 2)
        self.assertIn("ref:typography", err)
        self.assertIn("recipe:typography", err)

    def test_source_file_has_licence_header_and_line_range(self):
        code, out, err = read(self.layout, "alpha:src/a.js", "--lines", "2:3")
        self.assertEqual(code, 0, err)
        self.assertIn("licence: MIT (verified) | reuse: copy_with_attribution", out)
        self.assertIn("line2\nline3", out)
        self.assertNotIn("line4", out)
        code, out, _ = read(self.layout, "source:restricted:src/a.js")
        self.assertIn("reuse: reference_only", out)
        self.assertIn("secret = 1", out)

    def test_code_files_refuse_markdown_modes_and_missing_source_is_clear(self):
        self.assertEqual(read(self.layout, "alpha:src/a.js", "--toc")[0], 2)
        self.assertEqual(read(self.layout, "alpha:src/a.js", "--lines", "9:2")[0], 2)
        code, _, err = read(self.layout, "alpha:src/missing.js")
        self.assertEqual(code, 1)
        self.assertIn("not found", err)

    def test_conflicting_modes_are_usage_error(self):
        self.assertEqual(read(self.layout, "ref:typography", "--toc", "--full")[0], 2)


if __name__ == "__main__":
    unittest.main()
