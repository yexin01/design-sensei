import unittest
from pathlib import Path

from tests import helpers  # noqa: F401  (sets sys.path)
from dslib import yamlite
from dslib.yamlite import YamlError


class ParseTests(unittest.TestCase):
    def test_scalars(self):
        doc = yamlite.loads("a: 1\nb: 1.5\nc: true\nd: null\ne: ~\nf: text here\ng: \"q: x\"\nh: 'it''s'\ni:\n")
        self.assertEqual(doc, {"a": 1, "b": 1.5, "c": True, "d": None, "e": None, "f": "text here", "g": "q: x", "h": "it's", "i": None})

    def test_versions_and_urls_stay_strings(self):
        doc = yamlite.loads("v: 1.2.3\nu: https://example.com/a?b=c\nh: 0123abc\n")
        self.assertEqual(doc, {"v": "1.2.3", "u": "https://example.com/a?b=c", "h": "0123abc"})

    def test_comments(self):
        doc = yamlite.loads("# top\na: 1  # trailing\nb: \"x # not a comment\"\nc: x#y\n")
        self.assertEqual(doc, {"a": 1, "b": "x # not a comment", "c": "x#y"})

    def test_nested_mapping_and_sequences(self):
        text = "root:\n  items:\n    - one\n    - two: 2\n      three: 3\n    - - nested\n      - list\n  empty: []\n  none:\nsame:\n- a\n- b\n"
        self.assertEqual(yamlite.loads(text), {
            "root": {"items": ["one", {"two": 2, "three": 3}, ["nested", "list"]], "empty": [], "none": None},
            "same": ["a", "b"],
        })

    def test_sequence_of_mappings_at_top_level(self):
        self.assertEqual(yamlite.loads("- id: a\n  v: 1\n- id: b\n  v: 2\n"), [{"id": "a", "v": 1}, {"id": "b", "v": 2}])

    def test_flow_collections(self):
        doc = yamlite.loads("a: [x, 'y z', \"w\", 3]\nb: {k: v, n: 2}\nc: []\nd: {}\ne: [[1, 2], {a: b}]\n")
        self.assertEqual(doc, {"a": ["x", "y z", "w", 3], "b": {"k": "v", "n": 2}, "c": [], "d": {}, "e": [[1, 2], {"a": "b"}]})

    def test_block_scalars(self):
        text = "lit: |\n  line1\n    indented\n  line3\nfold: >\n  a\n  b\n\n  c\nstrip: |-\n  x\nkeep: |+\n  y\n\nnext: 1\n"
        doc = yamlite.loads(text)
        self.assertEqual(doc["lit"], "line1\n  indented\nline3\n")
        self.assertEqual(doc["fold"], "a b\nc\n")
        self.assertEqual(doc["strip"], "x")
        self.assertEqual(doc["keep"], "y\n\n")
        self.assertEqual(doc["next"], 1)

    def test_block_scalar_in_sequence_item(self):
        self.assertEqual(yamlite.loads("- |\n  text\n- b\n"), ["text\n", "b"])

    def test_document_start_marker(self):
        self.assertEqual(yamlite.loads("---\na: 1\n"), {"a": 1})

    def test_quoted_keys_and_escapes(self):
        self.assertEqual(yamlite.loads('"a b": 1\n"t\\tab": "x\\ny\\u00e9"\n'), {"a b": 1, "t\tab": "x\nyé"})

    def test_empty_document(self):
        self.assertIsNone(yamlite.loads(""))
        self.assertIsNone(yamlite.loads("# only a comment\n"))

    def test_crlf_and_bom(self):
        self.assertEqual(yamlite.loads("\ufeffa: 1\r\nb:\r\n  - x\r\n"), {"a": 1, "b": ["x"]})

    def test_unicode_and_spaces(self):
        self.assertEqual(yamlite.loads("name: Café déjà vu\n"), {"name": "Café déjà vu"})


class RejectTests(unittest.TestCase):
    CASES = {
        "yaml 1.1 boolean": "a: yes\n",
        "yaml 1.1 off": "a: Off\n",
        "date": "a: 2026-10-09\n",
        "octal-looking": "a: 0123\n",
        "exponent only": "a: 1e3\n",
        "sexagesimal": "a: 1:30\n",
        "colon in plain value": "a: b: c\n",
        "anchor": "a: &x 1\n",
        "alias": "a: *x\n",
        "tag": "a: !!str 1\n",
        "duplicate key": "a: 1\na: 2\n",
        "tab indentation": "a:\n\tb: 1\n",
        "unterminated quote": "a: 'oops\n",
        "multiline flow": "a: [1,\n 2]\n",
        "unterminated flow": "a: [1, 2\n",
        "multiple documents": "a: 1\n---\nb: 2\n",
        "non-string key": "1: x\n",
        "bool key": "true: x\n",
        "bad indentation": "a:\n  b: 1\n c: 2\n",
        "complex key": "? a\n: b\n",
        "indentation indicator": "a: |2\n  x\n",
        "no colon": "a: 1\nplain text\n",
    }

    def test_each_is_rejected(self):
        for name, text in self.CASES.items():
            with self.subTest(name):
                with self.assertRaises(YamlError):
                    yamlite.loads(text)

    def test_error_carries_line_and_source(self):
        with self.assertRaises(YamlError) as ctx:
            yamlite.loads("a: 1\nb: yes\n", source="file.yaml")
        self.assertEqual(ctx.exception.line, 2)
        self.assertIn("file.yaml:2", str(ctx.exception))


class DumpTests(unittest.TestCase):
    SAMPLES = [
        {"a": 1, "b": [1, 2, {"c": "d"}], "e": {"f": None, "g": True}},
        {"s": "needs: quoting", "t": "yes", "u": "2026-10-09", "v": "0123", "w": "# hash", "x": " lead", "y": "", "z": "multi\nline\n"},
        {"list": [], "map": {}, "nested": [[1, 2], [3]], "uni": "Café — ok"},
        [{"id": "a", "tags": ["x", "y"]}, {"id": "b", "tags": []}],
        {"quote\"d key": 1, "yes": 2, "1.5": 3},
        {"long": "a" * 300, "path": "src/app/page.tsx", "url": "https://x.dev/a#b"},
    ]

    def test_round_trip(self):
        for sample in self.SAMPLES:
            with self.subTest(sample=str(sample)[:40]):
                self.assertEqual(yamlite.loads(yamlite.dumps(sample)), sample)

    def test_dumps_is_deterministic(self):
        self.assertEqual(yamlite.dumps(self.SAMPLES[0]), yamlite.dumps(self.SAMPLES[0]))

    def test_unsupported_type(self):
        with self.assertRaises(TypeError):
            yamlite.dumps({"a": object()})


class CompatibilityTests(unittest.TestCase):
    """Everything yamlite accepts must load identically with PyYAML (checked when installed)."""

    def test_repo_yaml_files_match_pyyaml(self):
        try:
            import yaml  # type: ignore
        except ImportError:
            self.skipTest("PyYAML not installed")
        root = helpers.ROOT
        files = list((root / "catalog").glob("*.yaml")) + list((root / "catalog" / "patterns.d").glob("*.yaml")) + \
            list((root / "skills" / "design-sensei" / "config").glob("*.yaml"))
        self.assertTrue(files)
        for path in files:
            with self.subTest(path=path.name):
                self.assertEqual(yamlite.load(path), yaml.safe_load(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
