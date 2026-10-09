#!/usr/bin/env python3
"""Static design evaluation of a project or file (heuristic, read-only).

``design-sensei eval <path>`` scans HTML, CSS, JS/TS, JSX/TSX, Vue and Svelte files and
reports findings grouped by the Design Sensei evaluation rubric: accessibility, motion,
performance, responsive behaviour, typography, art-direction signals, source provenance
and technical hygiene. It reads the project's effective Design Sensei configuration
(motion_intensity, webgl_enabled, allowed_dependencies, performance_budget ...).

This is a *linter*, not a judge: it can show that something obviously required is
missing, never that a design is good. It cannot see rendered output, contrast, layout
quality or taste. Always follow it with real browser inspection (see
skills/design-sensei/references/design-qa.md).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dslib import EXIT_FAILURE, EXIT_OK, EXIT_USAGE
from dslib import catalog
from dslib.cli import add_global_options, fail, print_json, run_with_layout
from dslib.config import effective_config
from dslib.paths import Layout

SKIP_DIRS = {".git", "node_modules", "dist", "build", ".next", ".turbo", "coverage", "__pycache__", ".venv", ".cache", "out", ".vercel", ".nuxt", ".svelte-kit"}
EXTS = {".html", ".htm", ".css", ".scss", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".vue", ".svelte", ".astro"}
MAX_FILES = 600
MAX_BYTES = 600_000
CATEGORIES = ["accessibility", "motion", "performance", "responsive", "typography", "art-direction", "provenance", "technical"]
HEAVY_LIBS = ["three", "@react-three/fiber", "gsap", "framer-motion", "motion", "lenis", "@studio-freight/lenis", "ogl", "pixi.js", "@splinetool/react-spline"]
MOTION_CODE_RE = re.compile(r"""\b(gsap|ScrollTrigger|lenis|Lenis|framer-motion|requestAnimationFrame|useFrame|<Canvas|WebGLRenderer|@keyframes|animation\s*:|transition\s*:)""")
REDUCED_MOTION_RE = re.compile(r"prefers-reduced-motion|useReducedMotion|reduced-motion|reducedMotion|matchMedia\(")


class Finding(object):
    def __init__(self, code: str, level: str, category: str, path: str, line: int, message: str, hint: str = ""):
        self.code, self.level, self.category, self.path, self.line, self.message, self.hint = code, level, category, path, line, message, hint

    def as_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "level": self.level, "category": self.category, "path": self.path, "line": self.line, "message": self.message, "hint": self.hint}


class Project(object):
    def __init__(self, root: Path, files: List[Path], texts: Dict[Path, str]):
        self.root = root
        self.files = files
        self.texts = texts

    def rel(self, path: Path) -> str:
        try:
            return path.relative_to(self.root if self.root.is_dir() else self.root.parent).as_posix()
        except ValueError:
            return str(path)

    def all_text(self) -> str:
        return "\n".join(self.texts.values())

    def by_ext(self, *exts: str) -> List[Path]:
        return [p for p in self.files if p.suffix.lower() in exts]


def load_project(target: Path) -> Project:
    files = []  # type: List[Path]
    if target.is_file():
        files = [target]
    else:
        for dirpath, dirnames, filenames in os.walk(str(target), followlinks=False):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for name in sorted(filenames):
                p = Path(dirpath) / name
                if p.suffix.lower() in EXTS and not p.is_symlink():
                    files.append(p)
                if len(files) >= MAX_FILES:
                    break
    texts = {}  # type: Dict[Path, str]
    for p in files:
        try:
            if p.stat().st_size <= MAX_BYTES:
                texts[p] = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
    return Project(target, [p for p in files if p in texts], texts)


def lines_matching(text: str, pattern: "re.Pattern[str]") -> List[int]:
    return [text.count("\n", 0, m.start()) + 1 for m in pattern.finditer(text)]


def _tag_blocks(text: str, tag: str) -> Iterable[Tuple[int, str]]:
    for m in re.finditer(r"<%s\b[^>]*?/?>" % tag, text, re.IGNORECASE | re.DOTALL):
        yield text.count("\n", 0, m.start()) + 1, m.group(0)


def evaluate(project: Project, config: Dict[str, Any], source_ids: Dict[str, Dict[str, Any]]) -> List[Finding]:
    out = []  # type: List[Finding]
    markup = project.by_ext(".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro")
    styles = project.by_ext(".css", ".scss")
    code = project.by_ext(".js", ".jsx", ".ts", ".tsx", ".mjs", ".vue", ".svelte", ".astro")
    code_texts = {p: project.texts[p] for p in code}  # type: Dict[Path, str]
    for p in project.by_ext(".html", ".htm"):  # inline <script> blocks count as code
        inline = "\n".join(m.group(1) for m in re.finditer(r"<script\b[^>]*>(.*?)</script>", project.texts[p], re.DOTALL | re.IGNORECASE))
        if inline.strip():
            code_texts[p] = inline
    everything = project.all_text()
    has_reduced = bool(REDUCED_MOTION_RE.search(everything))
    css_text = "\n".join(project.texts[p] for p in styles) + "\n".join(
        m.group(1) for p in markup for m in re.finditer(r"<style[^>]*>(.*?)</style>", project.texts[p], re.DOTALL | re.IGNORECASE))

    # ---- accessibility ---------------------------------------------------
    for p in markup:
        t = project.texts[p]
        for ln, tag in list(_tag_blocks(t, "img")) + list(_tag_blocks(t, "Image")):
            if not re.search(r"\balt\s*=", tag):
                out.append(Finding("A11Y-001", "error", "accessibility", project.rel(p), ln, "image without alt attribute", "add alt text, or alt=\"\" for decorative images"))
        if p.suffix.lower() in (".html", ".htm"):
            for m in re.finditer(r"<html\b([^>]*)>", t, re.IGNORECASE):
                if "lang=" not in m.group(1).lower():
                    out.append(Finding("A11Y-003", "warning", "accessibility", project.rel(p), t.count("\n", 0, m.start()) + 1, "<html> has no lang attribute", "add lang=\"en\" (or the page language)"))
            if len(re.findall(r"<h1\b", t, re.IGNORECASE)) > 1:
                out.append(Finding("A11Y-008", "warning", "accessibility", project.rel(p), 1, "more than one <h1> in the document", "use one <h1> and a logical heading outline"))
        for m in re.finditer(r"<(div|span)\b[^>]*\bonClick\s*=[^>]*>", t):
            if not re.search(r"\brole\s*=", m.group(0)):
                out.append(Finding("A11Y-004", "warning", "accessibility", project.rel(p), t.count("\n", 0, m.start()) + 1, "click handler on a non-interactive element", "use <button>/<a>, or add role, tabIndex and keyboard handlers"))
        for m in re.finditer(r"<video\b[^>]*\bautoplay\b[^>]*>", t, re.IGNORECASE):
            if not re.search(r"\bmuted\b", m.group(0), re.IGNORECASE):
                out.append(Finding("A11Y-007", "warning", "accessibility", project.rel(p), t.count("\n", 0, m.start()) + 1, "autoplay video that is not muted", "autoplay is blocked or hostile without muted; offer controls"))
        for m in re.finditer(r"<meta[^>]+name=[\"']viewport[\"'][^>]*>", t, re.IGNORECASE):
            if re.search(r"user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0)?\b", m.group(0), re.IGNORECASE):
                out.append(Finding("A11Y-005", "error", "accessibility", project.rel(p), t.count("\n", 0, m.start()) + 1, "viewport meta blocks zooming", "remove user-scalable=no / maximum-scale=1"))
    if re.search(r"outline\s*:\s*(none|0)\b", css_text + everything) and not re.search(r":focus-visible", everything):
        out.append(Finding("A11Y-002", "warning", "accessibility", project.rel(project.root), 1, "focus outline removed and no :focus-visible style found", "provide a visible custom focus style"))

    # ---- motion ------------------------------------------------------------
    uses_motion = bool(MOTION_CODE_RE.search(everything))
    if uses_motion and not has_reduced:
        level = "error" if config.get("reduced_motion") == "static_first" else "warning"
        out.append(Finding("MOT-001", level, "motion", project.rel(project.root), 1, "animation or motion library used but no prefers-reduced-motion handling found", "gate non-essential motion behind prefers-reduced-motion (CSS media query or matchMedia / useReducedMotion)"))
    for p in styles + [q for q in markup if q.suffix.lower() in (".vue", ".svelte", ".html", ".htm")]:
        t = project.texts[p]
        for m in re.finditer(r"transition\s*:\s*all\b", t):
            out.append(Finding("MOT-005", "warning", "motion", project.rel(p), t.count("\n", 0, m.start()) + 1, "transition: all animates every property", "list the properties (prefer transform and opacity)"))
        for m in re.finditer(r"transition(?:-property)?\s*:[^;{}]*\b(width|height|top|left|right|bottom|margin|padding)\b", t):
            out.append(Finding("MOT-004", "warning", "motion", project.rel(p), t.count("\n", 0, m.start()) + 1, "transition on a layout property", "animate transform/opacity to avoid layout thrash"))
        for km in re.finditer(r"@keyframes\s+[\w-]+\s*\{(.*?)\n\}", t, re.DOTALL):
            if re.search(r"\b(width|height|top|left|margin|padding)\s*:", km.group(1)):
                out.append(Finding("MOT-004", "warning", "motion", project.rel(p), t.count("\n", 0, km.start()) + 1, "@keyframes animates a layout property", "animate transform/opacity instead"))
    for p, t in code_texts.items():
        if re.search(r"useEffect\(", t) and re.search(r"new\s+Lenis\(", t) and not re.search(r"\.destroy\(", t):
            out.append(Finding("MOT-006", "warning", "motion", project.rel(p), 1, "Lenis instance created in an effect without destroy()", "return a cleanup that calls lenis.destroy()"))
        if re.search(r"useEffect\(", t) and re.search(r"\bgsap\.(to|from|fromTo|timeline)\(", t) and not re.search(r"\.revert\(|gsap\.context|useGSAP|kill\(", t):
            out.append(Finding("MOT-006", "warning", "motion", project.rel(p), 1, "GSAP animation created in an effect without revert/kill cleanup", "wrap in gsap.context() or useGSAP and revert on unmount"))
        if re.search(r"requestAnimationFrame\(", t) and not re.search(r"cancelAnimationFrame\(", t):
            out.append(Finding("MOT-006", "warning", "motion", project.rel(p), 1, "requestAnimationFrame loop without cancelAnimationFrame", "keep the id and cancel it on teardown"))

    # ---- performance ---------------------------------------------------------
    for p in markup:
        t = project.texts[p]
        for ln, tag in _tag_blocks(t, "img"):
            if not re.search(r"\bwidth\s*=", tag) or not re.search(r"\bheight\s*=", tag):
                out.append(Finding("PERF-001", "warning", "performance", project.rel(p), ln, "<img> without width and height", "set intrinsic dimensions or aspect-ratio to avoid layout shift"))
    wills = len(re.findall(r"will-change\s*:", css_text + everything))
    if wills > 3:
        out.append(Finding("PERF-003", "warning", "performance", project.rel(project.root), 1, "%d will-change declarations" % wills, "use will-change sparingly and only on elements about to animate"))
    canvases = len(re.findall(r"new\s+(?:THREE\.)?WebGLRenderer\(|<Canvas\b|getContext\(\s*['\"]webgl2?['\"]", everything))
    budget = (config.get("performance_budget") or {}).get("max_webgl_canvases", 1)
    if canvases and config.get("webgl_enabled") is False:
        out.append(Finding("PERF-005", "error", "performance", project.rel(project.root), 1, "WebGL used but webgl_enabled is false in the Design Sensei config", "remove the WebGL effect or enable it deliberately"))
    elif canvases > budget:
        out.append(Finding("PERF-004", "warning", "performance", project.rel(project.root), 1, "%d WebGL canvases found (budget %d)" % (canvases, budget), "share one renderer or lazy-mount canvases only while visible"))
    for p, t in code_texts.items():
        if "devicePixelRatio" in t and not re.search(r"Math\.min\([^)]*devicePixelRatio|dpr\s*=\s*\[", t):
            out.append(Finding("PERF-006", "warning", "performance", project.rel(p), 1, "devicePixelRatio used without a cap", "cap it, for example Math.min(window.devicePixelRatio, 2)"))
    for m in re.finditer(r"fonts\.googleapis\.com/css[^\"')\s]*", everything):
        if "display=swap" not in m.group(0) and "display=optional" not in m.group(0):
            out.append(Finding("PERF-008", "warning", "performance", project.rel(project.root), 1, "Google Fonts URL without display=swap", "add &display=swap to avoid invisible text"))
            break
    out.extend(_dependency_findings(project, config))

    # ---- responsive ------------------------------------------------------------
    for p in project.by_ext(".html", ".htm"):
        if not re.search(r"<meta[^>]+name=[\"']viewport[\"']", project.texts[p], re.IGNORECASE):
            out.append(Finding("RESP-001", "error", "responsive", project.rel(p), 1, "HTML page without a viewport meta tag", "add <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"))
    if css_text and not re.search(r"@media|@container|clamp\(|min\(|max\(|\bvw\b|\bcqw\b|minmax\(|auto-fit|auto-fill", css_text) and not re.search(r"\b(sm|md|lg|xl):", everything):
        out.append(Finding("RESP-002", "warning", "responsive", project.rel(project.root), 1, "no responsive technique found in the styles", "use fluid sizing (clamp), media/container queries or a responsive grid"))
    if re.search(r"\b100vh\b", css_text) and not re.search(r"\b(100dvh|100svh|100lvh)\b", css_text):
        out.append(Finding("RESP-003", "info", "responsive", project.rel(project.root), 1, "100vh used without dvh/svh fallback", "mobile browser chrome makes 100vh taller than the visible area; use 100dvh/svh"))

    # ---- typography ------------------------------------------------------------
    families = set(m.group(1).split(",")[0].strip().strip("'\"") for m in re.finditer(r"font-family\s*:\s*([^;}{]+)", css_text) if "var(" not in m.group(1))
    families = {f for f in families if f.lower() not in ("inherit", "initial", "unset", "sans-serif", "serif", "monospace", "system-ui")}
    if len(families) > 3:
        out.append(Finding("TYPO-001", "warning", "typography", project.rel(project.root), 1, "%d different font families declared" % len(families), "limit to a deliberate pairing (display + text + optional mono)"))
    for m in re.finditer(r"@font-face\s*\{([^}]*)\}", css_text):
        if "font-display" not in m.group(1):
            out.append(Finding("TYPO-003", "warning", "typography", project.rel(project.root), 1, "@font-face without font-display", "add font-display: swap (or optional)"))
            break
    if len(re.findall(r"font-size\s*:\s*\d+px", css_text)) > 10:
        out.append(Finding("TYPO-002", "info", "typography", project.rel(project.root), 1, "many fixed px font sizes", "prefer rem and clamp() so text scales with user settings"))
    if css_text and families and all(f.lower() in ("inter", "roboto", "arial", "helvetica", "helvetica neue", "-apple-system", "segoe ui") for f in families):
        out.append(Finding("TYPO-005", "info", "art-direction", project.rel(project.root), 1, "only default UI fonts are used", "an intentional type pairing is one of the strongest art-direction levers"))

    # ---- art-direction signals ------------------------------------------------
    cliche = len(re.findall(r"#(?:6366f1|8b5cf6|a855f7|7c3aed|4f46e5)\b", css_text + everything, re.IGNORECASE))
    if cliche >= 4:
        out.append(Finding("ART-001", "info", "art-direction", project.rel(project.root), 1, "default Tailwind indigo/violet palette used %d times" % cliche, "check that the palette is a decision for this product, not a default"))
    if css_text and "--" not in css_text and "tailwind" not in everything.lower():
        out.append(Finding("ART-002", "info", "art-direction", project.rel(project.root), 1, "no CSS custom properties (design tokens) found", "define colour, type and spacing tokens once and reuse them"))

    # ---- provenance ---------------------------------------------------------------
    notice = any(re.match(r"^(third[-_ ]?party|attribution|notice|licenses?)", name, re.IGNORECASE) for name in _root_names(project))
    for sid, src in sorted(source_ids.items()):
        pat = re.compile(r"(?://|/\*|<!--|#)[^\n]*\b%s\b" % re.escape(sid), re.IGNORECASE)
        hits = [(p, lines_matching(project.texts[p], pat)) for p in project.files if pat.search(project.texts[p])]
        if not hits:
            continue
        reuse = catalog.reuse_for(str(src["redistribution_status"]))
        path, lns = hits[0]
        if reuse[0] in ("reference_only", "reimplement_only", "license_review_required", "verify_first"):
            out.append(Finding("PROV-002", "warning", "provenance", project.rel(path), lns[0], "comment mentions source '%s' whose reuse class is %s" % (sid, reuse[0]), reuse[1]))
        elif not notice:
            out.append(Finding("PROV-001", "warning", "provenance", project.rel(path), lns[0], "code credits '%s' but no attribution/notice file exists" % sid, "add THIRD_PARTY_NOTICES.md with the upstream copyright and license text"))

    # ---- technical ----------------------------------------------------------------
    for p in code + markup:
        t = project.texts[p]
        for m in re.finditer(r"^\s*debugger\s*;?\s*$", t, re.MULTILINE):
            out.append(Finding("TECH-001", "warning", "technical", project.rel(p), t.count("\n", 0, m.start()) + 1, "debugger statement left in code", "remove it"))
        if re.search(r"lorem ipsum", t, re.IGNORECASE):
            out.append(Finding("TECH-002", "warning", "technical", project.rel(p), lines_matching(t, re.compile("lorem ipsum", re.IGNORECASE))[0], "placeholder text (lorem ipsum) still present", "replace with real copy"))
        if len(re.findall(r"href\s*=\s*[\"']#[\"']", t)) > 3:
            out.append(Finding("TECH-003", "info", "technical", project.rel(p), 1, "several href=\"#\" placeholder links", "link somewhere real or use a button"))
    return sorted(out, key=lambda f: (CATEGORIES.index(f.category) if f.category in CATEGORIES else 99, f.path, f.line, f.code))


def _root_names(project: Project) -> List[str]:
    base = project.root if project.root.is_dir() else project.root.parent
    try:
        return [e.name for e in base.iterdir()]
    except OSError:
        return []


def _dependency_findings(project: Project, config: Dict[str, Any]) -> List[Finding]:
    base = project.root if project.root.is_dir() else project.root.parent
    pkg = base / "package.json"
    if not pkg.is_file():
        return []
    try:
        data = json.loads(pkg.read_text(encoding="utf-8"))
    except ValueError:
        return []
    deps = set((data.get("dependencies") or {}).keys())
    heavy = sorted(d for d in deps if d in HEAVY_LIBS)
    allowed = config.get("allowed_dependencies", "minimal")
    out = []  # type: List[Finding]
    rel = "package.json"
    if isinstance(allowed, list):
        extra = sorted(d for d in heavy if d not in allowed)
        if extra:
            out.append(Finding("PERF-007", "warning", "performance", rel, 1, "dependencies not in allowed_dependencies: %s" % ", ".join(extra), "remove them or extend allowed_dependencies deliberately"))
    elif allowed == "none" and heavy:
        out.append(Finding("PERF-007", "warning", "performance", rel, 1, "animation/3D libraries present but allowed_dependencies is none: %s" % ", ".join(heavy), "implement with CSS/native APIs or relax the setting"))
    elif allowed == "minimal" and len(heavy) > 3:
        out.append(Finding("PERF-007", "warning", "performance", rel, 1, "%d heavy animation/3D libraries (%s)" % (len(heavy), ", ".join(heavy)), "choose one animation system; avoid overlapping libraries"))
    return out


def summarize(findings: Sequence[Finding]) -> Dict[str, Dict[str, int]]:
    out = {c: {"error": 0, "warning": 0, "info": 0} for c in CATEGORIES}
    for f in findings:
        out.setdefault(f.category, {"error": 0, "warning": 0, "info": 0})[f.level] += 1
    return out


def cmd_eval(layout: Layout, args: argparse.Namespace) -> int:
    target = Path(args.path).expanduser()
    if not target.exists():
        return fail("path does not exist: %s" % target, EXIT_USAGE)
    project = load_project(target.resolve())
    if not project.files:
        return fail("no HTML/CSS/JS/TS/JSX/TSX/Vue/Svelte files found under %s" % target, EXIT_USAGE)
    config, _, problems = effective_config(layout, target if target.is_dir() else target.parent)
    if problems:
        return fail("invalid Design Sensei configuration: %s" % problems[0])
    sources = catalog.by_id(catalog.load_sources(layout))
    findings = evaluate(project, config, sources)  # type: ignore[arg-type]
    summary = summarize(findings)
    errors = sum(1 for f in findings if f.level == "error")
    warnings = sum(1 for f in findings if f.level == "warning")
    if args.json:
        print_json({"scanned_files": len(project.files), "summary": summary, "findings": [f.as_dict() for f in findings]})
    else:
        print("scanned %d file(s) in %s" % (len(project.files), target))
        current = None
        for f in findings:
            if f.level == "info" and not args.verbose:
                continue
            if f.category != current:
                current = f.category
                print("\n== %s ==" % current)
            print("  %-7s %s:%d  [%s] %s" % (f.level.upper(), f.path, f.line, f.code, f.message))
            if f.hint:
                print("          fix: %s" % f.hint)
        print("\nsummary (errors/warnings/info): " + "; ".join("%s %d/%d/%d" % (c, v["error"], v["warning"], v["info"]) for c, v in summary.items()))
        print("Static heuristics only: they cannot judge contrast, layout quality or taste. Inspect the running page in a browser before declaring the work done.")
    return EXIT_FAILURE if errors or (args.strict and warnings) else EXIT_OK


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", metavar="PATH", help="project directory or single file to evaluate")
    parser.add_argument("--strict", action="store_true", help="exit 1 on warnings as well as errors")
    parser.add_argument("--verbose", action="store_true", help="also print informational findings")
    parser.add_argument("--json", action="store_true")
    add_global_options(parser)
    parser.set_defaults(func=lambda a: run_with_layout(a, cmd_eval))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="design_eval.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arguments(parser)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
