"""A small JSON Schema (draft-07 subset) validator using only the standard library.

It implements the keywords the Design Sensei schemas use and refuses to run a
schema that uses a validation keyword it does not implement, so a constraint is
never silently skipped. The same ``*.schema.json`` files remain valid for any
full JSON Schema implementation (editors, CI, third-party tools).
"""

from __future__ import annotations

import datetime
import re
from typing import Any, Dict, List, Optional

# Keywords that only annotate and never constrain.
_ANNOTATIONS = {
    "$schema", "$id", "$comment", "title", "description", "default", "examples",
    "definitions", "$defs", "deprecated", "readOnly", "writeOnly",
}
_VALIDATION = {
    "$ref", "type", "enum", "const", "pattern", "minLength", "maxLength", "format",
    "minimum", "maximum", "minItems", "maxItems", "uniqueItems", "items",
    "required", "properties", "additionalProperties", "patternProperties",
    "allOf", "anyOf", "oneOf",
}

_TYPE_CHECKS = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
    "null": lambda v: v is None,
}

_URI_RE = re.compile(r"^https?://[^\s/$.?#][^\s]*$")


class SchemaError(ValueError):
    """The schema itself is unsupported or malformed."""


def _resolve_ref(ref: str, root: Dict[str, Any]) -> Any:
    if not ref.startswith("#"):
        raise SchemaError("only local $ref values are supported: %s" % ref)
    node = root  # type: Any
    for part in [p for p in ref[1:].split("/") if p != ""]:
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            raise SchemaError("unresolvable $ref %s" % ref)
        node = node[part]
    return node


def _type_name(value: Any) -> str:
    for name in ("null", "boolean", "integer", "number", "string", "array", "object"):
        if _TYPE_CHECKS[name](value):
            return name
    return type(value).__name__


def _check_format(fmt: str, value: str) -> Optional[str]:
    if fmt == "uri":
        return None if _URI_RE.match(value) else "is not a valid http(s) URL"
    if fmt == "date":
        try:
            datetime.datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return "is not a valid YYYY-MM-DD date"
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            return "is not a valid YYYY-MM-DD date"
    return None


def check_schema(schema: Any, path: str = "$") -> List[str]:
    """Walk a whole schema and report keywords this validator does not implement."""
    problems = []  # type: List[str]
    if schema is True or not isinstance(schema, dict):
        return problems
    for key, value in schema.items():
        if key not in _ANNOTATIONS and key not in _VALIDATION:
            problems.append("%s: unsupported keyword '%s'" % (path, key))
        if key in ("properties", "patternProperties", "definitions", "$defs") and isinstance(value, dict):
            for name, sub in value.items():
                problems.extend(check_schema(sub, "%s.%s.%s" % (path, key, name)))
        elif key in ("items", "additionalProperties") and isinstance(value, dict):
            problems.extend(check_schema(value, "%s.%s" % (path, key)))
        elif key in ("allOf", "anyOf", "oneOf") and isinstance(value, list):
            for idx, sub in enumerate(value):
                problems.extend(check_schema(sub, "%s.%s[%d]" % (path, key, idx)))
    return problems


def validate(instance: Any, schema: Dict[str, Any], root: Optional[Dict[str, Any]] = None, path: str = "$") -> List[str]:
    """Return a list of human-readable error strings (empty when valid)."""
    root = root if root is not None else schema
    if schema is True or schema == {}:
        return []
    if not isinstance(schema, dict):
        raise SchemaError("schema at %s must be an object" % path)
    unknown = [k for k in schema if k not in _ANNOTATIONS and k not in _VALIDATION]
    if unknown:
        raise SchemaError("unsupported schema keyword(s) at %s: %s" % (path, ", ".join(sorted(unknown))))

    if "$ref" in schema:
        return validate(instance, _resolve_ref(schema["$ref"], root), root, path)

    errors = []  # type: List[str]

    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_TYPE_CHECKS[t](instance) for t in types):
            return ["%s: expected %s, got %s" % (path, " or ".join(types), _type_name(instance))]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append("%s: %r is not one of %s" % (path, instance, ", ".join(repr(e) for e in schema["enum"])))
    if "const" in schema and instance != schema["const"]:
        errors.append("%s: must equal %r" % (path, schema["const"]))

    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append("%s: %r does not match pattern %s" % (path, instance, schema["pattern"]))
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append("%s: must be at least %d characters" % (path, schema["minLength"]))
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append("%s: must be at most %d characters" % (path, schema["maxLength"]))
        if "format" in schema:
            problem = _check_format(schema["format"], instance)
            if problem:
                errors.append("%s: %r %s" % (path, instance, problem))

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append("%s: must be >= %s" % (path, schema["minimum"]))
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append("%s: must be <= %s" % (path, schema["maximum"]))

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append("%s: needs at least %d item(s)" % (path, schema["minItems"]))
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append("%s: allows at most %d item(s)" % (path, schema["maxItems"]))
        if schema.get("uniqueItems"):
            seen = []  # type: List[Any]
            for item in instance:
                if item in seen:
                    errors.append("%s: duplicate item %r" % (path, item))
                seen.append(item)
        if "items" in schema:
            for idx, item in enumerate(instance):
                errors.extend(validate(item, schema["items"], root, "%s[%d]" % (path, idx)))

    if isinstance(instance, dict):
        for name in schema.get("required", []):
            if name not in instance:
                errors.append("%s: missing required field '%s'" % (path, name))
        props = schema.get("properties", {})
        patterns = schema.get("patternProperties", {})
        for key, value in instance.items():
            child = "%s.%s" % (path, key)
            matched = False
            if key in props:
                matched = True
                errors.extend(validate(value, props[key], root, child))
            for pattern, sub in patterns.items():
                if re.search(pattern, key):
                    matched = True
                    errors.extend(validate(value, sub, root, child))
            if not matched:
                extra = schema.get("additionalProperties", True)
                if extra is False:
                    errors.append("%s: unknown field '%s'" % (path, key))
                elif isinstance(extra, dict):
                    errors.extend(validate(value, extra, root, child))

    if "allOf" in schema:
        for sub in schema["allOf"]:
            errors.extend(validate(instance, sub, root, path))
    if "anyOf" in schema:
        if not any(not validate(instance, sub, root, path) for sub in schema["anyOf"]):
            errors.append("%s: does not match any allowed shape" % path)
    if "oneOf" in schema:
        matches = sum(1 for sub in schema["oneOf"] if not validate(instance, sub, root, path))
        if matches != 1:
            errors.append("%s: must match exactly one allowed shape (matched %d)" % (path, matches))
    return errors
