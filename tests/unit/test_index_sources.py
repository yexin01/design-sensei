import json
import os
import unittest

from tests import helpers
from tests.helpers import make_source
import build_index
import index_sources as ix


class IndexTests(helpers.TempDirTest):
    def setUp(self):
        super().setUp()
        self.layout = helpers.make_toolkit(self.tmp)
        root = self.layout.sources_dir / "alpha"
        files = {
            "README.md": "# Alpha Library\n\nAlpha makes interfaces glow and animate smoothly.\n",
            "LICENSE": "MIT License",
            "package.json": json.dumps({"name": "alpha-ui", "version": "1.2.3", "description": "Glowing UI", "license": "MIT", "dependencies": {"gsap": "^3"}}),
            "src/Hero Banner.tsx": "import gsap from 'gsap';\nexport default function HeroBanner() { return null }\nexport const Extra = 1;\n// prefers-reduced-motion\n",
            "src/shaders/wave.frag": "precision highp float;\nvoid main(){ gl_FragColor = vec4(1.0); }\n",
            "src/styles.css": ".a { backdrop-filter: blur(4px); } @keyframes x { from {opacity:0} to {opacity:1} }",
            "src/inline.js": "const src = `precision mediump float; void main(){ gl_FragColor=vec4(0.); }`;",
            "docs/guide.md": "# Guide\n\ntext",
            "examples/demo.html": "<canvas></canvas>",
            "tests/a.test.ts": "test()",
            "node_modules/dep/index.js": "module.exports = 1",
            "dist/bundle.js": "var a=1",
            "package-lock.json": "{}",
            ".env": "SECRET=1",
            "id_rsa.key": "-----BEGIN",
            ".github/workflows/ci.yml": "name: ci",
            "image.png": "binary",
        }
        for rel, text in files.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text, encoding="utf-8")
        os.symlink(str(self.tmp), str(root / "link-to-outside"))
        self.index = ix.build_index(self.layout)
        self.entry = self.index["sources"]["alpha"]
        self.paths = {f["path"]: f for f in self.entry["files"]}

    def test_excludes_dependencies_build_output_lockfiles_secrets_binaries_symlinks(self):
        for bad in ("node_modules/dep/index.js", "dist/bundle.js", "package-lock.json", ".env", "id_rsa.key", "image.png", "link-to-outside", ".github/workflows/ci.yml"):
            self.assertNotIn(bad, self.paths)
        self.assertEqual(self.entry["media_files"], {".png": 1})

    def test_kinds_and_titles(self):
        self.assertEqual(self.paths["README.md"]["kind"], "readme")
        self.assertEqual(self.paths["README.md"]["title"], "Alpha Library")
        self.assertEqual(self.paths["LICENSE"]["kind"], "license")
        self.assertEqual(self.paths["src/shaders/wave.frag"]["kind"], "shader")
        self.assertEqual(self.paths["src/inline.js"]["kind"], "shader")  # GLSL embedded in a script
        self.assertEqual(self.paths["src/styles.css"]["kind"], "style")
        self.assertEqual(self.paths["tests/a.test.ts"]["kind"], "test")
        self.assertEqual(self.paths["package.json"]["title"], "alpha-ui")

    def test_paths_with_spaces_exports_and_tags(self):
        entry = self.paths["src/Hero Banner.tsx"]
        self.assertEqual(entry["kind"], "component")
        self.assertEqual(entry["title"], "HeroBanner")
        self.assertEqual(entry["exports"], ["HeroBanner", "Extra"])
        self.assertIn("gsap", entry["tags"])
        self.assertIn("reduced-motion", entry["tags"])
        self.assertIn("backdrop-filter", self.paths["src/styles.css"]["tags"])
        self.assertIn("css-keyframes", self.paths["src/styles.css"]["tags"])
        self.assertIn("example", self.paths["examples/demo.html"]["tags"])

    def test_package_and_readme_summaries(self):
        pkg = self.entry["packages"][0]
        self.assertEqual((pkg["name"], pkg["version"], pkg["license"], pkg["dependencies"]), ("alpha-ui", "1.2.3", "MIT", ["gsap"]))
        self.assertIn("interfaces glow", self.entry["readme"]["summary"])

    def test_deterministic_output(self):
        a = json.dumps(ix.build_index(self.layout), sort_keys=True)
        b = json.dumps(ix.build_index(self.layout), sort_keys=True)
        self.assertEqual(a, b)
        ix.write_index(self.layout, self.index)
        first = self.layout.source_index_path.read_bytes()
        ix.write_index(self.layout, ix.build_index(self.layout))
        self.assertEqual(first, self.layout.source_index_path.read_bytes())

    def test_files_sorted_by_path(self):
        paths = [f["path"] for f in self.entry["files"]]
        self.assertEqual(paths, sorted(paths))

    def test_load_index_round_trip_and_version_guard(self):
        ix.write_index(self.layout, self.index)
        self.assertEqual(ix.load_index(self.layout)["sources"]["alpha"]["file_count"], self.entry["file_count"])
        self.layout.source_index_path.write_text(json.dumps({"version": 99}))
        self.assertIsNone(ix.load_index(self.layout))
        self.layout.source_index_path.write_text("not json")
        self.assertIsNone(ix.load_index(self.layout))

    def test_reference_only_and_missing_sources_are_skipped(self):
        layout = helpers.make_toolkit(self.tmp, home=self.tmp / "fresh home", sources=[make_source("alpha"), make_source("beta"),
                                                            make_source("site", type="website", acquisition_method="reference_only", pinned_commit=None,
                                                                        license="NOASSERTION", license_status="unknown", redistribution_status="reference_only")])
        (layout.sources_dir / "alpha").mkdir(parents=True)
        (layout.sources_dir / "alpha" / "a.js").write_text("export const a = 1")
        self.assertEqual(list(ix.build_index(layout)["sources"]), ["alpha"])

    def test_command_writes_index(self):
        code, out, _ = helpers.call_main(ix.main, ["--root", str(self.layout.root), "--home", str(self.layout.home)])
        self.assertEqual(code, 0)
        self.assertTrue(self.layout.source_index_path.is_file())
        self.assertIn("alpha", out)


class PatternIndexDocsTests(helpers.TempDirTest):
    def make(self):
        doc = '---\ntitle: "A note"\nkind: guide\nsummary: "A summary that is long enough to pass."\nsource_ids: ["alpha"]\npattern_ids: ["one"]\nupdated: "2026-10-09"\n---\n\nBody\n'
        return helpers.make_toolkit(self.tmp, patterns=[helpers.make_pattern("one"), helpers.make_pattern("two", category="scroll", tags=["scroll"], frameworks=["gsap"])],
                                    docs={"knowledge/guides/a.md": doc})

    def test_generate_write_and_check(self):
        layout = self.make()
        files = build_index.generate_docs(layout)
        self.assertEqual(sorted(files), ["README.md", "by-category.md", "by-framework.md", "by-source.md", "by-tag.md", "notes.md", "pattern-index.json"])
        self.assertIn("## hero (1)", files["by-category.md"])
        self.assertIn("## scroll (1)", files["by-category.md"])
        data = json.loads(files["pattern-index.json"])
        self.assertEqual([p["id"] for p in data["patterns"]], ["one", "two"])
        self.assertEqual(data["patterns"][0]["reuse"], "copy_with_attribution")
        self.assertEqual(build_index.stale_docs(layout), sorted("knowledge/pattern-index/" + n for n in files))
        build_index.write_docs(layout)
        self.assertEqual(build_index.stale_docs(layout), [])
        self.assertEqual(files, build_index.generate_docs(layout))  # deterministic
        (layout.knowledge_dir / "pattern-index" / "by-tag.md").write_text("tampered")
        self.assertEqual(build_index.stale_docs(layout), ["knowledge/pattern-index/by-tag.md"])

    def test_check_command_exit_codes(self):
        layout = self.make()
        base = ["--root", str(layout.root), "--home", str(layout.home)]
        self.assertEqual(helpers.call_main(build_index.main, ["build", "--check"] + base)[0], 1)
        self.assertEqual(helpers.call_main(build_index.main, ["build", "--docs-only"] + base)[0], 0)
        self.assertEqual(helpers.call_main(build_index.main, ["build", "--check"] + base)[0], 0)


if __name__ == "__main__":
    unittest.main()
