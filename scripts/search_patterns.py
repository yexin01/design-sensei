#!/usr/bin/env python3
"""Search the Design Sensei catalog: patterns, knowledge notes and source files.

Deterministic local search (no embeddings, no network): tokens are matched against
weighted fields (title, tags, use cases, summary ...) with inverse-document-frequency
weighting, a small synonym table and optional filters. Results always carry the source
ids, licence status, reuse guidance and absolute file paths so an agent can open the
real implementation.

Examples
  design-sensei search "liquid glass button"
  design-sensei search scroll --framework react --max-gpu low --reduced-motion-safe
  design-sensei search shader --category background-shader --source react-bits
  design-sensei search "text reveal" --scope all --limit 5 --json
  design-sensei search --facets
"""

from __future__ import annotations

import argparse
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dslib import EXIT_FAILURE, EXIT_OK, EXIT_USAGE
from dslib import catalog, knowledge
from dslib.cli import add_global_options, fail, print_json, run_with_layout
from dslib.paths import Layout
from dslib.textutil import tokenize, truncate

GPU_ORDER = {"none": 0, "low": 1, "medium": 2, "unknown": 2, "high": 3}
PATTERN_WEIGHTS = {"id": 4.0, "title": 5.0, "tags": 4.0, "category": 3.0, "use_cases": 3.0, "summary": 2.0, "frameworks": 2.0, "dependencies": 1.5, "source_ids": 1.0, "notes": 1.0}
DOC_WEIGHTS = {"title": 5.0, "summary": 3.0, "headings": 2.0, "body": 0.5, "kind": 1.0, "source_ids": 1.0}
FILE_WEIGHTS = {"path": 2.0, "title": 3.0, "exports": 2.5, "tags": 3.0, "kind": 1.5, "source": 1.0}
SYNONYM_WEIGHT = 0.5

SYNONYMS = {
    "glass": ["glassmorphism", "frosted", "blur", "backdrop"], "frosted": ["glass", "blur"], "liquid": ["fluid", "metal", "chrome", "morph"],
    "fluid": ["liquid"], "gradient": ["aurora", "mesh", "shader"], "aurora": ["gradient", "mesh"],
    "scroll": ["lenis", "scrolltrigger", "parallax", "smooth"], "smooth": ["inertia", "lenis"], "parallax": ["scroll"],
    "text": ["typography", "type", "headline"], "headline": ["typography", "text"], "font": ["typography"], "type": ["typography"],
    "animation": ["motion", "animate", "transition"], "motion": ["animation", "animate"], "shader": ["glsl", "webgl", "fragment"],
    "webgl": ["glsl", "three", "shader"], "3d": ["three", "r3f", "webgl"], "threejs": ["three", "r3f"], "cursor": ["pointer", "mouse", "trail"],
    "mouse": ["cursor", "pointer"], "button": ["cta", "microinteraction"], "card": ["grid", "bento"], "hero": ["landing", "header"],
    "nav": ["navigation", "menu"], "menu": ["navigation", "nav"], "transition": ["page-transition", "route"], "logo": ["brand", "mark"],
    "dashboard": ["chart", "data", "visualization"], "chart": ["visualization", "dashboard", "graph"], "dark": ["night", "noir"],
    "retro": ["vintage", "nostalgia"], "futuristic": ["futurism", "cyberpunk"], "minimal": ["minimalism", "whitespace"], "brutal": ["brutalism"],
}


class Entry(object):
    def __init__(self, kind: str, key: str, fields: Mapping[str, List[str]], payload: Dict[str, Any], phrase_text: str = ""):
        self.kind = kind
        self.key = key
        self.fields = fields
        self.payload = payload
        self.phrase_text = phrase_text.lower()


def build_idf(entries: Sequence[Entry]) -> Dict[str, float]:
    df = {}  # type: Dict[str, int]
    for e in entries:
        seen = set()  # type: set
        for toks in e.fields.values():
            seen.update(toks)
        for t in seen:
            df[t] = df.get(t, 0) + 1
    n = max(len(entries), 1)
    return {t: math.log(1.0 + n / (1.0 + c)) + 0.5 for t, c in df.items()}


def score_entry(entry: Entry, qtokens: Sequence[str], expansions: Mapping[str, Sequence[str]], idf: Mapping[str, float], weights: Mapping[str, float], phrase: str) -> float:
    """Weighted token score. A query token matches directly, or at reduced weight through a synonym."""
    total = 0.0
    matched = 0
    for tok in qtokens:
        direct = 0.0
        for fname, toks in entry.fields.items():
            if tok in toks:
                direct = max(direct, weights.get(fname, 1.0) * (1.0 + math.log(toks.count(tok))))
        if direct:
            matched += 1
            total += direct * idf.get(tok, 1.0)
            continue
        via_synonym = 0.0
        for syn in expansions.get(tok, ()):
            for fname, toks in entry.fields.items():
                if syn in toks:
                    via_synonym = max(via_synonym, weights.get(fname, 1.0) * SYNONYM_WEIGHT * idf.get(syn, 1.0))
        if via_synonym:
            matched += 1
            total += via_synonym
    if not matched:
        return 0.0
    if len(qtokens) > 1:
        total *= 0.5 + 0.5 * (matched / float(len(qtokens)))
        if phrase and phrase in entry.phrase_text:
            total += 3.0
    return total


# ---------------------------------------------------------------------------
# entries
# ---------------------------------------------------------------------------

def _license_info(source_ids: Sequence[str], sources: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    redis = catalog.derive_redistribution(list(source_ids), sources) if source_ids else "redistributable_with_notice"
    reuse = catalog.reuse_for(redis) if source_ids else ("original", "Project-authored guidance (MIT).")
    items = []
    for sid in source_ids:
        s = sources.get(sid)
        if s:
            items.append({"id": sid, "license": s["license"], "license_status": s["license_status"], "redistribution_status": s["redistribution_status"]})
    return {
        "sources": items,
        "license_status": catalog.derive_license_status(list(source_ids), sources) if source_ids else "verified",
        "redistribution_status": redis if source_ids else "original",
        "reuse": reuse[0],
        "reuse_guidance": reuse[1],
    }


def pattern_entries(layout: Layout, sources: Mapping[str, Mapping[str, Any]]) -> List[Entry]:
    entries = []
    for p in catalog.load_patterns(layout):
        sids = list(p.get("source_ids") or [])
        fields = {
            "id": tokenize(p["id"]), "title": tokenize(p["title"]), "tags": [t for tag in p.get("tags", []) for t in tokenize(tag)],
            "category": tokenize(p["category"]), "use_cases": [t for u in p.get("use_cases", []) for t in tokenize(u)],
            "summary": tokenize(p.get("summary", "")), "frameworks": [t for f in p.get("frameworks", []) for t in tokenize(f)],
            "dependencies": [t for d in p.get("dependencies", []) for t in tokenize(d)], "source_ids": [t for s in sids for t in tokenize(s)],
            "notes": tokenize(p.get("notes", "")),
        }
        info = _license_info(sids, sources)
        payload = dict(p)
        payload.update(info)
        payload["type"] = "pattern"
        phrase = " ".join([p["title"], p.get("summary", ""), " ".join(p.get("use_cases", [])), " ".join(p.get("tags", []))])
        entries.append(Entry("pattern", p["id"], fields, payload, phrase))
    return entries


def doc_entries(layout: Layout, sources: Mapping[str, Mapping[str, Any]]) -> List[Entry]:
    entries = []
    for d in knowledge.iter_docs(layout):
        if not d.meta:
            continue
        sids = list(d.meta.get("source_ids") or [])
        headings = " ".join(re.findall(r"^#{1,4}\s+(.+)$", d.body, re.MULTILINE))
        fields = {
            "title": tokenize(str(d.meta.get("title", ""))), "summary": tokenize(str(d.meta.get("summary", ""))), "headings": tokenize(headings),
            "body": tokenize(d.body[:6000]), "kind": tokenize(str(d.meta.get("kind", ""))), "source_ids": [t for s in sids for t in tokenize(s)],
        }
        payload = {"type": "doc", "id": d.rel, "title": d.meta.get("title"), "kind": d.meta.get("kind"), "summary": d.meta.get("summary"),
                   "source_ids": sids, "pattern_ids": list(d.meta.get("pattern_ids") or []), "path": str(d.path)}
        payload.update(_license_info(sids, sources))
        entries.append(Entry("doc", d.rel, fields, payload, str(d.meta.get("title", "")) + " " + str(d.meta.get("summary", ""))))
    return entries


def file_entries(layout: Layout, sources: Mapping[str, Mapping[str, Any]], index: Mapping[str, Any]) -> List[Entry]:
    entries = []
    for sid, sdata in sorted(index.get("sources", {}).items()):
        if sid not in sources:
            continue
        info = _license_info([sid], sources)
        base = layout.source_path(sources[sid])
        for f in sdata.get("files", []):
            if f["kind"] in ("test", "license", "data", "package"):
                continue
            fields = {
                "path": tokenize(f["path"]), "title": tokenize(str(f.get("title", ""))), "exports": [t for e in f.get("exports", []) for t in tokenize(e)],
                "tags": [t for tag in f.get("tags", []) for t in tokenize(tag)], "kind": tokenize(f["kind"]), "source": tokenize(sid),
            }
            payload = {"type": "file", "id": "%s:%s" % (sid, f["path"]), "source_id": sid, "path": str(base / f["path"]), "kind": f["kind"],
                       "title": f.get("title"), "tags": f.get("tags", []), "size": f.get("size")}
            payload.update(info)
            entries.append(Entry("file", payload["id"], fields, payload, f["path"]))
    return entries


# ---------------------------------------------------------------------------
# filtering
# ---------------------------------------------------------------------------

def passes_filters(p: Mapping[str, Any], args: argparse.Namespace) -> bool:
    if p["type"] != "pattern":
        if args.source and not any(s in args.source for s in (p.get("source_ids") or [p.get("source_id")])):
            return False
        if args.license_status and p.get("license_status") not in args.license_status:
            return False
        if args.redistribution and p.get("redistribution_status") not in args.redistribution:
            return False
        return True
    if args.category and p["category"] not in args.category:
        return False
    for tag in args.tag:
        if tag not in p.get("tags", []):
            return False
    if args.framework and not any(f in p.get("frameworks", []) for f in args.framework):
        return False
    if args.source and not any(s in p.get("source_ids", []) for s in args.source):
        return False
    if args.dependency and not any(d in p.get("dependencies", []) for d in args.dependency):
        return False
    if args.license_status and p.get("license_status") not in args.license_status:
        return False
    if args.redistribution and p.get("redistribution_status") not in args.redistribution:
        return False
    if args.use_case and not any(args.use_case.lower() in u.lower() for u in p.get("use_cases", [])):
        return False
    if args.status and p.get("implementation_status") not in args.status:
        return False
    gpu = (p.get("performance") or {}).get("gpu_intensity", "unknown")
    if args.max_gpu and GPU_ORDER.get(gpu, 2) > GPU_ORDER[args.max_gpu]:
        return False
    if args.reduced_motion_safe:
        acc = p.get("accessibility") or {}
        if acc.get("motion", "none") != "none" and not acc.get("reduced_motion_alternative"):
            return False
    if args.webgl is False and (gpu != "none" or any(f in ("webgl", "glsl", "three", "r3f") for f in p.get("frameworks", []))):
        return False
    if args.webgl is True and not (any(f in ("webgl", "glsl", "three", "r3f") for f in p.get("frameworks", [])) or gpu in ("medium", "high")):
        return False
    return True


def decorate(layout: Layout, sources: Mapping[str, Mapping[str, Any]], p: Dict[str, Any]) -> Dict[str, Any]:
    """Add absolute paths and local availability to a result payload."""
    out = dict(p)
    if p["type"] == "pattern":
        files = []
        missing = set()  # type: set
        for ref in p.get("source_paths") or []:
            sid, rel = catalog.split_source_path(ref)
            src = sources.get(sid)
            full = layout.source_path(src) / rel if src else None
            present = bool(full and full.exists())
            if src and not present and not layout.source_path(src).is_dir():
                missing.add(sid)
            files.append({"ref": ref, "path": str(full) if full else None, "present": present})
        out["files"] = files
        out["missing_sources"] = sorted(missing)
        for field in ("knowledge_doc", "recipe"):
            if p.get(field):
                out[field + "_path"] = str(layout.root / p[field])
    return out


def format_result(rank: int, r: Dict[str, Any]) -> str:
    lines = []
    if r["type"] == "pattern":
        lines.append("%d. %s  [%s]  score %.1f" % (rank, r["id"], r["category"], r["score"]))
        lines.append("   %s" % r["title"])
        lines.append("   " + truncate(r.get("summary", ""), 220))
        src = ", ".join("%s (%s, %s)" % (s["id"], s["license"], s["license_status"]) for s in r["sources"]) or "none (original guidance)"
        lines.append("   sources: %s | reuse: %s" % (src, r["reuse"]))
        perf = r.get("performance") or {}
        acc = r.get("accessibility") or {}
        lines.append("   frameworks: %s | deps: %s | gpu: %s | motion: %s (reduced-motion alt: %s) | status: %s" % (
            ", ".join(r.get("frameworks", [])) or "-", ", ".join(r.get("dependencies", [])) or "-", perf.get("gpu_intensity", "?"),
            acc.get("motion", "?"), "yes" if acc.get("reduced_motion_alternative") else "no", r.get("implementation_status")))
        for field, label in (("knowledge_doc_path", "doc"), ("recipe_path", "recipe")):
            if r.get(field):
                lines.append("   %s: %s" % (label, r[field]))
        for f in r.get("files", [])[:5]:
            lines.append("   file: %s%s" % (f["path"] or f["ref"], "" if f["present"] else "  (not downloaded)"))
        if r.get("missing_sources"):
            lines.append("   download: design-sensei sources sync %s" % " ".join(r["missing_sources"]))
    elif r["type"] == "doc":
        lines.append("%d. [note] %s  (%s)  score %.1f" % (rank, r["title"], r["kind"], r["score"]))
        lines.append("   " + truncate(r.get("summary") or "", 220))
        lines.append("   path: %s" % r["path"])
        if r.get("pattern_ids"):
            lines.append("   patterns: %s" % ", ".join(r["pattern_ids"][:8]))
    else:
        lines.append("%d. [file] %s  (%s, %s)  score %.1f" % (rank, r["id"], r["kind"], r["license"] if "license" in r else "-", r["score"]))
        lines.append("   path: %s" % r["path"])
        lines.append("   source: %s | licence status: %s | reuse: %s" % (r["source_id"], r["license_status"], r["reuse"]))
    return "\n".join(lines)


def run_search(layout: Layout, args: argparse.Namespace) -> Tuple[List[Dict[str, Any]], List[str]]:
    sources = catalog.by_id(catalog.load_sources(layout))
    notes = []  # type: List[str]
    entries = []  # type: List[Entry]
    weights = {}  # type: Dict[str, Mapping[str, float]]
    scopes = ["patterns", "docs", "files"] if args.scope == "all" else [args.scope]
    if "patterns" in scopes:
        entries.extend(pattern_entries(layout, sources))
    if "docs" in scopes:
        entries.extend(doc_entries(layout, sources))
    if "files" in scopes:
        from index_sources import load_index  # local import: only needed for file search
        index = load_index(layout)
        if index is None:
            notes.append("no source index yet: run `design-sensei index build` after syncing sources to search files")
        else:
            entries.extend(file_entries(layout, sources, index))
    qtokens = tokenize(args.query) if args.query else []
    expansions = {}  # type: Dict[str, List[str]]
    for t in qtokens:
        for syn in SYNONYMS.get(t, []):
            for st in tokenize(syn):
                if st not in qtokens and st not in expansions.setdefault(t, []):
                    expansions[t].append(st)
    phrase = " ".join(qtokens)
    wmap = {"pattern": PATTERN_WEIGHTS, "doc": DOC_WEIGHTS, "file": FILE_WEIGHTS}
    idf_by_kind = {k: build_idf([e for e in entries if e.kind == k]) for k in wmap}
    results = []  # type: List[Dict[str, Any]]
    for e in entries:
        if not passes_filters(e.payload, args):
            continue
        if qtokens:
            s = score_entry(e, qtokens, expansions, idf_by_kind[e.kind], wmap[e.kind], phrase)
            if s <= 0:
                continue
        else:
            s = 0.0
        item = decorate(layout, sources, e.payload)
        item["score"] = round(s, 3)
        results.append(item)
    results.sort(key=lambda r: (-r["score"], r["id"]))
    if args.content and qtokens:
        results.extend(_content_hits(layout, sources, args))
    return results[: args.limit], notes


def _content_hits(layout: Layout, sources: Mapping[str, Mapping[str, Any]], args: argparse.Namespace) -> List[Dict[str, Any]]:
    """Plain substring search over downloaded source files (bounded, no regex from user input)."""
    needle = args.query.lower()
    hits = []  # type: List[Dict[str, Any]]
    for sid, src in sorted(sources.items()):
        if args.source and sid not in args.source:
            continue
        root = layout.source_path(src)
        if src["acquisition_method"] == "reference_only" or not root.is_dir():
            continue
        info = _license_info([sid], sources)
        count = 0
        for dirpath, dirnames, filenames in os.walk(str(root), followlinks=False):
            dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "dist", "build", ".next")]
            for name in filenames:
                full = Path(dirpath) / name
                if full.is_symlink() or full.suffix.lower() in (".png", ".jpg", ".gif", ".webp", ".mp4", ".woff", ".woff2", ".map", ".glb", ".lock"):
                    continue
                try:
                    if full.stat().st_size > 400000:
                        continue
                    text = full.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                idx = text.lower().find(needle)
                if idx < 0:
                    continue
                line_no = text.count("\n", 0, idx) + 1
                item = {"type": "file", "id": "%s:%s" % (sid, full.relative_to(root).as_posix()), "source_id": sid, "path": str(full), "kind": "content-match",
                        "title": "line %d" % line_no, "tags": [], "score": 0.0, "size": None}
                item.update(info)
                hits.append(item)
                count += 1
                if count >= 8:
                    break
            if count >= 8:
                break
    return hits[: args.limit]


def facets(layout: Layout) -> Dict[str, Any]:
    patterns = catalog.load_patterns(layout)
    out = {"categories": {}, "tags": {}, "frameworks": {}, "sources": {}}  # type: Dict[str, Dict[str, int]]
    for p in patterns:
        out["categories"][p["category"]] = out["categories"].get(p["category"], 0) + 1
        for key, field in (("tags", "tags"), ("frameworks", "frameworks"), ("sources", "source_ids")):
            for v in p.get(field, []):
                out[key][v] = out[key].get(v, 0) + 1
    return {k: dict(sorted(v.items(), key=lambda kv: (-kv[1], kv[0]))) for k, v in out.items()}


def cmd_search(layout: Layout, args: argparse.Namespace) -> int:
    if args.facets:
        data = facets(layout)
        if args.json:
            print_json(data)
        else:
            for name, values in data.items():
                print("%s (%d): %s" % (name, len(values), ", ".join("%s(%d)" % kv for kv in list(values.items())[:60])))
        return EXIT_OK
    has_filter = any([args.category, args.tag, args.framework, args.source, args.dependency, args.use_case, args.status, args.license_status,
                      args.redistribution, args.max_gpu, args.reduced_motion_safe, args.webgl is not None])
    if not args.query and not has_filter:
        return fail("give a query or at least one filter (see --help, --facets lists the vocabulary)", EXIT_USAGE)
    results, notes = run_search(layout, args)
    if args.json:
        print_json({"query": args.query, "count": len(results), "results": results, "notes": notes})
        return EXIT_OK
    if not results:
        print("no matches. Try fewer filters, other words, or `design-sensei search --facets` to see the vocabulary.")
    for i, r in enumerate(results, start=1):
        print(format_result(i, r))
        print()
    for n in notes:
        print("note: %s" % n)
    return EXIT_OK


def csv(value: str) -> List[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("query", nargs="?", default="", help="words to search for (natural language is fine)")
    parser.add_argument("--scope", choices=["patterns", "docs", "files", "all"], default="patterns", help="what to search (default: patterns)")
    parser.add_argument("--category", type=csv, default=[], metavar="LIST", help="comma-separated pattern categories")
    parser.add_argument("--tag", action="append", default=[], metavar="TAG", help="require this tag (repeatable)")
    parser.add_argument("--framework", type=csv, default=[], metavar="LIST", help="any of these frameworks")
    parser.add_argument("--source", type=csv, default=[], metavar="LIST", help="restrict to these source ids")
    parser.add_argument("--dependency", type=csv, default=[], metavar="LIST", help="patterns that depend on any of these packages")
    parser.add_argument("--use-case", metavar="TEXT", help="substring of a use case")
    parser.add_argument("--status", type=csv, default=[], metavar="LIST", help="implementation_status values (reference_only, recipe_available, verified_example)")
    parser.add_argument("--license-status", type=csv, default=[], metavar="LIST", help="verified, custom_terms, proprietary_terms, not_found, pending_verification, unknown")
    parser.add_argument("--redistribution", type=csv, default=[], metavar="LIST", help="redistributable_with_notice, license_specific, reference_only, unresolved, pending_verification")
    parser.add_argument("--max-gpu", choices=["none", "low", "medium", "high"], help="exclude patterns above this GPU intensity (unknown counts as medium)")
    parser.add_argument("--reduced-motion-safe", action="store_true", help="only patterns without motion or with a defined reduced-motion alternative")
    webgl = parser.add_mutually_exclusive_group()
    webgl.add_argument("--webgl", dest="webgl", action="store_true", default=None, help="only WebGL/3D patterns")
    webgl.add_argument("--no-webgl", dest="webgl", action="store_false", help="exclude WebGL/3D patterns")
    parser.add_argument("--content", action="store_true", help="also grep downloaded source files for the query text (slower)")
    parser.add_argument("--facets", action="store_true", help="list available categories, tags, frameworks and sources")
    parser.add_argument("--limit", type=int, default=10, metavar="N")
    parser.add_argument("--json", action="store_true")
    add_global_options(parser)
    parser.set_defaults(func=lambda a: run_with_layout(a, cmd_search))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="search_patterns.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arguments(parser)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
