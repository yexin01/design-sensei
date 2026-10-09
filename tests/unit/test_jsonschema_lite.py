import unittest

from tests import helpers  # noqa: F401
from dslib.jsonschema_lite import SchemaError, check_schema, validate


class SchemaTests(unittest.TestCase):
    def test_types_and_required(self):
        schema = {"type": "object", "required": ["a"], "properties": {"a": {"type": "integer"}, "b": {"type": ["string", "null"]}}}
        self.assertEqual(validate({"a": 1, "b": None}, schema), [])
        self.assertTrue(any("missing required field 'a'" in e for e in validate({}, schema)))
        self.assertTrue(any("expected integer" in e for e in validate({"a": "x"}, schema)))
        self.assertTrue(any("expected integer" in e for e in validate({"a": True}, schema)))  # bool is not an integer

    def test_additional_properties(self):
        schema = {"type": "object", "additionalProperties": False, "properties": {"a": {}}}
        self.assertEqual(validate({"a": 1}, schema), [])
        self.assertTrue(any("unknown field 'z'" in e for e in validate({"a": 1, "z": 2}, schema)))

    def test_enum_const_pattern_length(self):
        self.assertEqual(validate("x", {"enum": ["x", "y"]}), [])
        self.assertTrue(validate("z", {"enum": ["x", "y"]}))
        self.assertTrue(validate(2, {"const": 1}))
        self.assertTrue(validate("abc", {"type": "string", "pattern": "^[0-9]+$"}))
        self.assertTrue(validate("a", {"type": "string", "minLength": 2}))
        self.assertTrue(validate("abc", {"type": "string", "maxLength": 2}))

    def test_formats(self):
        self.assertEqual(validate("https://example.com/x", {"format": "uri"}), [])
        self.assertTrue(validate("not a url", {"format": "uri"}))
        self.assertTrue(validate("ftp://example.com", {"format": "uri"}))
        self.assertEqual(validate("2026-10-09", {"format": "date"}), [])
        self.assertTrue(validate("2026-13-09", {"format": "date"}))
        self.assertTrue(validate("2026-1-9", {"format": "date"}))

    def test_arrays(self):
        schema = {"type": "array", "minItems": 1, "uniqueItems": True, "items": {"type": "string"}}
        self.assertEqual(validate(["a", "b"], schema), [])
        self.assertTrue(validate([], schema))
        self.assertTrue(validate(["a", "a"], schema))
        self.assertTrue(validate([1], schema))

    def test_numbers(self):
        schema = {"type": "integer", "minimum": 1, "maximum": 10}
        self.assertEqual(validate(5, schema), [])
        self.assertTrue(validate(0, schema))
        self.assertTrue(validate(11, schema))

    def test_ref_and_one_of(self):
        schema = {"definitions": {"n": {"type": "integer"}}, "oneOf": [{"$ref": "#/definitions/n"}, {"enum": ["none"]}]}
        self.assertEqual(validate(3, schema), [])
        self.assertEqual(validate("none", schema), [])
        self.assertTrue(validate("other", schema))

    def test_check_schema_flags_unsupported_keywords_deeply(self):
        bad = {"type": "object", "properties": {"a": {"type": "array", "items": {"if": {}}}}}
        self.assertTrue(any("unsupported keyword 'if'" in p for p in check_schema(bad)))
        self.assertEqual(check_schema({"type": "object", "properties": {"type": {"type": "string"}}}), [])

    def test_error_paths(self):
        schema = {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {"n": {"type": "integer"}}}}}}
        errors = validate({"items": [{"n": 1}, {"n": "x"}]}, schema)
        self.assertEqual(len(errors), 1)
        self.assertIn("$.items[1].n", errors[0])

    def test_unsupported_keyword_is_an_error_not_silently_skipped(self):
        with self.assertRaises(SchemaError):
            validate(1, {"if": {}, "then": {}})
        with self.assertRaises(SchemaError):
            validate(1, {"$ref": "http://example.com/schema.json"})

    def test_repository_schemas_use_only_supported_keywords(self):
        import json
        for path in (helpers.ROOT / "catalog" / "schemas").glob("*.json"):
            with self.subTest(schema=path.name):
                schema = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(check_schema(schema), [])


if __name__ == "__main__":
    unittest.main()
