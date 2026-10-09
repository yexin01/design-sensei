"""`design-sensei recommend`: styles, patterns, licence gate, fallback, filters, config, offline behaviour."""

import json
import socket
import unittest

from tests import helpers
from tests.helpers import make_pattern, make_source, run_cli
import recommend as rc

NOTE = '---\ntitle: "%(title)s"\nkind: design-style\nsummary: "Fixture style note for %(title)s."\nsource_ids: []\npattern_ids: ["style-%(slug)s"]\nupdated: "2026-10-09"\n---\n\n# %(title)s\n\n## When it fits\n- Fits: fixtures.\n- %(line)s\n'

STYLE_NOTES = {
    "glassmorphism": ("Glassmorphism", "Supporting influences that work: liquid-materials, editorial. Avoid brutalism and neo-glass."),
    "liquid-materials": ("Liquid materials", "Supporting influences that work: glassmorphism. Avoid brutalism."),
    "brutalism": ("Brutalism", "Supporting influences that work: editorial. Avoid glassmorphism."),
    "editorial": ("Editorial design", "Supporting influences that work: minimalism. Avoid mixing with brutalism."),
}


def style(slug, title, summary, tags, **kw):
    return make_pattern("style-" + slug, title=title, category="design-style", summary=summary, provenance="original", source_ids=[], tags=tags,
                        frameworks=kw.pop("frameworks", ["css", "react"]), knowledge_doc="knowledge/design-styles/%s.md" % slug, **kw)


def patterns():
    return [
        style("glassmorphism", "Glassmorphism", "Frosted translucent glass panels with backdrop blur over rich backdrops.", ["glassmorphism", "glass", "blur", "frosted"],
              related=["liquid-glass-button", "liquid-glass-css"], performance={"gpu_intensity": "medium", "fallback_required": False},
              accessibility={"motion": "subtle", "reduced_motion_alternative": True}),
        style("liquid-materials", "Liquid materials", "Surfaces that flow like liquid metal or glass through shaders.", ["liquid", "metal", "chrome", "glass"],
              frameworks=["webgl", "glsl"], performance={"gpu_intensity": "high", "fallback_required": True}, accessibility={"motion": "moderate", "reduced_motion_alternative": True}),
        style("brutalism", "Brutalism", "Raw exposed structure with heavy type and hard borders.", ["brutalism", "raw", "heavy"]),
        style("editorial", "Editorial design", "Magazine hierarchy with kicker, headline and rules.", ["editorial", "magazine", "serif"]),
        make_pattern("liquid-glass-button", title="Liquid glass button", category="button", summary="A frosted glass button with a refractive liquid edge and hover response.",
                     tags=["glass", "liquid", "button", "hero"], source_ids=["alpha"], frameworks=["javascript", "webgl"], dependencies=["glassy", "html2canvas"],
                     use_cases=["hero button"], performance={"gpu_intensity": "medium", "fallback_required": True},
                     accessibility={"motion": "subtle", "reduced_motion_alternative": True}, implementation_status="recipe_available",
                     knowledge_doc="knowledge/shaders/glass.md", recipe="knowledge/implementation-recipes/glass-recipe.md",
                     source_paths=["alpha:src/glass.js", "alpha:src/glass.css", "alpha:src/controls.js", "alpha:src/fourth.js"]),
        make_pattern("liquid-glass-css", title="Frosted glass with plain CSS", category="liquid-glass", summary="Frosted glass cards in plain CSS with backdrop blur and a solid fallback.",
                     tags=["glass", "blur", "css", "frosted"], source_ids=["beta"], frameworks=["css"], dependencies=[], use_cases=["hero card"],
                     performance={"gpu_intensity": "low", "fallback_required": False}, accessibility={"motion": "subtle", "reduced_motion_alternative": True},
                     implementation_status="recipe_available", knowledge_doc="knowledge/shaders/glass.md", source_paths=["beta:css/glass.css"]),
        make_pattern("smooth-scroll", title="Smooth scroll", category="scroll", summary="Inertia based smooth scrolling that keeps native scroll semantics intact.",
                     tags=["scroll", "inertia", "lenis"], source_ids=["beta"], frameworks=["react", "javascript"], dependencies=["lenis"], use_cases=["marketing site"],
                     accessibility={"motion": "moderate", "reduced_motion_alternative": False}, source_paths=["beta:src/lenis.ts"]),
        make_pattern("vue-only-scroll", title="Vue scroll reveal", category="scroll", summary="Scroll reveal composable for Vue applications.",
                     tags=["scroll", "reveal"], source_ids=["beta"], frameworks=["vue"], use_cases=["marketing site"], source_paths=["beta:src/vue.ts"]),
        make_pattern("shader-glass-background", title="Shader glass background", category="background-shader", summary="Animated glass gradient background rendered by a fragment shader.",
                     tags=["glass", "gradient", "shader"], source_ids=["alpha"], frameworks=["webgl", "glsl"], performance={"gpu_intensity": "high", "fallback_required": True},
                     accessibility={"motion": "moderate", "reduced_motion_alternative": True}),
        make_pattern("unlicensed-effect", title="Unlicensed cursor effect", category="cursor", summary="A cursor trail effect found in a repository that carries no license.",
                     tags=["cursor", "trail"], source_ids=["gamma"], frameworks=["react"], source_paths=["gamma:src/trail.js"]),
        make_pattern("custom-terms-marquee", title="Custom terms marquee", category="animation", summary="A looping marquee distributed under custom terms.",
                     tags=["marquee", "loop"], source_ids=["delta"], frameworks=["css"], source_paths=["delta:src/marquee.css"]),
        make_pattern("reference-gallery", title="Reference gallery workflow", category="workflow", summary="A reference-only gallery of styles for inspiration and mood boards.",
                     tags=["gallery", "inspiration"], source_ids=["web"], frameworks=["css"], source_paths=["web:index"]),
    ]


def sources():
    return [
        make_source("alpha"), make_source("beta", license="Apache-2.0"),
        make_source("gamma", license="NOASSERTION", license_status="not_found", redistribution_status="unresolved"),
        make_source("delta", license="LicenseRef-Custom-Terms", license_status="custom_terms", redistribution_status="license_specific"),
        make_source("web", type="website", acquisition_method="reference_only", license="NOASSERTION", license_status="not_found", redistribution_status="reference_only"),
    ]


def docs():
    out = {}
    for slug, (title, line) in STYLE_NOTES.items():
        out["knowledge/design-styles/%s.md" % slug] = NOTE % {"title": title, "slug": slug, "line": line}
    return out


class RecommendBase(helpers.TempDirTest):
    def setUp(self):
        super().setUp()
        self.layout = helpers.make_toolkit(self.tmp, sources=sources(), patterns=patterns(), docs=docs())
        self.project = self.tmp / "project dir"
        self.project.mkdir()

    def argv(self, *words):
        return list(words) + ["--root", str(self.layout.root), "--home", str(self.layout.home), "--project", str(self.project)]

    def run_cmd(self, *words):
        return helpers.call_main(rc.main, self.argv(*words))

    def data(self, *words):
        code, out, err = self.run_cmd(*(list(words) + ["--json"]))
        self.assertEqual(code, 0, err)
        return json.loads(out)

    def ids(self, *words):
        return [p["id"] for p in self.data(*words)["patterns"]]

    def make_present(self, source_id, *rels):
        for rel in rels:
            target = self.layout.sources_dir / source_id / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("x")


class OutputTests(RecommendBase):
    def test_text_output_has_every_section(self):
        code, out, err = self.run_cmd("glass hero button", "--allowed-deps", "any")
        self.assertEqual(code, 0, err)
        for needle in ("RECOMMENDATION for \"glass hero button\"", "STYLE", "PRIMARY:", "style-glassmorphism", "PATTERNS (", "1. liquid-glass-button",
                       "LICENSE GATE:", "NEXT STEPS", "sources: alpha (MIT)", "reuse: copy_with_attribution", "gpu: medium"):
            self.assertIn(needle, out)
        self.assertIn(str(self.layout.root / "knowledge" / "design-styles" / "glassmorphism.md"), out)
        self.assertIn(str(self.layout.root / "knowledge" / "shaders" / "glass.md"), out)
        self.assertIn(str(self.layout.root / "knowledge" / "implementation-recipes" / "glass-recipe.md"), out)

    def test_json_schema(self):
        d = self.data("glass hero button")
        self.assertEqual({"brief", "query", "count", "policy", "filters", "style", "patterns", "license_gate", "fallback", "notes", "next_steps"}, set(d))
        self.assertEqual(d["count"], len(d["patterns"]))
        self.assertEqual({"primary", "supporting", "conflicts"}, set(d["style"]))
        primary = d["style"]["primary"]
        for key in ("id", "title", "slug", "score", "summary", "note_path", "pairs_well_with", "avoid", "reuse", "gpu_intensity"):
            self.assertIn(key, primary)
        p = d["patterns"][0]
        for key in ("id", "title", "category", "score", "source_ids", "source_licenses", "reuse", "license_status", "gpu_intensity", "reduced_motion_alternative", "dependencies",
                    "dependencies_outside_policy", "implementation_status", "knowledge_doc", "knowledge_doc_path", "recipe", "recipe_path", "source_paths", "warnings"):
            self.assertIn(key, p)
        self.assertEqual(p["id"], "liquid-glass-button")
        self.assertEqual((p["source_ids"], p["reuse"], p["license_status"], p["gpu_intensity"]), (["alpha"], "copy_with_attribution", "verified", "medium"))
        self.assertEqual(p["dependencies"], ["glassy", "html2canvas"])
        self.assertTrue(p["reduced_motion_alternative"])
        self.assertEqual(p["implementation_status"], "recipe_available")
        self.assertTrue(p["recipe_path"].endswith("glass-recipe.md"))
        self.assertEqual(set(d["license_gate"]), {"strictest_reuse", "strictest_license_status", "allowed", "by_reuse", "review_sources", "line"})
        self.assertIsInstance(d["next_steps"], list)

    def test_only_first_three_source_paths_with_state(self):
        p = self.data("glass hero button")["patterns"][0]
        self.assertEqual([f["ref"] for f in p["source_paths"]], ["alpha:src/glass.js", "alpha:src/glass.css", "alpha:src/controls.js"])
        self.assertTrue(all(f["state"] == "not downloaded" and f["present"] is False for f in p["source_paths"]))
        self.make_present("alpha", "src/glass.js")
        p = self.data("glass hero button")["patterns"][0]
        # the source directory now exists, so the other files are missing from the download rather than "not downloaded"
        self.assertEqual([f["state"] for f in p["source_paths"]], ["downloaded", "path not found in download", "path not found in download"])
        self.assertTrue(p["source_paths"][0]["path"].endswith("glass.js"))
        _, out, _ = self.run_cmd("glass hero button")
        self.assertIn("glass.js  (downloaded)", out)
        self.assertIn("glass.css  (path not found in download)", out)

    def test_limit_and_stable_output(self):
        self.assertEqual(len(self.ids("glass", "--limit", "1")), 1)
        self.assertLessEqual(len(self.ids("glass")), 3)
        self.assertEqual(self.run_cmd("glass hero"), self.run_cmd("glass hero"))

    def test_stopwords_are_dropped_from_the_query(self):
        self.assertEqual(rc.clean_query("liquid glass hero for a fintech"), "liquid glass hero fintech")
        self.assertEqual(rc.clean_query("the for"), "the for")  # nothing left: keep the brief
        self.assertEqual(self.data("a glass hero for the page")["query"], "glass hero")

    def test_results_can_be_listed_by_the_chosen_style(self):
        # no implementation pattern contains the word "glassmorphism"; the style's `related` patterns fill the slots
        d = self.data("glassmorphism", "--limit", "2", "--allowed-deps", "any")
        self.assertEqual(d["style"]["primary"]["id"], "style-glassmorphism")
        self.assertEqual([(p["id"], p["match"], p["score"]) for p in d["patterns"]], [("liquid-glass-button", "style", 0.0), ("liquid-glass-css", "style", 0.0)])
        _, out, _ = self.run_cmd("glassmorphism", "--limit", "2")
        self.assertIn("listed by the chosen style", out)
        # a style without related patterns leaves the list empty
        d = self.data("magazine")
        self.assertEqual((d["style"]["primary"]["id"], d["patterns"]), ("style-editorial", []))


class StyleTests(RecommendBase):
    def test_primary_supporting_and_hints_from_the_note(self):
        d = self.data("glassmorphism liquid")
        self.assertEqual(d["style"]["primary"]["id"], "style-glassmorphism")
        self.assertEqual(sorted(d["style"]["primary"]["pairs_well_with"]), ["editorial", "liquid-materials"])
        self.assertEqual(d["style"]["primary"]["avoid"], ["brutalism"])
        self.assertEqual(d["style"]["supporting"]["id"], "style-liquid-materials")
        self.assertTrue(d["style"]["primary"]["note_path"].endswith("design-styles/glassmorphism.md"))

    def test_at_most_one_supporting_style_and_avoided_styles_are_not_combined(self):
        d = self.data("glassmorphism brutalism")  # both match, and each note says to avoid the other
        self.assertIsNone(d["style"]["supporting"])
        self.assertEqual({d["style"]["primary"]["id"]} | set(d["style"]["conflicts"]), {"style-glassmorphism", "style-brutalism"})
        self.assertEqual(len(d["style"]["conflicts"]), 1)
        _, out, _ = self.run_cmd("glassmorphism brutalism")
        self.assertIn("not combined (the notes say avoid)", out)

    def test_naming_a_style_outright_wins(self):
        brief = "editorial glass frosted"  # plain search ranking puts glassmorphism first
        self.assertEqual(self.data(brief)["style"]["primary"]["id"], "style-editorial")
        original = rc.STYLE_NAME_BOOST
        rc.STYLE_NAME_BOOST = 1.0
        try:
            self.assertEqual(self.data(brief)["style"]["primary"]["id"], "style-glassmorphism")
        finally:
            rc.STYLE_NAME_BOOST = original

    def test_hint_parser_ignores_unknown_words_and_splits_at_avoid(self):
        pairs, avoid = rc.parse_style_hints({"id": "style-glassmorphism", "knowledge_doc": "knowledge/design-styles/glassmorphism.md",
                                             "knowledge_doc_path": str(self.layout.root / "knowledge/design-styles/glassmorphism.md")},
                                            ["liquid-materials", "brutalism", "editorial", "glassmorphism"])
        self.assertEqual((sorted(pairs), avoid), (["editorial", "liquid-materials"], ["brutalism"]))
        self.assertEqual(rc.parse_style_hints({"id": "x", "knowledge_doc_path": str(self.tmp / "missing.md")}, ["a"]), ([], []))

    def test_3d_bound_styles_are_dropped_when_webgl_is_off(self):
        self.assertEqual(self.data("liquid metal chrome")["style"]["primary"]["id"], "style-liquid-materials")
        self.assertNotEqual((self.data("liquid metal chrome", "--no-webgl")["style"]["primary"] or {}).get("id"), "style-liquid-materials")
        # glassmorphism is gpu medium but has a CSS route, so it survives
        self.assertEqual(self.data("frosted", "--no-webgl", "--max-gpu", "low")["style"]["primary"]["id"], "style-glassmorphism")


class FilterTests(RecommendBase):
    def test_framework_filter_keeps_framework_agnostic_patterns(self):
        self.assertNotIn("vue-only-scroll", self.ids("scroll reveal", "--framework", "react"))
        self.assertIn("vue-only-scroll", self.ids("scroll reveal", "--framework", "vue"))
        self.assertIn("smooth-scroll", self.ids("scroll", "--framework", "nextjs"))  # next is react family
        self.assertNotIn("smooth-scroll", self.ids("scroll", "--framework", "vue"))
        self.assertIn("liquid-glass-css", self.ids("glass", "--framework", "vue"))  # plain CSS fits any framework

    def test_framework_without_any_pattern_says_so(self):
        d = self.data("scroll", "--framework", "svelte", "--limit", "2")
        self.assertEqual(d["patterns"], [])
        self.assertTrue(any("svelte" in n for n in d["notes"]))

    def test_max_gpu(self):
        self.assertNotIn("shader-glass-background", self.ids("glass", "--max-gpu", "medium", "--limit", "9"))
        self.assertEqual(self.ids("glass", "--max-gpu", "low", "--limit", "9"), ["liquid-glass-css"])
        self.assertEqual(self.ids("glass", "--max-gpu", "none", "--limit", "9"), [])

    def test_no_webgl_keeps_css_routes_but_drops_webgl(self):
        ids = self.ids("glass", "--no-webgl", "--limit", "9")
        self.assertEqual(ids, ["liquid-glass-css"])

    def test_reduced_motion_safe(self):
        self.assertIn("smooth-scroll", self.ids("scroll", "--limit", "9"))
        self.assertNotIn("smooth-scroll", self.ids("scroll", "--reduced-motion-safe", "--limit", "9"))

    def test_motion_without_alternative_gets_a_warning(self):
        p = {x["id"]: x for x in self.data("scroll", "--framework", "react")["patterns"]}["smooth-scroll"]
        self.assertTrue(p["warnings"])
        _, out, _ = self.run_cmd("scroll", "--framework", "react")
        self.assertIn("warning: has motion but no documented reduced-motion alternative", out)

    def test_bad_usage(self):
        self.assertEqual(self.run_cmd()[0], 2)
        self.assertEqual(self.run_cmd("glass", "--limit", "0")[0], 2)
        self.assertEqual(self.run_cmd("glass", "--max-gpu", "huge")[0], 2)
        code, _, err = self.run_cmd()
        self.assertIn("give a short brief", err)


class LicenseGateTests(RecommendBase):
    def test_permissive_only(self):
        gate = self.data("glass", "--max-gpu", "low")["license_gate"]
        self.assertEqual((gate["strictest_reuse"], gate["strictest_license_status"]), ("copy_with_attribution", "verified"))
        self.assertTrue(gate["line"].startswith("LICENSE GATE: strictest reuse class is copy_with_attribution"))
        self.assertIn("keeping the upstream copyright", gate["line"])

    def test_unlicensed_pattern_means_reimplement_only(self):
        gate = self.data("cursor trail")["license_gate"]
        self.assertEqual(gate["strictest_reuse"], "reimplement_only")
        self.assertEqual(gate["strictest_license_status"], "not_found")
        self.assertIn("copy no code", gate["line"])

    def test_custom_terms_points_at_the_source_to_review(self):
        gate = self.data("marquee")["license_gate"]
        self.assertEqual(gate["strictest_reuse"], "license_review_required")
        self.assertEqual(gate["review_sources"], ["delta"])
        self.assertIn("`design-sensei sources show delta`", gate["line"])

    def test_strictest_class_wins_and_each_pattern_is_listed(self):
        d = self.data("glass cursor trail marquee", "--limit", "9")
        order = ["original", "copy_with_attribution", "license_review_required", "verify_first", "reimplement_only", "reference_only"]
        classes = {p["reuse"] for p in d["patterns"]}
        self.assertEqual(d["license_gate"]["strictest_reuse"], max(classes, key=order.index))
        self.assertIn("Per pattern:", d["license_gate"]["line"])
        for p in d["patterns"]:
            self.assertIn(p["id"], d["license_gate"]["line"])

    def test_gate_line_in_text_output(self):
        _, out, _ = self.run_cmd("cursor trail")
        self.assertIn("LICENSE GATE: strictest reuse class is reimplement_only (licence status not_found)", out)

    def test_no_patterns_means_original_guidance(self):
        gate = self.data("magazine")["license_gate"]
        self.assertEqual(gate["strictest_reuse"], "original")
        self.assertIn("original guidance", gate["line"])


class FallbackTests(RecommendBase):
    def test_gpu_heavy_top_result_names_a_low_gpu_alternative(self):
        d = self.data("glass hero button", "--allowed-deps", "any")
        self.assertEqual(d["patterns"][0]["id"], "liquid-glass-button")
        fb = d["fallback"]
        self.assertIsNotNone(fb)
        self.assertEqual(fb["alternative"]["id"], "liquid-glass-css")
        self.assertIn("liquid-glass-button is gpu medium", fb["line"])
        self.assertTrue(fb["line"].startswith("FALLBACK:"))
        self.assertIn("`liquid-glass-css`", fb["line"])
        _, out, _ = self.run_cmd("glass hero button", "--allowed-deps", "any")
        self.assertIn("FALLBACK: liquid-glass-button is gpu medium", out)

    def test_dependencies_outside_the_allowed_list_trigger_the_fallback(self):
        d = self.data("scroll", "--framework", "react", "--allowed-deps", "gsap")
        self.assertEqual(d["patterns"][0]["id"], "smooth-scroll")
        self.assertEqual(d["patterns"][0]["dependencies_outside_policy"], ["lenis"])
        self.assertIn("outside allowed_dependencies", d["fallback"]["line"])
        self.assertIn("lenis", d["fallback"]["line"])
        _, out, _ = self.run_cmd("scroll", "--framework", "react", "--allowed-deps", "gsap")
        self.assertIn("(outside allowed: lenis)", out)

    def test_allowed_dependency_means_no_fallback(self):
        d = self.data("scroll", "--framework", "react", "--allowed-deps", "lenis")
        self.assertIsNone(d["fallback"])
        _, out, _ = self.run_cmd("scroll", "--framework", "react", "--allowed-deps", "lenis")
        self.assertNotIn("FALLBACK", out)

    def test_css_only_note_when_no_alternative_exists(self):
        d = self.data("shader gradient", "--allowed-deps", "none")
        self.assertEqual(d["patterns"][0]["id"], "shader-glass-background")
        self.assertIsNone(d["fallback"]["alternative"])
        self.assertIn("CSS-only version", d["fallback"]["line"])
        self.assertIn("gpu high", d["fallback"]["line"])

    def test_workflow_patterns_are_never_offered_as_a_fallback(self):
        d = self.data("shader gallery inspiration", "--allowed-deps", "none", "--limit", "5")
        if d["fallback"] and d["fallback"]["alternative"]:
            self.assertNotEqual(d["fallback"]["alternative"]["id"], "reference-gallery")

    def test_installed_packages_count_as_allowed(self):
        (self.project / "package.json").write_text(json.dumps({"dependencies": {"lenis": "^1.0.0"}}))
        d = self.data("scroll", "--framework", "react", "--allowed-deps", "existing")
        self.assertEqual(d["patterns"][0]["dependencies_outside_policy"], [])
        self.assertIsNone(d["fallback"])

    def test_dependency_policy_values(self):
        P = rc.DependencyPolicy
        self.assertEqual(P("any", []).outside(["a", "b"]), [])
        self.assertEqual(P("none", []).outside(["a"]), ["a"])
        self.assertEqual(P("minimal", []).outside(["a"]), [])
        self.assertEqual(P("minimal", []).outside(["a", "b"]), ["a", "b"])
        self.assertEqual(P("minimal", ["a"]).outside(["a", "b"]), [])
        self.assertEqual(P("existing", ["a"]).outside(["a", "b"]), ["b"])
        self.assertEqual(P(["gsap", "Lenis"], []).outside(["gsap", "lenis", "three"]), ["three"])
        self.assertEqual(P(["none"], []).allowed, "none")


class EmptyResultTests(RecommendBase):
    def test_no_match_is_exit_zero_with_a_hint(self):
        code, out, err = self.run_cmd("zzzzqqq")
        self.assertEqual(code, 0, err)
        self.assertIn("none matched", out)
        self.assertIn("no design style matched", out)
        self.assertIn("note: no matches", out)

    def test_no_match_json_is_well_formed(self):
        d = self.data("zzzzqqq")
        self.assertEqual((d["count"], d["patterns"], d["style"]["primary"], d["fallback"], d["next_steps"]), (0, [], None, None, []))
        self.assertEqual(d["license_gate"]["strictest_reuse"], "original")
        self.assertTrue(d["notes"])


class OfflineAndSourcesTests(RecommendBase):
    def test_works_with_no_network_and_nothing_downloaded(self):
        real_connect = socket.socket.connect
        real_create = socket.create_connection

        def refuse(*a, **k):
            raise AssertionError("recommend must not touch the network")

        socket.socket.connect = refuse
        socket.create_connection = refuse
        try:
            d = self.data("glass hero button", "--allowed-deps", "any")
        finally:
            socket.socket.connect = real_connect
            socket.create_connection = real_create
        self.assertFalse(self.layout.sources_dir.exists())
        self.assertGreaterEqual(len(d["patterns"]), 1)
        steps = " ".join(d["next_steps"])
        self.assertIn("design-sensei sources sync alpha", steps)
        self.assertNotIn("Open the files marked", steps)

    def test_sync_hint_names_only_missing_downloadable_sources(self):
        self.make_present("beta", "css/glass.css")
        steps = self.data("glass hero button", "--allowed-deps", "any")["next_steps"]
        sync = [s for s in steps if "sources sync" in s]
        self.assertEqual(len(sync), 1)
        self.assertTrue(sync[0].endswith("design-sensei sources sync alpha"))
        self.assertTrue(any("Open the files marked" in s for s in steps))
        self.make_present("alpha", "src/glass.js", "src/glass.css", "src/controls.js")
        steps = self.data("glass hero button", "--allowed-deps", "any")["next_steps"]
        self.assertFalse([s for s in steps if "sources sync" in s])

    def test_reference_only_sources_are_never_synced(self):
        d = self.data("gallery inspiration")
        p = d["patterns"][0]
        self.assertEqual(p["id"], "reference-gallery")
        self.assertEqual(p["source_paths"][0]["state"], "reference only (no download)")
        self.assertFalse([s for s in d["next_steps"] if "sources sync" in s])

    def test_offline_mode_never_suggests_a_download(self):
        (self.project / ".design-sensei.yaml").write_text("source_acquisition_mode: offline\n")
        steps = self.data("glass hero button", "--allowed-deps", "any")["next_steps"]
        self.assertFalse([s for s in steps if "sources sync" in s])
        self.assertTrue([s for s in steps if "Offline mode" in s])

    def test_next_steps_list_the_files_to_read(self):
        steps = self.data("glass hero button", "--allowed-deps", "any")["next_steps"]
        self.assertTrue(steps[0].startswith("Read the style note"))
        joined = "\n".join(steps)
        self.assertIn("glass.md", joined)
        self.assertIn("glass-recipe.md", joined)
        self.assertTrue(steps[-1].startswith("When done: design-sensei eval"))


class ConfigTests(RecommendBase):
    def test_config_turns_webgl_and_reduced_motion_filters_on(self):
        (self.project / ".design-sensei.yaml").write_text("webgl_enabled: false\nreduced_motion: static_first\n")
        d = self.data("glass", "--limit", "9")
        self.assertTrue(d["filters"]["no_webgl"])
        self.assertTrue(d["filters"]["reduced_motion_safe"])
        self.assertEqual(d["filters"]["origins"], {"no_webgl": "config", "reduced_motion_safe": "config"})
        self.assertEqual([p["id"] for p in d["patterns"]], ["liquid-glass-css"])
        _, out, _ = self.run_cmd("glass")
        self.assertIn("no-webgl (config)", out)

    def test_zero_webgl_canvas_budget_means_no_webgl(self):
        (self.project / ".design-sensei.yaml").write_text("performance_budget:\n  max_webgl_canvases: 0\n")
        self.assertTrue(self.data("glass")["filters"]["no_webgl"])

    def test_config_allowed_dependencies_and_option_override(self):
        (self.project / ".design-sensei.yaml").write_text("allowed_dependencies: none\n")
        d = self.data("scroll", "--framework", "react")
        self.assertEqual(d["filters"]["allowed_dependencies"], "none")
        self.assertEqual(d["patterns"][0]["dependencies_outside_policy"], ["lenis"])
        d = self.data("scroll", "--framework", "react", "--allowed-deps", "lenis")
        self.assertEqual(d["filters"]["allowed_dependencies"], ["lenis"])
        self.assertEqual(d["patterns"][0]["dependencies_outside_policy"], [])

    def test_preferred_frameworks_is_a_soft_preference(self):
        base = {p["id"]: p["score"] for p in self.data("scroll", "--limit", "9")["patterns"]}
        (self.project / ".design-sensei.yaml").write_text("preferred_frameworks: [vue]\n")
        pref = {p["id"]: p["score"] for p in self.data("scroll", "--limit", "9")["patterns"]}
        self.assertEqual(set(base), set(pref))  # nothing is filtered out
        self.assertGreater(pref["vue-only-scroll"], base["vue-only-scroll"])
        self.assertEqual(pref["smooth-scroll"], base["smooth-scroll"])

    def test_invalid_config_is_reported_not_fatal(self):
        (self.project / ".design-sensei.yaml").write_text("motion_intensity: 99\n")
        code, out, err = self.run_cmd("glass", "--json")
        self.assertEqual(code, 0, err)
        self.assertTrue(any("config problem" in n for n in json.loads(out)["notes"]))


class CliTests(helpers.TempDirTest):
    def test_registered_in_the_main_command_line(self):
        code, out, _ = run_cli(["recommend", "--help"])
        self.assertEqual(code, 0)
        for flag in ("--framework", "--max-gpu", "--reduced-motion-safe", "--no-webgl", "--allowed-deps", "--limit", "--json", "--project"):
            self.assertIn(flag, out)
        code, out, _ = run_cli(["--help"])
        self.assertIn("recommend", out)

    def test_real_catalog_end_to_end(self):
        env = {"DESIGN_SENSEI_HOME": str(self.tmp / "lib home")}
        code, out, err = run_cli(["recommend", "liquid glass hero for a fintech", "--json", "--project", str(self.tmp)], env)
        self.assertEqual(code, 0, err)
        d = json.loads(out)
        self.assertEqual(d["style"]["primary"]["id"], "style-glassmorphism")
        self.assertTrue(d["style"]["primary"]["pairs_well_with"])
        self.assertTrue(d["patterns"])
        self.assertIn("LICENSE GATE", d["license_gate"]["line"])
        self.assertTrue(all(f["state"] == "not downloaded" for p in d["patterns"] for f in p["source_paths"]))
        code, out, _ = run_cli(["recommend", "--project", str(self.tmp)], env)
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
