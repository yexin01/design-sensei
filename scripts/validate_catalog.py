#!/usr/bin/env python3
"""Validate the catalog: schemas, cross references, licenses and knowledge notes.

``design-sensei catalog validate`` checks

  * catalog/sources.yaml, patterns.yaml and licenses.yaml against their JSON Schemas
  * unique ids, source references, pinned commits and acquisition consistency
  * license / redistribution consistency (a source cannot claim to be redistributable
    with a custom or missing license)
  * every `source-id:path` file reference of every pattern and knowledge note: when a
    source is present in the local library the file must exist at the pinned commit
  * front matter of every note under knowledge/ and the links between notes,
    patterns and sources

Errors make the command exit 1. Warnings do not, unless --strict is given (CI uses it).
"""

from __future__ import annotations

import argparse
import datetime
import glob
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dslib import EXIT_FAILURE, EXIT_OK
from dslib import catalog, gitops, knowledge
from dslib.cli import add_global_options, print_json, run_with_layout
from dslib.jsonschema_lite import SchemaError, validate
from dslib.paths import Layout

# The 18 sources the project was asked to track, normalized (lowercase, no trailing slash / .git).
REQUIRED_SOURCE_URLS = [
    "https://github.com/leonxlnx/taste-skill",
    "https://github.com/google-labs-code/design.md",
    "https://github.com/yihui-dev/awesome-opus5-5-videos",
    "https://styles.refero.design",
    "https://uxplanet.org/50-design-styles-every-designer-should-know-for-better-prompting-56c09d55db62",
    "https://github.com/collidingscopes/liquid-logo",
    "https://github.com/nischayhq/skiper-ui",
    "https://github.com/ashutoshx7/vengeanceui",
    "https://github.com/danielpetho/fancy",
    "https://github.com/davidhdev/react-bits",
    "https://animmasterlib.dev",
    "https://github.com/facebook/astryx",
    "https://github.com/pmndrs/react-three-fiber",
    "https://github.com/dashersw/liquid-glass-js",
    "https://github.com/ruucm/shadergradient",
    "https://github.com/img2threejs/img2threejs",
    "https://github.com/darkroomengineering/lenis",
    "https://github.com/greensock/gsap",
]


class Report(object):
    def __init__(self) -> None:
        self.errors = []  # type: List[str]
        self.warnings = []  # type: List[str]
        self.notes = []  # type: List[str]

    def error(self, where: str, message: str) -> None:
        self.errors.append("%s: %s" % (where, message))

    def warn(self, where: str, message: str) -> None:
        self.warnings.append("%s: %s" % (where, message))

    def note(self, message: str) -> None:
        self.notes.append(message)


def _normalize(url: str) -> str:
    return gitops.normalize_url(url)


def _load(report: Report, layout: Layout, path: Path, schema_name: str) -> Optional[Any]:
    where = path.name
    try:
        data = catalog.load_yaml(path)
    except catalog.CatalogError as exc:
        report.error(where, str(exc))
        return None
    try:
        schema = catalog.load_json(layout.schemas_dir / schema_name)
        problems = validate(data, schema)
    except (catalog.CatalogError, SchemaError) as exc:
        report.error(schema_name, str(exc))
        return None
    for problem in problems:
        report.error(where, problem)
    return data


def _in_sparse_set(rel: str, sparse: List[str]) -> bool:
    return "/" not in rel.rstrip("/") or any(rel == s or rel.startswith(s.rstrip("/") + "/") for s in sparse)


def check_path_reference(layout: Layout, sources: Dict[str, Dict[str, Any]], sid: str, rel: str) -> Tuple[str, str]:
    """Return (state, detail) with state in ok | missing | unchecked | invalid."""
    src = sources.get(sid)
    if src is None:
        return "invalid", "unknown source id %r" % sid
    reason = catalog.unsafe_relative_path(rel)
    if reason:
        return "invalid", "path %r %s" % (rel, reason)
    if src["acquisition_method"] == "reference_only":
        return "invalid", "source %r is reference-only, there are no local files to point at" % sid
    root = layout.source_path(src)
    if not root.is_dir():
        return "unchecked", "source %r is not present locally" % sid
    target = rel.rstrip("/")
    if any(ch in target for ch in "*?["):
        matches = glob.glob(str(root / target))
        return ("ok", "") if matches else ("missing", "glob %r matches nothing in %s" % (rel, sid))
    full = root / target
    if full.exists() or full.is_symlink():
        return "ok", ""
    if src["acquisition_method"] == "git_sparse" and not _in_sparse_set(target, list(src.get("sparse_paths") or [])):
        return "unchecked", "%s is outside the sparse checkout of %s" % (rel, sid)
    return "missing", "%s does not exist in %s at the checked-out commit" % (rel, sid)


def validate_sources(report: Report, layout: Layout, data: Dict[str, Any], strict: bool) -> Dict[str, Dict[str, Any]]:
    sources = data.get("sources", []) if isinstance(data, dict) else []
    index = {}  # type: Dict[str, Dict[str, Any]]
    seen_urls = {}  # type: Dict[str, str]
    seen_paths = {}  # type: Dict[str, str]
    try:
        licenses = catalog.load_licenses(layout)
    except catalog.CatalogError:
        licenses = {}
    policy = (licenses.get("policy", {}) or {}).get("spdx", {}) if isinstance(licenses, dict) else {}
    reviews = {r.get("source_id"): r for r in licenses.get("reviews", []) if isinstance(r, dict)} if isinstance(licenses, dict) else {}
    today = datetime.date.today().isoformat()
    for src in sources:
        if not isinstance(src, dict) or "id" not in src:
            continue
        sid = str(src["id"])
        where = "sources.yaml[%s]" % sid
        if sid in index:
            report.error(where, "duplicate source id")
            continue
        index[sid] = src
        url = _normalize(str(src.get("url", "")))
        if url in seen_urls:
            report.error(where, "duplicate url (also used by %s)" % seen_urls[url])
        seen_urls[url] = sid
        local = str(src.get("local_path", sid))
        if catalog.unsafe_relative_path(local):
            report.error(where, "local_path %r %s" % (local, catalog.unsafe_relative_path(local)))
        if local in seen_paths:
            report.error(where, "local_path %r is also used by %s" % (local, seen_paths[local]))
        seen_paths[local] = sid
        method = src.get("acquisition_method")
        stype = src.get("type")
        if stype in catalog.SOURCE_TYPES_WITHOUT_CLONE and method != "reference_only":
            report.error(where, "type %s cannot be downloaded; acquisition_method must be reference_only" % stype)
        if stype == "git_repository" and method == "reference_only":
            report.note("%s is a git repository registered as reference-only (never cloned)" % sid)
        if method in ("git_shallow", "git_sparse"):
            if stype != "git_repository":
                report.error(where, "acquisition_method %s requires type git_repository" % method)
            if not src.get("pinned_commit"):
                (report.error if strict else report.warn)(where, "git source has no pinned_commit (run: design-sensei sources sync %s --update --write-pins)" % sid)
            if not src.get("default_branch"):
                report.warn(where, "git source has no default_branch")
        if method == "git_sparse":
            paths = src.get("sparse_paths") or []
            if not paths:
                report.error(where, "git_sparse requires a non-empty sparse_paths list")
            for rel in paths:
                reason = catalog.unsafe_relative_path(str(rel))
                if reason:
                    report.error(where, "sparse path %r %s" % (rel, reason))
        elif src.get("sparse_paths"):
            report.error(where, "sparse_paths is only allowed with acquisition_method git_sparse")
        if method == "reference_only" and src.get("pinned_commit") and stype != "git_repository":
            report.error(where, "pinned_commit makes no sense for a %s" % stype)
        lic, lstatus, redis = src.get("license"), src.get("license_status"), src.get("redistribution_status")
        if lstatus == "verified":
            if lic in ("NOASSERTION", "LicenseRef-Custom") or str(lic).startswith("LicenseRef-"):
                report.error(where, "license_status 'verified' needs a concrete SPDX id, not %s" % lic)
            if method == "reference_only":
                report.error(where, "license_status 'verified' is impossible for a reference-only source (no license files are inspected)")
            if lic not in policy:
                report.warn(where, "SPDX id %s is not in the policy table of licenses.yaml" % lic)
        if redis == "redistributable_with_notice":
            if lstatus != "verified":
                report.error(where, "redistribution_status redistributable_with_notice requires license_status verified (is %s)" % lstatus)
            elif lic in policy and policy[lic].get("class") not in ("permissive", "public_domain"):
                report.error(where, "license %s has policy class %s and cannot be redistributable_with_notice" % (lic, policy[lic].get("class")))
        if lstatus in ("custom_terms", "proprietary_terms", "not_found") and redis == "redistributable_with_notice":
            report.error(where, "license_status %s conflicts with redistribution_status redistributable_with_notice" % lstatus)
        if lstatus == "not_found" and redis not in ("unresolved", "reference_only"):
            report.error(where, "a source with no license (not_found) must be unresolved or reference_only")
        if lstatus == "proprietary_terms" and redis != "reference_only":
            report.error(where, "proprietary_terms sources must be reference_only")
        if src.get("last_checked") and str(src["last_checked"]) > today:
            report.error(where, "last_checked %s is in the future" % src["last_checked"])
        if method != "reference_only" and lstatus == "verified":
            review = reviews.get(sid)
            if review is None:
                report.warn(where, "no review entry in licenses.yaml (run: design-sensei licenses scan %s --write)" % sid)
            elif review.get("reviewed_commit") != src.get("pinned_commit"):
                report.warn(where, "license review was done at %s but the pin is %s" % ((review.get("reviewed_commit") or "-")[:7], str(src.get("pinned_commit"))[:7]))
    for sid, review in reviews.items():
        if sid not in index:
            report.error("licenses.yaml[%s]" % sid, "review refers to an unknown source")
    required = set(REQUIRED_SOURCE_URLS)
    missing = sorted(required - set(seen_urls))
    for url in missing:
        (report.error if strict else report.warn)("sources.yaml", "required upstream source missing from the catalog: %s" % url)
    return index


def validate_patterns(report: Report, layout: Layout, data: Dict[str, Any], sources: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    patterns = data.get("patterns", []) if isinstance(data, dict) else []
    index = {}  # type: Dict[str, Dict[str, Any]]
    unchecked = 0
    checked = 0
    for pat in patterns:
        if not isinstance(pat, dict) or "id" not in pat:
            continue
        pid = str(pat["id"])
        where = "patterns.yaml[%s]" % pid
        if pid in index:
            report.error(where, "duplicate pattern id")
            continue
        index[pid] = pat
        sids = list(pat.get("source_ids") or [])
        for sid in sids:
            if sid not in sources:
                report.error(where, "unknown source id %r" % sid)
        if pat.get("provenance") in ("upstream", "mixed") and not sids:
            report.error(where, "provenance %s needs at least one source_ids entry" % pat["provenance"])
        if pat.get("provenance") == "original" and sids:
            report.warn(where, "provenance 'original' lists sources; use 'mixed' if the pattern is informed by them")
        for ref in pat.get("source_paths") or []:
            sid, rel = catalog.split_source_path(str(ref))
            if sid not in sids:
                report.error(where, "source_paths entry %r uses source %r which is not in source_ids" % (ref, sid))
                continue
            state, detail = check_path_reference(layout, sources, sid, rel)
            if state in ("invalid", "missing"):
                report.error(where, "source_paths entry %r: %s" % (ref, detail))
            elif state == "unchecked":
                unchecked += 1
            else:
                checked += 1
        derived = catalog.derive_license_status(sids, sources)
        if "license_status" in pat and pat["license_status"] != derived:
            report.error(where, "license_status %s does not match the status derived from its sources (%s)" % (pat["license_status"], derived))
        status = pat.get("implementation_status")
        for field in ("knowledge_doc", "recipe"):
            rel = pat.get(field)
            if rel:
                if catalog.unsafe_relative_path(str(rel)) or not str(rel).startswith("knowledge/"):
                    report.error(where, "%s %r must be a path under knowledge/" % (field, rel))
                elif not (layout.root / str(rel)).is_file():
                    report.error(where, "%s %r does not exist" % (field, rel))
        if status in ("recipe_available", "verified_example") and not pat.get("recipe"):
            report.error(where, "implementation_status %s requires a recipe path" % status)
        access = pat.get("accessibility") or {}
        if access.get("motion") in ("moderate", "intense") and not access.get("reduced_motion_alternative"):
            report.warn(where, "%s motion without a reduced-motion alternative" % access.get("motion"))
        perf = pat.get("performance") or {}
        if perf.get("gpu_intensity") in ("medium", "high") and not perf.get("fallback_required"):
            report.warn(where, "gpu_intensity %s but fallback_required is false" % perf.get("gpu_intensity"))
    for pid, pat in index.items():
        for rel in pat.get("related") or []:
            if rel not in index:
                report.error("patterns.yaml[%s]" % pid, "related pattern %r does not exist" % rel)
    report.note("%d pattern(s); %d source file reference(s) verified, %d not checkable (source not present or outside sparse checkout)" % (len(index), checked, unchecked))
    return index


def validate_docs(report: Report, layout: Layout, sources: Dict[str, Dict[str, Any]], patterns: Dict[str, Dict[str, Any]]) -> None:
    schema = catalog.load_json(layout.schemas_dir / "knowledge-doc.schema.json")
    docs = knowledge.iter_docs(layout)
    cited = 0
    unchecked = 0
    for doc in docs:
        where = doc.rel
        if doc.error:
            report.error(where, doc.error)
            continue
        for problem in validate(doc.meta, schema):
            report.error(where, problem)
        meta = doc.meta or {}
        for sid in meta.get("source_ids") or []:
            if sid not in sources:
                report.error(where, "front matter source_ids has unknown source %r" % sid)
        for pid in meta.get("pattern_ids") or []:
            if pid not in patterns:
                report.error(where, "front matter pattern_ids has unknown pattern %r" % pid)
        if meta.get("kind") not in ("guide", "index") and not (meta.get("source_ids") or meta.get("pattern_ids")):
            report.warn(where, "note links to no sources or patterns")
        for sid, rel in knowledge.extract_citations(doc.body, sources.keys()):
            state, detail = check_path_reference(layout, sources, sid, rel)
            if state in ("invalid", "missing"):
                report.error(where, "citation `%s:%s`: %s" % (sid, rel, detail))
            elif state == "unchecked":
                unchecked += 1
            else:
                cited += 1
            if sid not in (meta.get("source_ids") or []):
                report.warn(where, "cites source %r that is not in its front matter source_ids" % sid)
    for pid, pat in patterns.items():
        doc_rel = pat.get("knowledge_doc")
        if doc_rel:
            doc = next((d for d in docs if d.rel == doc_rel), None)
            if doc is not None and doc.meta and pid not in (doc.meta.get("pattern_ids") or []):
                report.warn("patterns.yaml[%s]" % pid, "knowledge_doc %s does not list this pattern in its pattern_ids" % doc_rel)
    report.note("%d knowledge note(s); %d file citation(s) verified, %d not checkable" % (len(docs), cited, unchecked))


def check_coverage(report: Report, sources: Dict[str, Dict[str, Any]], patterns: Dict[str, Dict[str, Any]], layout: Layout, strict: bool) -> None:
    used = set()  # type: Set[str]
    for pat in patterns.values():
        used.update(pat.get("source_ids") or [])
    for doc in knowledge.iter_docs(layout):
        if doc.meta:
            used.update(doc.meta.get("source_ids") or [])
    for sid in sources:
        if sid not in used:
            (report.error if strict else report.warn)("sources.yaml[%s]" % sid, "no pattern or knowledge note references this source")


def run_validation(layout: Layout, strict: bool = False, check_docs: bool = True, require_sources: bool = False) -> Report:
    report = Report()
    sources_data = _load(report, layout, layout.sources_yaml, "sources.schema.json")
    pattern_files = layout.pattern_files()
    if not pattern_files:
        report.error("patterns.yaml", "missing file: %s" % layout.patterns_yaml)
    merged = {"patterns": []}  # type: Dict[str, Any]
    for path in pattern_files:
        data = _load(report, layout, path, "patterns.schema.json")
        if isinstance(data, dict) and isinstance(data.get("patterns"), list):
            merged["patterns"].extend(data["patterns"])
    _load(report, layout, layout.licenses_yaml, "licenses.schema.json")
    sources = validate_sources(report, layout, sources_data, strict) if isinstance(sources_data, dict) else {}
    patterns = validate_patterns(report, layout, merged, sources) if merged["patterns"] else {}
    if check_docs and sources:
        validate_docs(report, layout, sources, patterns)
    if sources and patterns:
        check_coverage(report, sources, patterns, layout, strict)
    if require_sources:
        for sid, src in sources.items():
            if src["acquisition_method"] != "reference_only" and not layout.source_path(src).is_dir():
                report.error("sources.yaml[%s]" % sid, "source is not present in the local library (required by --require-sources)")
    report.note("%d source(s)" % len(sources))
    return report


def cmd_validate(layout: Layout, args: argparse.Namespace) -> int:
    report = run_validation(layout, strict=args.strict, check_docs=not args.no_docs, require_sources=args.require_sources)
    failed = bool(report.errors) or (args.strict and bool(report.warnings))
    if args.json:
        print_json({"ok": not failed, "errors": report.errors, "warnings": report.warnings, "notes": report.notes})
    else:
        for line in report.errors:
            print("ERROR   %s" % line)
        for line in report.warnings:
            print("WARNING %s" % line)
        for line in report.notes:
            print("note    %s" % line)
        print("\n%s: %d error(s), %d warning(s)" % ("FAILED" if failed else "OK", len(report.errors), len(report.warnings)))
    return EXIT_FAILURE if failed else EXIT_OK


def add_subcommands(subparsers: "argparse._SubParsersAction") -> None:
    p = subparsers.add_parser("validate", help="validate catalog files and knowledge notes", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--strict", action="store_true", help="treat warnings as errors and require pins, review entries and full source coverage (used by CI)")
    p.add_argument("--no-docs", action="store_true", help="skip knowledge/ note validation")
    p.add_argument("--require-sources", action="store_true", help="fail when a downloadable source is not present locally, so every file reference is verified")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    add_global_options(p)
    p.set_defaults(func=lambda a: run_with_layout(a, cmd_validate))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="validate_catalog.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True
    add_subcommands(sub)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
