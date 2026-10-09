"""Knowledge notes: Markdown files with YAML front matter under ``knowledge/``."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from . import yamlite
from .paths import Layout

# Notes that are generated or purely navigational carry no front matter.
SKIP_NAMES = {"README.md"}
SKIP_DIRS = {"pattern-index"}

_CITATION_RE = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)*):([^`\s]+)`")
_LINE_SUFFIX_RE = re.compile(r"(#L\d+(-L?\d+)?|:\d+(-\d+)?)$")


class Doc(object):
    def __init__(self, path: Path, rel: str, meta: Optional[Dict[str, Any]], body: str, error: Optional[str]):
        self.path = path
        self.rel = rel
        self.meta = meta
        self.body = body
        self.error = error


def parse_frontmatter(text: str) -> Tuple[Optional[Dict[str, Any]], str, Optional[str]]:
    """Split ``---`` front matter from the body. Returns (meta, body, error)."""
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None, text, "missing YAML front matter (file must start with '---')"
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            end = i
            break
    if end is None:
        return None, text, "front matter is not closed with '---'"
    block = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1 :])
    try:
        meta = yamlite.loads(block)
    except yamlite.YamlError as exc:
        return None, body, "invalid front matter: %s" % exc
    if not isinstance(meta, dict):
        return None, body, "front matter must be a mapping"
    return meta, body, None


def iter_docs(layout: Layout) -> List[Doc]:
    docs = []  # type: List[Doc]
    root = layout.knowledge_dir
    if not root.is_dir():
        return docs
    for path in sorted(root.rglob("*.md")):
        rel_parts = path.relative_to(root).parts
        if path.name in SKIP_NAMES or (rel_parts and rel_parts[0] in SKIP_DIRS):
            continue
        text = path.read_text(encoding="utf-8")
        meta, body, error = parse_frontmatter(text)
        docs.append(Doc(path, "knowledge/" + "/".join(rel_parts), meta, body, error))
    return docs


def extract_citations(text: str, known_ids: Iterable[str]) -> List[Tuple[str, str]]:
    """Find `source-id:path` citations for known source ids (line suffixes are stripped)."""
    known = set(known_ids)
    found = []  # type: List[Tuple[str, str]]
    for sid, rel in _CITATION_RE.findall(text):
        if sid in known:
            found.append((sid, _LINE_SUFFIX_RE.sub("", rel).rstrip(".,;)")))
    return found
