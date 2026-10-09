#!/usr/bin/env python3
"""Acquire, pin and inspect the upstream sources of the local library.

Commands (also available as ``design-sensei sources <command>``):

  list    show every source in the catalog
  sync    download or update sources (pinned commits, non-destructive)
  status  compare local checkouts with the catalog pins (and optionally upstream)
  show    everything known about one source

Safety rules enforced here:
  * only https URLs are cloned (file:// only with --allow-local-urls, for tests)
  * a checkout with local modifications, an unrelated directory or a different
    remote is reported and never touched
  * downloads happen in a temporary directory and are renamed into place only on
    success, so an interrupted sync never leaves a half-initialized source behind
  * no script from an upstream repository is ever executed
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dslib import (EXIT_ENVIRONMENT, EXIT_FAILURE, EXIT_OK, EXIT_PARTIAL, EXIT_USAGE)
from dslib import catalog, gitops
from dslib.cli import (add_global_options, csv_list, eprint, fail, format_table, print_json, run_with_layout, short)
from dslib.config import effective_config
from dslib.paths import Layout

ACQUIRED = "acquired"
UPDATED = "updated"
UP_TO_DATE = "up_to_date"
REFERENCE_ONLY = "reference_only"
SKIPPED_OFFLINE = "skipped_offline"
BLOCKED = "blocked"
FAILED = "failed"
WOULD_ACQUIRE = "would_acquire"
WOULD_UPDATE = "would_update"

OK_STATUSES = (ACQUIRED, UPDATED, UP_TO_DATE, REFERENCE_ONLY, WOULD_ACQUIRE, WOULD_UPDATE)
PROBLEM_STATUSES = (BLOCKED, FAILED)


class SyncOptions(object):
    def __init__(
        self,
        update: bool = False,
        offline: bool = False,
        dry_run: bool = False,
        allow_local_urls: bool = False,
        min_free_mb: int = 1024,
        retries: int = 3,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.update = update
        self.offline = offline
        self.dry_run = dry_run
        self.allow_local_urls = allow_local_urls
        self.min_free_mb = min_free_mb
        self.retries = retries
        self.sleep = sleep


class SyncResult(object):
    def __init__(self, source_id: str, status: str, message: str, commit: Optional[str] = None, kind: Optional[str] = None, path: Optional[Path] = None):
        self.id = source_id
        self.status = status
        self.message = message
        self.commit = commit
        self.kind = kind  # failure kind: network | not_found | auth | timeout | disk | missing_git | git_error | policy
        self.path = path

    def as_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "status": self.status, "message": self.message, "commit": self.commit, "kind": self.kind, "path": str(self.path) if self.path else None}


# ---------------------------------------------------------------------------
# lock file (local state; never committed)
# ---------------------------------------------------------------------------

def read_lock(layout: Layout) -> Dict[str, Any]:
    try:
        with open(str(layout.lock_path), "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict) and isinstance(data.get("sources"), dict):
            return data
    except (OSError, ValueError):
        pass
    return {"version": 1, "sources": {}}


def write_lock(layout: Layout, lock: Dict[str, Any]) -> None:
    layout.state_dir.mkdir(parents=True, exist_ok=True)
    tmp = layout.lock_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(layout.lock_path))


def record_lock(layout: Layout, src: Dict[str, Any], result: SyncResult) -> None:
    lock = read_lock(layout)
    lock["sources"][src["id"]] = {
        "commit": result.commit,
        "url": src["url"],
        "method": src["acquisition_method"],
        "sparse_paths": sorted(src.get("sparse_paths") or []),
        "synced_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    write_lock(layout, lock)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def free_mb(path: Path) -> float:
    probe = path
    while not probe.exists() and probe.parent != probe:
        probe = probe.parent
    return shutil.disk_usage(str(probe)).free / (1024.0 * 1024.0)


def _url_allowed(url: str, opts: SyncOptions) -> Optional[str]:
    if url.startswith("https://"):
        return None
    if url.startswith("file://") and opts.allow_local_urls:
        return None
    return "refusing to clone %r: only https URLs are allowed (file:// needs --allow-local-urls)" % url


def _sparse_paths(src: Dict[str, Any]) -> List[str]:
    if src.get("acquisition_method") != "git_sparse":
        return []
    return list(src.get("sparse_paths") or [])


def _fetch(tmp_or_dest: str, src: Dict[str, Any], ref: str, opts: SyncOptions, depth: int = 1) -> None:
    sparse = bool(_sparse_paths(src))
    args = ["fetch", "-q", "--depth", str(depth)]
    if sparse:
        args.append("--filter=blob:none")
    args += ["origin", ref]
    gitops.with_retries(lambda: gitops.run_git(args, cwd=tmp_or_dest), attempts=opts.retries, sleep=opts.sleep)


def _fetch_commit(path: str, src: Dict[str, Any], sha: str, opts: SyncOptions) -> None:
    """Make ``sha`` available locally: fetch it by hash, fall back to the branch history."""
    try:
        _fetch(path, src, sha, opts)
        return
    except gitops.GitError as exc:
        if exc.kind in ("network", "timeout", "auth", "missing_git"):
            raise
    branch = src.get("default_branch") or "HEAD"
    _fetch(path, src, branch, opts, depth=1)
    if gitops.has_commit(path, sha):
        return
    _fetch(path, src, branch, opts, depth=400)
    if not gitops.has_commit(path, sha):
        raise gitops.GitError(
            "pinned commit %s is not reachable from %s; it may have been rewritten upstream. Run with --update to move the pin." % (short(sha), branch),
            1, "", "not_found",
        )


def resolve_target(src: Dict[str, Any], opts: SyncOptions) -> str:
    """Commit to check out: the pin, or (with --update / no pin) the tip of the default branch."""
    pin = src.get("pinned_commit")
    if pin and not opts.update:
        return str(pin)
    branch = src.get("default_branch")
    ref = "refs/heads/%s" % branch if branch else "HEAD"
    sha = gitops.ls_remote(src["url"], ref, attempts=opts.retries)
    if not sha and branch:
        sha = gitops.ls_remote(src["url"], "HEAD", attempts=opts.retries)
    if not sha:
        raise gitops.GitError("could not resolve %s on %s" % (ref, src["url"]), 1, "", "not_found")
    return sha


def _apply_sparse(path: str, src: Dict[str, Any]) -> None:
    paths = _sparse_paths(src)
    if paths:
        gitops.run_git(["sparse-checkout", "init", "--cone"], cwd=path)
        gitops.run_git(["sparse-checkout", "set", "--cone"] + paths, cwd=path)


# ---------------------------------------------------------------------------
# core: sync one source
# ---------------------------------------------------------------------------

def sync_one(layout: Layout, src: Dict[str, Any], opts: SyncOptions) -> SyncResult:
    sid = src["id"]
    method = src["acquisition_method"]
    dest = layout.source_path(src)
    if method == "reference_only":
        return SyncResult(sid, REFERENCE_ONLY, "reference-only source: nothing is downloaded (%s)" % src["url"])
    bad_url = _url_allowed(src["url"], opts)
    if bad_url:
        return SyncResult(sid, FAILED, bad_url, kind="policy")
    for rel in _sparse_paths(src):
        reason = catalog.unsafe_relative_path(rel)
        if reason:
            return SyncResult(sid, FAILED, "invalid sparse path %r: %s" % (rel, reason), kind="policy")
    try:
        if gitops.git_executable() is None and not (opts.offline and not dest.exists()):
            return SyncResult(sid, FAILED, "git is not installed or not on PATH", kind="missing_git")
        if dest.exists() or dest.is_symlink():
            return _sync_existing(layout, src, dest, opts)
        return _acquire_fresh(layout, src, dest, opts)
    except gitops.GitError as exc:
        return SyncResult(sid, FAILED, str(exc), kind=exc.kind, path=dest)
    except OSError as exc:
        return SyncResult(sid, FAILED, "filesystem error: %s" % exc, kind="git_error", path=dest)


def _acquire_fresh(layout: Layout, src: Dict[str, Any], dest: Path, opts: SyncOptions) -> SyncResult:
    sid = src["id"]
    if opts.offline:
        return SyncResult(sid, SKIPPED_OFFLINE, "not present locally and offline mode is on", kind="offline", path=dest)
    if opts.dry_run:
        return SyncResult(sid, WOULD_ACQUIRE, "would clone %s at %s" % (src["url"], short(src.get("pinned_commit")) if src.get("pinned_commit") else "default branch tip"), path=dest)
    free = free_mb(dest.parent)
    if free < opts.min_free_mb:
        return SyncResult(sid, FAILED, "only %d MB free in %s (need %d MB); free space or lower --min-free-mb" % (free, dest.parent, opts.min_free_mb), kind="disk", path=dest)
    sha = resolve_target(src, opts)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / (".%s.partial-%d" % (dest.name, os.getpid()))
    if tmp.exists():
        shutil.rmtree(str(tmp))
    try:
        gitops.run_git(["init", "-q", str(tmp)])
        gitops.run_git(["remote", "add", "origin", src["url"]], cwd=str(tmp))
        _apply_sparse(str(tmp), src)
        _fetch_commit(str(tmp), src, sha, opts)
        gitops.run_git(["checkout", "-q", "--detach", sha], cwd=str(tmp))
        head = gitops.head_commit(str(tmp))
        if head != sha:
            raise gitops.GitError("checked out %s but expected %s" % (short(head), short(sha)), 1, "", "git_error")
        os.rename(str(tmp), str(dest))
    except BaseException:
        shutil.rmtree(str(tmp), ignore_errors=True)
        raise
    note = "sparse: %s" % ", ".join(_sparse_paths(src)) if _sparse_paths(src) else "shallow clone"
    return SyncResult(sid, ACQUIRED, "%s at %s (%s)" % (src["url"], short(sha), note), commit=sha, path=dest)


def _sync_existing(layout: Layout, src: Dict[str, Any], dest: Path, opts: SyncOptions) -> SyncResult:
    sid = src["id"]
    if not dest.is_dir() or not gitops.is_repo(str(dest)):
        return SyncResult(sid, BLOCKED, "%s exists but is not a git checkout; move it away or change local_path (left untouched)" % dest, kind="policy", path=dest)
    remote = gitops.remote_url(str(dest))
    if remote is None or gitops.normalize_url(remote) != gitops.normalize_url(src["url"]):
        return SyncResult(sid, BLOCKED, "%s has remote %s, expected %s (left untouched)" % (dest, remote or "<none>", src["url"]), kind="policy", path=dest)
    changes = gitops.tracked_changes(str(dest))
    head = gitops.head_commit(str(dest))
    if changes:
        return SyncResult(sid, BLOCKED, "%d locally modified file(s) in %s; commit or discard them yourself (left untouched)" % (len(changes), dest), commit=head, kind="policy", path=dest)
    wanted_pin = src.get("pinned_commit")
    if opts.offline:
        if wanted_pin and head != wanted_pin:
            return SyncResult(sid, SKIPPED_OFFLINE, "local checkout is at %s, pin is %s; offline mode so not updated" % (short(head), short(wanted_pin)), commit=head, kind="offline", path=dest)
        return SyncResult(sid, UP_TO_DATE, "present at %s (offline, not checked against upstream)" % short(head), commit=head, path=dest)
    sha = resolve_target(src, opts)
    sparse_ok = sorted(_sparse_paths(src)) == gitops.sparse_list(str(dest))
    if head == sha and sparse_ok:
        return SyncResult(sid, UP_TO_DATE, "already at %s" % short(sha), commit=sha, path=dest)
    if opts.dry_run:
        return SyncResult(sid, WOULD_UPDATE, "would move %s -> %s" % (short(head), short(sha)), commit=head, path=dest)
    if not sparse_ok:
        if _sparse_paths(src):
            _apply_sparse(str(dest), src)
        else:
            gitops.run_git(["sparse-checkout", "disable"], cwd=str(dest), check=False)
    if head != sha:
        _fetch_commit(str(dest), src, sha, opts)
        gitops.run_git(["checkout", "-q", "--detach", sha], cwd=str(dest))
    new_head = gitops.head_commit(str(dest))
    if new_head != sha:
        raise gitops.GitError("checked out %s but expected %s" % (short(new_head), short(sha)), 1, "", "git_error")
    return SyncResult(sid, UPDATED, "%s -> %s" % (short(head), short(sha)), commit=sha, path=dest)


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

def source_status(layout: Layout, src: Dict[str, Any], check_upstream: bool = False, retries: int = 2) -> Dict[str, Any]:
    dest = layout.source_path(src)
    lock = read_lock(layout)["sources"].get(src["id"], {})
    info = {
        "id": src["id"], "method": src["acquisition_method"], "path": str(dest), "pinned": src.get("pinned_commit"),
        "commit": None, "state": "missing", "dirty_files": 0, "upstream_commit": None, "upstream": None,
        "synced_at": lock.get("synced_at"),
    }  # type: Dict[str, Any]
    if src["acquisition_method"] == "reference_only":
        info["state"] = "reference_only"
        return info
    if dest.exists():
        if not gitops.is_repo(str(dest)):
            info["state"] = "not_git"
            return info
        head = gitops.head_commit(str(dest))
        info["commit"] = head
        try:
            info["dirty_files"] = len(gitops.tracked_changes(str(dest)))
        except gitops.GitError:
            info["dirty_files"] = -1
        if info["dirty_files"]:
            info["state"] = "dirty"
        elif not src.get("pinned_commit"):
            info["state"] = "unpinned"
        elif head == src.get("pinned_commit"):
            info["state"] = "at_pin"
        else:
            info["state"] = "off_pin"
        remote = gitops.remote_url(str(dest))
        if remote and gitops.normalize_url(remote) != gitops.normalize_url(src["url"]):
            info["state"] = "remote_mismatch"
    if check_upstream and gitops.git_executable():
        branch = src.get("default_branch")
        try:
            upstream = gitops.ls_remote(src["url"], "refs/heads/%s" % branch if branch else "HEAD", attempts=retries)
        except gitops.GitError:
            upstream = None
            info["upstream"] = "unreachable"
        if upstream:
            info["upstream_commit"] = upstream
            reference = src.get("pinned_commit") or info["commit"]
            info["upstream"] = "same_as_pin" if reference == upstream else "ahead_of_pin"
    return info


# ---------------------------------------------------------------------------
# selection and exit codes
# ---------------------------------------------------------------------------

def select_sources(all_sources: List[Dict[str, Any]], ids: Sequence[str], select_all: bool) -> List[Dict[str, Any]]:
    if select_all or not ids:
        return list(all_sources)
    index = catalog.by_id(all_sources)
    unknown = [i for i in ids if i not in index]
    if unknown:
        raise KeyError("unknown source id(s): %s (see: design-sensei sources list)" % ", ".join(unknown))
    return [index[i] for i in ids]  # type: ignore[misc]


def exit_code_for(results: Sequence[SyncResult]) -> int:
    ok = [r for r in results if r.status in OK_STATUSES]
    problems = [r for r in results if r.status in PROBLEM_STATUSES]
    offline = [r for r in results if r.status == SKIPPED_OFFLINE]
    if not problems and not offline:
        return EXIT_OK
    if not problems and offline:
        return EXIT_PARTIAL if ok else EXIT_ENVIRONMENT
    if all(r.kind in ("missing_git",) for r in problems) and not ok:
        return EXIT_ENVIRONMENT
    return EXIT_PARTIAL if ok else EXIT_FAILURE


def sync_many(layout: Layout, sources: List[Dict[str, Any]], opts: SyncOptions, jobs: int = 4, record: bool = True) -> List[SyncResult]:
    jobs = max(1, min(jobs, len(sources) or 1))
    if jobs == 1:
        results = [sync_one(layout, s, opts) for s in sources]
    else:
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            results = list(pool.map(lambda s: sync_one(layout, s, opts), sources))
    if record and not opts.dry_run:
        by_source = catalog.by_id(sources)
        for res in results:
            if res.status in (ACQUIRED, UPDATED, UP_TO_DATE) and res.commit:
                record_lock(layout, by_source[res.id], res)  # type: ignore[arg-type]
    return results


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------

def _offline_requested(layout: Layout, args: argparse.Namespace) -> bool:
    if getattr(args, "online", False):
        return False
    if getattr(args, "offline", False) or os.environ.get("DESIGN_SENSEI_OFFLINE") == "1":
        return True
    try:
        values, _, _ = effective_config(layout)
    except Exception:  # config problems must not block syncing
        return False
    return values.get("source_acquisition_mode") == "offline"


def cmd_list(layout: Layout, args: argparse.Namespace) -> int:
    sources = catalog.load_sources(layout)
    rows = []
    out = []
    for s in sources:
        if args.category and s["category"] != args.category:
            continue
        if args.method and s["acquisition_method"] != args.method:
            continue
        status = source_status(layout, s)
        present = "-" if status["state"] == "reference_only" else ("yes" if status["commit"] else "no")
        if args.present and present != "yes":
            continue
        if args.missing and present != "no":
            continue
        out.append(dict(s, local_state=status["state"], local_commit=status["commit"]))
        rows.append([s["id"], s["category"], s["acquisition_method"], s["license"], s["license_status"], s["redistribution_status"], present, s["name"]])
    if args.json:
        print_json(out)
    else:
        print(format_table(rows, ["ID", "CATEGORY", "METHOD", "LICENSE", "LICENSE STATUS", "REDISTRIBUTION", "LOCAL", "NAME"]))
        print("\n%d source(s). Library: %s" % (len(rows), layout.sources_dir))
    return EXIT_OK


def cmd_sync(layout: Layout, args: argparse.Namespace) -> int:
    all_sources = catalog.load_sources(layout)
    try:
        selected = select_sources(all_sources, args.ids, args.all)
    except KeyError as exc:
        return fail(str(exc.args[0]), EXIT_USAGE)
    if args.update and args.offline:
        return fail("--update needs the network; drop --offline", EXIT_USAGE)
    opts = SyncOptions(
        update=args.update, offline=_offline_requested(layout, args), dry_run=args.dry_run,
        allow_local_urls=args.allow_local_urls, min_free_mb=args.min_free_mb, retries=args.retries,
    )
    if opts.offline:
        eprint("offline mode: the network will not be used")
    results = sync_many(layout, selected, opts, jobs=args.jobs)
    pins_written = []  # type: List[str]
    if args.write_pins and not args.dry_run:
        today = datetime.date.today().isoformat()
        by_source = catalog.by_id(selected)
        for res in results:
            src = by_source[res.id]
            if res.status in (ACQUIRED, UPDATED, UP_TO_DATE) and res.commit and src.get("pinned_commit") != res.commit:
                catalog.update_source_fields(layout.sources_yaml, res.id, {"pinned_commit": res.commit, "last_checked": today})
                pins_written.append(res.id)
    if args.json:
        print_json({"results": [r.as_dict() for r in results], "pins_written": pins_written})
    else:
        rows = [[r.id, r.status, short(r.commit), r.message] for r in results]
        print(format_table(rows, ["ID", "RESULT", "COMMIT", "DETAIL"]))
        counts = {}  # type: Dict[str, int]
        for r in results:
            counts[r.status] = counts.get(r.status, 0) + 1
        print("\n" + ", ".join("%d %s" % (n, s.replace("_", " ")) for s, n in sorted(counts.items())))
        if pins_written:
            print("pins written to %s: %s" % (layout.sources_yaml.name, ", ".join(pins_written)))
        for r in results:
            if r.status in PROBLEM_STATUSES or r.status == SKIPPED_OFFLINE:
                eprint("%s: %s" % (r.id, r.message))
    return exit_code_for(results)


def cmd_status(layout: Layout, args: argparse.Namespace) -> int:
    sources = catalog.load_sources(layout)
    try:
        selected = select_sources(sources, args.ids, False)
    except KeyError as exc:
        return fail(str(exc.args[0]), EXIT_USAGE)
    check = args.check_upstream and not _offline_requested(layout, args)
    infos = [source_status(layout, s, check_upstream=check) for s in selected]
    if args.json:
        print_json(infos)
    else:
        rows = []
        for i in infos:
            detail = i["state"]
            if i["dirty_files"]:
                detail += " (%d modified)" % i["dirty_files"]
            if i["upstream"]:
                detail += "; upstream " + i["upstream"].replace("_", " ")
                if i["upstream"] == "ahead_of_pin":
                    detail += " (%s)" % short(i["upstream_commit"])
            rows.append([i["id"], i["method"], short(i["commit"]), short(i["pinned"]), detail])
        print(format_table(rows, ["ID", "METHOD", "LOCAL", "PIN", "STATE"]))
        present = sum(1 for i in infos if i["commit"])
        clonable = sum(1 for i in infos if i["method"] != "reference_only")
        print("\n%d of %d downloadable source(s) present in %s" % (present, clonable, layout.sources_dir))
        if check is False and args.check_upstream:
            print("(offline: upstream not checked)")
    bad = [i for i in infos if i["state"] in ("not_git", "remote_mismatch")]
    return EXIT_FAILURE if bad else EXIT_OK


def cmd_show(layout: Layout, args: argparse.Namespace) -> int:
    sources = catalog.load_sources(layout)
    index = catalog.by_id(sources)
    src = index.get(args.id)
    if src is None:
        return fail("unknown source id %r (see: design-sensei sources list)" % args.id, EXIT_USAGE)
    status = source_status(layout, src, check_upstream=False)  # type: ignore[arg-type]
    review = None
    try:
        for r in catalog.load_licenses(layout).get("reviews", []):
            if r.get("source_id") == args.id:
                review = r
    except catalog.CatalogError:
        pass
    patterns = [p["id"] for p in catalog.load_patterns(layout) if args.id in (p.get("source_ids") or [])]
    reuse = catalog.reuse_for(str(src["redistribution_status"]))
    if args.json:
        print_json({"source": src, "local": status, "license_review": review, "pattern_ids": patterns, "reuse": {"class": reuse[0], "guidance": reuse[1]}})
        return EXIT_OK
    print("%s  (%s)" % (src["name"], src["id"]))
    print("  url:            %s" % src["url"])
    print("  type/category:  %s / %s" % (src["type"], src["category"]))
    print("  acquisition:    %s%s" % (src["acquisition_method"], " -> " + ", ".join(src.get("sparse_paths") or []) if src.get("sparse_paths") else ""))
    print("  pinned commit:  %s (branch %s, last checked %s)" % (src.get("pinned_commit") or "-", src.get("default_branch") or "-", src.get("last_checked") or "-"))
    print("  license:        %s [%s]" % (src["license"], src["license_status"]))
    print("  redistribution: %s" % src["redistribution_status"])
    print("  reuse:          %s - %s" % reuse)
    print("  attribution:    %s" % src["attribution"])
    print("  inspection:     %s" % src["inspection_status"])
    print("  frameworks:     %s" % (", ".join(src["frameworks"]) or "-"))
    print("  tags:           %s" % (", ".join(src["tags"]) or "-"))
    print("  local:          %s (%s)" % (status["state"], status["path"]))
    if status["commit"]:
        print("  local commit:   %s" % status["commit"])
    if review:
        print("  license files:  %s" % (", ".join(f["path"] for f in review.get("license_files", [])) or "-"))
        print("  review:         %s (detected %s)" % (review.get("review_status"), review.get("spdx_detected")))
        for line in review.get("copyright", []):
            print("  copyright:      %s" % line)
        for line in review.get("restrictions", []):
            print("  restriction:    %s" % line)
    print("  patterns:       %s" % (", ".join(patterns) or "-"))
    print("  notes:          %s" % " ".join(str(src["notes"]).split()))
    return EXIT_OK


# ---------------------------------------------------------------------------
# argparse wiring
# ---------------------------------------------------------------------------

def add_subcommands(subparsers: "argparse._SubParsersAction") -> None:
    p = subparsers.add_parser("list", help="list catalog sources", description="List every source in catalog/sources.yaml with its local state.")
    p.add_argument("--category", choices=["design_intelligence", "ui_components", "graphics_3d", "animation"])
    p.add_argument("--method", choices=["git_shallow", "git_sparse", "reference_only"])
    group = p.add_mutually_exclusive_group()
    group.add_argument("--present", action="store_true", help="only sources present locally")
    group.add_argument("--missing", action="store_true", help="only downloadable sources not yet present")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    add_global_options(p)
    p.set_defaults(func=lambda a: run_with_layout(a, cmd_list))

    p = subparsers.add_parser(
        "sync", help="download or update sources",
        description="Download (or update) sources into the local library at the commits pinned in catalog/sources.yaml. "
                    "Existing checkouts with local changes are never modified.",
    )
    p.add_argument("ids", nargs="*", metavar="ID", help="source ids (default with --all: every source)")
    p.add_argument("--all", action="store_true", help="sync every source")
    p.add_argument("--update", action="store_true", help="move to the tip of the upstream default branch instead of the pin")
    p.add_argument("--write-pins", action="store_true", help="write the resolved commit and today's date back to catalog/sources.yaml")
    p.add_argument("--offline", action="store_true", help="never use the network; only report what is present")
    p.add_argument("--online", action="store_true", help="override source_acquisition_mode: offline from the config")
    p.add_argument("--dry-run", action="store_true", help="show what would happen without changing anything")
    p.add_argument("--jobs", type=int, default=4, metavar="N", help="parallel downloads (default 4)")
    p.add_argument("--retries", type=int, default=3, metavar="N", help="attempts for transient network failures (default 3)")
    p.add_argument("--min-free-mb", type=int, default=1024, metavar="MB", help="refuse to download below this much free disk space (default 1024)")
    p.add_argument("--allow-local-urls", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--json", action="store_true", help="machine-readable output")
    add_global_options(p)
    p.set_defaults(func=lambda a: run_with_layout(a, cmd_sync))

    p = subparsers.add_parser("status", help="show local state of sources", description="Compare local checkouts with the catalog pins.")
    p.add_argument("ids", nargs="*", metavar="ID")
    p.add_argument("--check-upstream", action="store_true", help="also ask the remote whether the default branch moved past the pin")
    p.add_argument("--offline", action="store_true")
    p.add_argument("--online", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--json", action="store_true")
    add_global_options(p)
    p.set_defaults(func=lambda a: run_with_layout(a, cmd_status))

    p = subparsers.add_parser("show", help="show everything known about one source")
    p.add_argument("id", metavar="ID")
    p.add_argument("--json", action="store_true")
    add_global_options(p)
    p.set_defaults(func=lambda a: run_with_layout(a, cmd_show))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="sync_sources.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True
    add_subcommands(sub)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
