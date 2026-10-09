#!/usr/bin/env python3
"""Build a deterministic file-level index of the sources in the local library.

For every downloaded source the index records real file paths with a kind
(component, shader, style, docs, ...), a title, exported names and technology tags
detected from imports and keywords, plus package manifests and README summaries.
Dependency folders, build output, lock files, binaries and secrets are skipped, and
symlinks are never followed. The same input always produces the same output file
(no timestamps inside the index).

Used by ``design-sensei index build`` and by ``design-sensei search --scope files``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dslib import EXIT_FAILURE, EXIT_OK
from dslib import catalog, gitops
from dslib.cli import add_global_options, print_json, run_with_layout
from dslib.paths import Layout
from dslib.textutil import truncate

INDEX_VERSION = 1
SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", ".next", ".turbo", ".cache", "coverage", "__pycache__",
    ".venv", "venv", "vendor", ".nuxt", ".output", ".svelte-kit", ".parcel-cache", "out", ".vercel",
    ".github", ".vscode", ".husky", ".changeset", ".idea", ".storybook",
}
SKIP_FILES = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb", "npm-shrinkwrap.json", ".DS_Store"}
SECRET_FILE_RE = re.compile(r"(^\.env($|\.)|\.pem$|\.key$|id_rsa|credentials)", re.IGNORECASE)
BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".ico", ".bmp", ".tiff", ".mp4", ".webm", ".mov", ".mp3", ".wav",
    ".ogg", ".woff", ".woff2", ".ttf", ".otf", ".eot", ".zip", ".gz", ".tgz", ".wasm", ".pdf", ".glb", ".gltf", ".hdr",
    ".exr", ".ktx2", ".bin", ".psd", ".fig", ".sketch", ".map", ".svg", ".lottie", ".riv",
}
SHADER_EXTS = {".glsl", ".frag", ".vert", ".wgsl", ".fs", ".vs"}
COMPONENT_EXTS = {".tsx", ".jsx", ".vue", ".svelte", ".astro"}
SCRIPT_EXTS = {".ts", ".js", ".mjs", ".cjs", ".mts", ".cts"}
STYLE_EXTS = {".css", ".scss", ".sass", ".less", ".styl", ".pcss"}
DOC_EXTS = {".md", ".mdx", ".markdown", ".txt"}
DATA_EXTS = {".json", ".yaml", ".yml", ".toml"}
MAX_FILE_BYTES = 1_000_000
HEAD_BYTES = 65536
MAX_FILES_PER_SOURCE = 25000

IMPORT_TAGS = [
    (re.compile(r"""['"]three(/[^'"]*)?['"]"""), "three"),
    (re.compile(r"""['"]@react-three/fiber['"]"""), "r3f"),
    (re.compile(r"""['"]@react-three/drei['"]"""), "drei"),
    (re.compile(r"""['"]@react-three/postprocessing['"]|['"]postprocessing['"]"""), "postprocessing"),
    (re.compile(r"""['"](gsap|@gsap/react)(/[^'"]*)?['"]"""), "gsap"),
    (re.compile(r"""['"](lenis|@studio-freight/lenis|lenis/react|lenis/snap)(/[^'"]*)?['"]"""), "lenis"),
    (re.compile(r"""['"](framer-motion|motion|motion/react)(/[^'"]*)?['"]"""), "motion"),
    (re.compile(r"""['"]ogl['"]"""), "ogl"),
    (re.compile(r"""['"]react['"]"""), "react"),
    (re.compile(r"""['"]vue['"]"""), "vue"),
    (re.compile(r"""['"]svelte['"]"""), "svelte"),
    (re.compile(r"""['"]next(/[^'"]*)?['"]"""), "nextjs"),
    (re.compile(r"""['"]@stylexjs/stylex['"]"""), "stylex"),
    (re.compile(r"""['"]tailwind-merge['"]|['"]clsx['"]"""), "tailwind"),
]
KEYWORD_TAGS = [
    (re.compile(r"gl_FragColor|gl_FragCoord|precision\s+(highp|mediump|lowp)\s+float|#version\s+\d{3}|void\s+main\s*\("), "glsl"),
    (re.compile(r"getContext\(\s*['\"]webgl2?['\"]|WebGLRenderer|WebGL2RenderingContext"), "webgl"),
    (re.compile(r"backdrop-filter"), "backdrop-filter"),
    (re.compile(r"prefers-reduced-motion|useReducedMotion|matchMedia\(\s*['\"]\(prefers-reduced-motion"), "reduced-motion"),
    (re.compile(r"@keyframes"), "css-keyframes"),
    (re.compile(r"ScrollTrigger"), "scrolltrigger"),
    (re.compile(r"requestAnimationFrame"), "raf"),
    (re.compile(r"useFrame\s*\("), "r3f-frame-loop"),
    (re.compile(r"IntersectionObserver"), "intersection-observer"),
    (re.compile(r"mix-blend-mode|mixBlendMode"), "blend-mode"),
    (re.compile(r"clip-path|clipPath"), "clip-path"),
    (re.compile(r"\bfeTurbulence\b|\bfeDisplacementMap\b"), "svg-filter"),
    (re.compile(r"(?<![\w-])view-transition|startViewTransition"), "view-transition"),
    (re.compile(r"\bShaderMaterial\b|\bRawShaderMaterial\b"), "shader-material"),
    (re.compile(r"\bcanvas\b", re.IGNORECASE), "canvas"),
]
EXPORT_RE = re.compile(r"export\s+(?:default\s+)?(?:async\s+)?(?:function\*?|const|class|let)\s+([A-Za-z_$][\w$]*)")
HEADING_RE = re.compile(r"^#{1,3}\s+(.+?)\s*#*\s*$", re.MULTILINE)
EXAMPLE_DIR_RE = re.compile(r"(^|/)(examples?|demos?|playground|stories|storybook|sandbox)(/|$)", re.IGNORECASE)
TEST_RE = re.compile(r"(\.(test|spec)\.[a-z]+$)|(^|/)(__tests__|tests?|e2e|__mocks__)(/|$)", re.IGNORECASE)


def classify(rel: str, ext: str, name: str) -> Optional[str]:
    low = name.lower()
    if re.match(r"^(licen[cs]e|copying|notice)([-_.].*)?$", low):
        return "license"
    if low.startswith("readme"):
        return "readme"
    if low == "skill.md":
        return "skill"
    if low == "design.md":
        return "design-md"
    if low == "package.json":
        return "package"
    if ext in SHADER_EXTS:
        return "shader"
    if TEST_RE.search(rel):
        return "test"
    if ext in COMPONENT_EXTS:
        return "component"
    if ext in SCRIPT_EXTS:
        return "script"
    if ext in STYLE_EXTS:
        return "style"
    if ext in DOC_EXTS:
        return "docs"
    if ext == ".html":
        return "markup"
    if ext == ".py":
        return "python"
    if ext in DATA_EXTS:
        return "data"
    return None


def first_paragraph(text: str) -> str:
    for block in re.split(r"\n\s*\n", text):
        stripped = block.strip()
        if not stripped or stripped.startswith(("#", "![", "<", "[!", "|", "```", "---", "===")):
            continue
        if re.match(r"^(\[!\[|<img|<p|<div|<a )", stripped):
            continue
        return truncate(re.sub(r"[`*_>]", "", stripped), 240)
    return ""


def analyse_file(path: Path, rel: str, kind: str) -> Dict[str, Any]:
    entry = {"path": rel, "kind": kind, "size": path.stat().st_size}  # type: Dict[str, Any]
    try:
        with open(str(path), "rb") as handle:
            head = handle.read(HEAD_BYTES).decode("utf-8", errors="replace")
    except OSError:
        return entry
    tags = set()
    if kind in ("component", "script", "style", "shader", "markup", "python"):
        for pattern, tag in IMPORT_TAGS + KEYWORD_TAGS:
            if pattern.search(head):
                tags.add(tag)
        if kind == "script" and "glsl" in tags:
            entry["kind"] = "shader"
    if kind in ("component", "script"):
        names = []  # type: List[str]
        for match in EXPORT_RE.finditer(head):
            if match.group(1) not in names:
                names.append(match.group(1))
        if names:
            entry["title"] = names[0]
            if len(names) > 1:
                entry["exports"] = names[:6]
    elif kind in ("docs", "readme", "skill", "design-md"):
        m = HEADING_RE.search(head)
        if m:
            entry["title"] = truncate(m.group(1), 120)
        if kind == "skill":
            fm = re.search(r"^---\n(.*?)\n---", head, re.DOTALL)
            if fm:
                nm = re.search(r"^name:\s*(.+)$", fm.group(1), re.MULTILINE)
                if nm:
                    entry["title"] = nm.group(1).strip().strip("\"'")
    elif kind == "package":
        try:
            pkg = json.loads(head if len(head) < HEAD_BYTES else path.read_text(encoding="utf-8"))
            entry["title"] = str(pkg.get("name", ""))
        except (ValueError, OSError):
            pass
    if EXAMPLE_DIR_RE.search(rel):
        tags.add("example")
    if tags:
        entry["tags"] = sorted(tags)
    return entry


def package_summary(path: Path, rel: str) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or not data.get("name"):
        return None
    deps = sorted(set((data.get("dependencies") or {}).keys())) if isinstance(data.get("dependencies"), dict) else []
    peers = sorted(set((data.get("peerDependencies") or {}).keys())) if isinstance(data.get("peerDependencies"), dict) else []
    lic = data.get("license")
    if isinstance(lic, dict):
        lic = lic.get("type")
    return {
        "path": rel, "name": str(data["name"]), "version": str(data.get("version", "")),
        "description": truncate(str(data.get("description", "")), 200),
        "license": lic if isinstance(lic, str) else None,
        "private": bool(data.get("private", False)),
        "dependencies": deps[:40], "peer_dependencies": peers[:20],
    }


def index_source(layout: Layout, src: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    root = layout.source_path(src)
    if src["acquisition_method"] == "reference_only" or not root.is_dir():
        return None
    files = []  # type: List[Dict[str, Any]]
    packages = []  # type: List[Dict[str, Any]]
    kinds = {}  # type: Dict[str, int]
    media = {}  # type: Dict[str, int]
    readme = None  # type: Optional[Dict[str, str]]
    truncated = False
    for dirpath, dirnames, filenames in os.walk(str(root), followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not os.path.islink(os.path.join(dirpath, d)))
        for name in sorted(filenames):
            full = Path(dirpath) / name
            if full.is_symlink() or name in SKIP_FILES or SECRET_FILE_RE.search(name):
                continue
            rel = full.relative_to(root).as_posix()
            ext = full.suffix.lower()
            if ext in BINARY_EXTS:
                media[ext] = media.get(ext, 0) + 1
                continue
            try:
                size = full.stat().st_size
            except OSError:
                continue
            if size > MAX_FILE_BYTES:
                continue
            kind = classify(rel, ext, name)
            if kind is None:
                continue
            if len(files) >= MAX_FILES_PER_SOURCE:
                truncated = True
                break
            entry = analyse_file(full, rel, kind)
            files.append(entry)
            kinds[entry["kind"]] = kinds.get(entry["kind"], 0) + 1
            if kind == "package" and len(packages) < 60:
                summary = package_summary(full, rel)
                if summary:
                    packages.append(summary)
            if kind == "readme" and rel.lower() in ("readme.md", "readme.mdx", "readme.markdown", "readme.txt", "readme") and readme is None:
                try:
                    text = full.read_text(encoding="utf-8", errors="replace")[:20000]
                except OSError:
                    text = ""
                m = HEADING_RE.search(text)
                readme = {"path": rel, "title": m.group(1).strip() if m else "", "summary": first_paragraph(text)}
    files.sort(key=lambda e: e["path"])
    packages.sort(key=lambda p: p["path"])
    return {
        "commit": gitops.head_commit(str(root)) if gitops.is_repo(str(root)) else None,
        "file_count": len(files),
        "kinds": dict(sorted(kinds.items())),
        "media_files": dict(sorted(media.items())),
        "packages": packages,
        "readme": readme,
        "files": files,
        "truncated": truncated,
    }


def build_index(layout: Layout, ids: Sequence[str] = ()) -> Dict[str, Any]:
    sources = catalog.load_sources(layout)
    result = {"version": INDEX_VERSION, "sources": {}}  # type: Dict[str, Any]
    for src in sources:
        if ids and src["id"] not in ids:
            continue
        entry = index_source(layout, src)
        if entry is not None:
            result["sources"][src["id"]] = entry
    return result


def write_index(layout: Layout, index: Dict[str, Any]) -> Path:
    layout.state_dir.mkdir(parents=True, exist_ok=True)
    tmp = layout.source_index_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(index, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(layout.source_index_path))
    return layout.source_index_path


def load_index(layout: Layout) -> Optional[Dict[str, Any]]:
    try:
        with open(str(layout.source_index_path), "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) and data.get("version") == INDEX_VERSION else None


def cmd_build(layout: Layout, args: argparse.Namespace) -> int:
    index = build_index(layout, args.ids)
    if not index["sources"]:
        print("no sources present in %s; nothing to index. Run: design-sensei setup --full  (or sources sync <id>)" % layout.sources_dir)
    path = write_index(layout, index)
    if args.json:
        print_json({"path": str(path), "sources": {k: v["file_count"] for k, v in index["sources"].items()}})
    else:
        for sid, entry in index["sources"].items():
            kinds = ", ".join("%s %d" % (k, n) for k, n in entry["kinds"].items())
            print("%-20s %6d files  (%s)" % (sid, entry["file_count"], kinds))
        print("\nsource index written to %s" % path)
    return EXIT_OK


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("ids", nargs="*", metavar="ID", help="only index these sources (default: every source present)")
    parser.add_argument("--json", action="store_true")
    add_global_options(parser)
    parser.set_defaults(func=lambda a: run_with_layout(a, cmd_build))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="index_sources.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arguments(parser)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
