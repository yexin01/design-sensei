import json
import unittest

from tests import helpers
from tests.helpers import make_pattern, make_source
import search_patterns as sp
import index_sources as ix


def patterns():
    return [
        make_pattern("liquid-glass-button", title="Liquid glass button", category="liquid-glass", summary="A frosted glass button with a refractive liquid edge and hover response.",
                     tags=["glass", "liquid", "button"], source_ids=["alpha"], frameworks=["javascript", "webgl"], dependencies=["glassy"],
                     use_cases=["call to action", "hero button"], performance={"gpu_intensity": "medium", "fallback_required": True},
                     accessibility={"motion": "subtle", "reduced_motion_alternative": True}, source_paths=["alpha:src/glass.js"]),
        make_pattern("smooth-scroll", title="Smooth scroll", category="scroll", summary="Inertia based smooth scrolling that keeps native scroll semantics intact.",
                     tags=["scroll", "inertia"], source_ids=["beta"], frameworks=["react", "javascript"], dependencies=["lenis"], use_cases=["marketing site"],
                     accessibility={"motion": "moderate", "reduced_motion_alternative": False}),
        make_pattern("shader-background", title="Shader gradient background", category="background-shader", summary="Animated gradient background rendered by a fragment shader on a canvas.",
                     tags=["gradient", "shader"], source_ids=["alpha"], frameworks=["webgl", "glsl"], performance={"gpu_intensity": "high", "fallback_required": True},
                     accessibility={"motion": "moderate", "reduced_motion_alternative": True}),
        make_pattern("style-brutalism", title="Brutalism", category="design-style", summary="Raw, high contrast, grid-breaking visual style with heavy type and hard shadows.",
                     provenance="original", source_ids=[], tags=["brutalism", "raw"], frameworks=["css"]),
        make_pattern("unlicensed-effect", title="Unlicensed effect", category="cursor", summary="A cursor trail effect found in a repository that carries no license at all.",
                     tags=["cursor", "trail"], source_ids=["gamma"], frameworks=["react"]),
    ]


class SearchTests(helpers.TempDirTest):
    def setUp(self):
        super().setUp()
        sources = [make_source("alpha"), make_source("beta", license="Apache-2.0"),
                   make_source("gamma", license="NOASSERTION", license_status="not_found", redistribution_status="unresolved")]
        doc = '---\ntitle: "Glass notes"\nkind: guide\nsummary: "How frosted glass surfaces behave in interfaces."\nsource_ids: ["alpha"]\npattern_ids: ["liquid-glass-button"]\nupdated: "2026-10-09"\n---\n\n## Frosted glass\n\nBlur and refraction.\n'
        self.layout = helpers.make_toolkit(self.tmp, sources=sources, patterns=patterns(), docs={"knowledge/guides/glass.md": doc})

    def run_search(self, argv):
        code, out, err = helpers.call_main(sp.main, list(argv) + ["--root", str(self.layout.root), "--home", str(self.layout.home), "--json"])
        self.assertEqual(code, 0, err)
        return json.loads(out)["results"]

    def ids(self, argv):
        return [r["id"] for r in self.run_search(argv)]

    def test_ranking_prefers_title_and_tag_matches(self):
        ids = self.ids(["liquid glass button"])
        self.assertEqual(ids[0], "liquid-glass-button")

    def test_synonyms_expand_queries(self):
        self.assertIn("liquid-glass-button", self.ids(["frosted"]))
        self.assertIn("style-brutalism", self.ids(["brutal"]))
        self.assertIn("smooth-scroll", self.ids(["parallax"]))  # parallax -> scroll

    def test_stemming_matches_plurals(self):
        self.assertIn("shader-background", self.ids(["shaders"]))

    def test_filters(self):
        self.assertEqual(self.ids(["--category", "scroll", "--tag", "inertia"]), ["smooth-scroll"])
        self.assertEqual(self.ids(["--framework", "react"]), ["smooth-scroll", "unlicensed-effect"])
        self.assertEqual(self.ids(["--source", "beta"]), ["smooth-scroll"])
        self.assertEqual(self.ids(["--dependency", "lenis"]), ["smooth-scroll"])
        self.assertEqual(self.ids(["--use-case", "call to"]), ["liquid-glass-button"])
        self.assertEqual(self.ids(["--license-status", "not_found"]), ["unlicensed-effect"])
        self.assertEqual(self.ids(["--redistribution", "unresolved"]), ["unlicensed-effect"])
        self.assertEqual(self.ids(["--status", "recipe_available"]), [])

    def test_max_gpu_and_webgl_filters(self):
        self.assertNotIn("shader-background", self.ids(["background", "--max-gpu", "medium"]))
        self.assertIn("liquid-glass-button", self.ids(["glass", "--max-gpu", "medium"]))
        self.assertNotIn("liquid-glass-button", self.ids(["glass", "--max-gpu", "low"]))
        self.assertEqual(set(self.ids(["--webgl"])), {"liquid-glass-button", "shader-background"})
        self.assertNotIn("shader-background", self.ids(["--no-webgl", "gradient"]))

    def test_reduced_motion_safe(self):
        ids = self.ids(["--reduced-motion-safe", "--category", "scroll,liquid-glass,background-shader"])
        self.assertEqual(set(ids), {"liquid-glass-button", "shader-background"})  # smooth-scroll has moderate motion and no alternative

    def test_results_carry_license_and_reuse_guidance(self):
        by_id = {r["id"]: r for r in self.run_search(["effect"])}
        r = by_id["unlicensed-effect"]
        self.assertEqual((r["license_status"], r["redistribution_status"], r["reuse"]), ("not_found", "unresolved", "reimplement_only"))
        glass = {x["id"]: x for x in self.run_search(["glass"])}["liquid-glass-button"]
        self.assertEqual(glass["reuse"], "copy_with_attribution")
        brut = {x["id"]: x for x in self.run_search(["brutalism"])}["style-brutalism"]
        self.assertEqual(brut["reuse"], "original")

    def test_file_availability_and_download_hint(self):
        r = {x["id"]: x for x in self.run_search(["glass"])}["liquid-glass-button"]
        self.assertFalse(r["files"][0]["present"])
        self.assertEqual(r["missing_sources"], ["alpha"])
        (self.layout.sources_dir / "alpha" / "src").mkdir(parents=True)
        (self.layout.sources_dir / "alpha" / "src" / "glass.js").write_text("x")
        r = {x["id"]: x for x in self.run_search(["glass"])}["liquid-glass-button"]
        self.assertTrue(r["files"][0]["present"])
        self.assertEqual(r["missing_sources"], [])
        self.assertTrue(r["files"][0]["path"].endswith("glass.js"))

    def test_scope_docs_and_text_output(self):
        results = self.run_search(["frosted", "--scope", "docs"])
        self.assertEqual(results[0]["id"], "knowledge/guides/glass.md")
        code, out, _ = helpers.call_main(sp.main, ["frosted", "--scope", "all", "--root", str(self.layout.root), "--home", str(self.layout.home)])
        self.assertEqual(code, 0)
        self.assertIn("liquid-glass-button", out)
        self.assertIn("[note] Glass notes", out)
        self.assertIn("reuse: copy_with_attribution", out)
        self.assertIn("download: design-sensei sources sync alpha", out)

    def test_scope_files_uses_the_source_index(self):
        root = self.layout.sources_dir / "alpha"
        (root / "src").mkdir(parents=True)
        (root / "src" / "GlassPanel.tsx").write_text("export default function GlassPanel() { return null }\n// backdrop-filter: blur\n")
        code, out, _ = helpers.call_main(sp.main, ["glass", "--scope", "files", "--root", str(self.layout.root), "--home", str(self.layout.home)])
        self.assertIn("no source index yet", out)
        ix.write_index(self.layout, ix.build_index(self.layout))
        results = self.run_search(["glass panel", "--scope", "files"])
        self.assertEqual(results[0]["id"], "alpha:src/GlassPanel.tsx")
        self.assertTrue(results[0]["path"].endswith("GlassPanel.tsx"))

    def test_content_grep(self):
        root = self.layout.sources_dir / "alpha"
        root.mkdir(parents=True)
        (root / "a.glsl").write_text("uniform float u_time;\nvoid main() {}\n")
        (root / "b.png").write_bytes(b"u_time")
        results = self.run_search(["u_time", "--content", "--scope", "docs"])
        hits = [r for r in results if r.get("kind") == "content-match"]
        self.assertEqual([h["id"] for h in hits], ["alpha:a.glsl"])

    def test_facets(self):
        code, out, _ = helpers.call_main(sp.main, ["--facets", "--json", "--root", str(self.layout.root), "--home", str(self.layout.home)])
        data = json.loads(out)
        self.assertEqual(data["categories"]["scroll"], 1)
        self.assertIn("webgl", data["frameworks"])

    def test_no_query_no_filter_is_a_usage_error(self):
        code, _, err = helpers.call_main(sp.main, ["--root", str(self.layout.root), "--home", str(self.layout.home)])
        self.assertEqual(code, 2)
        self.assertIn("give a query", err)

    def test_no_match_message(self):
        code, out, _ = helpers.call_main(sp.main, ["zzzzqqq", "--root", str(self.layout.root), "--home", str(self.layout.home)])
        self.assertEqual(code, 0)
        self.assertIn("no matches", out)

    def test_limit_and_stable_order(self):
        a = self.ids(["button scroll shader glass", "--limit", "2"])
        self.assertEqual(len(a), 2)
        self.assertEqual(a, self.ids(["button scroll shader glass", "--limit", "2"]))


if __name__ == "__main__":
    unittest.main()
