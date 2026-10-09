#!/usr/bin/env python3
"""Diagnose a Design Sensei installation.

Checks the Python and git environment, catalog validity, plugin/skill packaging,
the local source library (present, dirty, off-pin, remote mismatch), the freshness of
the file index and the effective configuration. Network is only touched with --online.
Exit code 0 when there are no failures (warnings allowed), 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import index_sources
import sync_sources
import validate_catalog
from dslib import EXIT_FAILURE, EXIT_OK
from dslib import catalog, gitops, knowledge
from dslib.cli import add_global_options, print_json, run_with_layout
from dslib.config import effective_config
from dslib.paths import Layout

OK, WARN, FAIL, INFO = "ok", "warn", "fail", "info"
MIN_PYTHON = (3, 9)
SKILL_DESCRIPTION_LIMIT = 1536


class Check(object):
    def __init__(self, level: str, name: str, message: str, hint: str = ""):
        self.level, self.name, self.message, self.hint = level, name, message, hint

    def as_dict(self) -> Dict[str, str]:
        return {"level": self.level, "name": self.name, "message": self.message, "hint": self.hint}


def check_python() -> List[Check]:
    ver = "%d.%d.%d" % sys.version_info[:3]
    if sys.version_info[:2] < MIN_PYTHON:
        return [Check(FAIL, "python", "Python %s is too old (need %d.%d+)" % (ver, MIN_PYTHON[0], MIN_PYTHON[1]), "install a newer python3")]
    return [Check(OK, "python", "Python %s" % ver)]


def check_git(online: bool) -> List[Check]:
    version = gitops.git_version()
    if not version:
        return [Check(WARN, "git", "git not found on PATH", "install git; without it sources cannot be downloaded (existing sources keep working)")]
    out = [Check(OK, "git", version)]
    if online:
        try:
            sha = gitops.ls_remote("https://github.com/pmndrs/react-three-fiber", "HEAD", attempts=2)
            out.append(Check(OK if sha else WARN, "network", "github.com reachable" if sha else "github.com answered without a HEAD"))
        except gitops.GitError as exc:
            out.append(Check(WARN, "network", "cannot reach github.com: %s" % exc, "sources can only be synced online; use --offline for existing sources"))
    else:
        out.append(Check(INFO, "network", "not checked (use --online)"))
    return out


def check_layout(layout: Layout) -> List[Check]:
    out = [Check(INFO, "toolkit", str(layout.root)), Check(INFO, "library", "%s  (%s)" % (layout.home, layout.home_reason))]
    for name in ("sources.yaml", "patterns.yaml", "licenses.yaml"):
        if not (layout.catalog_dir / name).is_file():
            out.append(Check(FAIL, "catalog", "missing catalog/%s" % name))
    for name in ("sources", "patterns", "licenses", "config", "knowledge-doc"):
        if not (layout.schemas_dir / ("%s.schema.json" % name)).is_file():
            out.append(Check(FAIL, "schemas", "missing catalog/schemas/%s.schema.json" % name))
    probe = layout.home if layout.home.exists() else layout.home.parent
    while not probe.exists() and probe.parent != probe:
        probe = probe.parent
    if not os.access(str(probe), os.W_OK):
        out.append(Check(FAIL, "library", "%s is not writable" % probe, "set DESIGN_SENSEI_HOME to a writable directory"))
    else:
        free = sync_sources.free_mb(layout.home)
        out.append(Check(OK if free > 2048 else WARN, "disk", "%d MB free near the library" % free, "a full library needs roughly 600 MB" if free <= 2048 else ""))
    return out


def check_catalog(layout: Layout) -> List[Check]:
    report = validate_catalog.run_validation(layout, strict=False, check_docs=True)
    if report.errors:
        return [Check(FAIL, "catalog", "%d error(s), first: %s" % (len(report.errors), report.errors[0]), "run: design-sensei catalog validate")]
    msg = "valid (%s)" % report.notes[-1] if report.notes else "valid"
    out = [Check(OK, "catalog", msg)]
    if report.warnings:
        out.append(Check(WARN, "catalog", "%d warning(s); run design-sensei catalog validate" % len(report.warnings)))
    return out


def _frontmatter(path: Path) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    meta, _, error = knowledge.parse_frontmatter(path.read_text(encoding="utf-8"))
    return meta, error


def check_plugin(layout: Layout) -> List[Check]:
    out = []  # type: List[Check]
    plugin_json = layout.root / ".claude-plugin" / "plugin.json"
    market_json = layout.root / ".claude-plugin" / "marketplace.json"
    if not plugin_json.is_file():
        return [Check(WARN, "plugin", ".claude-plugin/plugin.json missing (not a plugin checkout?)")]
    try:
        manifest = json.loads(plugin_json.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [Check(FAIL, "plugin", "plugin.json is not valid JSON: %s" % exc)]
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", str(manifest.get("name", ""))):
        out.append(Check(FAIL, "plugin", "plugin.json name must be kebab-case, got %r" % manifest.get("name")))
    for field in ("version", "description", "license"):
        if not manifest.get(field):
            out.append(Check(WARN, "plugin", "plugin.json has no %s" % field))
    if market_json.is_file():
        try:
            market = json.loads(market_json.read_text(encoding="utf-8"))
            names = [p.get("name") for p in market.get("plugins", [])]
            if manifest.get("name") not in names:
                out.append(Check(FAIL, "marketplace", "marketplace.json does not list plugin %r" % manifest.get("name")))
        except ValueError as exc:
            out.append(Check(FAIL, "marketplace", "marketplace.json is not valid JSON: %s" % exc))
    skill = layout.skill_dir / "SKILL.md"
    if not skill.is_file():
        out.append(Check(FAIL, "skill", "skills/design-sensei/SKILL.md missing"))
    else:
        meta, error = _frontmatter(skill)
        if error or meta is None:
            out.append(Check(FAIL, "skill", "SKILL.md front matter: %s" % error))
        else:
            if meta.get("name") != "design-sensei":
                out.append(Check(FAIL, "skill", "SKILL.md name should be design-sensei, got %r" % meta.get("name")))
            desc = str(meta.get("description", ""))
            if not desc:
                out.append(Check(FAIL, "skill", "SKILL.md has no description"))
            elif len(desc) + len(str(meta.get("when_to_use", ""))) > SKILL_DESCRIPTION_LIMIT:
                out.append(Check(WARN, "skill", "description is longer than %d characters and will be cut in the skill listing" % SKILL_DESCRIPTION_LIMIT))
            lines = len(skill.read_text(encoding="utf-8").splitlines())
            if lines > 500:
                out.append(Check(WARN, "skill", "SKILL.md has %d lines; keep it under 500 and move detail into references/" % lines))
        for ref in re.findall(r"\]\((references/[^)#]+|patterns/[^)#]+|config/[^)#]+)", skill.read_text(encoding="utf-8")):
            if not (layout.skill_dir / ref).exists():
                out.append(Check(FAIL, "skill", "SKILL.md links to missing file %s" % ref))
    shim = layout.skill_dir / "scripts" / "design-sensei"
    for path in (shim, layout.root / "bin" / "design-sensei"):
        if not path.is_file():
            out.append(Check(FAIL, "launcher", "%s missing" % path.relative_to(layout.root)))
        elif not os.access(str(path), os.X_OK):
            out.append(Check(FAIL, "launcher", "%s is not executable" % path.relative_to(layout.root), "chmod +x %s" % path.relative_to(layout.root)))
    if not out:
        out.append(Check(OK, "plugin", "plugin %s v%s, skill and launchers present" % (manifest.get("name"), manifest.get("version"))))
    return out


def check_sources(layout: Layout) -> Tuple[List[Check], int, int]:
    sources = catalog.load_sources(layout)
    out = []  # type: List[Check]
    present = 0
    downloadable = 0
    for s in sources:
        if s["acquisition_method"] == "reference_only":
            continue
        downloadable += 1
        info = sync_sources.source_status(layout, s)
        state = info["state"]
        if state == "missing":
            continue
        present += 1
        if state == "not_git":
            out.append(Check(FAIL, "source:%s" % s["id"], "%s exists but is not a git checkout" % info["path"], "move it away, then: design-sensei sources sync %s" % s["id"]))
        elif state == "remote_mismatch":
            out.append(Check(FAIL, "source:%s" % s["id"], "checkout has a different remote than the catalog", "remove it and sync again"))
        elif state == "dirty":
            out.append(Check(WARN, "source:%s" % s["id"], "%d locally modified file(s); sync will not touch it" % info["dirty_files"]))
        elif state == "off_pin":
            out.append(Check(WARN, "source:%s" % s["id"], "at %s but catalog pins %s" % (info["commit"][:7], str(info["pinned"])[:7]), "design-sensei sources sync %s" % s["id"]))
        elif state == "unpinned":
            out.append(Check(WARN, "source:%s" % s["id"], "no pinned commit in the catalog"))
    mode = "none" if present == 0 else ("all" if present == downloadable else "partial")
    level = OK if present else INFO
    hint = "" if present == downloadable else "download more with: design-sensei sources sync <id>  (or setup --full)"
    out.insert(0, Check(level, "sources", "%d of %d downloadable sources present (%s)" % (present, downloadable, mode), hint))
    return out, present, downloadable


def check_index(layout: Layout, present: int) -> List[Check]:
    index = index_sources.load_index(layout)
    if present == 0:
        return [Check(INFO, "index", "no sources present, nothing to index")]
    if index is None:
        return [Check(WARN, "index", "source index not built yet", "design-sensei index build")]
    stale = []
    for s in catalog.load_sources(layout):
        root = layout.source_path(s)
        if s["acquisition_method"] != "reference_only" and root.is_dir() and gitops.is_repo(str(root)):
            entry = index["sources"].get(s["id"])
            head = gitops.head_commit(str(root))
            if entry is None or entry.get("commit") != head:
                stale.append(s["id"])
    if stale:
        return [Check(WARN, "index", "stale or missing for: %s" % ", ".join(stale), "design-sensei index build")]
    return [Check(OK, "index", "source index current (%d source(s))" % len(index["sources"]))]


def check_config(layout: Layout) -> List[Check]:
    values, origins, problems = effective_config(layout)
    if problems:
        return [Check(FAIL, "config", problems[0], "design-sensei config show")]
    layers = sorted(set(origins.values()) - {"default"})
    return [Check(OK, "config", "effective configuration valid%s" % ((" (overrides from: %s)" % ", ".join(layers)) if layers else " (defaults)"))]


def run_doctor(layout: Layout, online: bool = False) -> Tuple[List[Check], Dict[str, Any]]:
    checks = []  # type: List[Check]
    checks += check_python()
    checks += check_git(online)
    checks += check_layout(layout)
    checks += check_catalog(layout)
    checks += check_plugin(layout)
    source_checks, present, downloadable = check_sources(layout)
    checks += source_checks
    checks += check_index(layout, present)
    checks += check_config(layout)
    summary = {
        "toolkit": str(layout.root), "library": str(layout.home), "library_reason": layout.home_reason,
        "sources_present": present, "sources_downloadable": downloadable,
        "failures": sum(1 for c in checks if c.level == FAIL), "warnings": sum(1 for c in checks if c.level == WARN),
    }
    return checks, summary


def cmd_doctor(layout: Layout, args: argparse.Namespace) -> int:
    checks, summary = run_doctor(layout, online=args.online)
    if args.json:
        print_json({"summary": summary, "checks": [c.as_dict() for c in checks]})
    elif args.brief:
        print("toolkit: %s" % summary["toolkit"])
        print("library: %s (%s)" % (summary["library"], summary["library_reason"]))
        print("sources: %d of %d downloadable present" % (summary["sources_present"], summary["sources_downloadable"]))
        print("status: %d failure(s), %d warning(s)" % (summary["failures"], summary["warnings"]))
        for c in checks:
            if c.level in (FAIL, WARN):
                print("  [%s] %s: %s%s" % (c.level, c.name, c.message, ("  -> " + c.hint) if c.hint else ""))
    else:
        for c in checks:
            print("[%-4s] %-14s %s" % (c.level, c.name, c.message))
            if c.hint and c.level in (WARN, FAIL):
                print("       %s -> %s" % (" " * 14, c.hint))
        print("\n%d failure(s), %d warning(s)" % (summary["failures"], summary["warnings"]))
        if summary["sources_present"] == 0:
            print("Next step: design-sensei setup            (light, on demand)  or  design-sensei setup --full")
    return EXIT_FAILURE if summary["failures"] else EXIT_OK


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--online", action="store_true", help="also check that github.com is reachable")
    parser.add_argument("--brief", action="store_true", help="short summary (used by the skill)")
    parser.add_argument("--json", action="store_true")
    add_global_options(parser)
    parser.set_defaults(func=lambda a: run_with_layout(a, cmd_doctor))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="doctor.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arguments(parser)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
