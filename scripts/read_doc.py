#!/usr/bin/env python3
"""Read only the part of a Design Sensei document you need (saves tokens).

Whole files are expensive: a style note is ~1.8k tokens, a skill reference ~3.4k, a
recipe ~2.6k. This command prints a card, a table of contents, chosen sections or a
line range instead. Files are never modified and no text is invented: every output
line is copied (or truncated with an ellipsis) from the source.

Targets (no path typing needed)
  glassmorphism | style-glassmorphism   a design-style note (slug or pattern id)
  <pattern-id>                          its knowledge_doc (add --recipe for its recipe)
  ref:typography                        skills/design-sensei/references/typography.md
  playbook:hero-sections                skills/design-sensei/patterns/hero-sections.md
  recipe:lenis-smooth-scroll-setup      knowledge/implementation-recipes/<slug>.md
  note:lenis                            any knowledge note by file name
  fancy:src/fancy/components/...        a file of a downloaded source (licence header)
  knowledge/animations/lenis.md         a path under the toolkit or the library
Ambiguous names list their candidates and exit 2; paths outside the toolkit and the
library (or containing '..') are refused with exit 2.

Modes (markdown documents; default is --card)
  --card               compact quick card (title, summary, key bullets, first code block)
  --toc                headings with approximate token counts
  --section "A,B"      sections whose heading starts with A or B (case-insensitive);
                       sub-headings are included
  --max-tokens N       whole document, cut at a section boundary after N tokens
  --full               the whole file
  --lines A:B          1-based inclusive line range (the way to read code files)
Source/code files default to their first 80 lines; every library file shows its licence
reuse class first so the licence gate is visible before any code is read.

Token counts are an estimate: characters / 4.

Examples
  design-sensei read glassmorphism
  design-sensei read ref:typography --toc
  design-sensei read recipe:lenis-smooth-scroll-setup --section "Goal,Steps"
  design-sensei read fancy:src/fancy/components/text/scramble-hover.tsx --lines 1:60

Exit codes: 0 success, 1 not found / failure, 2 usage error or refused target.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dslib import EXIT_FAILURE, EXIT_OK, EXIT_USAGE
from dslib import catalog, knowledge
from dslib.cli import add_global_options, eprint, fail, run_with_layout
from dslib.paths import Layout

CARD_BUDGET = 450  # estimated tokens the card tries to stay under
DEFAULT_CODE_LINES = 80
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_FENCE_RE = re.compile(r"^\s*(```|~~~)")
_BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")


class ReadError(Exception):
    def __init__(self, message: str, code: int = EXIT_FAILURE):
        Exception.__init__(self, message)
        self.message = message
        self.code = code


def est_tokens(text: str) -> int:
    """Token estimate: characters / 4 (rounded up). An estimate, not a tokenizer."""
    return (len(text) + 3) // 4


def clip(text: str, width: int) -> str:
    """Collapse whitespace and cut at a word boundary with an ellipsis."""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= width:
        return text
    cut = text[: width - 1]
    if " " in cut[width // 2:]:
        cut = cut[: cut.rindex(" ")]
    return cut.rstrip(" ,;:-") + "…"


# ---------------------------------------------------------------------------
# document model
# ---------------------------------------------------------------------------

class Section(object):
    def __init__(self, level: int, title: str, start: int):
        self.level = level
        self.title = title
        self.start = start  # index into body lines of the heading
        self.end = start  # exclusive; includes sub-sections

    def lines(self, body: Sequence[str]) -> List[str]:
        return list(body[self.start:self.end])

    def text(self, body: Sequence[str]) -> str:
        return "\n".join(self.lines(body))


class Document(object):
    def __init__(self, text: str):
        meta, body, _error = knowledge.parse_frontmatter(text)
        self.meta = meta or {}
        self.body = body.split("\n")
        self.sections = []  # type: List[Section]
        in_fence = False
        for i, line in enumerate(self.body):
            if _FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            m = None if in_fence else _HEADING_RE.match(line)
            if m:
                self.sections.append(Section(len(m.group(1)), m.group(2), i))
        for idx, sec in enumerate(self.sections):
            sec.end = len(self.body)
            for nxt in self.sections[idx + 1:]:
                if nxt.level <= sec.level:
                    sec.end = nxt.start
                    break

    @property
    def title(self) -> str:
        if self.meta.get("title"):
            return str(self.meta["title"])
        return self.sections[0].title if self.sections else ""

    @property
    def summary(self) -> str:
        return str(self.meta.get("summary") or "")

    @property
    def kind(self) -> str:
        return str(self.meta.get("kind") or "")

    def preamble(self) -> List[str]:
        """Lines before the first heading below the title (title heading excluded)."""
        first = self.sections[0].start if self.sections else 0
        return self.body[:first]

    def top_level(self) -> List[Section]:
        """Sections at the shallowest heading level below a single H1 title (or all of the shallowest)."""
        secs = self.sections
        if not secs:
            return []
        if secs[0].level == 1 and sum(1 for s in secs if s.level == 1) == 1:
            below = [s for s in secs if s.level > 1]
            if not below:
                return []
            lvl = min(s.level for s in below)
            return [s for s in below if s.level == lvl]
        lvl = min(s.level for s in secs)
        return [s for s in secs if s.level == lvl]

    def own_lines(self, sec: Section) -> List[str]:
        """Lines of a section before its first sub-section."""
        end = sec.end
        for other in self.sections:
            if other.start > sec.start and other.level > sec.level:
                end = other.start
                break
        return self.body[sec.start + 1:end]


def header_line(layout_label: str, doc: Document, full_tokens: int) -> str:
    bits = [layout_label]
    if doc.kind:
        bits.append(doc.kind)
    bits.append("~%d tokens full" % full_tokens)
    return "[%s]" % ", ".join(bits)


def title_block(doc: Document) -> List[str]:
    lines = []
    if doc.title:
        lines.append("# " + doc.title)
    if doc.summary:
        lines.append(doc.summary)
    return lines


# ---------------------------------------------------------------------------
# modes
# ---------------------------------------------------------------------------

def render_toc(doc: Document) -> str:
    lines = title_block(doc)
    lines.append("")
    lines.append("headings (approximate tokens, sub-sections included):")
    for sec in doc.sections:
        if sec.level == 1 and sec is doc.sections[0] and doc.title:
            continue
        indent = "  " * max(sec.level - 2, 0)
        lines.append("%s%s  (~%d tok)" % (indent, sec.title, est_tokens(sec.text(doc.body))))
    return "\n".join(lines)


def match_sections(doc: Document, wanted: Sequence[str]) -> Tuple[List[Section], List[str]]:
    """Sections whose heading starts with any wanted prefix (case-insensitive), without nested duplicates."""
    picked = []  # type: List[Section]
    missing = []  # type: List[str]
    for want in wanted:
        w = want.strip().lower()
        hits = [s for s in doc.sections if s.title.lower().startswith(w)]
        if not hits:
            missing.append(want)
        for s in hits:
            if s not in picked:
                picked.append(s)
    ordered = sorted(picked, key=lambda s: s.start)
    result = []  # type: List[Section]
    for s in ordered:  # drop a section already contained in a previously kept one
        if result and s.start < result[-1].end and s.level > result[-1].level:
            continue
        result.append(s)
    return result, missing


def render_sections(doc: Document, sections: Sequence[Section], max_tokens: Optional[int] = None) -> str:
    out = title_block(doc)
    return _append_sections(out, doc, sections, max_tokens)


def _append_sections(out: List[str], doc: Document, sections: Sequence[Section], max_tokens: Optional[int]) -> str:
    used = est_tokens("\n".join(out))
    for idx, sec in enumerate(sections):
        text = sec.text(doc.body).rstrip()
        cost = est_tokens(text)
        if max_tokens is not None and idx > 0 and used + cost > max_tokens:
            rest = sum(est_tokens(s.text(doc.body)) for s in sections[idx:])
            out.append("")
            out.append("[truncated: %d more tokens; use --section or --full]" % rest)
            return "\n".join(out)
        if max_tokens is not None and idx == 0 and used + cost > max_tokens:
            keep, dropped = _cut_lines(text.split("\n"), max(max_tokens - used, 20))
            out.append("")
            out.extend(keep)
            if dropped:
                rest = dropped + sum(est_tokens(s.text(doc.body)) for s in sections[1:])
                out.append("")
                out.append("[truncated: %d more tokens; use --section or --full]" % rest)
                return "\n".join(out)
            used += cost
            continue
        out.append("")
        out.extend(text.split("\n"))
        used += cost
    return "\n".join(out)


def _cut_lines(lines: Sequence[str], budget: int) -> Tuple[List[str], int]:
    """Keep leading lines that fit the budget; return them and the tokens dropped."""
    keep = []  # type: List[str]
    used = 0
    for i, line in enumerate(lines):
        cost = est_tokens(line + "\n")
        if used + cost > budget and keep:
            return keep, est_tokens("\n".join(lines[i:]))
        keep.append(line)
        used += cost
    return keep, 0


def render_max_tokens(doc: Document, max_tokens: int) -> str:
    """Whole document, cut at section boundaries (intro text, then top-level sections)."""
    out = title_block(doc)
    top = doc.top_level()
    if not top:
        keep, dropped = _cut_lines(doc.body, max_tokens)
        text = "\n".join(keep)
        if dropped:
            text += "\n\n[truncated: %d more tokens; use --section or --full]" % dropped
        return text
    skip_title = 1 if doc.sections and doc.sections[0].level == 1 and doc.sections[0].start == 0 else 0
    intro = "\n".join(doc.body[skip_title:top[0].start]).strip()
    if intro:
        out.append("")
        out.append(intro)
    return _append_sections(out, doc, top, max_tokens)


def _bullets(lines: Sequence[str]) -> List[str]:
    out = []
    for line in lines:
        m = _BULLET_RE.match(line)
        if m:
            out.append(m.group(1).strip())
    return out


def _first_sentences(lines: Sequence[str], n: int = 1) -> List[str]:
    text = " ".join(l.strip() for l in lines if l.strip() and not l.lstrip().startswith(("|", "```", "#", "<")))
    text = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p for p in parts if p][:n]


def _first_code_block(lines: Sequence[str]) -> Optional[Tuple[str, List[str]]]:
    in_fence, lang, block = False, "", []  # type: Tuple[bool, str, List[str]]
    for line in lines:
        m = _FENCE_RE.match(line)
        if m and not in_fence:
            in_fence, lang, block = True, line.strip().lstrip("`~").strip(), []
            continue
        if m and in_fence:
            return lang, block
        if in_fence:
            block.append(line)
    return (lang, block) if in_fence else None


CARD_SECTIONS = [
    ("Visual characteristics", "visual characteristics"),
    ("When it fits", "when it fits"),
    ("Typography", "typography"),
    ("Colour", "colo"),
    ("Interaction and motion", "interaction"),
    ("Accessibility cautions", "accessibility"),
]
# (bullets per section, bullet width, code lines, code width) - tried in order until the card fits.
CARD_LADDER = [(2, 170, 12, 100), (2, 130, 10, 100), (2, 100, 8, 90), (2, 80, 6, 80), (1, 110, 8, 90), (1, 90, 6, 80), (1, 70, 5, 70), (1, 60, 4, 60)]


def _style_card(doc: Document, label: str, full_tokens: int, bullets: int, width: int, code_lines: int, code_width: int) -> str:
    out = [header_line(label, doc, full_tokens)] + title_block(doc)
    used_titles = set()  # type: set
    for display, prefix in CARD_SECTIONS:
        sec = next((s for s in doc.sections if s.level >= 2 and s.title.lower().startswith(prefix)), None)
        if sec is None:
            continue
        used_titles.add(sec.title)
        items = _bullets(doc.own_lines(sec)) or _first_sentences(doc.own_lines(sec))
        take = min(bullets + 1, 3) if prefix == "when it fits" else bullets
        if not items:
            continue
        out.append("")
        out.append("%s:" % sec.title)
        for item in items[:take]:
            out.append("- " + clip(item, width + (40 if prefix == "when it fits" else 0)))
    build = next((s for s in doc.sections if s.level >= 2 and s.title.lower().startswith("how to build")), None)
    if build is not None:
        used_titles.add(build.title)
        block = _first_code_block(doc.body[build.start + 1:build.end])
        out.append("")
        out.append("%s:" % build.title)
        if block is not None:
            lang, code = block
            shown = [clip_code(l, code_width) for l in code[:code_lines]]
            out.append("```" + lang)
            out.extend(shown)
            if len(code) > code_lines:
                out.append("… (%d more lines)" % (len(code) - code_lines))
            out.append("```")
        else:
            for item in (_bullets(doc.own_lines(build)) or _first_sentences(doc.own_lines(build)))[:1]:
                out.append("- " + clip(item, width))
    others = [s.title for s in doc.sections if s.level == 2 and s.title not in used_titles]
    out.append("")
    out.append("more: --section \"<heading>\" | --toc | --full" + ("  (not on card: %s)" % ", ".join(others) if others else ""))
    return "\n".join(out)


def clip_code(line: str, width: int) -> str:
    line = line.rstrip()
    return line if len(line) <= width else line[: width - 1] + "…"


def _generic_card(doc: Document, label: str, full_tokens: int, width: int, max_heads: int) -> str:
    out = [header_line(label, doc, full_tokens)] + title_block(doc)
    if not doc.summary:
        first = _first_sentences([l for l in doc.preamble() if not _HEADING_RE.match(l)] or [])
        if first:
            out.append(clip(first[0], 220))
    out.append("")
    heads = [s for s in doc.sections if not (s.level == 1 and s is doc.sections[0])]
    for sec in heads[:max_heads]:
        own = doc.own_lines(sec)
        item = (_bullets(own) or _first_sentences(own) or [""])[0]
        indent = "  " * max(sec.level - 2, 0)
        line = "%s%s (~%d tok)" % (indent, sec.title, est_tokens(sec.text(doc.body)))
        if item:
            line += ": " + clip(item, width)
        out.append(line)
    if len(heads) > max_heads:
        out.append("… %d more headings (use --toc)" % (len(heads) - max_heads))
    out.append("")
    out.append("more: --section \"<heading>\" | --toc | --full")
    return "\n".join(out)


def render_card(doc: Document, label: str, full_tokens: int, is_style: bool) -> str:
    if is_style:
        result = ""
        for bullets, width, code_lines, code_width in CARD_LADDER:
            result = _style_card(doc, label, full_tokens, bullets, width, code_lines, code_width)
            if est_tokens(result) <= CARD_BUDGET:
                break
        return result
    result = ""
    for width, heads in ((140, 30), (100, 24), (70, 18), (50, 12)):
        result = _generic_card(doc, label, full_tokens, width, heads)
        if est_tokens(result) <= CARD_BUDGET + 150:
            break
    return result


# ---------------------------------------------------------------------------
# target resolution
# ---------------------------------------------------------------------------

class Resolved(object):
    def __init__(self, path: Path, label: str, source_id: Optional[str] = None):
        self.path = path
        self.label = label  # path shown to the user
        self.source_id = source_id


def _roots(layout: Layout) -> List[Path]:
    roots = [layout.root.resolve()]
    for extra in (layout.sources_dir, layout.skill_dir):
        try:
            roots.append(extra.resolve())
        except OSError:
            pass
    return roots


def _within(path: Path, roots: Sequence[Path]) -> bool:
    for r in roots:
        try:
            path.relative_to(r)
            return True
        except ValueError:
            continue
    return False


def display_path(layout: Layout, path: Path) -> str:
    try:
        return path.resolve().relative_to(layout.root.resolve()).as_posix()
    except ValueError:
        pass
    try:
        rel = path.resolve().relative_to(layout.sources_dir.resolve())
    except ValueError:
        return str(path)
    for src in _sources(layout).values():
        lp = str(src.get("local_path") or src["id"])
        if rel.parts and rel.parts[0] == lp:
            return "%s:%s" % (src["id"], "/".join(rel.parts[1:]))
    return "sources/" + rel.as_posix()


def _sources(layout: Layout) -> Dict[str, Mapping[str, Any]]:
    try:
        return dict(catalog.by_id(catalog.load_sources(layout)))  # type: ignore[arg-type]
    except catalog.CatalogError:
        return {}


def _patterns(layout: Layout) -> Dict[str, Mapping[str, Any]]:
    try:
        return dict(catalog.by_id(catalog.load_patterns(layout)))  # type: ignore[arg-type]
    except catalog.CatalogError:
        return {}


def _md_by_stem(directory: Path) -> Dict[str, Path]:
    if not directory.is_dir():
        return {}
    return {p.stem: p for p in sorted(directory.glob("*.md")) if p.name != "README.md"}


def _pick(kind: str, name: str, mapping: Mapping[str, Path], layout: Layout) -> Resolved:
    name = name[:-3] if name.endswith(".md") else name
    if "/" in name or "\\" in name or ".." in name or "\0" in name:
        raise ReadError("refused: %s name must not contain path separators or '..'" % kind, EXIT_USAGE)
    if name in mapping:
        return Resolved(mapping[name], display_path(layout, mapping[name]))
    near = [k for k in mapping if k.startswith(name) or name in k]
    if len(near) == 1:
        return Resolved(mapping[near[0]], display_path(layout, mapping[near[0]]))
    if near:
        raise ReadError("ambiguous %s %r; candidates:\n%s" % (kind, name, "\n".join("  %s:%s" % (kind, n) for n in sorted(near))), EXIT_USAGE)
    raise ReadError("no %s named %r (try: design-sensei search %s)" % (kind, name, name))


def _kinds(layout: Layout) -> Dict[str, Dict[str, Path]]:
    know = layout.knowledge_dir
    notes = {}  # type: Dict[str, List[Path]]
    if know.is_dir():
        for p in sorted(know.rglob("*.md")):
            if p.name == "README.md" or "pattern-index" in p.relative_to(know).parts:
                continue
            notes.setdefault(p.stem, []).append(p)
    return {
        "ref": _md_by_stem(layout.skill_dir / "references"),
        "playbook": _md_by_stem(layout.skill_dir / "patterns"),
        "recipe": _md_by_stem(know / "implementation-recipes"),
        "style": _md_by_stem(know / "design-styles"),
        "note": {k: v[0] for k, v in notes.items() if len(v) == 1},
        "_dupes": {k: v for k, v in notes.items() if len(v) > 1},  # type: ignore[dict-item]
    }


def resolve_source_file(layout: Layout, sid: str, rel: str) -> Resolved:
    srcs = _sources(layout)
    if sid not in srcs:
        raise ReadError("unknown source id %r (design-sensei sources list)" % sid, EXIT_USAGE)
    reason = catalog.unsafe_relative_path(rel)
    if reason:
        raise ReadError("refused: source path %s" % reason, EXIT_USAGE)
    base = layout.source_path(srcs[sid])
    target = base / rel
    if not target.exists():
        hint = "" if base.is_dir() else " (source not downloaded: design-sensei sources sync %s)" % sid
        raise ReadError("%s:%s not found%s" % (sid, rel, hint))
    if not _within(target.resolve(), [base.resolve()]):
        raise ReadError("refused: %s:%s resolves outside the source" % (sid, rel), EXIT_USAGE)
    return Resolved(target, "%s:%s" % (sid, rel), sid)


def resolve_path(layout: Layout, raw: str) -> Resolved:
    if "\0" in raw or ".." in re.split(r"[\\/]", raw):
        raise ReadError("refused: path must not contain '..'", EXIT_USAGE)
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = layout.root / candidate
        if not candidate.exists() and (layout.home / raw).exists():
            candidate = layout.home / raw
    resolved = candidate.resolve()
    if not _within(resolved, _roots(layout)):
        raise ReadError("refused: %s is outside the toolkit and the source library" % raw, EXIT_USAGE)
    if not resolved.is_file():
        raise ReadError("file not found: %s" % raw)
    return Resolved(resolved, display_path(layout, resolved), source_for_path(layout, resolved))


def source_for_path(layout: Layout, path: Path) -> Optional[str]:
    try:
        rel = path.resolve().relative_to(layout.sources_dir.resolve())
    except ValueError:
        return None
    for src in _sources(layout).values():
        if rel.parts and rel.parts[0] == str(src.get("local_path") or src["id"]):
            return str(src["id"])
    return None


def resolve_target(layout: Layout, target: str, want_recipe: bool = False) -> Resolved:
    target = target.strip()
    if not target:
        raise ReadError("give a target (a style slug, ref:NAME, playbook:NAME, recipe:SLUG, note:NAME, pattern id or path)", EXIT_USAGE)
    kinds = _kinds(layout)
    if ":" in target and not re.match(r"^[A-Za-z]:[\\/]", target):
        prefix, _, rest = target.partition(":")
        if prefix in ("ref", "playbook", "recipe", "style"):
            return _pick(prefix, rest, kinds[prefix], layout)
        if prefix == "note":
            name = rest[:-3] if rest.endswith(".md") else rest
            if name in kinds["_dupes"]:
                raise ReadError("ambiguous note %r; candidates:\n%s" % (name, "\n".join("  " + display_path(layout, p) for p in kinds["_dupes"][name])), EXIT_USAGE)  # type: ignore[index]
            return _pick("note", name, kinds["note"], layout)
        if prefix == "source":
            sid, _, rel = rest.partition(":")
            return resolve_source_file(layout, sid, rel)
        if prefix in _sources(layout):
            return resolve_source_file(layout, prefix, rest)
        raise ReadError("unknown target prefix %r (use ref:, playbook:, recipe:, style:, note:, source:ID:path or a source id)" % prefix, EXIT_USAGE)
    if "/" in target or target.endswith((".md", ".txt", ".json", ".yaml")):
        return resolve_path(layout, target)
    pats = _patterns(layout)
    if target in pats:
        p = pats[target]
        key = "recipe" if want_recipe else "knowledge_doc"
        if not p.get(key):
            raise ReadError("pattern %s has no %s%s" % (target, key.replace("_", " "), "" if want_recipe or not p.get("recipe") else " (try --recipe)"))
        return resolve_path(layout, str(p[key]))
    # bare name: look across every kind; several distinct files -> ambiguity
    found = {}  # type: Dict[Path, str]
    slug = target[6:] if target.startswith("style-") else target
    for kind in ("style", "recipe", "ref", "playbook", "note"):
        for name in (slug, target):
            if name in kinds[kind]:
                found.setdefault(kinds[kind][name].resolve(), "%s:%s" % (kind, name))
    if "style-" + target in pats and pats["style-" + target].get("knowledge_doc"):
        try:
            r = resolve_path(layout, str(pats["style-" + target]["knowledge_doc"]))
            found.setdefault(r.path.resolve(), "style:" + target)
        except ReadError:
            pass
    if len(found) == 1:
        path = next(iter(found))
        return Resolved(path, display_path(layout, path))
    if len(found) > 1:
        raise ReadError("ambiguous target %r; use one of:\n%s" % (target, "\n".join("  " + v for v in sorted(found.values()))), EXIT_USAGE)
    # fuzzy: unique substring among styles / recipes
    fuzzy = {}  # type: Dict[Path, str]
    for kind in ("style", "recipe", "ref", "playbook", "note"):
        for name, path in kinds[kind].items():
            if name.startswith(slug):
                fuzzy.setdefault(path.resolve(), "%s:%s" % (kind, name))
    if len(fuzzy) == 1:
        path = next(iter(fuzzy))
        return Resolved(path, display_path(layout, path))
    if fuzzy:
        raise ReadError("ambiguous target %r; candidates:\n%s" % (target, "\n".join("  " + v for v in sorted(fuzzy.values()))), EXIT_USAGE)
    raise ReadError("no document matches %r (try: design-sensei search %s)" % (target, target))


# ---------------------------------------------------------------------------
# licence header
# ---------------------------------------------------------------------------

def licence_header(layout: Layout, source_id: Optional[str]) -> str:
    if not source_id:
        return ""
    src = _sources(layout).get(source_id)
    if not src:
        return ""
    reuse = catalog.reuse_for(str(src.get("redistribution_status")))
    return "licence: %s (%s) | reuse: %s | %s" % (src.get("license"), src.get("license_status"), reuse[0], reuse[1])


# ---------------------------------------------------------------------------
# command
# ---------------------------------------------------------------------------

def _parse_lines(spec: str, total: int) -> Tuple[int, int]:
    m = re.match(r"^(\d+):(\d+)$", spec.strip())
    if not m:
        raise ReadError("--lines expects A:B (1-based, inclusive), for example 1:60", EXIT_USAGE)
    a, b = int(m.group(1)), int(m.group(2))
    if a < 1 or b < a:
        raise ReadError("--lines A:B needs 1 <= A <= B", EXIT_USAGE)
    return a, min(b, total)


def read_target(layout: Layout, args: argparse.Namespace) -> str:
    res = resolve_target(layout, args.target, want_recipe=args.recipe)
    try:
        raw = res.path.read_bytes()
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise ReadError("%s is not a UTF-8 text file" % res.label)
    except OSError as exc:
        raise ReadError("cannot read %s: %s" % (res.label, exc))
    source_id = res.source_id or source_for_path(layout, res.path)
    lic = licence_header(layout, source_id)
    is_md = res.path.suffix.lower() == ".md"
    all_lines = text.split("\n")
    if all_lines and all_lines[-1] == "":
        all_lines.pop()
    total_tokens = est_tokens(text)
    head = []  # type: List[str]
    modes = [m for m in ("card", "toc", "section", "lines", "full", "max_tokens") if getattr(args, m, None) not in (None, False)]
    if len([m for m in modes if m != "max_tokens"]) > 1:
        raise ReadError("choose one of --card, --toc, --section, --lines, --full", EXIT_USAGE)
    if args.max_tokens is not None and args.max_tokens < 1:
        raise ReadError("--max-tokens must be at least 1", EXIT_USAGE)

    if not is_md:
        if args.card or args.toc or args.section:
            raise ReadError("--card, --toc and --section work on markdown files; use --lines A:B or --full for %s" % res.label, EXIT_USAGE)
        head.append("[%s, %d lines, ~%d tokens full]" % (res.label, len(all_lines), total_tokens))
        if lic:
            head.append(lic)
        if args.lines:
            a, b = _parse_lines(args.lines, len(all_lines))
            if a > len(all_lines):
                raise ReadError("%s has only %d lines" % (res.label, len(all_lines)))
            body = all_lines[a - 1:b]
            head.append("lines %d-%d of %d" % (a, b, len(all_lines)))
        elif args.full:
            body = all_lines
        else:
            limit = DEFAULT_CODE_LINES
            body = all_lines[:limit]
            if len(all_lines) > limit:
                head.append("first %d of %d lines; use --lines A:B for more" % (limit, len(all_lines)))
        out = "\n".join(head + [""] + body)
        if args.max_tokens is not None and est_tokens(out) > args.max_tokens:
            keep, dropped = _cut_lines(body, max(args.max_tokens - est_tokens("\n".join(head)), 10))
            out = "\n".join(head + [""] + keep + ["", "[truncated: %d more tokens; use --lines A:B or --full]" % dropped])
        return out

    doc = Document(text)
    label = res.label
    if lic:
        head_extra = [lic]
    else:
        head_extra = []
    if args.lines:
        a, b = _parse_lines(args.lines, len(all_lines))
        if a > len(all_lines):
            raise ReadError("%s has only %d lines" % (res.label, len(all_lines)))
        out = ["[%s, lines %d-%d of %d]" % (label, a, b, len(all_lines))] + head_extra + [""] + all_lines[a - 1:b]
        return "\n".join(out)
    if args.full:
        return "\n".join([header_line(label, doc, total_tokens)] + head_extra + [""] + all_lines)
    if args.toc:
        return "\n".join([header_line(label, doc, total_tokens)] + head_extra + [render_toc(doc)])
    if args.section:
        wanted = [w for w in args.section.split(",") if w.strip()]
        if not wanted:
            raise ReadError("--section needs at least one heading", EXIT_USAGE)
        sections, missing = match_sections(doc, wanted)
        if missing and not sections:
            raise ReadError("no heading starts with %s in %s; headings: %s" % (", ".join(repr(m) for m in missing), label, "; ".join(s.title for s in doc.sections)), EXIT_USAGE)
        body = render_sections(doc, sections, args.max_tokens)
        note = "" if not missing else "\n\n[no heading starts with: %s]" % ", ".join(missing)
        return "\n".join([header_line(label, doc, total_tokens)] + head_extra + [body]) + note
    if args.max_tokens is not None:
        return "\n".join([header_line(label, doc, total_tokens)] + head_extra + [render_max_tokens(doc, args.max_tokens)])
    is_style = doc.kind == "design-style" or "design-styles" in res.label.split("/")
    card = render_card(doc, label, total_tokens, is_style)
    if head_extra:
        lines = card.split("\n")
        card = "\n".join(lines[:1] + head_extra + lines[1:])
    return card


def cmd_read(layout: Layout, args: argparse.Namespace) -> int:
    try:
        out = read_target(layout, args)
    except ReadError as exc:
        return fail(exc.message, exc.code)
    sys.stdout.write(out.rstrip("\n") + "\n")
    return EXIT_OK


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("target", metavar="TARGET", help="style slug, pattern id, ref:NAME, playbook:NAME, recipe:SLUG, note:NAME, SOURCE:path or a path")
    group = parser.add_argument_group("modes (default: --card for documents, first 80 lines for code)")
    group.add_argument("--card", action="store_true", help="compact quick card (~450 tokens)")
    group.add_argument("--toc", action="store_true", help="headings with approximate token counts")
    group.add_argument("--section", metavar="A,B", help="sections whose heading starts with A or B (case-insensitive prefix)")
    group.add_argument("--lines", metavar="A:B", help="1-based inclusive line range")
    group.add_argument("--full", action="store_true", help="the whole file")
    parser.add_argument("--max-tokens", type=int, metavar="N", help="cut at a section boundary after about N tokens (estimate: characters / 4)")
    parser.add_argument("--recipe", action="store_true", help="with a pattern id, open its implementation recipe instead of its knowledge note")
    add_global_options(parser)
    parser.set_defaults(func=lambda a: run_with_layout(a, cmd_read))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="read_doc.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arguments(parser)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
