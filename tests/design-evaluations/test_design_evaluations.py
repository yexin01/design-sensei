"""The static evaluator must flag a known-bad page and stay quiet on a well-formed one."""

import json
import unittest
from pathlib import Path

from tests import helpers
import design_eval as de

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class EvalBase(helpers.TempDirTest):
    def setUp(self):
        super().setUp()
        self.layout = helpers.make_toolkit(self.tmp, sources=[helpers.make_source("alpha"), helpers.make_source("react-bits", license="LicenseRef-X",
                                           license_status="custom_terms", redistribution_status="license_specific")])
        self.config = {"reduced_motion": "respect", "webgl_enabled": True, "allowed_dependencies": "minimal", "performance_budget": {"max_webgl_canvases": 1}}
        self.sources = {s["id"]: s for s in __import__("dslib.catalog", fromlist=["x"]).load_sources(self.layout)}

    def codes(self, path, config=None):
        project = de.load_project(Path(path))
        return {f.code for f in de.evaluate(project, config or self.config, self.sources)}

    def findings(self, path, config=None):
        project = de.load_project(Path(path))
        return de.evaluate(project, config or self.config, self.sources)


class GoodAndBadSiteTests(EvalBase):
    def test_well_formed_page_has_no_errors_or_warnings(self):
        findings = self.findings(FIXTURES / "good-site")
        self.assertEqual([f for f in findings if f.level in ("error", "warning")], [], [f.as_dict() for f in findings])

    def test_problem_page_is_flagged_for_each_known_problem(self):
        codes = self.codes(FIXTURES / "bad-site")
        for expected in ("A11Y-001", "A11Y-002", "A11Y-003", "A11Y-004", "A11Y-005", "A11Y-007", "A11Y-008", "MOT-001", "MOT-004", "MOT-005", "MOT-006",
                         "PERF-001", "PERF-003", "PERF-006", "PERF-008", "RESP-003", "TYPO-001", "TYPO-003", "TECH-001", "TECH-002", "ART-001"):
            self.assertIn(expected, codes)

    def test_findings_carry_file_line_and_hint(self):
        f = next(x for x in self.findings(FIXTURES / "bad-site") if x.code == "A11Y-001")
        self.assertEqual(f.path, "index.html")
        self.assertEqual(f.level, "error")
        self.assertGreater(f.line, 1)
        self.assertTrue(f.hint)

    def test_cli_exit_codes_and_json(self):
        base = ["--root", str(self.layout.root), "--home", str(self.layout.home)]
        code, out, _ = helpers.call_main(de.main, [str(FIXTURES / "good-site"), "--json"] + base)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["scanned_files"], 2)
        code, out, _ = helpers.call_main(de.main, [str(FIXTURES / "bad-site")] + base)
        self.assertEqual(code, 1)
        self.assertIn("A11Y-001", out)
        self.assertIn("Static heuristics only", out)
        self.assertEqual(helpers.call_main(de.main, [str(self.tmp / "missing")] + base)[0], 2)
        empty = self.tmp / "empty"
        empty.mkdir()
        self.assertEqual(helpers.call_main(de.main, [str(empty)] + base)[0], 2)

    def test_strict_mode_fails_on_warnings(self):
        site = self.tmp / "warn-only"
        site.mkdir()
        (site / "index.html").write_text('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width"></head><body><h1>x</h1><p>Lorem ipsum</p></body></html>')
        base = ["--root", str(self.layout.root), "--home", str(self.layout.home)]
        self.assertEqual(helpers.call_main(de.main, [str(site)] + base)[0], 0)
        self.assertEqual(helpers.call_main(de.main, [str(site), "--strict"] + base)[0], 1)


class ConfigDrivenTests(EvalBase):
    def make_site(self, html, css=""):
        site = self.tmp / "site"
        site.mkdir(exist_ok=True)
        (site / "index.html").write_text(html)
        if css:
            (site / "s.css").write_text(css)
        return site

    PAGE = '<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width"></head><body><h1>x</h1><canvas></canvas><script>const gl = canvas.getContext("webgl");</script></body></html>'

    def test_webgl_disabled_makes_webgl_an_error(self):
        site = self.make_site(self.PAGE)
        self.assertNotIn("PERF-005", self.codes(site))
        cfg = dict(self.config, webgl_enabled=False)
        self.assertIn("PERF-005", self.codes(site, cfg))
        self.assertEqual(next(f for f in self.findings(site, cfg) if f.code == "PERF-005").level, "error")

    def test_canvas_budget(self):
        page = self.PAGE.replace("</script>", 'const g2 = other.getContext("webgl2");</script>')
        site = self.make_site(page)
        self.assertIn("PERF-004", self.codes(site))
        cfg = dict(self.config, performance_budget={"max_webgl_canvases": 3})
        self.assertNotIn("PERF-004", self.codes(site, cfg))

    def test_static_first_makes_missing_reduced_motion_an_error(self):
        site = self.make_site(self.PAGE.replace("</body>", "<style>.a{animation: x 1s}</style></body>"))
        level = lambda cfg: next(f for f in self.findings(site, cfg) if f.code == "MOT-001").level
        self.assertEqual(level(self.config), "warning")
        self.assertEqual(level(dict(self.config, reduced_motion="static_first")), "error")

    def test_reduced_motion_handling_silences_the_finding(self):
        site = self.make_site(self.PAGE.replace("</body>", "<style>.a{animation: x 1s} @media (prefers-reduced-motion: reduce){.a{animation:none}}</style></body>"))
        self.assertNotIn("MOT-001", self.codes(site))

    def test_dependency_budget_from_package_json(self):
        site = self.make_site(self.PAGE)
        (site / "package.json").write_text(json.dumps({"dependencies": {"three": "1", "gsap": "3", "lenis": "1", "framer-motion": "11"}}))
        self.assertIn("PERF-007", self.codes(site))  # four heavy libraries with 'minimal'
        self.assertIn("PERF-007", self.codes(site, dict(self.config, allowed_dependencies="none")))
        self.assertNotIn("PERF-007", self.codes(site, dict(self.config, allowed_dependencies=["three", "gsap", "lenis", "framer-motion"])))
        self.assertNotIn("PERF-007", self.codes(site, dict(self.config, allowed_dependencies="any")))

    def test_provenance_comments_and_notices(self):
        site = self.make_site(self.PAGE)
        (site / "fx.js").write_text("// adapted from alpha\nexport const x = 1;\n")
        findings = {f.code: f for f in self.findings(site)}
        self.assertIn("PROV-001", findings)  # permissive source credited, no notice file
        (site / "THIRD_PARTY_NOTICES.md").write_text("alpha: MIT")
        self.assertNotIn("PROV-001", self.codes(site))
        (site / "fx.js").write_text("// ported from react-bits\nexport const y = 1;\n")
        self.assertIn("PROV-002", self.codes(site))  # restricted source mentioned

    def test_missing_viewport_meta(self):
        site = self.make_site('<!doctype html><html lang="en"><head><title>t</title></head><body><h1>x</h1></body></html>')
        self.assertIn("RESP-001", self.codes(site))
        self.assertEqual(next(f for f in self.findings(site) if f.code == "RESP-001").level, "error")

    def test_single_file_target_and_paths_with_spaces(self):
        folder = self.tmp / "my site"
        folder.mkdir()
        page = folder / "index page.html"
        page.write_text('<html><body><img src="x.png"></body></html>')
        self.assertIn("A11Y-001", self.codes(page))


if __name__ == "__main__":
    unittest.main()
