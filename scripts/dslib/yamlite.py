"""A strict, dependency-free parser for the YAML subset used by Design Sensei.

Why this exists: the Python standard library has no YAML parser and the tooling
must run on a stock Python 3 without ``pip install``. Catalog files are written
in a deliberately small, unambiguous dialect, and this module parses exactly that
dialect and *rejects everything else loudly* instead of guessing.

Supported:
  * block mappings and block sequences (nested, including ``- key: value`` items)
  * plain, single-quoted and double-quoted scalars
  * ``|`` and ``>`` block scalars with ``-``/``+`` chomping indicators
  * single-line flow sequences ``[a, b]`` and flow mappings ``{a: 1}``
  * ``#`` comments, one optional leading ``---``

Rejected with a ``YamlError`` (never silently mis-parsed):
  * tabs in indentation, duplicate keys, anchors/aliases/tags, multiple documents,
    multi-line flow collections or quoted scalars, complex keys
  * plain scalars whose type differs between YAML 1.1 and 1.2 parsers (for example
    ``yes``/``no``/``on``/``off``, ``0123``, ``1e3``, ``2026-10-09``, ``1:30``).
    Quote them. Everything this parser accepts therefore loads identically with
    PyYAML, which the test-suite cross-checks when PyYAML is installed.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple


class YamlError(ValueError):
    """Raised for malformed or unsupported YAML, with a source location."""

    def __init__(self, message: str, line: Optional[int] = None, source: Optional[str] = None):
        self.message = message
        self.line = line
        self.source = source
        where = ""
        if source and line:
            where = "%s:%d: " % (source, line)
        elif source:
            where = "%s: " % source
        elif line:
            where = "line %d: " % line
        super().__init__(where + message)


# Canonical forms this parser converts to numbers.
_INT_RE = re.compile(r"^[-+]?(0|[1-9][0-9]*)$")
_FLOAT_RE = re.compile(r"^[-+]?[0-9]+\.[0-9]+$")
# Forms PyYAML (YAML 1.1) would turn into numbers that are not canonical above.
_YAML11_INT_RE = re.compile(
    r"^(?:[-+]?0b[0-1_]+|[-+]?0[0-7_]+|[-+]?(?:0|[1-9][0-9_]*)|[-+]?0x[0-9a-fA-F_]+|[-+]?[1-9][0-9_]*(?::[0-5]?[0-9])+)$"
)
_YAML11_FLOAT_RE = re.compile(
    r"^(?:[-+]?(?:[0-9][0-9_]*)\.[0-9_]*(?:[eE][-+][0-9]+)?|\.[0-9][0-9_]*(?:[eE][-+][0-9]+)?"
    r"|[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\.[0-9_]*|[-+]?\.(?:inf|Inf|INF)|\.(?:nan|NaN|NAN))$"
)
_EXPONENT_ONLY_RE = re.compile(r"^[-+]?[0-9]+[eE][-+]?[0-9]+$")
_DATEISH_RE = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}([Tt ].*)?$")
_YAML11_BOOLS = {"yes", "no", "on", "off"}
_BLOCK_HEADER_RE = re.compile(r"^([|>])([+-]?)$")
_COLON_RE = re.compile(r":(\s|$)")
_RESERVED_START = "&*!%@`"


class _Line(object):
    __slots__ = ("no", "indent", "raw", "text")

    def __init__(self, no: int, raw: str):
        self.no = no
        self.raw = raw
        stripped = raw.lstrip(" ")
        self.indent = len(raw) - len(stripped)
        self.text = _strip_comment(stripped).rstrip()


def _strip_comment(s: str) -> str:
    """Remove a trailing ``# comment`` that is not inside a quoted scalar."""
    quote = None  # type: Optional[str]
    prev_sig = ""  # previous non-space character
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if quote is None:
            if c in "\"'" and (prev_sig == "" or prev_sig in ":,[{-"):
                quote = c
            elif c == "#" and (i == 0 or s[i - 1] in " \t"):
                return s[:i]
            if c not in " \t":
                prev_sig = c
        else:
            if quote == '"' and c == "\\":
                i += 2
                continue
            if c == quote:
                if quote == "'" and i + 1 < n and s[i + 1] == "'":
                    i += 2
                    continue
                quote = None
                prev_sig = c
        i += 1
    return s


def _is_dash(text: str) -> bool:
    return text == "-" or text.startswith("- ")


def _resolve_plain(s: str, line: int) -> Any:
    if s in ("", "~", "null", "Null", "NULL"):
        return None
    if s in ("true", "True", "TRUE"):
        return True
    if s in ("false", "False", "FALSE"):
        return False
    if s.lower() in _YAML11_BOOLS:
        raise YamlError("ambiguous plain scalar %r (a boolean in YAML 1.1); quote it" % s, line)
    if _INT_RE.match(s):
        return int(s)
    if _FLOAT_RE.match(s):
        return float(s)
    if (
        _YAML11_INT_RE.match(s)
        or _YAML11_FLOAT_RE.match(s)
        or _EXPONENT_ONLY_RE.match(s)
        or _DATEISH_RE.match(s)
    ):
        raise YamlError("ambiguous plain scalar %r (number/date forms differ across YAML parsers); quote it" % s, line)
    return s


def _check_plain(s: str, line: int) -> None:
    if s and s[0] in _RESERVED_START:
        raise YamlError("unsupported or reserved YAML syntax at start of scalar %r (anchors, aliases, tags); quote it" % s, line)
    if s and s[0] in "?:-" and (len(s) == 1 or s[1] == " "):
        raise YamlError("ambiguous indicator at start of scalar %r; quote it" % s, line)
    if s and s[0] in "|>":
        raise YamlError("block scalar header not allowed here: %r" % s, line)
    if _COLON_RE.search(s):
        raise YamlError("plain scalar %r contains ': '; quote the value" % s, line)


_DQ_ESCAPES = {
    "0": "\0", "a": "\a", "b": "\b", "t": "\t", "n": "\n", "v": "\v", "f": "\f", "r": "\r",
    "e": "\x1b", " ": " ", '"': '"', "/": "/", "\\": "\\", "N": "\x85", "_": "\xa0",
    "L": "\u2028", "P": "\u2029",
}


def _parse_quoted(s: str, start: int, line: int) -> Tuple[str, int]:
    """Parse a quoted scalar beginning at ``s[start]``; return (value, index after closing quote)."""
    quote = s[start]
    i = start + 1
    out = []  # type: List[str]
    n = len(s)
    while i < n:
        c = s[i]
        if quote == "'":
            if c == "'":
                if i + 1 < n and s[i + 1] == "'":
                    out.append("'")
                    i += 2
                    continue
                return "".join(out), i + 1
            out.append(c)
            i += 1
        else:
            if c == '"':
                return "".join(out), i + 1
            if c == "\\":
                if i + 1 >= n:
                    break
                e = s[i + 1]
                if e in _DQ_ESCAPES:
                    out.append(_DQ_ESCAPES[e])
                    i += 2
                elif e in "xuU":
                    width = {"x": 2, "u": 4, "U": 8}[e]
                    hexpart = s[i + 2 : i + 2 + width]
                    if len(hexpart) != width or not re.match(r"^[0-9a-fA-F]+$", hexpart):
                        raise YamlError("bad \\%s escape in double-quoted scalar" % e, line)
                    out.append(chr(int(hexpart, 16)))
                    i += 2 + width
                else:
                    raise YamlError("unsupported escape \\%s in double-quoted scalar" % e, line)
            else:
                out.append(c)
                i += 1
    raise YamlError("unterminated quoted scalar (multi-line quoted scalars are not supported)", line)


class _Flow(object):
    """Parser for single-line flow collections."""

    def __init__(self, text: str, line: int):
        self.s = text
        self.i = 0
        self.line = line

    def _ws(self) -> None:
        while self.i < len(self.s) and self.s[self.i] in " \t":
            self.i += 1

    def parse(self) -> Any:
        value = self._value(in_map_key=False, closers="")
        self._ws()
        if self.i != len(self.s):
            raise YamlError("unexpected trailing text in flow collection: %r" % self.s[self.i :], self.line)
        return value

    def _value(self, in_map_key: bool, closers: str) -> Any:
        self._ws()
        if self.i >= len(self.s):
            raise YamlError("unexpected end of flow collection", self.line)
        c = self.s[self.i]
        if c == "[":
            return self._seq()
        if c == "{":
            return self._map()
        if c in "\"'":
            value, self.i = _parse_quoted(self.s, self.i, self.line)
            return value
        return self._plain(in_map_key, closers)

    def _plain(self, in_map_key: bool, closers: str) -> Any:
        start = self.i
        while self.i < len(self.s):
            c = self.s[self.i]
            if c == "," or c in closers:
                break
            if in_map_key and c == ":" and (self.i + 1 >= len(self.s) or self.s[self.i + 1] in " ,}"):
                break
            self.i += 1
        token = self.s[start : self.i].strip()
        if token == "" and not in_map_key:
            raise YamlError("empty item in flow collection", self.line)
        _check_plain(token, self.line)
        if in_map_key:
            return token
        return _resolve_plain(token, self.line)

    def _seq(self) -> List[Any]:
        self.i += 1  # [
        items = []  # type: List[Any]
        self._ws()
        if self.i < len(self.s) and self.s[self.i] == "]":
            self.i += 1
            return items
        while True:
            items.append(self._value(False, "]"))
            self._ws()
            if self.i >= len(self.s):
                raise YamlError("unterminated flow sequence (multi-line flow collections are not supported)", self.line)
            c = self.s[self.i]
            self.i += 1
            if c == ",":
                continue
            if c == "]":
                return items
            raise YamlError("expected ',' or ']' in flow sequence", self.line)

    def _map(self) -> Dict[str, Any]:
        self.i += 1  # {
        out = {}  # type: Dict[str, Any]
        self._ws()
        if self.i < len(self.s) and self.s[self.i] == "}":
            self.i += 1
            return out
        while True:
            key = self._value(True, "}")
            if not isinstance(key, str):
                raise YamlError("flow mapping keys must be strings", self.line)
            self._ws()
            if self.i >= len(self.s) or self.s[self.i] != ":":
                raise YamlError("expected ':' after flow mapping key %r" % key, self.line)
            self.i += 1
            if key in out:
                raise YamlError("duplicate key %r" % key, self.line)
            self._ws()
            if self.i < len(self.s) and self.s[self.i] in ",}":
                out[key] = None
            else:
                out[key] = self._value(False, "}")
            self._ws()
            if self.i >= len(self.s):
                raise YamlError("unterminated flow mapping (multi-line flow collections are not supported)", self.line)
            c = self.s[self.i]
            self.i += 1
            if c == ",":
                continue
            if c == "}":
                return out
            raise YamlError("expected ',' or '}' in flow mapping", self.line)


class _Parser(object):
    def __init__(self, text: str):
        self.lines = []  # type: List[_Line]
        raw_lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        for no, raw in enumerate(raw_lines, start=1):
            if no == 1 and raw.startswith("\ufeff"):
                raw = raw[1:]
            lead = raw[: len(raw) - len(raw.lstrip(" \t"))]
            if "\t" in lead and raw.strip() != "":
                raise YamlError("tab character in indentation", no)
            self.lines.append(_Line(no, raw))
        self.pos = 0

    def _peek(self) -> Optional[_Line]:
        while self.pos < len(self.lines) and self.lines[self.pos].text == "":
            self.pos += 1
        if self.pos >= len(self.lines):
            return None
        return self.lines[self.pos]

    # -- entry ------------------------------------------------------------
    def parse_document(self) -> Any:
        first = self._peek()
        if first is not None and first.text == "---" and first.indent == 0:
            self.pos += 1
        ln = self._peek()
        if ln is None:
            return None
        value = self._parse_block()
        extra = self._peek()
        if extra is not None:
            if extra.text in ("---", "..."):
                raise YamlError("multiple YAML documents are not supported", extra.no)
            raise YamlError("unexpected content (check indentation): %r" % extra.text, extra.no)
        return value

    # -- blocks -----------------------------------------------------------
    def _parse_block(self) -> Any:
        ln = self._peek()
        assert ln is not None
        if _is_dash(ln.text):
            return self._parse_seq(ln.indent)
        if self._looks_like_mapping(ln.text):
            return self._parse_map(ln.indent)
        self.pos += 1
        return self._parse_inline(ln.text, ln, ln.indent - 1)

    @staticmethod
    def _looks_like_mapping(text: str) -> bool:
        if text[0] in "\"'":
            try:
                _, end = _parse_quoted(text, 0, 0)
            except YamlError:
                return False
            rest = text[end:].lstrip(" ")
            return rest.startswith(":") and (len(rest) == 1 or rest[1] == " ")
        return _COLON_RE.search(text) is not None

    def _parse_seq(self, indent: int) -> List[Any]:
        items = []  # type: List[Any]
        while True:
            ln = self._peek()
            if ln is None or ln.indent < indent:
                break
            if ln.indent > indent:
                raise YamlError("unexpected indentation inside sequence", ln.no)
            if not _is_dash(ln.text):
                break
            rest = ln.text[1:]
            content = rest.lstrip(" ")
            if content == "":
                self.pos += 1
                nxt = self._peek()
                if nxt is not None and nxt.indent > indent:
                    items.append(self._parse_block())
                else:
                    items.append(None)
                continue
            col = ln.indent + 1 + (len(rest) - len(content))
            if _is_dash(content):
                ln.indent, ln.text = col, content
                items.append(self._parse_seq(col))
            elif self._looks_like_mapping(content):
                ln.indent, ln.text = col, content
                items.append(self._parse_map(col))
            else:
                self.pos += 1
                items.append(self._parse_inline(content, ln, indent))
        return items

    @staticmethod
    def _split_key(ln: _Line) -> Tuple[str, str]:
        t = ln.text
        if t[0] in "\"'":
            key, end = _parse_quoted(t, 0, ln.no)
            rest = t[end:].lstrip(" ")
            if not rest.startswith(":"):
                raise YamlError("expected ':' after quoted key", ln.no)
            return key, rest[1:]
        m = _COLON_RE.search(t)
        if m is None:
            raise YamlError("expected 'key: value' but found %r" % t, ln.no)
        key = t[: m.start()].rstrip()
        if key == "":
            raise YamlError("empty mapping key", ln.no)
        if key[0] in _RESERVED_START or key[0] == "?":
            raise YamlError("unsupported key syntax %r (anchors, tags and complex keys are not supported)" % key, ln.no)
        if not isinstance(_resolve_plain(key, ln.no), str):
            raise YamlError("mapping key %r would not be a string; quote it" % key, ln.no)
        return key, t[m.start() + 1 :]

    def _parse_map(self, indent: int) -> Dict[str, Any]:
        result = {}  # type: Dict[str, Any]
        while True:
            ln = self._peek()
            if ln is None or ln.indent < indent:
                break
            if ln.indent > indent:
                raise YamlError("unexpected indentation inside mapping", ln.no)
            if _is_dash(ln.text):
                raise YamlError("sequence item where a mapping key was expected", ln.no)
            key, rest = self._split_key(ln)
            if key in result:
                raise YamlError("duplicate key %r" % key, ln.no)
            self.pos += 1
            rest = rest.strip()
            if rest == "":
                nxt = self._peek()
                if nxt is not None and (nxt.indent > indent or (nxt.indent == indent and _is_dash(nxt.text))):
                    result[key] = self._parse_block()
                else:
                    result[key] = None
            else:
                result[key] = self._parse_inline(rest, ln, indent)
        return result

    # -- inline values ----------------------------------------------------
    def _parse_inline(self, text: str, ln: _Line, parent_indent: int) -> Any:
        text = text.strip()
        m = _BLOCK_HEADER_RE.match(text)
        if m:
            return self._read_block_scalar(m.group(1), m.group(2), parent_indent)
        if text[0] in "|>":
            raise YamlError("unsupported block scalar header %r (indentation indicators are not supported)" % text, ln.no)
        if text[0] in "[{":
            return _Flow(text, ln.no).parse()
        if text[0] in "\"'":
            value, end = _parse_quoted(text, 0, ln.no)
            if text[end:].strip() != "":
                raise YamlError("unexpected text after quoted scalar: %r" % text[end:].strip(), ln.no)
            return value
        _check_plain(text, ln.no)
        return _resolve_plain(text, ln.no)

    def _read_block_scalar(self, style: str, chomp: str, parent_indent: int) -> str:
        body = []  # type: List[str]
        i = self.pos
        while i < len(self.lines):
            raw = self.lines[i].raw
            if raw.strip() == "":
                body.append("")
                i += 1
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            if indent <= parent_indent:
                break
            body.append(raw)
            i += 1
        # Trailing blank lines belong to chomping, not to the content.
        trailing = 0
        while body and body[-1] == "":
            body.pop()
            trailing += 1
        self.pos = i
        if not body:
            return "\n" * trailing if chomp == "+" else ""
        first = next(b for b in body if b != "")
        block_indent = len(first) - len(first.lstrip(" "))
        lines = [b[block_indent:] if b != "" else "" for b in body]
        text = "\n".join(lines) if style == "|" else self._fold(lines)
        if chomp == "-":
            return text
        if chomp == "+":
            return text + "\n" + "\n" * trailing
        return text + "\n"

    @staticmethod
    def _fold(lines: List[str]) -> str:
        out = lines[0]
        for idx in range(1, len(lines)):
            line, prev = lines[idx], lines[idx - 1]
            if line == "":
                out += "\n"
            elif prev == "":
                out += line
            elif line.startswith(" ") or prev.startswith(" "):
                out += "\n" + line
            else:
                out += " " + line
        return out


def loads(text: str, source: Optional[str] = None) -> Any:
    """Parse YAML text in the supported subset and return Python objects."""
    try:
        return _Parser(text).parse_document()
    except YamlError as exc:
        if source is not None and exc.source is None:
            raise YamlError(exc.message, exc.line, source) from None
        raise


def load(path: Any) -> Any:
    """Parse a YAML file (UTF-8)."""
    with open(str(path), "r", encoding="utf-8") as handle:
        text = handle.read()
    return loads(text, source=str(path))


def quote(value: str) -> str:
    """Return ``value`` as a YAML double-quoted scalar (JSON string syntax is valid YAML)."""
    return json.dumps(value, ensure_ascii=False)


_SAFE_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
_PLAIN_OK_RE = re.compile(r"^[A-Za-z0-9_./+()=,;<>$^~\\-][^#\n]*$")


def _plain_ok(s: str) -> bool:
    if s == "" or s != s.strip() or "\n" in s or " #" in s or _COLON_RE.search(s):
        return False
    if not _PLAIN_OK_RE.match(s) or s[0] in "-?:" and (len(s) == 1 or s[1] == " "):
        return False
    try:
        _check_plain(s, 0)
        return _resolve_plain(s, 0) == s
    except YamlError:
        return False


def _scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return value if _plain_ok(value) else quote(value)
    raise TypeError("cannot serialize %s to YAML" % type(value).__name__)


def _emit(value: Any, indent: int, out: List[str]) -> None:
    pad = " " * indent
    if isinstance(value, dict):
        for key, item in value.items():
            k = key if _SAFE_KEY_RE.match(key) and isinstance(_resolve_key(key), str) else quote(key)
            _emit_entry(pad + k + ":", item, indent, out)
    elif isinstance(value, list):
        for item in value:
            _emit_entry(pad + "-", item, indent, out, in_list=True)
    else:
        out.append(pad + _scalar(value))


def _resolve_key(key: str) -> Any:
    try:
        return _resolve_plain(key, 0)
    except YamlError:
        return None


def _emit_entry(head: str, item: Any, indent: int, out: List[str], in_list: bool = False) -> None:
    if isinstance(item, dict) and item:
        if in_list:
            sub = []  # type: List[str]
            _emit(item, indent + 2, sub)
            out.append(head + " " + sub[0].lstrip(" "))
            out.extend(sub[1:])
        else:
            out.append(head)
            _emit(item, indent + 2, out)
    elif isinstance(item, list) and item:
        if in_list:
            sub = []
            _emit(item, indent + 2, sub)
            out.append(head + " " + sub[0].lstrip(" "))
            out.extend(sub[1:])
        else:
            out.append(head)
            _emit(item, indent + 2, out)
    elif isinstance(item, dict):
        out.append(head + " {}")
    elif isinstance(item, list):
        out.append(head + " []")
    elif isinstance(item, str) and "\n" in item and item.strip() != "" and not item.startswith((" ", "\n")):
        chomp = "" if item.endswith("\n") and not item.endswith("\n\n") else ("-" if not item.endswith("\n") else "+")
        out.append(head + " |" + chomp)
        body = item[:-1] if item.endswith("\n") and chomp != "-" else item
        pad = " " * (indent + 2)
        for line in body.split("\n"):
            out.append((pad + line) if line else "")
    else:
        out.append(head + " " + _scalar(item))


def dumps(value: Any) -> str:
    """Serialize dict/list/scalar data into the same YAML subset ``loads`` accepts."""
    out = []  # type: List[str]
    _emit(value, 0, out)
    return "\n".join(out) + "\n"
