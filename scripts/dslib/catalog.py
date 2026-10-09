"""Load the catalog files and derive reuse/licence guidance from them."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from . import yamlite
from .paths import Layout

# Ordered from least to most restrictive; used to derive a pattern's status from its sources.
LICENSE_STATUS_ORDER = ["verified", "custom_terms", "pending_verification", "unknown", "not_found", "proprietary_terms"]
REDISTRIBUTION_ORDER = ["redistributable_with_notice", "license_specific", "pending_verification", "unresolved", "reference_only"]

REUSE_GUIDANCE = {
    "redistributable_with_notice": ("copy_with_attribution", "Permissive license: code may be copied or adapted if you keep the copyright and license notice."),
    "license_specific": ("license_review_required", "License has special terms: read the license text and the review notes before copying anything."),
    "pending_verification": ("verify_first", "Rights not verified yet: treat as reference-only until the license is checked."),
    "unresolved": ("reimplement_only", "No license granted: study the idea, do not copy code or assets; reimplement independently."),
    "reference_only": ("reference_only", "Link and describe only: do not copy or redistribute any of its content."),
}

SOURCE_TYPES_WITHOUT_CLONE = ("website", "article", "documentation_site")


class CatalogError(RuntimeError):
    pass


def load_yaml(path: Path) -> Any:
    try:
        return yamlite.load(path)
    except FileNotFoundError:
        raise CatalogError("missing file: %s" % path)
    except yamlite.YamlError as exc:
        raise CatalogError(str(exc))


def load_json(path: Path) -> Any:
    try:
        with open(str(path), "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise CatalogError("missing file: %s" % path)
    except ValueError as exc:
        raise CatalogError("invalid JSON in %s: %s" % (path, exc))


def load_sources(layout: Layout) -> List[Dict[str, Any]]:
    data = load_yaml(layout.sources_yaml)
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        raise CatalogError("%s must contain a 'sources' list" % layout.sources_yaml)
    return [s for s in data["sources"] if isinstance(s, dict)]


def load_patterns(layout: Layout) -> List[Dict[str, Any]]:
    data = load_yaml(layout.patterns_yaml)
    if not isinstance(data, dict) or not isinstance(data.get("patterns"), list):
        raise CatalogError("%s must contain a 'patterns' list" % layout.patterns_yaml)
    return [p for p in data["patterns"] if isinstance(p, dict)]


def load_licenses(layout: Layout) -> Dict[str, Any]:
    data = load_yaml(layout.licenses_yaml)
    if not isinstance(data, dict):
        raise CatalogError("%s must be a mapping" % layout.licenses_yaml)
    return data


def by_id(items: List[Mapping[str, Any]], key: str = "id") -> Dict[str, Mapping[str, Any]]:
    return {str(item.get(key)): item for item in items if item.get(key) is not None}


def split_source_path(value: str) -> Tuple[str, str]:
    """``'lenis:packages/core/src'`` -> ``('lenis', 'packages/core/src')``."""
    sid, _, rel = value.partition(":")
    return sid, rel


def unsafe_relative_path(rel: str) -> Optional[str]:
    """Return a reason when ``rel`` is not a safe path relative to a source root."""
    if rel == "" or rel.startswith("/") or re.match(r"^[A-Za-z]:", rel) or "\\" in rel or "\0" in rel:
        return "must be a relative POSIX path"
    parts = rel.split("/")
    if any(p == ".." for p in parts):
        return "must not contain '..'"
    return None


def derive_license_status(source_ids: List[str], sources: Mapping[str, Mapping[str, Any]]) -> str:
    """Most restrictive ``license_status`` among the given sources ('verified' when there are none)."""
    worst = 0
    for sid in source_ids:
        src = sources.get(sid)
        if src is None:
            continue
        status = str(src.get("license_status"))
        if status in LICENSE_STATUS_ORDER:
            worst = max(worst, LICENSE_STATUS_ORDER.index(status))
    return LICENSE_STATUS_ORDER[worst]


def derive_redistribution(source_ids: List[str], sources: Mapping[str, Mapping[str, Any]]) -> str:
    worst = 0
    for sid in source_ids:
        src = sources.get(sid)
        if src is None:
            continue
        status = str(src.get("redistribution_status"))
        if status in REDISTRIBUTION_ORDER:
            worst = max(worst, REDISTRIBUTION_ORDER.index(status))
    return REDISTRIBUTION_ORDER[worst]


def reuse_for(redistribution_status: str) -> Tuple[str, str]:
    return REUSE_GUIDANCE.get(redistribution_status, REUSE_GUIDANCE["pending_verification"])


def update_source_fields(sources_yaml: Path, source_id: str, fields: Mapping[str, Optional[str]]) -> None:
    """Rewrite scalar fields of one source *in place*, preserving comments and layout.

    Only single-line scalar fields that already exist in the source's block are
    supported (``pinned_commit``, ``last_checked`` ...). Values are written quoted
    where needed; ``None`` writes ``null``.
    """
    text = sources_yaml.read_text(encoding="utf-8")
    lines = text.split("\n")
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^\s*-\s+id:\s*%s\s*(#.*)?$" % re.escape(source_id), line):
            start = i
            break
    if start is None:
        raise CatalogError("source %r not found in %s" % (source_id, sources_yaml))
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^\s*-\s+id:\s*", lines[j]):
            end = j
            break
    for key, value in fields.items():
        rendered = "null" if value is None else (value if re.match(r"^[0-9a-f]{40}$", value) else yamlite.quote(value))
        pattern = re.compile(r"^(\s+%s:\s*)(\S.*?)?(\s+#.*)?$" % re.escape(key))
        for k in range(start + 1, end):
            m = pattern.match(lines[k])
            if m:
                lines[k] = "%s%s%s" % (m.group(1), rendered, m.group(3) or "")
                break
        else:
            raise CatalogError("field %r not found in the block of source %r" % (key, source_id))
    sources_yaml.write_text("\n".join(lines), encoding="utf-8")
