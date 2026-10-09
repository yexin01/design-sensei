"""Tiny text helpers: tokenizing for search and consistent hashing/formatting."""

from __future__ import annotations

import hashlib
import re
from typing import Iterable, List

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_KEEP_SHORT = {"ui", "ux", "3d", "2d", "gl", "ar", "vr", "js", "ts", "r3f", "css", "svg"}


def stem(token: str) -> str:
    """Very light singularization so 'shaders' matches 'shader' (deterministic, no deps)."""
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 4 and token.endswith("sses"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith(("ss", "us", "is")):
        return token[:-1]
    return token


def tokenize(text: str) -> List[str]:
    """Lower-case alphanumeric tokens with light stemming. Camel/kebab/snake case is split."""
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text or "")
    out = []
    for raw in _TOKEN_RE.findall(text.lower()):
        if len(raw) < 2 and raw not in _KEEP_SHORT:
            continue
        out.append(stem(raw))
    return out


def unique(items: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def sha256_file(path: "str") -> str:
    digest = hashlib.sha256()
    with open(str(path), "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def truncate(text: str, limit: int = 200) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"
