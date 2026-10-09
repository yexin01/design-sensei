#!/usr/bin/env python3
"""Turn a short design brief into one actionable recommendation (offline, deterministic).

`recommend` runs the catalog search twice (design styles, then implementation patterns)
with the same ranking as `search`, applies the project configuration and returns:

  1. a PRIMARY design style (and at most one SUPPORTING style) with its note and the
     "pairs well with / avoid" hints from the note;
  2. up to N implementation patterns with licence, GPU, dependency, reduced-motion and
     file availability details;
  3. a LICENSE GATE line (strictest reuse class among the patterns and what it allows);
  4. a FALLBACK line when the top pattern is GPU heavy or needs dependencies the project
     does not allow;
  5. next steps: which files to read and which `sources sync` to run.

Examples
  design-sensei recommend "liquid glass hero for a fintech"
  design-sensei recommend "editorial scroll storytelling" --framework nextjs --max-gpu low
  design-sensei recommend "dark developer tool landing" --no-webgl --allowed-deps gsap,lenis --json

Defaults come from .design-sensei.yaml (see `design-sensei config show`): preferred_frameworks
(soft preference), webgl_enabled and performance_budget.max_webgl_canvases (no WebGL),
reduced_motion static_first (only patterns with a reduced-motion alternative) and
allowed_dependencies. Command line options win over the configuration.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import search_patterns
from dslib import EXIT_OK, EXIT_USAGE
from dslib import catalog, compact, config as ds_config, knowledge
from dslib.cli import add_global_options, csv_list, fail, print_json, run_with_layout
from dslib.paths import Layout
from dslib.textutil import tokenize, truncate

STYLE_CATEGORY = "design-style"
# Design styles are chosen separately; `workflow` patterns (checklists, reference sites, tooling) may be shown when
# they match but are never offered as a fallback implementation.
NON_IMPLEMENTATION_CATEGORIES = (STYLE_CATEGORY,)
NON_FALLBACK_CATEGORIES = ("workflow",)

GPU_ORDER = search_patterns.GPU_ORDER
GPU_HEAVY = ("medium", "high", "unknown")  # unknown counts as medium, as in `search --max-gpu`
GPU_NAMES = ("none", "low", "medium", "high")

# Strictest last. "original" is project-authored guidance; the rest follow catalog.REDISTRIBUTION_ORDER.
REUSE_ORDER = ["original"] + [catalog.REUSE_GUIDANCE[r][0] for r in catalog.REDISTRIBUTION_ORDER]
REUSE_ALLOWED = {
    "original": "Project-authored guidance: free to use.",
    "copy_with_attribution": "Copy or adapt freely, keeping the upstream copyright and licence notice.",
    "license_review_required": "Custom terms: use as a dependency per the upstream terms; never bundle or republish its code.",
    "verify_first": "Rights not verified: treat as reference only until the licence is checked.",
    "reimplement_only": "No licence granted: study the idea, write your own implementation, copy no code or assets.",
    "reference_only": "Link and describe only: copy nothing.",
}

# Words that carry no design meaning in a brief; dropping them keeps `search` ranking focused.
STOPWORDS = frozenset(
    "a an the for of to in on at by with and or but my our your their its is are be as into from that this these those "
    "i we you it they me us want need like make build create design designing page site website app new some very really "
    "please should would could can will using use".split()
)

# What "no WebGL" means for an implementation pattern (`search --no-webgl` is stricter: it also drops every gpu low pattern).
WEBGL_FRAMEWORKS = frozenset(["webgl", "glsl", "three", "r3f", "tresjs"])
WEBGL_TAGS = frozenset(["webgl", "glsl", "r3f", "ogl", "shader", "fragment-shader"])
SUPPORTING_MIN_SHARE = 0.3  # a supporting style must score at least this share of the primary's score

# Frameworks that do not tie a pattern to one UI framework.
AGNOSTIC_FRAMEWORKS = frozenset(["css", "javascript", "typescript", "html", "svg", "webgl", "glsl", "three", "gsap", "lenis", "matter-js", "vite", "tailwind"])
REACT_FAMILY = frozenset(["react", "nextjs", "r3f", "framer-motion", "motion", "stylex"])
VUE_FAMILY = frozenset(["vue", "nuxt", "tresjs"])
FRAMEWORK_ALIASES = {"next": "nextjs", "next.js": "nextjs", "reactjs": "react", "vuejs": "vue", "nuxtjs": "nuxt"}

DEPENDENCY_KEYWORDS = ("none", "existing", "minimal", "any")
MINIMAL_NEW_DEPENDENCIES = 1  # `minimal` tolerates one package the project does not already have

SUPPORT_LINE_RE = re.compile(r"^\s*[-*]\s*Supporting influences that work:\s*(.+)$", re.MULTILINE)
AVOID_SPLIT_RE = re.compile(r"\b(?:[Aa]void|[Dd]o not mix|[Dd]on't mix)\b")
RELEVANCE_FLOOR = 0.25  # a fallback alternative must score at least this share of the top pattern
NOISE_FLOOR = 0.2  # matches scoring below this share of the best match are dropped (one weak synonym hit)
STYLE_NAME_BOOST = 1.5  # the brief names the style outright (all words of its slug appear in the brief)
STYLE_RELATED_BOOST = 1.3  # implementation pattern listed in the primary style's `related`
SUPPORTING_RELATED_BOOST = 1.15
PREFERRED_FRAMEWORK_BOOST = 1.2
CSS_ONLY_ACTION = ("no catalog alternative with gpu none/low and allowed dependencies matched, so build a CSS-only version "
                   "(custom properties, transitions, transforms, gradients, SVG) from the project's own components, adding no packages")
FALLBACK_BOILERPLATE = "ship the heavy version only as progressive enhancement with a static fallback and a prefers-reduced-motion path"


# ---------------------------------------------------------------------------
# options and configuration
# ---------------------------------------------------------------------------

class Options(object):
    """Resolved request options. ``None`` means "not given on the command line"."""

    def __init__(self, frameworks: Optional[Sequence[str]] = None, max_gpu: Optional[str] = None, reduced_motion_safe: Optional[bool] = None,
                 no_webgl: Optional[bool] = None, allowed_deps: Optional[Sequence[str]] = None, limit: int = 3, project: Optional[Path] = None):
        self.frameworks = [normalize_framework(f) for f in (frameworks or [])]
        self.max_gpu = max_gpu
        self.reduced_motion_safe = reduced_motion_safe
        self.no_webgl = no_webgl
        self.allowed_deps = list(allowed_deps) if allowed_deps else None
        self.limit = limit
        self.project = project


def normalize_framework(name: str) -> str:
    key = name.strip().lower()
    return FRAMEWORK_ALIASES.get(key, key)


def framework_family(name: str) -> frozenset:
    name = normalize_framework(name)
    if name in REACT_FAMILY:
        return REACT_FAMILY
    if name in VUE_FAMILY:
        return VUE_FAMILY
    return frozenset([name])


def framework_fit(pattern_frameworks: Sequence[str], wanted: Sequence[str]) -> Tuple[bool, bool]:
    """(compatible, named). Patterns tied to no UI framework are compatible; ``named`` means the pattern lists one of the wanted frameworks."""
    specific = set(pattern_frameworks) - AGNOSTIC_FRAMEWORKS
    if not specific:
        return True, False
    family = set()  # type: set
    for w in wanted:
        family |= framework_family(w)
    named = bool(specific & family)
    return named, named


def read_project_dependencies(project: Path) -> List[str]:
    """Package names from the project's package.json (empty when absent or unreadable)."""
    try:
        data = json.loads((project / "package.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    names = []  # type: List[str]
    if isinstance(data, dict):
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            block = data.get(key)
            if isinstance(block, dict):
                names.extend(str(n).lower() for n in block)
    return sorted(set(names))


class DependencyPolicy(object):
    """allowed_dependencies: none | existing | minimal | any | explicit list."""

    def __init__(self, allowed: Any, project_dependencies: Sequence[str]):
        if isinstance(allowed, (list, tuple)):
            items = [str(a).strip() for a in allowed if str(a).strip()]
            if len(items) == 1 and items[0] in DEPENDENCY_KEYWORDS:
                allowed = items[0]
            else:
                allowed = items
        elif allowed not in DEPENDENCY_KEYWORDS:
            allowed = "minimal"
        self.allowed = allowed
        self.installed = set(project_dependencies)

    def outside(self, dependencies: Sequence[str]) -> List[str]:
        """Dependencies that break the policy (empty list = compliant)."""
        deps = list(dependencies)
        if self.allowed == "any":
            return []
        if self.allowed == "none":
            return deps
        if isinstance(self.allowed, list):
            allowed = set(a.lower() for a in self.allowed) | self.installed
            return [d for d in deps if d.lower() not in allowed]
        new = [d for d in deps if d.lower() not in self.installed]
        if self.allowed == "existing":
            return new
        return new if len(new) > MINIMAL_NEW_DEPENDENCIES else []  # minimal

    def describe(self) -> str:
        if isinstance(self.allowed, list):
            return "only %s (plus installed packages)" % (", ".join(self.allowed) or "nothing")
        return {"none": "none (no packages)", "existing": "existing (packages already in package.json)",
                "minimal": "minimal (at most %d new package)" % MINIMAL_NEW_DEPENDENCIES, "any": "any"}[self.allowed]


def resolve_settings(layout: Layout, opts: Options) -> Dict[str, Any]:
    """Merge configuration layers with command line options (options win)."""
    notes = []  # type: List[str]
    values = {}  # type: Dict[str, Any]
    origins = {}  # type: Dict[str, str]
    try:
        values, origins, problems = ds_config.effective_config(layout, opts.project)
        for p in problems:
            notes.append("config problem (ignored, using defaults for the affected layer): %s" % p)
    except catalog.CatalogError as exc:
        notes.append("configuration unavailable (%s); using built-in defaults" % exc)
    budget = values.get("performance_budget") or {}
    no_webgl = opts.no_webgl
    webgl_origin = "option"
    if no_webgl is None:
        no_webgl = values.get("webgl_enabled") is False or budget.get("max_webgl_canvases") == 0
        webgl_origin = "config" if no_webgl else "default"
    reduced = opts.reduced_motion_safe
    reduced_origin = "option"
    if reduced is None:
        reduced = values.get("reduced_motion") == "static_first"
        reduced_origin = "config" if reduced else "default"
    allowed = opts.allowed_deps if opts.allowed_deps is not None else values.get("allowed_dependencies", "minimal")
    project_dir = opts.project or Path.cwd()
    return {
        "frameworks": list(opts.frameworks),
        "preferred_frameworks": [normalize_framework(f) for f in values.get("preferred_frameworks") or []],
        "max_gpu": opts.max_gpu,
        "no_webgl": bool(no_webgl),
        "no_webgl_from": webgl_origin,
        "reduced_motion_safe": bool(reduced),
        "reduced_motion_from": reduced_origin,
        "reduced_motion": values.get("reduced_motion", "respect"),
        "allowed_dependencies": allowed,
        "performance_budget": budget,
        "source_acquisition_mode": values.get("source_acquisition_mode", "on_demand"),
        "project": str(project_dir),
        "project_arg": str(opts.project) if opts.project else None,
        "project_dependencies": read_project_dependencies(project_dir),
        "notes": notes,
        "origins": origins,
    }


# ---------------------------------------------------------------------------
# search plumbing
# ---------------------------------------------------------------------------

def clean_query(brief: str) -> str:
    kept = [w for w in brief.split() if re.sub(r"[^a-z0-9]", "", w.lower()) not in STOPWORDS]
    return " ".join(kept) if kept else brief.strip()


def _search_namespace(query: str, **overrides: Any) -> argparse.Namespace:
    """A `search` namespace with the real parser's defaults, so new search options never break us."""
    parser = argparse.ArgumentParser(add_help=False)
    search_patterns.add_arguments(parser)
    ns = parser.parse_args([])
    ns.query = query
    ns.limit = 10 ** 6
    for key, value in overrides.items():
        setattr(ns, key, value)
    return ns


def _run_search(layout: Layout, query: str, settings: Mapping[str, Any], **overrides: Any) -> List[Dict[str, Any]]:
    """`search` ranking (same scoring and filters) with the reduced-motion filter of this request."""
    ns = _search_namespace(query, reduced_motion_safe=settings["reduced_motion_safe"], **overrides)
    results, _ = search_patterns.run_search(layout, ns)
    return results


def uses_webgl(p: Mapping[str, Any]) -> bool:
    return bool(set(p.get("frameworks") or []) & WEBGL_FRAMEWORKS or set(p.get("tags") or []) & WEBGL_TAGS or _gpu(p) == "high")


def is_3d_bound_style(p: Mapping[str, Any]) -> bool:
    """Styles whose note is built on a GPU scene (gpu high or react-three-fiber); the others have a CSS route."""
    return _gpu(p) == "high" or "r3f" in (p.get("frameworks") or [])


def _gpu(p: Mapping[str, Any]) -> str:
    return (p.get("performance") or {}).get("gpu_intensity", "unknown")


# ---------------------------------------------------------------------------
# styles
# ---------------------------------------------------------------------------

def style_slug(style: Mapping[str, Any]) -> str:
    doc = style.get("knowledge_doc")
    if doc:
        return Path(str(doc)).stem
    sid = str(style["id"])
    return sid[len("style-"):] if sid.startswith("style-") else sid


def parse_style_hints(style: Mapping[str, Any], known_slugs: Sequence[str]) -> Tuple[List[str], List[str]]:
    """(pairs well with, avoid) style slugs from the note's "Supporting influences that work" line."""
    path = style.get("knowledge_doc_path")
    if not path:
        return [], []
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return [], []
    _, body, _ = knowledge.parse_frontmatter(text)
    m = SUPPORT_LINE_RE.search(body)
    if not m:
        return [], []
    line = m.group(1)
    split = AVOID_SPLIT_RE.search(line)
    pair_text, avoid_text = (line[: split.start()], line[split.start():]) if split else (line, "")
    own = style_slug(style)

    def slugs_in(part: str) -> List[str]:
        found = []  # type: List[Tuple[int, str]]
        for slug in known_slugs:
            if slug == own:
                continue
            hit = re.search(r"(?<![a-z0-9-])%s(?![a-z0-9-])" % re.escape(slug), part)
            if hit:
                found.append((hit.start(), slug))
        return [slug for _, slug in sorted(found)]

    return slugs_in(pair_text), slugs_in(avoid_text)


def _style_view(style: Mapping[str, Any], hints: Tuple[List[str], List[str]]) -> Dict[str, Any]:
    acc = style.get("accessibility") or {}
    return {
        "id": style["id"], "title": style["title"], "slug": style_slug(style), "score": style["score"],
        "summary": truncate(style.get("summary", ""), 240), "note_path": style.get("knowledge_doc_path"),
        "pairs_well_with": hints[0], "avoid": hints[1], "related_patterns": list(style.get("related") or []),
        "reuse": style.get("reuse"), "gpu_intensity": _gpu(style), "motion": acc.get("motion"),
        "reduced_motion_alternative": bool(acc.get("reduced_motion_alternative")),
    }


def pick_styles(layout: Layout, query: str, settings: Mapping[str, Any]) -> Dict[str, Any]:
    """Primary style = best `search` hit among design-style patterns; supporting = best ranked style the primary note lists as a pairing."""
    gpu_capped = settings["no_webgl"] or settings["max_gpu"] in ("none", "low", "medium")
    ranked = [r for r in _run_search(layout, query, settings, category=[STYLE_CATEGORY])
              if r["score"] > 0 and not (gpu_capped and is_3d_bound_style(r))]
    if not ranked:
        return {"primary": None, "supporting": None, "conflicts": []}
    qtokens = set(tokenize(query))
    for r in ranked:  # the brief names the style outright ("editorial ...", "kinetic typography")
        name = set(tokenize(style_slug(r).replace("-", " ")))
        if name and name <= qtokens:
            r["score"] = round(r["score"] * STYLE_NAME_BOOST, 3)
    ranked.sort(key=lambda r: (-r["score"], r["id"]))
    known = {style_slug(p) for p in catalog.load_patterns(layout) if p.get("category") == STYLE_CATEGORY}
    known_slugs = sorted(known | {style_slug(r) for r in ranked}, key=lambda s: (-len(s), s))
    cache = {}  # type: Dict[str, Tuple[List[str], List[str]]]

    def hints(style: Mapping[str, Any]) -> Tuple[List[str], List[str]]:
        if style["id"] not in cache:
            cache[style["id"]] = parse_style_hints(style, known_slugs)
        return cache[style["id"]]

    primary = ranked[0]
    p_pairs, p_avoid = hints(primary)
    supporting = None
    conflicts = []  # type: List[str]
    for cand in ranked[1:]:
        if cand["score"] < SUPPORTING_MIN_SHARE * primary["score"]:
            break
        c_pairs, c_avoid = hints(cand)
        if style_slug(cand) in p_avoid or style_slug(primary) in c_avoid:
            conflicts.append(cand["id"])
        elif style_slug(cand) in p_pairs or style_slug(primary) in c_pairs:
            supporting = cand
            break
    return {"primary": _style_view(primary, (p_pairs, p_avoid)), "supporting": _style_view(supporting, hints(supporting)) if supporting else None,
            "conflicts": conflicts}


# ---------------------------------------------------------------------------
# implementation patterns
# ---------------------------------------------------------------------------

def source_state(entry: Mapping[str, Any], sources: Mapping[str, Mapping[str, Any]], layout: Layout) -> str:
    """downloaded | not downloaded | path not found in download | reference only (no download)."""
    if entry["present"]:
        return "downloaded"
    src = sources.get(catalog.split_source_path(entry["ref"])[0])
    if src is None:
        return "unknown source"
    if src.get("acquisition_method") == "reference_only" or src.get("type") in catalog.SOURCE_TYPES_WITHOUT_CLONE:
        return "reference only (no download)"
    return "path not found in download" if layout.source_path(src).is_dir() else "not downloaded"


def _pattern_view(layout: Layout, p: Mapping[str, Any], sources: Mapping[str, Mapping[str, Any]], policy: DependencyPolicy) -> Dict[str, Any]:
    perf, acc = p.get("performance") or {}, p.get("accessibility") or {}
    deps = list(p.get("dependencies") or [])
    files = []
    for f in (p.get("files") or [])[:3]:
        entry = {"ref": f["ref"], "path": f["path"], "present": f["present"]}
        entry["state"] = source_state(entry, sources, layout)
        files.append(entry)
    warnings = []  # type: List[str]
    if acc.get("motion", "none") != "none" and not acc.get("reduced_motion_alternative"):
        warnings.append("has motion but no documented reduced-motion alternative: add a prefers-reduced-motion path yourself")
    return {
        "id": p["id"], "title": p["title"], "category": p["category"], "score": p["score"], "match": p.get("match", "query"),
        "summary": truncate(p.get("summary", ""), 240), "source_ids": list(p.get("source_ids") or []), "source_licenses": list(p.get("sources") or []),
        "reuse": p["reuse"], "license_status": p["license_status"], "redistribution_status": p["redistribution_status"], "gpu_intensity": _gpu(p),
        "fallback_required": bool(perf.get("fallback_required")), "motion": acc.get("motion"),
        "reduced_motion_alternative": bool(acc.get("reduced_motion_alternative")), "dependencies": deps,
        "dependencies_outside_policy": policy.outside(deps), "frameworks": list(p.get("frameworks") or []),
        "implementation_status": p.get("implementation_status"), "knowledge_doc": p.get("knowledge_doc"),
        "knowledge_doc_path": p.get("knowledge_doc_path"), "recipe": p.get("recipe"), "recipe_path": p.get("recipe_path"),
        "source_paths": files, "source_paths_total": len(p.get("files") or []), "warnings": warnings,
    }


def rank_patterns(layout: Layout, query: str, settings: Mapping[str, Any], styles: Mapping[str, Any], limit: int) -> List[Dict[str, Any]]:
    """Scored implementation patterns, best first (enough to fill ``limit``, plus candidates for the fallback).

    Ranking is `search` ranking; recommend only adds small, explainable adjustments: a boost for patterns listed in
    the chosen styles' ``related``, a soft boost for ``preferred_frameworks`` and a drop of one-synonym noise. When
    fewer than ``limit`` patterns match the words, style-related patterns fill the remaining slots (``match: style``).
    """
    wanted, preferred = settings["frameworks"], settings["preferred_frameworks"]
    primary, supporting = styles.get("primary"), styles.get("supporting")
    related = [(rid, STYLE_RELATED_BOOST) for rid in (primary or {}).get("related_patterns", [])]
    related += [(rid, SUPPORTING_RELATED_BOOST) for rid in (supporting or {}).get("related_patterns", [])]
    boost = {}  # type: Dict[str, float]
    for rid, factor in related:
        boost.setdefault(rid, factor)

    def usable(r: Mapping[str, Any]) -> bool:
        if r["category"] in NON_IMPLEMENTATION_CATEGORIES:
            return False
        if settings["no_webgl"] and uses_webgl(r):
            return False
        return not wanted or framework_fit(r.get("frameworks") or [], wanted)[0]

    pool = []  # type: List[Dict[str, Any]]
    for r in _run_search(layout, query, settings, max_gpu=settings["max_gpu"]):
        if r["score"] <= 0 or not usable(r):
            continue
        item = dict(r, match="query")
        factor = boost.get(r["id"], 1.0)
        if not wanted and preferred and framework_fit(r.get("frameworks") or [], preferred)[1]:
            factor *= PREFERRED_FRAMEWORK_BOOST
        item["score"] = round(item["score"] * factor, 3)
        pool.append(item)
    pool.sort(key=lambda r: (-r["score"], r["id"]))
    if pool:
        pool = [r for r in pool if r["score"] >= NOISE_FLOOR * pool[0]["score"]]
    if len(pool) < limit and related:
        have = {r["id"] for r in pool}
        universe = {r["id"]: r for r in _run_search(layout, "", settings, max_gpu=settings["max_gpu"])}
        for rid, _ in related:
            if len(pool) >= limit:
                break
            cand = universe.get(rid)
            if cand is not None and rid not in have and usable(cand):
                pool.append(dict(cand, score=0.0, match="style"))
                have.add(rid)
    return pool


# ---------------------------------------------------------------------------
# gate, fallback, next steps
# ---------------------------------------------------------------------------

def license_gate(patterns: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    if not patterns:
        return {"strictest_reuse": "original", "strictest_license_status": "verified", "allowed": REUSE_ALLOWED["original"], "by_reuse": {}, "review_sources": [],
                "line": "LICENSE GATE: no implementation patterns matched; the style notes are original guidance and free to use."}
    by_reuse = {}  # type: Dict[str, List[str]]
    for p in patterns:
        by_reuse.setdefault(p["reuse"], []).append(p["id"])

    def strictness(reuse: str) -> int:
        return REUSE_ORDER.index(reuse) if reuse in REUSE_ORDER else len(REUSE_ORDER)

    strictest = max(by_reuse, key=strictness)
    statuses = [p["license_status"] for p in patterns]
    worst = max(statuses, key=lambda s: catalog.LICENSE_STATUS_ORDER.index(s) if s in catalog.LICENSE_STATUS_ORDER else 0)
    allowed = REUSE_ALLOWED.get(strictest, catalog.reuse_for("pending_verification")[1])
    review = []  # type: List[str]
    if strictest in ("license_review_required", "verify_first", "reimplement_only", "reference_only"):
        for p in patterns:
            for src in p["source_licenses"]:
                if catalog.reuse_for(src["redistribution_status"])[0] == strictest and src["id"] not in review:
                    review.append(src["id"])
        if review:
            allowed += " Read the terms first: %s." % ", ".join("`design-sensei sources show %s`" % sid for sid in review)
    line = "LICENSE GATE: strictest reuse class is %s (licence status %s). %s" % (strictest, worst, allowed)
    if len(by_reuse) > 1:
        line += " Per pattern: %s." % "; ".join("%s -> %s" % (r, ", ".join(ids)) for r, ids in sorted(by_reuse.items(), key=lambda kv: strictness(kv[0])))
    return {"strictest_reuse": strictest, "strictest_license_status": worst, "allowed": allowed, "by_reuse": by_reuse, "review_sources": review, "line": line}


def fallback_for(top: Optional[Mapping[str, Any]], pool: Sequence[Mapping[str, Any]], policy: DependencyPolicy) -> Optional[Dict[str, Any]]:
    """Present only when the top pattern is GPU heavy or needs dependencies the project does not allow."""
    if top is None:
        return None
    reasons = []  # type: List[str]
    if top["gpu_intensity"] in GPU_HEAVY:
        reasons.append("%s is gpu %s%s" % (top["id"], top["gpu_intensity"], " (counts as medium)" if top["gpu_intensity"] == "unknown" else ""))
    if top["dependencies_outside_policy"]:
        reasons.append("%s needs %s, outside allowed_dependencies = %s" % (top["id"], ", ".join(top["dependencies_outside_policy"]), policy.describe()))
    if not reasons:
        return None
    floor = RELEVANCE_FLOOR * top["score"]
    best, best_key = None, None
    for cand in pool:
        deps = cand.get("dependencies") or []
        if cand["id"] == top["id"] or cand["score"] < floor or cand["category"] in NON_FALLBACK_CATEGORIES or _gpu(cand) in GPU_HEAVY or policy.outside(deps):
            continue
        key = (GPU_ORDER.get(_gpu(cand), 2), len(deps), -cand["score"], cand["id"])
        if best_key is None or key < best_key:
            best, best_key = cand, key
    alternative = None
    if best is not None:
        deps = list(best.get("dependencies") or [])
        alternative = {"id": best["id"], "title": best["title"], "score": best["score"], "gpu_intensity": _gpu(best), "dependencies": deps, "reuse": best["reuse"],
                       "knowledge_doc_path": best.get("knowledge_doc_path"), "recipe_path": best.get("recipe_path")}
        action = "use `%s` instead (gpu %s, %s, reuse %s)" % (best["id"], _gpu(best), "no dependencies" if not deps else "needs " + ", ".join(deps), best["reuse"])
    else:
        action = CSS_ONLY_ACTION
    if top["gpu_intensity"] in GPU_HEAVY:
        action += "; " + FALLBACK_BOILERPLATE
    if top["dependencies_outside_policy"]:
        action += "; add %s only after the user agrees" % ", ".join(top["dependencies_outside_policy"])
    return {"reasons": reasons, "alternative": alternative, "line": "FALLBACK: %s. Suggestion: %s." % ("; ".join(reasons), action)}


def next_steps(styles: Mapping[str, Any], patterns: Sequence[Mapping[str, Any]], fallback: Optional[Mapping[str, Any]], settings: Mapping[str, Any]) -> List[str]:
    steps = []  # type: List[str]
    notes = [s["note_path"] for s in (styles.get("primary"), styles.get("supporting")) if s and s.get("note_path")]
    if notes:
        steps.append("Read the style note%s: %s" % ("s" if len(notes) > 1 else "", "; ".join(notes)))
    listed = set(notes)
    for i, p in enumerate(patterns, start=1):
        paths = [x for x in (p.get("knowledge_doc_path"), p.get("recipe_path")) if x and x not in listed]
        listed.update(paths)
        if paths:
            steps.append("Read for #%d %s: %s" % (i, p["id"], "; ".join(paths)))
    alt = (fallback or {}).get("alternative")
    if alt:
        paths = [x for x in (alt.get("knowledge_doc_path"), alt.get("recipe_path")) if x and x not in listed]
        if paths:
            steps.append("Read the fallback `%s`: %s" % (alt["id"], "; ".join(paths)))
    missing = []  # type: List[str]
    present = 0
    for p in patterns:
        for f in p["source_paths"]:
            if f["state"] == "not downloaded":
                sid = catalog.split_source_path(f["ref"])[0]
                if sid not in missing:
                    missing.append(sid)
            elif f["present"]:
                present += 1
    offline = settings["source_acquisition_mode"] == "offline" or os.environ.get("DESIGN_SENSEI_OFFLINE") == "1"
    if missing and offline:
        steps.append("Sources not downloaded: %s. Offline mode: do not sync; work from the notes and recipes." % ", ".join(missing))
    elif missing:
        steps.append("Download missing sources (needs network and git; `design-sensei sources show <id>` first): design-sensei sources sync %s" % " ".join(missing))
    if present:
        steps.append("Open the files marked (downloaded) above; they are the real implementations.")
    if patterns or notes:
        steps.append("When done: design-sensei eval %s" % (settings["project_arg"] or "."))
    return steps


# ---------------------------------------------------------------------------
# entry points
# ---------------------------------------------------------------------------

def recommend(layout: Layout, brief: str, opts: Optional[Options] = None) -> Dict[str, Any]:
    """Build the recommendation as a JSON-serialisable dict (no printing, no network)."""
    opts = opts or Options()
    settings = resolve_settings(layout, opts)
    query = clean_query(brief)
    sources = catalog.by_id(catalog.load_sources(layout))
    policy = DependencyPolicy(settings["allowed_dependencies"], settings["project_dependencies"])
    styles = pick_styles(layout, query, settings)
    pool = rank_patterns(layout, query, settings, styles, opts.limit)
    shown = [_pattern_view(layout, p, sources, policy) for p in pool[: opts.limit]]
    notes = list(settings["notes"])
    if opts.frameworks and not shown:
        notes.append("no implementation pattern matched framework %s; rerun without --framework and adapt a React or vanilla pattern" % ", ".join(opts.frameworks))
    if not styles["primary"] and not shown:
        notes.append("no matches: try fewer or different words, relax the filters, or see `design-sensei search --facets` for the vocabulary")
    fallback = fallback_for(shown[0] if shown else None, pool, policy)
    rec = {
        "brief": brief, "query": query, "count": len(shown), "policy": policy.describe(),
        "filters": {
            "framework": settings["frameworks"], "preferred_frameworks": settings["preferred_frameworks"], "max_gpu": settings["max_gpu"],
            "no_webgl": settings["no_webgl"], "reduced_motion_safe": settings["reduced_motion_safe"], "reduced_motion": settings["reduced_motion"],
            "allowed_dependencies": settings["allowed_dependencies"], "performance_budget": settings["performance_budget"], "limit": opts.limit,
            "source_acquisition_mode": settings["source_acquisition_mode"],
            "origins": {"no_webgl": settings["no_webgl_from"], "reduced_motion_safe": settings["reduced_motion_from"]},
        },
        "style": {"primary": styles["primary"], "supporting": styles["supporting"], "conflicts": styles["conflicts"]},
        "patterns": shown, "license_gate": license_gate(shown), "fallback": fallback, "notes": notes,
    }
    rec["next_steps"] = next_steps(styles, shown, fallback, settings)
    return rec


def _style_lines(label: str, s: Mapping[str, Any]) -> List[str]:
    return ["  %s %s  \"%s\"  score %.1f" % (label, s["id"], s["title"], s["score"]), "      " + s["summary"], "      note: %s" % s["note_path"],
            "      pairs well with: %s | avoid: %s" % (", ".join(s["pairs_well_with"]) or "-", ", ".join(s["avoid"]) or "-")]


def render_text(rec: Mapping[str, Any], detail: str = "full", root: Optional[Path] = None, home: Optional[Path] = None) -> str:
    """Text rendering. ``full`` is the verbose legacy layout; ``normal`` and ``brief`` print paths relative to one ``root:`` line."""
    if detail == "full" or root is None:
        return _render_full(rec)
    if detail == "brief":
        return _render_brief(rec)
    return _render_normal(rec, root, home)


def _active_filters(rec: Mapping[str, Any], short: bool = False) -> List[str]:
    f = rec["filters"]
    active = []  # type: List[str]
    if f["framework"]:
        active.append("framework=" + ",".join(f["framework"]))
    elif f["preferred_frameworks"]:
        active.append("prefers " + ",".join(f["preferred_frameworks"]))
    if f["max_gpu"]:
        active.append("max-gpu=" + f["max_gpu"])
    if f["no_webgl"]:
        active.append("no-webgl" + (" (config)" if f["origins"]["no_webgl"] == "config" else ""))
    if f["reduced_motion_safe"]:
        active.append("reduced-motion-safe" + (" (config)" if f["origins"]["reduced_motion_safe"] == "config" else ""))
    active.append("deps: " + (rec["policy"].split(" (")[0] if short else rec["policy"]))
    return active


def _deps_text(p: Mapping[str, Any]) -> str:
    deps = ", ".join(p["dependencies"]) or "-"
    outside = p["dependencies_outside_policy"]
    if outside and len(outside) == len(p["dependencies"]):
        deps += " (all outside allowed)"
    elif outside:
        deps += " (outside allowed: %s)" % ", ".join(outside)
    return deps


def _non_read_steps(rec: Mapping[str, Any]) -> List[str]:
    """Next steps that carry no file paths (sync hint, offline note, eval); the read steps are re-created cheaply."""
    return [s.replace("(needs network and git; `design-sensei sources show <id>` first)", "(needs network + git; run `sources show <id>` first)")
            for s in rec["next_steps"] if not s.startswith("Read ")]


def _read_suggestion(rec: Mapping[str, Any], brief: bool) -> List[str]:
    slugs = [s["slug"] for s in (rec["style"]["primary"], rec["style"]["supporting"]) if s]
    ids = [p["id"] for p in rec["patterns"] if p.get("knowledge_doc") or p.get("recipe")]
    alt = (rec["fallback"] or {}).get("alternative")
    if alt and alt["id"] not in ids:
        ids.append(alt["id"])
    steps = []  # type: List[str]
    if slugs:
        steps.append("Read a style cheaply: " + " ; ".join(compact.read_style(sl) for sl in slugs[: 1 if brief else 2]))
    if ids:
        steps.append("Read a pattern section: %s" % compact.read_pattern("<id>") if not brief else "Then: %s for %s" % (compact.read_pattern("<id>"), ids[0]))
    return steps


def _render_brief(rec: Mapping[str, Any]) -> str:
    style = rec["style"]
    lines = ["RECOMMEND \"%s\" | deps: %s" % (rec["brief"], rec["policy"])]
    if style["primary"]:
        names = style["primary"]["slug"] + (" + " + style["supporting"]["slug"] if style["supporting"] else "")
        lines.append("STYLE %s (%s, reuse %s, gpu %s)" % (names, style["primary"]["id"], style["primary"]["reuse"], style["primary"]["gpu_intensity"]))
    else:
        lines.append("STYLE none matched; try `design-sensei search --category design-style <words>`")
    for i, p in enumerate(rec["patterns"], start=1):
        lines.append("%d. %s | %s | reuse %s | gpu %s | deps %s" % (i, p["id"], p["title"], p["reuse"], p["gpu_intensity"], _deps_text(p)))
    if not rec["patterns"]:
        lines.append("PATTERNS none matched")
    gate = rec["license_gate"]
    lines.append("LICENSE GATE: strictest reuse class is %s (licence status %s)." % (gate["strictest_reuse"], gate["strictest_license_status"])
                 + ("".join(" `design-sensei sources show %s` first." % sid for sid in gate["review_sources"][:1])))
    fb = rec["fallback"]
    if fb:
        alt = fb["alternative"]
        lines.append("FALLBACK: %s -> %s" % ("; ".join(fb["reasons"]), "use `%s` (gpu %s)" % (alt["id"], alt["gpu_intensity"]) if alt else "build a CSS-only version, no packages"))
    steps = _read_suggestion(rec, brief=True)
    lines.append("NEXT: " + " | ".join(steps) if steps else "NEXT: design-sensei search --facets")
    lines += ["note: %s" % n for n in rec["notes"]]
    return "\n".join(lines) + "\n"


def _style_block(label: str, s: Mapping[str, Any], rel: Any, seen_pairs: Sequence[str], seen_avoid: Sequence[str]) -> List[str]:
    head = "%s %s \"%s\" %.1f: %s" % (label, s["id"], s["title"], s["score"], compact.clip(s["summary"]))
    pairs = [x for x in s["pairs_well_with"] if x not in seen_pairs]
    avoid = [x for x in s["avoid"] if x not in seen_avoid]
    tail = ["note: " + rel(s["note_path"])]
    if pairs:
        tail.append("pairs: " + ", ".join(pairs))
    if avoid:
        tail.append("avoid: " + ", ".join(avoid))
    return [head, "   " + " | ".join(tail)]


def _fallback_normal(rec: Mapping[str, Any]) -> str:
    """The FALLBACK line without repeating the dependency list, the policy or boilerplate already shown elsewhere."""
    fb = rec["fallback"]
    top = rec["patterns"][0]
    reasons = []  # type: List[str]
    if top["gpu_intensity"] in GPU_HEAVY:
        reasons.append("%s is gpu %s" % (top["id"], top["gpu_intensity"]))
    if top["dependencies_outside_policy"]:
        reasons.append("%s needs deps outside allowed_dependencies" % top["id"])
    alt = fb["alternative"]
    action = ("use `%s` instead (gpu %s, %s, reuse %s)" % (alt["id"], alt["gpu_intensity"], "no deps" if not alt["dependencies"] else "needs " + ", ".join(alt["dependencies"]), alt["reuse"])
              if alt else CSS_ONLY_ACTION)
    if top["gpu_intensity"] in GPU_HEAVY:
        action += "; ship heavy only as progressive enhancement (static + reduced-motion fallback)"
    if top["dependencies_outside_policy"]:
        action += "; add the outside deps only after the user agrees"
    return "FALLBACK: %s. Suggestion: %s." % ("; ".join(reasons), action)


def _render_normal(rec: Mapping[str, Any], root: Path, home: Optional[Path] = None) -> str:
    rel = lambda path: compact.rel_path(path, root, home)  # noqa: E731
    lines = [compact.root_header(root, home), "RECOMMENDATION for \"%s\" | %s" % (rec["brief"], " | ".join(_active_filters(rec, short=True)))]
    style = rec["style"]
    if style["primary"]:
        lines += _style_block("PRIMARY", style["primary"], rel, [], [])
        if style["supporting"]:
            lines += _style_block("SUPPORTING", style["supporting"], rel, style["primary"]["pairs_well_with"], style["primary"]["avoid"])
        else:
            lines.append("SUPPORTING: none")
        if style["conflicts"]:
            lines.append("also matched but not combined (the notes say avoid): %s" % ", ".join(style["conflicts"]))
    else:
        lines.append("no design style matched; try `design-sensei search --category design-style <words>`")
    lines.append("PATTERNS (%d)" % len(rec["patterns"]) + ("" if rec["patterns"] else ": none matched"))
    seen_docs = {}  # type: Dict[str, int]
    for i, p in enumerate(rec["patterns"], start=1):
        lines.append("%d. %s [%s] %.1f%s - %s" % (i, p["id"], p["category"], p["score"], "" if p["match"] == "query" else " (listed by the chosen style, no direct word match)", p["title"]))
        lines.append("   " + compact.clip(p["summary"], 120))
        srcs = ", ".join("%s %s" % (x["id"], x["license"]) for x in p["source_licenses"]) or "original"
        status = "" if p["license_status"] in ("verified",) else " | license %s" % p["license_status"]
        lines.append("   %s | reuse %s%s | gpu %s | motion %s%s | deps %s | %s" % (
            srcs, p["reuse"], status, p["gpu_intensity"], p["motion"] or "?", " +reduced-motion alt" if p["reduced_motion_alternative"] else " (no reduced-motion alt)", _deps_text(p),
            p["implementation_status"]))
        shown = []  # type: List[str]
        for key, path in (("doc", p["knowledge_doc_path"]), ("recipe", p["recipe_path"])):
            if path:
                shown.append("%s: %s" % (key, "same as #%d" % (seen_docs[path]) if path in seen_docs else rel(path)))
                seen_docs.setdefault(path, i)
        if shown:
            lines.append("   " + " | ".join(shown))
        files = p["source_paths"]
        if files:
            names = [rel(f["path"] or f["ref"]) for f in files]
            prefix, names = compact.split_common_dir(names)
            states = {f["state"] for f in files}
            extra = compact.more(p.get("source_paths_total", len(files)), len(files))
            if len(states) == 1:
                lines.append("   files (%s) in %s: %s%s" % (files[0]["state"], prefix or "./", ", ".join(names), extra))
            else:
                lines.append("   files in %s: %s%s" % (prefix or "./", ", ".join("%s (%s)" % (n, f["state"]) for n, f in zip(names, files)), extra))
        for w in p["warnings"]:
            lines.append("   warning: %s" % w)
    gate = rec["license_gate"]
    gate_line = gate["line"]
    cut = gate_line.find(" Per pattern:")
    lines.append(gate_line[:cut] if cut > 0 else gate_line)  # each pattern already shows its own reuse class
    if rec["fallback"]:
        lines.append(_fallback_normal(rec))
    steps = _read_suggestion(rec, brief=False) + _non_read_steps(rec)
    if any(f["state"] == "downloaded" for p in rec["patterns"] for f in p["source_paths"]):
        steps = [x for x in steps if not x.startswith("Open the files marked")]
        steps = [x.replace("When done:", "Open the (downloaded) files above for the real code. When done:") for x in steps]
    if steps:
        lines.append("NEXT STEPS")
        lines += ["%d. %s" % (i, step) for i, step in enumerate(steps, start=1)]
    lines += ["note: %s" % n for n in rec["notes"]]
    return "\n".join(lines) + "\n"


def _render_full(rec: Mapping[str, Any]) -> str:
    active = _active_filters(rec)
    lines = ["RECOMMENDATION for \"%s\"" % rec["brief"], "  filters: " + " | ".join(active), "", "STYLE"]
    style = rec["style"]
    if style["primary"]:
        lines.extend(_style_lines("PRIMARY:   ", style["primary"]))
        if style["supporting"]:
            lines.extend(_style_lines("SUPPORTING:", style["supporting"]))
        else:
            lines.append("  SUPPORTING: none (no other matching style is a listed pairing of the primary)")
        if style["conflicts"]:
            lines.append("  also matched but not combined (the notes say avoid): %s" % ", ".join(style["conflicts"]))
    else:
        lines.append("  no design style matched; try `design-sensei search --category design-style <words>`")
    lines += ["", "PATTERNS (%d)" % len(rec["patterns"])]
    if not rec["patterns"]:
        lines.append("  none matched")
    for i, p in enumerate(rec["patterns"], start=1):
        deps = ", ".join(p["dependencies"]) or "-"
        if p["dependencies_outside_policy"]:
            deps += " (outside allowed: %s)" % ", ".join(p["dependencies_outside_policy"])
        lines.append("%d. %s  [%s]  score %.1f%s" % (i, p["id"], p["category"], p["score"], "" if p["match"] == "query" else "  (listed by the chosen style, no direct word match)"))
        lines.append("   %s" % p["title"])
        lines.append("   " + p["summary"])
        srcs = ", ".join("%s (%s)" % (x["id"], x["license"]) for x in p["source_licenses"]) or "none (original guidance)"
        lines.append("   sources: %s | reuse: %s | license status: %s" % (srcs, p["reuse"], p["license_status"]))
        lines.append("   gpu: %s | motion: %s (reduced-motion alt: %s) | deps: %s | status: %s" % (
            p["gpu_intensity"], p["motion"] or "?", "yes" if p["reduced_motion_alternative"] else "no", deps, p["implementation_status"]))
        lines.append("   doc: %s" % (p["knowledge_doc_path"] or "-"))
        lines.append("   recipe: %s" % (p["recipe_path"] or "-"))
        for fl in p["source_paths"]:
            lines.append("   file: %s  (%s)" % (fl["path"] or fl["ref"], fl["state"]))
        for w in p["warnings"]:
            lines.append("   warning: %s" % w)
    lines += ["", rec["license_gate"]["line"]]
    if rec["fallback"]:
        lines.append(rec["fallback"]["line"])
    if rec["next_steps"]:
        lines += ["", "NEXT STEPS"] + ["  %d. %s" % (i, step) for i, step in enumerate(rec["next_steps"], start=1)]
    lines += ["note: %s" % n for n in rec["notes"]]
    return "\n".join(lines) + "\n"


def cmd_recommend(layout: Layout, args: argparse.Namespace) -> int:
    brief = " ".join(args.brief).strip()
    if not brief:
        return fail("give a short brief in quotes, for example: design-sensei recommend \"liquid glass hero for a fintech\"", EXIT_USAGE)
    if args.limit < 1:
        return fail("--limit must be at least 1", EXIT_USAGE)
    opts = Options(frameworks=args.framework, max_gpu=args.max_gpu, reduced_motion_safe=True if args.reduced_motion_safe else None,
                   no_webgl=True if args.no_webgl else None, allowed_deps=args.allowed_deps, limit=args.limit,
                   project=Path(args.project).resolve() if args.project else None)
    rec = recommend(layout, brief, opts)
    if args.json:
        print_json(rec)
    else:
        detail = compact.resolve_detail(args.detail, layout, opts.project)
        sys.stdout.write(render_text(rec, detail, layout.root, layout.home))
    return EXIT_OK


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("brief", nargs="*", metavar="BRIEF", help="mood / goal words, quoted (for example \"liquid glass hero for a fintech\")")
    parser.add_argument("--framework", type=csv_list, default=[], metavar="LIST",
                        help="project framework(s), for example react, nextjs, vue; framework-agnostic patterns (css, gsap, three ...) always qualify")
    parser.add_argument("--max-gpu", choices=["none", "low", "medium", "high"], help="exclude patterns above this GPU intensity (unknown counts as medium)")
    parser.add_argument("--reduced-motion-safe", action="store_true", help="only patterns without motion or with a reduced-motion alternative")
    parser.add_argument("--no-webgl", action="store_true", help="exclude WebGL/3D patterns (CSS and SVG routes stay available)")
    parser.add_argument("--allowed-deps", type=csv_list, default=None, metavar="LIST",
                        help="comma-separated packages you may add, or one of none|existing|minimal|any")
    parser.add_argument("--limit", type=int, default=3, metavar="N", help="implementation patterns to return (default 3)")
    parser.add_argument("--project", metavar="DIR", help="project directory for .design-sensei.yaml and package.json (default: current directory)")
    compact.add_detail_option(parser)
    parser.add_argument("--json", action="store_true")
    add_global_options(parser)
    parser.set_defaults(func=lambda a: run_with_layout(a, cmd_recommend))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="recommend.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arguments(parser)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
