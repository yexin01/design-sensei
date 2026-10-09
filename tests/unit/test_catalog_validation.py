import unittest

from tests import helpers
from tests.helpers import make_pattern, make_source
import validate_catalog as vc
from dslib import catalog


def errors_for(layout, **kw):
    return vc.run_validation(layout, **kw).errors


class ValidCatalogTests(helpers.TempDirTest):
    def test_minimal_valid_catalog(self):
        layout = helpers.make_toolkit(self.tmp, patterns=[make_pattern()])
        report = vc.run_validation(layout)
        self.assertEqual(report.errors, [])

    def test_real_catalog_has_no_errors(self):
        from dslib.paths import resolve_layout
        layout = resolve_layout(home=str(self.tmp / "home"))
        self.assertEqual(vc.run_validation(layout).errors, [])


class SourceRuleTests(helpers.TempDirTest):
    def validate(self, *sources, **kw):
        layout = helpers.make_toolkit(self.tmp, sources=list(sources), patterns=[])
        return vc.run_validation(layout, **kw).errors

    def assert_error(self, errors, needle):
        self.assertTrue(any(needle in e for e in errors), "expected %r in %s" % (needle, errors))

    def test_duplicate_ids_and_urls(self):
        self.assert_error(self.validate(make_source("a"), make_source("a", url="https://github.com/x/y")), "duplicate source id")
        self.assert_error(self.validate(make_source("a"), make_source("b", url="https://GitHub.com/example/a.git")), "duplicate url")

    def test_duplicate_local_path(self):
        self.assert_error(self.validate(make_source("a", local_path="same"), make_source("b", local_path="same")), "also used by")

    def test_missing_required_metadata(self):
        broken = make_source("a")
        del broken["license"]
        self.assert_error(self.validate(broken), "missing required field 'license'")

    def test_invalid_urls(self):
        for bad in ("not a url", "ftp://example.com/x", "github.com/x/y", ""):
            with self.subTest(url=bad):
                self.assertTrue(self.validate(make_source("a", url=bad)))

    def test_invalid_commit_hash(self):
        for bad in ("abc123", "G" * 40, "A" * 40, "a" * 39):
            with self.subTest(pin=bad):
                self.assert_error(self.validate(make_source("a", pinned_commit=bad)), "pinned_commit")

    def test_missing_pin_is_warning_non_strict_error_strict(self):
        layout = helpers.make_toolkit(self.tmp, sources=[make_source("a", pinned_commit=None)])
        self.assertEqual(vc.run_validation(layout).errors, [])
        self.assertTrue(any("no pinned_commit" in w for w in vc.run_validation(layout).warnings))
        self.assert_error(vc.run_validation(layout, strict=True).errors, "no pinned_commit")

    def test_sparse_rules(self):
        self.assert_error(self.validate(make_source("a", acquisition_method="git_sparse")), "non-empty sparse_paths")
        self.assert_error(self.validate(make_source("a", sparse_paths=["src"])), "only allowed with acquisition_method git_sparse")
        self.assert_error(self.validate(make_source("a", acquisition_method="git_sparse", sparse_paths=["../etc"])), "must not contain '..'")
        self.assertEqual(self.validate(make_source("a", acquisition_method="git_sparse", sparse_paths=["src", "docs/x"])), [])

    def test_website_cannot_be_cloned(self):
        self.assert_error(self.validate(make_source("a", type="website")), "must be reference_only")
        site = make_source("a", type="website", acquisition_method="reference_only", pinned_commit=None, default_branch=None,
                           license="NOASSERTION", license_status="unknown", redistribution_status="reference_only")
        self.assertEqual(self.validate(site), [])

    def test_redistributable_requires_verified_permissive_license(self):
        self.assert_error(self.validate(make_source("a", license_status="pending_verification")), "requires license_status verified")
        self.assert_error(self.validate(make_source("a", license_status="custom_terms")), "redistributable_with_notice")
        self.assert_error(self.validate(make_source("a", license="LicenseRef-Custom-Terms")), "needs a concrete SPDX id")

    def test_unlicensed_and_proprietary_rules(self):
        self.assert_error(self.validate(make_source("a", license_status="not_found", redistribution_status="license_specific", license="NOASSERTION")), "must be unresolved or reference_only")
        self.assert_error(self.validate(make_source("a", license_status="proprietary_terms", redistribution_status="unresolved", license="NOASSERTION")), "proprietary_terms sources must be reference_only")

    def test_verified_cannot_apply_to_reference_only(self):
        self.assert_error(self.validate(make_source("a", acquisition_method="reference_only", pinned_commit=None)), "impossible for a reference-only source")

    def test_future_date_rejected(self):
        self.assert_error(self.validate(make_source("a", last_checked="2999-01-01")), "in the future")

    def test_unsafe_local_path(self):
        self.assert_error(self.validate(make_source("a", local_path="../escape")), "local_path")
        self.assert_error(self.validate(make_source("a", local_path="/abs")), "local_path")

    def test_unknown_field_rejected(self):
        self.assert_error(self.validate(make_source("a", surprise=True)), "unknown field 'surprise'")

    def test_required_upstream_sources_enforced_in_strict_mode(self):
        errors = self.validate(make_source("a"), strict=True)
        self.assert_error(errors, "required upstream source missing")

    def test_review_for_unknown_source(self):
        review = {"source_id": "ghost", "license_files": [], "spdx_detected": "MIT", "detection": "manual", "copyright": [],
                  "reviewed_commit": None, "review_status": "auto_checked"}
        layout = helpers.make_toolkit(self.tmp, reviews=[review])
        self.assert_error(vc.run_validation(layout).errors, "review refers to an unknown source")


class PatternRuleTests(helpers.TempDirTest):
    def validate(self, patterns, sources=None, **kw):
        layout = helpers.make_toolkit(self.tmp, sources=sources or [make_source("alpha")], patterns=patterns, **kw.pop("toolkit", {}))
        return vc.run_validation(layout, **kw)

    def assert_error(self, report, needle):
        self.assertTrue(any(needle in e for e in report.errors), "expected %r in %s" % (needle, report.errors))

    def test_unknown_source_and_duplicate_ids(self):
        self.assert_error(self.validate([make_pattern(source_ids=["ghost"])]), "unknown source id 'ghost'")
        self.assert_error(self.validate([make_pattern("x"), make_pattern("x")]), "duplicate pattern id")

    def test_duplicate_across_pattern_files(self):
        layout = helpers.make_toolkit(self.tmp, patterns=[make_pattern("x")], pattern_files={"more.yaml": [make_pattern("x")]})
        self.assert_error(vc.run_validation(layout), "duplicate pattern id")

    def test_pattern_files_are_merged(self):
        layout = helpers.make_toolkit(self.tmp, patterns=[make_pattern("one")], pattern_files={"more.yaml": [make_pattern("two")]})
        self.assertEqual(vc.run_validation(layout).errors, [])
        self.assertEqual([p["id"] for p in catalog.load_patterns(layout)], ["one", "two"])

    def test_upstream_pattern_needs_a_source(self):
        self.assert_error(self.validate([make_pattern(source_ids=[], provenance="upstream")]), "needs at least one source_ids")
        self.assertEqual(self.validate([make_pattern(source_ids=[], provenance="original")]).errors, [])

    def test_schema_violations(self):
        self.assert_error(self.validate([make_pattern(category="nonsense")]), "category")
        self.assert_error(self.validate([make_pattern(summary="short")]), "at least 30 characters")
        self.assert_error(self.validate([make_pattern(tags=["Not Kebab"])]), "tags")

    def test_source_paths_checked_against_local_clone(self):
        layout = helpers.make_toolkit(self.tmp, patterns=[make_pattern(source_paths=["alpha:src/a.js", "alpha:missing.txt"])])
        # source not downloaded: unchecked, no error
        self.assertEqual(vc.run_validation(layout).errors, [])
        (layout.sources_dir / "alpha" / "src").mkdir(parents=True)
        (layout.sources_dir / "alpha" / "src" / "a.js").write_text("x")
        report = vc.run_validation(layout)
        self.assertTrue(any("missing.txt" in e and "does not exist" in e for e in report.errors))
        self.assertFalse(any("src/a.js" in e for e in report.errors))

    def test_source_path_must_use_listed_source_and_be_safe(self):
        report = self.validate([make_pattern(source_paths=["other:x.js"])])
        self.assert_error(report, "not in source_ids")
        (self.tmp / "again").mkdir()
        self.assert_error(self.validate([make_pattern(source_paths=["alpha:../x"])]), "must not contain '..'")

    def test_paths_with_spaces_are_supported(self):
        layout = helpers.make_toolkit(self.tmp, patterns=[make_pattern(source_paths=["alpha:my dir/file name.js"])])
        (layout.sources_dir / "alpha" / "my dir").mkdir(parents=True)
        (layout.sources_dir / "alpha" / "my dir" / "file name.js").write_text("x")
        self.assertEqual(vc.run_validation(layout).errors, [])

    def test_reference_only_source_has_no_files(self):
        site = make_source("site", type="website", acquisition_method="reference_only", pinned_commit=None, default_branch=None,
                           license="NOASSERTION", license_status="unknown", redistribution_status="reference_only")
        self.assert_error(self.validate([make_pattern(source_ids=["site"], source_paths=["site:x"])], sources=[site]), "reference-only")

    def test_sparse_outside_checkout_is_unchecked_not_error(self):
        sparse = make_source("alpha", acquisition_method="git_sparse", sparse_paths=["src"])
        layout = helpers.make_toolkit(self.tmp, sources=[sparse], patterns=[make_pattern(source_paths=["alpha:docs/readme.md"])])
        (layout.sources_dir / "alpha").mkdir(parents=True)
        self.assertEqual(vc.run_validation(layout).errors, [])

    def test_declared_license_status_must_match_derived(self):
        bad = make_pattern(license_status="verified")
        sources = [make_source("alpha", license_status="custom_terms", redistribution_status="license_specific", license="LicenseRef-Custom-Terms")]
        self.assert_error(self.validate([bad], sources=sources), "does not match the status derived")

    def test_recipe_required_for_recipe_status_and_must_exist(self):
        self.assert_error(self.validate([make_pattern(implementation_status="recipe_available")]), "requires a recipe path")
        self.assert_error(self.validate([make_pattern(implementation_status="recipe_available", recipe="knowledge/implementation-recipes/x.md")]), "does not exist")
        self.assert_error(self.validate([make_pattern(knowledge_doc="docs/x.md")]), "path under knowledge/")

    def test_warnings_for_motion_without_alternative(self):
        report = self.validate([make_pattern(accessibility={"motion": "intense", "reduced_motion_alternative": False},
                                              performance={"gpu_intensity": "high", "fallback_required": False})])
        self.assertTrue(any("reduced-motion alternative" in w for w in report.warnings))
        self.assertTrue(any("fallback_required is false" in w for w in report.warnings))

    def test_related_must_exist(self):
        self.assert_error(self.validate([make_pattern(related=["ghost"])]), "related pattern 'ghost'")

    def test_coverage_warning_and_strict_error(self):
        layout = helpers.make_toolkit(self.tmp, sources=[make_source("alpha"), make_source("beta")], patterns=[make_pattern()])
        self.assertTrue(any("beta" in w for w in vc.run_validation(layout).warnings))
        self.assertTrue(any("beta" in e and "no pattern or knowledge note" in e for e in vc.run_validation(layout, strict=True).errors))


class KnowledgeDocTests(helpers.TempDirTest):
    def doc(self, body="Body text.", **meta):
        data = {"title": "A note", "kind": "guide", "summary": "A summary that is long enough to pass.", "source_ids": ["alpha"], "pattern_ids": [], "updated": "2026-10-09"}
        data.update(meta)
        fm = "\n".join("%s: %s" % (k, v if isinstance(v, str) and k in ("kind",) else __import__("json").dumps(v)) for k, v in data.items())
        return "---\n%s\n---\n\n%s\n" % (fm, body)

    def run_with(self, text, patterns=None):
        layout = helpers.make_toolkit(self.tmp, patterns=patterns or [make_pattern()], docs={"knowledge/guides/a.md": text})
        return layout, vc.run_validation(layout)

    def test_valid_note(self):
        _, report = self.run_with(self.doc())
        self.assertEqual(report.errors, [])

    def test_missing_front_matter(self):
        _, report = self.run_with("# no front matter\n")
        self.assertTrue(any("missing YAML front matter" in e for e in report.errors))

    def test_bad_front_matter_values(self):
        _, report = self.run_with(self.doc(kind="nonsense", source_ids=["ghost"], pattern_ids=["ghost"]))
        text = " ".join(report.errors)
        self.assertIn("kind", text)
        self.assertIn("unknown source 'ghost'", text)
        self.assertIn("unknown pattern 'ghost'", text)

    def test_citations_are_verified_when_source_present(self):
        layout, report = self.run_with(self.doc("See `alpha:src/real.js` and `alpha:src/fake.js:12`."))
        self.assertEqual(report.errors, [])  # not downloaded -> unchecked
        (layout.sources_dir / "alpha" / "src").mkdir(parents=True)
        (layout.sources_dir / "alpha" / "src" / "real.js").write_text("x")
        report = vc.run_validation(layout)
        self.assertEqual(len([e for e in report.errors if "citation" in e]), 1)
        self.assertTrue(any("fake.js" in e for e in report.errors))

    def test_citation_line_suffixes_and_non_source_ids_are_ignored(self):
        layout, _ = self.run_with(self.doc("Use `npm:install` and `alpha:src/real.js#L10-L20` and `alpha:src/real.js:42`."))
        (layout.sources_dir / "alpha" / "src").mkdir(parents=True)
        (layout.sources_dir / "alpha" / "src" / "real.js").write_text("x")
        self.assertEqual(vc.run_validation(layout).errors, [])

    def test_readme_files_are_skipped(self):
        layout = helpers.make_toolkit(self.tmp, patterns=[make_pattern()], docs={"knowledge/guides/README.md": "# plain index\n"})
        self.assertEqual(vc.run_validation(layout).errors, [])


class CliTests(helpers.TempDirTest):
    def test_exit_codes_and_json(self):
        layout = helpers.make_toolkit(self.tmp, patterns=[make_pattern()])
        code, out, _ = helpers.call_main(vc.main, ["validate", "--root", str(layout.root), "--home", str(layout.home), "--json"])
        self.assertEqual(code, 0)
        self.assertTrue(__import__("json").loads(out)["ok"])
        (layout.root / "catalog" / "sources.yaml").write_text("schema_version: 1\nsources: []\n")
        code, out, _ = helpers.call_main(vc.main, ["validate", "--root", str(layout.root), "--home", str(layout.home)])
        self.assertEqual(code, 1)
        self.assertIn("FAILED", out)

    def test_strict_turns_warnings_into_failure(self):
        layout = helpers.make_toolkit(self.tmp, patterns=[make_pattern()])
        code, _, _ = helpers.call_main(vc.main, ["validate", "--strict", "--root", str(layout.root), "--home", str(layout.home)])
        self.assertEqual(code, 1)  # required upstream sources are missing in the fixture


if __name__ == "__main__":
    unittest.main()


class SkillDocTests(helpers.TempDirTest):
    def validate(self, text, relpath="skills/design-sensei/references/x.md", extra=None):
        docs = {relpath: text}
        docs.update(extra or {})
        layout = helpers.make_toolkit(self.tmp, patterns=[make_pattern("known-pattern")], docs=docs)
        return layout, vc.run_validation(layout).errors

    def test_valid_links_pass(self):
        _, errors = self.validate("# X\n\nUse [[known-pattern]] and [note](../../../knowledge/guides/n.md).\n",
                                  extra={"knowledge/guides/n.md": "---\ntitle: \"Note\"\nkind: guide\nsummary: \"A summary that is long enough to pass.\"\nsource_ids: []\npattern_ids: []\nupdated: \"2026-10-09\"\n---\nbody\n"})
        self.assertEqual(errors, [])

    def test_unknown_pattern_id_and_broken_link_are_errors(self):
        _, errors = self.validate("# X\n\n[[ghost-pattern]] and [gone](../../../knowledge/missing.md) and [ext](https://example.com) and [anchor](#a)\n")
        self.assertTrue(any("[[ghost-pattern]]" in e for e in errors))
        self.assertTrue(any("broken relative link ../../../knowledge/missing.md" in e for e in errors))
        self.assertEqual(len(errors), 2)

    def test_citations_in_skill_docs_are_checked(self):
        layout, errors = self.validate("# X\n\nSee `alpha:src/real.js` and `alpha:src/fake.js`.\n", relpath="skills/design-sensei/patterns/p.md")
        self.assertEqual(errors, [])
        (layout.sources_dir / "alpha" / "src").mkdir(parents=True)
        (layout.sources_dir / "alpha" / "src" / "real.js").write_text("x")
        errors = vc.run_validation(layout).errors
        self.assertEqual(len(errors), 1)
        self.assertIn("fake.js", errors[0])


class RealSkillTests(unittest.TestCase):
    def test_skill_has_all_referenced_files_and_valid_front_matter(self):
        from dslib import knowledge
        skill = helpers.ROOT / "skills" / "design-sensei" / "SKILL.md"
        meta, _, error = knowledge.parse_frontmatter(skill.read_text(encoding="utf-8"))
        self.assertIsNone(error)
        self.assertEqual(meta["name"], "design-sensei")
        self.assertLess(len(meta["description"]), 1536)
        self.assertLessEqual(len(skill.read_text(encoding="utf-8").splitlines()), 500)
        refs = sorted(p.name for p in (skill.parent / "references").glob("*.md"))
        self.assertEqual(refs, sorted(["art-direction.md", "design-principles.md", "typography.md", "color-systems.md", "layout-composition.md",
                                       "component-selection.md", "motion-design.md", "shaders-and-webgl.md", "three-dimensional-design.md",
                                       "responsive-design.md", "accessibility.md", "performance.md", "design-qa.md", "source-usage.md"]))
        self.assertEqual(len(list((skill.parent / "patterns").glob("*.md"))), 15)
