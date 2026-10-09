#!/usr/bin/env python3
"""Inspect upstream licenses, keep the review ledger and produce the attribution report.

Commands (also ``design-sensei licenses <command>``):

  check    compare catalog claims with the license files found in local clones
  scan     inspect local clones and (with --write) update catalog/licenses.yaml
  report   write the attribution / third-party notice document (ATTRIBUTION.md)

IMPORTANT: license detection here is a *heuristic text match*. It finds well-known
license texts and obvious restrictions, preserves notices and flags disagreement.
It is not legal analysis. Anything marked custom_terms / needs_human_review needs a
person to read the actual license text before code or assets are reused.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dslib import EXIT_FAILURE, EXIT_OK, EXIT_USAGE
from dslib import catalog, gitops, yamlite
from dslib.cli import add_global_options, eprint, fail, format_table, print_json, run_with_layout, short
from dslib.jsonschema_lite import validate
from dslib.paths import Layout
from dslib.textutil import sha256_file

LICENSE_FILE_RE = re.compile(r"^(licen[cs]e|copying|unlicense|copyright)([-_.][\w.-]*)?$", re.IGNORECASE)
NOTICE_FILE_RE = re.compile(r"^notice([-_.][\w.-]*)?$", re.IGNORECASE)
COPYRIGHT_RE = re.compile(r"^\s*(?:copyright\b\s*(?:\(c\)|©)?|\(c\)|©)\s*\d{4}", re.IGNORECASE)
SKIP_DIRS = {".git", "node_modules", "dist", "build", ".next", ".turbo", "vendor", "__pycache__", ".venv"}
MAX_NESTED_DEPTH = 4
MAX_FILES_SCANNED = 20000

# (spdx, required phrases, forbidden phrases). First match wins, so order matters.
SIGNATURES = [
    ("LicenseRef-MIT-Commons-Clause", ["permission is hereby granted, free of charge", "commons clause"], []),
    ("MIT", ["permission is hereby granted, free of charge, to any person obtaining a copy", "the software is provided \"as is\""], ["commons clause"]),
    ("Apache-2.0", ["apache license", "version 2.0, january 2004"], []),
    ("AGPL-3.0", ["gnu affero general public license", "version 3"], []),
    ("LGPL-3.0", ["gnu lesser general public license", "version 3"], []),
    ("GPL-3.0", ["gnu general public license", "version 3, 29 june 2007"], []),
    ("GPL-2.0", ["gnu general public license", "version 2, june 1991"], []),
    ("MPL-2.0", ["mozilla public license version 2.0"], []),
    ("BSD-3-Clause", ["redistribution and use in source and binary forms", "neither the name of"], []),
    ("BSD-2-Clause", ["redistribution and use in source and binary forms", "this list of conditions"], ["neither the name of"]),
    ("ISC", ["permission to use, copy, modify, and/or distribute this software for any purpose with or without fee"], []),
    ("Unlicense", ["this is free and unencumbered software released into the public domain"], []),
    ("CC0-1.0", ["creative commons", "cc0"], []),
    ("CC-BY-NC-4.0", ["creative commons", "noncommercial"], []),
    ("CC-BY-4.0", ["creative commons", "attribution 4.0"], []),
]
RESTRICTION_HINTS = [
    ("commons clause", "Commons Clause: the software may not be sold, sublicensed or redistributed as such"),
    ("noncommercial", "non-commercial restriction"),
    ("non-commercial", "non-commercial restriction"),
    ("no derivative", "no-derivatives restriction"),
    ("all rights reserved", "'All rights reserved' notice present"),
]
MANIFEST_LICENSE_PROBLEMS = ("see license", "unlicensed", "proprietary")


def _norm(text: str) -> str:
    text = text.replace("\u201c", '"').replace("\u201d", '"').replace("\u2018", "'").replace("\u2019", "'")
    return re.sub(r"\s+", " ", text.lower())


def detect_spdx(text: str) -> Tuple[str, List[str]]:
    """Return (spdx-or-LicenseRef-Custom, restriction hints) for a license text."""
    t = _norm(text)
    hints = [msg for needle, msg in RESTRICTION_HINTS if needle in t and msg not in ("'All rights reserved' notice present",)]
    for spdx, required, forbidden in SIGNATURES:
        if all(r in t for r in required) and not any(f in t for f in forbidden):
            return spdx, hints
    return "LicenseRef-Custom", hints


def copyright_lines(text: str, limit: int = 4) -> List[str]:
    out = []  # type: List[str]
    for line in text.splitlines():
        if COPYRIGHT_RE.match(line):
            cleaned = re.sub(r"\s+", " ", line.strip().strip("*#/ "))
            if cleaned not in out:
                out.append(cleaned)
        if len(out) >= limit:
            break
    return out


def find_license_files(root: Path, nested: bool = False) -> List[Path]:
    """License/notice files at the top of ``root`` (or, with ``nested``, anywhere below, depth-limited)."""
    found = []  # type: List[Path]
    if not root.is_dir():
        return found
    if not nested:
        for entry in sorted(root.iterdir()):
            if entry.is_file() and not entry.is_symlink() and (LICENSE_FILE_RE.match(entry.name) or NOTICE_FILE_RE.match(entry.name)):
                found.append(entry)
        return found
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(str(root), followlinks=False):
        rel_depth = len(Path(dirpath).relative_to(root).parts)
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".") and rel_depth < MAX_NESTED_DEPTH)
        for name in sorted(filenames):
            scanned += 1
            full = Path(dirpath) / name
            if rel_depth > 0 and LICENSE_FILE_RE.match(name) and full.is_file() and not full.is_symlink():
                found.append(full)
        if scanned > MAX_FILES_SCANNED:
            break
    return found


def manifest_licenses(root: Path) -> List[str]:
    """License fields declared by package.json files (root and a bounded number of nested ones)."""
    values = []  # type: List[str]
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(str(root), followlinks=False):
        rel_depth = len(Path(dirpath).relative_to(root).parts)
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".") and rel_depth < MAX_NESTED_DEPTH)
        if "package.json" in filenames:
            scanned += 1
            try:
                data = json.loads((Path(dirpath) / "package.json").read_text(encoding="utf-8"))
            except (OSError, ValueError):
                data = None
            if isinstance(data, dict):
                lic = data.get("license")
                if isinstance(lic, dict):
                    lic = lic.get("type")
                if isinstance(lic, str) and lic.strip():
                    values.append(lic.strip())
        if scanned > 400:
            break
    return sorted(set(values))


def scan_source(layout: Layout, src: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Inspect one local clone. Returns None when the source is not present locally."""
    root = layout.source_path(src)
    if src["acquisition_method"] == "reference_only" or not root.is_dir():
        return None
    files = find_license_files(root)
    license_files = []  # type: List[Dict[str, str]]
    detected = []  # type: List[str]
    copyrights = []  # type: List[str]
    restrictions = []  # type: List[str]
    for path in files:
        rel = path.relative_to(root).as_posix()
        license_files.append({"path": rel, "sha256": sha256_file(str(path))})
        if NOTICE_FILE_RE.match(path.name):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        spdx, hints = detect_spdx(text)
        detected.append(spdx)
        for line in copyright_lines(text):
            if line not in copyrights:
                copyrights.append(line)
        for hint in hints:
            if hint not in restrictions:
                restrictions.append(hint)
    nested = []  # type: List[Dict[str, str]]
    for path in find_license_files(root, nested=True)[:40]:
        try:
            spdx, _ = detect_spdx(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        nested.append({"path": path.relative_to(root).as_posix(), "spdx": spdx})
    return {
        "source_id": src["id"],
        "license_files": license_files,
        "spdx_detected": detected[0] if detected else "NONE",
        "all_detected": detected,
        "copyright": copyrights,
        "restrictions": restrictions,
        "package_manifest_licenses": manifest_licenses(root),
        "nested_license_files": nested,
        "commit": gitops.head_commit(str(root)) if gitops.is_repo(str(root)) else None,
    }


# ---------------------------------------------------------------------------
# comparison
# ---------------------------------------------------------------------------

class Finding(object):
    def __init__(self, source_id: str, level: str, code: str, message: str):
        self.source_id, self.level, self.code, self.message = source_id, level, code, message

    def as_dict(self) -> Dict[str, str]:
        return {"source": self.source_id, "level": self.level, "code": self.code, "message": self.message}


def _declared_matches(declared: str, detected: str) -> bool:
    return declared == detected or (declared.startswith("LicenseRef-") and detected == "LicenseRef-Custom")


def check_source(layout: Layout, src: Dict[str, Any], review: Optional[Dict[str, Any]], scan: Optional[Dict[str, Any]]) -> List[Finding]:
    sid = src["id"]
    out = []  # type: List[Finding]
    if src["acquisition_method"] == "reference_only":
        out.append(Finding(sid, "info", "reference_only", "reference-only source: no local license files; terms must be read at %s" % src["url"]))
        if src["license_status"] == "verified":
            out.append(Finding(sid, "error", "claims_verified", "license_status is 'verified' but the source is never downloaded"))
        return out
    if scan is None:
        out.append(Finding(sid, "info", "not_synced", "not present locally; run: design-sensei sources sync %s" % sid))
        return out
    declared = str(src["license"])
    detected = scan["spdx_detected"]
    status = src["license_status"]
    if not scan["license_files"]:
        manifest = scan["package_manifest_licenses"]
        out.append(Finding(sid, "warning" if status != "verified" else "error", "no_license_file",
                           "no license file at the repository root%s" % ("; package manifests declare: %s" % ", ".join(manifest) if manifest else "")))
        if status == "verified":
            out.append(Finding(sid, "error", "claims_verified", "license_status is 'verified' but no license file exists"))
        if declared not in ("NOASSERTION",) and not declared.startswith("LicenseRef-"):
            out.append(Finding(sid, "warning", "declared_without_file", "catalog declares %s but no license file backs it" % declared))
    elif not _declared_matches(declared, detected):
        out.append(Finding(sid, "error", "mismatch", "catalog says %s but the license text looks like %s" % (declared, detected)))
    elif status == "pending_verification":
        out.append(Finding(sid, "warning", "ready_to_verify", "license text matches %s; update license_status once reviewed" % detected))
    if detected == "LicenseRef-Custom" or scan["restrictions"]:
        out.append(Finding(sid, "warning", "needs_human_review", "custom or restrictive terms (%s); read the license text" % (", ".join(scan["restrictions"]) or "unrecognized text")))
    nested_other = sorted({n["spdx"] for n in scan["nested_license_files"] if n["spdx"] != detected})
    if nested_other and scan["license_files"]:
        out.append(Finding(sid, "warning", "nested_licenses", "nested license files with other licenses: %s (see 'scan --json' for paths)" % ", ".join(nested_other)))
    if len(set(scan["all_detected"])) > 1:
        out.append(Finding(sid, "warning", "multiple_root_licenses", "several root license files with different licenses: %s" % ", ".join(sorted(set(scan["all_detected"])))))
    manifests = [m for m in scan["package_manifest_licenses"] if m != declared and not _declared_matches(declared, m)]
    if manifests and scan["license_files"]:
        out.append(Finding(sid, "warning", "manifest_differs", "package manifests declare %s" % ", ".join(manifests)))
    if review is not None:
        stored = {f["path"]: f["sha256"] for f in review.get("license_files", [])}
        current = {f["path"]: f["sha256"] for f in scan["license_files"]}
        if stored != current:
            out.append(Finding(sid, "warning", "license_changed", "license files differ from the recorded review (re-run: design-sensei licenses scan %s --write)" % sid))
        if scan["commit"] and review.get("reviewed_commit") and scan["commit"] != review["reviewed_commit"]:
            out.append(Finding(sid, "warning", "stale_review", "review was done at %s but the checkout is at %s" % (short(review["reviewed_commit"]), short(scan["commit"]))))
    elif scan["license_files"]:
        out.append(Finding(sid, "warning", "no_review_entry", "no entry in catalog/licenses.yaml (run: design-sensei licenses scan %s --write)" % sid))
    return out


def run_check(layout: Layout, ids: Sequence[str]) -> Tuple[List[Finding], Dict[str, Optional[Dict[str, Any]]]]:
    sources = catalog.load_sources(layout)
    selected = [s for s in sources if not ids or s["id"] in ids]
    ledger = {r["source_id"]: r for r in catalog.load_licenses(layout).get("reviews", [])}
    findings = []  # type: List[Finding]
    scans = {}  # type: Dict[str, Optional[Dict[str, Any]]]
    for src in selected:
        scan = scan_source(layout, src)
        scans[src["id"]] = scan
        findings.extend(check_source(layout, src, ledger.get(src["id"]), scan))
    return findings, scans


# ---------------------------------------------------------------------------
# ledger writing
# ---------------------------------------------------------------------------

LEDGER_HEADER = (
    "# License policy and review ledger. Heuristic detection only - NOT legal advice.\n"
    "# `policy` is hand-written. `reviews` is maintained with:\n"
    "#   design-sensei licenses scan --write\n"
    "# which records what was found in each local clone at its pinned commit; human\n"
    "# fields (restrictions, notes, review_status, attribution_required) are preserved.\n"
)


def merge_review(existing: Optional[Dict[str, Any]], scan: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    review = dict(existing or {})
    review["source_id"] = scan["source_id"]
    review["license_files"] = scan["license_files"]
    review["spdx_detected"] = scan["spdx_detected"]
    review["detection"] = "heuristic" if scan["license_files"] else "not_applicable"
    review["copyright"] = scan["copyright"]
    review["package_manifest_licenses"] = scan["package_manifest_licenses"]
    review["reviewed_commit"] = scan["commit"]
    restrictions = list(review.get("restrictions") or [])
    for hint in scan["restrictions"]:
        if hint not in restrictions:
            restrictions.append(hint)
    review["restrictions"] = restrictions
    needs_human = scan["spdx_detected"] in ("LicenseRef-Custom", "NONE") or scan["spdx_detected"].startswith("LicenseRef-") or bool(scan["restrictions"])
    previous = (existing or {}).get("review_status")
    changed = existing is None or {f["path"]: f["sha256"] for f in existing.get("license_files", [])} != {f["path"]: f["sha256"] for f in scan["license_files"]}
    if previous == "human_reviewed" and not changed:
        review["review_status"] = "human_reviewed"
    else:
        review["review_status"] = "needs_human_review" if needs_human else "auto_checked"
    review.setdefault("attribution_required", True)
    review.setdefault("license_url", None)
    ordered = {}  # type: Dict[str, Any]
    for key in ("source_id", "license_files", "license_url", "spdx_detected", "detection", "copyright", "package_manifest_licenses",
                "reviewed_commit", "review_status", "attribution_required", "restrictions", "notes"):
        if key in review:
            ordered[key] = review[key]
    return ordered


def write_ledger(layout: Layout, scans: Dict[str, Optional[Dict[str, Any]]], sources: List[Dict[str, Any]]) -> List[str]:
    data = catalog.load_licenses(layout)
    reviews = {r["source_id"]: r for r in data.get("reviews", [])}
    index = catalog.by_id(sources)
    touched = []  # type: List[str]
    for sid, scan in scans.items():
        if scan is None:
            continue
        reviews[sid] = merge_review(reviews.get(sid), scan, index[sid])  # type: ignore[arg-type]
        touched.append(sid)
    order = [s["id"] for s in sources]
    data["reviews"] = [reviews[i] for i in order if i in reviews]
    schema = catalog.load_json(layout.schemas_dir / "licenses.schema.json")
    errors = validate(data, schema)
    if errors:
        raise catalog.CatalogError("refusing to write an invalid ledger:\n  " + "\n  ".join(errors))
    layout.licenses_yaml.write_text(LEDGER_HEADER + yamlite.dumps(data), encoding="utf-8")
    return touched


# ---------------------------------------------------------------------------
# attribution report
# ---------------------------------------------------------------------------

def render_attribution(layout: Layout) -> str:
    sources = catalog.load_sources(layout)
    ledger = {r["source_id"]: r for r in catalog.load_licenses(layout).get("reviews", [])}
    lines = [
        "# Attribution and third-party notices",
        "",
        "<!-- Generated by `design-sensei licenses report`. Do not edit by hand. -->",
        "",
        "Design Sensei's own code and documentation are MIT licensed (see `LICENSE`).",
        "Design Sensei **does not include or redistribute** any of the upstream projects",
        "below. Git-based sources are cloned on the user's own machine into a local",
        "library (`sources/` or `~/.design-sensei/sources/`), keep their own license",
        "files and copyright notices, and stay out of this repository (`.gitignore`).",
        "Websites and articles are only linked.",
        "",
        "License fields come from heuristic inspection of each project's license files at",
        "the pinned commit. They are a convenience for contributors, **not legal advice**.",
        "Items marked *needs human review* have custom or restrictive terms: read the",
        "upstream license text before copying any code or assets.",
        "",
        "| Source | Type | License | Status | Redistribution | Pinned commit |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for s in sources:
        lines.append("| [%s](%s) | %s | %s | %s | %s | %s |" % (
            s["name"].replace("|", "/"), s["url"], s["type"], s["license"], s["license_status"],
            s["redistribution_status"], ("`%s`" % s["pinned_commit"][:12]) if s.get("pinned_commit") else "-"))
    lines += ["", "## Details", ""]
    for s in sources:
        review = ledger.get(s["id"])
        lines.append("### %s (`%s`)" % (s["name"], s["id"]))
        lines.append("")
        lines.append("- URL: %s" % s["url"])
        lines.append("- Attribution: %s" % s["attribution"])
        lines.append("- License: `%s` (status: %s)" % (s["license"], s["license_status"]))
        lines.append("- Redistribution: %s - %s" % (s["redistribution_status"], catalog.reuse_for(s["redistribution_status"])[1]))
        lines.append("- Acquisition: %s%s" % (s["acquisition_method"], " (sparse: %s)" % ", ".join(s["sparse_paths"]) if s.get("sparse_paths") else ""))
        if review:
            files = ", ".join("`%s`" % f["path"] for f in review.get("license_files", [])) or "none found"
            lines.append("- License files at the pinned commit: %s" % files)
            for c in review.get("copyright", []):
                lines.append("- Copyright notice: %s" % c)
            for r in review.get("restrictions", []):
                lines.append("- Restriction noted: %s" % r)
            lines.append("- Review status: %s" % review.get("review_status", "unknown").replace("_", " "))
            if review.get("notes"):
                lines.append("- Review notes: %s" % " ".join(str(review["notes"]).split()))
        lines.append("- Notes: %s" % " ".join(str(s["notes"]).split()))
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------

def cmd_check(layout: Layout, args: argparse.Namespace) -> int:
    known = {s["id"] for s in catalog.load_sources(layout)}
    unknown = [i for i in args.ids if i not in known]
    if unknown:
        return fail("unknown source id(s): %s" % ", ".join(unknown), EXIT_USAGE)
    findings, scans = run_check(layout, args.ids)
    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]
    if args.json:
        print_json({"findings": [f.as_dict() for f in findings], "scanned": sorted(k for k, v in scans.items() if v)})
    else:
        shown = [f for f in findings if f.level != "info" or args.verbose]
        if shown:
            print(format_table([[f.source_id, f.level.upper(), f.code, f.message] for f in shown], ["SOURCE", "LEVEL", "CODE", "MESSAGE"]))
        scanned = sum(1 for v in scans.values() if v)
        print("\n%d source(s) inspected locally, %d error(s), %d warning(s)." % (scanned, len(errors), len(warnings)))
        print("Heuristic detection only: custom or restrictive licenses need a human to read the text.")
    if errors or (args.strict and warnings):
        return EXIT_FAILURE
    return EXIT_OK


def cmd_scan(layout: Layout, args: argparse.Namespace) -> int:
    sources = catalog.load_sources(layout)
    selected = [s for s in sources if not args.ids or s["id"] in args.ids]
    scans = {s["id"]: scan_source(layout, s) for s in selected}
    if args.write:
        try:
            touched = write_ledger(layout, scans, sources)
        except catalog.CatalogError as exc:
            return fail(str(exc))
        print("updated %d review entr%s in %s: %s" % (len(touched), "y" if len(touched) == 1 else "ies", layout.licenses_yaml.name, ", ".join(touched) or "-"))
        return EXIT_OK
    if args.json:
        print_json({k: v for k, v in scans.items() if v})
        return EXIT_OK
    rows = []
    for sid, scan in scans.items():
        if scan is None:
            rows.append([sid, "-", "not present locally", ""])
            continue
        rows.append([sid, scan["spdx_detected"], ", ".join(f["path"] for f in scan["license_files"]) or "no license file", "; ".join(scan["copyright"][:1])])
    print(format_table(rows, ["SOURCE", "DETECTED", "LICENSE FILES", "COPYRIGHT"]))
    print("\nUse --write to record these results in catalog/licenses.yaml.")
    return EXIT_OK


def cmd_report(layout: Layout, args: argparse.Namespace) -> int:
    text = render_attribution(layout)
    out = Path(args.output) if args.output else layout.root / "ATTRIBUTION.md"
    if args.check:
        current = out.read_text(encoding="utf-8") if out.is_file() else ""
        if current != text:
            eprint("%s is out of date; regenerate it with: design-sensei licenses report" % out)
            return EXIT_FAILURE
        print("%s is up to date" % out)
        return EXIT_OK
    if args.stdout:
        sys.stdout.write(text)
        return EXIT_OK
    out.write_text(text, encoding="utf-8")
    print("wrote %s (%d sources)" % (out, len(catalog.load_sources(layout))))
    return EXIT_OK


def add_subcommands(subparsers: "argparse._SubParsersAction") -> None:
    p = subparsers.add_parser("check", help="compare catalog license claims with local license files",
                              description="Heuristically compare each source's declared license with the license files in its local clone.")
    p.add_argument("ids", nargs="*", metavar="ID")
    p.add_argument("--strict", action="store_true", help="exit 1 on warnings as well as errors")
    p.add_argument("--verbose", action="store_true", help="also show informational findings")
    p.add_argument("--json", action="store_true")
    add_global_options(p)
    p.set_defaults(func=lambda a: run_with_layout(a, cmd_check))

    p = subparsers.add_parser("scan", help="inspect local clones; --write updates catalog/licenses.yaml")
    p.add_argument("ids", nargs="*", metavar="ID")
    p.add_argument("--write", action="store_true", help="record results in the review ledger")
    p.add_argument("--json", action="store_true")
    add_global_options(p)
    p.set_defaults(func=lambda a: run_with_layout(a, cmd_scan))

    p = subparsers.add_parser("report", help="generate ATTRIBUTION.md from the catalog")
    p.add_argument("--output", metavar="FILE", help="default: <repo>/ATTRIBUTION.md")
    p.add_argument("--stdout", action="store_true", help="print instead of writing a file")
    p.add_argument("--check", action="store_true", help="exit 1 if the file on disk is not up to date")
    add_global_options(p)
    p.set_defaults(func=lambda a: run_with_layout(a, cmd_report))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="check_licenses.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True
    add_subcommands(sub)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
