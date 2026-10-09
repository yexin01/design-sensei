#!/usr/bin/env python3
"""design-sensei: design intelligence toolkit for Claude Code.

Typical use:
  design-sensei doctor                      check the installation
  design-sensei setup [--full]              prepare the local source library
  design-sensei search "liquid glass"       find patterns, notes and real files
  design-sensei recommend "liquid glass hero for a fintech"   one-call style + pattern recommendation
  design-sensei sources sync lenis          download one upstream source
  design-sensei eval ./my-site              static design evaluation of a project

Run `design-sensei COMMAND --help` for the options of each command.

Exit codes: 0 success, 1 failure or validation errors, 2 usage error,
3 partial success (some sources failed), 4 required tool or network unavailable.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_index
import build_portable_skill
import check_licenses
import design_eval
import doctor
import read_doc
import recommend
import search_patterns
import sync_sources
import token_report
import validate_catalog
from dslib import (EXIT_ENVIRONMENT, EXIT_FAILURE, EXIT_OK, EXIT_PARTIAL, EXIT_USAGE, __version__)
from dslib import catalog, config as ds_config, gitops
from dslib.cli import add_global_options, csv_list, eprint, fail, print_json, run_with_layout
from dslib.paths import Layout


def cmd_setup(layout: Layout, args: argparse.Namespace) -> int:
    print("toolkit: %s" % layout.root)
    print("library: %s  (%s)" % (layout.home, layout.home_reason))
    report = validate_catalog.run_validation(layout, strict=False, check_docs=True)
    if report.errors:
        for line in report.errors[:10]:
            eprint("ERROR " + line)
        return fail("the catalog is invalid (%d error(s)); fix it before setting up" % len(report.errors))
    print("catalog: valid (%s)" % (report.notes[-1] if report.notes else "ok"))
    try:
        layout.sources_dir.mkdir(parents=True, exist_ok=True)
        layout.state_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return fail("cannot create the library at %s: %s (set DESIGN_SENSEI_HOME to a writable directory)" % (layout.home, exc), EXIT_ENVIRONMENT)
    all_sources = catalog.load_sources(layout)
    if args.sources:
        wanted = csv_list(args.sources)
        unknown = [w for w in wanted if w not in {s["id"] for s in all_sources}]
        if unknown:
            return fail("unknown source id(s): %s" % ", ".join(unknown), EXIT_USAGE)
        selected = [s for s in all_sources if s["id"] in wanted]
    elif args.full:
        selected = all_sources
    else:
        selected = []
    code = EXIT_OK
    if selected:
        if gitops.git_executable() is None:
            return fail("git is required to download sources but was not found on PATH", EXIT_ENVIRONMENT)
        opts = sync_sources.SyncOptions(offline=args.offline, min_free_mb=args.min_free_mb)
        results = sync_sources.sync_many(layout, selected, opts, jobs=args.jobs)
        for r in results:
            print("  %-26s %-15s %s" % (r.id, r.status, r.message))
        code = sync_sources.exit_code_for(results)
    else:
        print("sources: light setup, nothing downloaded. Sources are fetched on demand:")
        print("         design-sensei sources sync <id>      (design-sensei sources list)")
    import index_sources
    index = index_sources.build_index(layout)
    index_sources.write_index(layout, index)
    total = sum(e["file_count"] for e in index["sources"].values())
    print("index: %d source(s), %d file(s) indexed" % (len(index["sources"]), total))
    print("\nNext:")
    print("  design-sensei doctor")
    print("  design-sensei search \"liquid glass button\"")
    if not args.full and not args.sources:
        print("  design-sensei setup --full          (optional: download every source, about 300 MB)")
    return code


def cmd_config_show(layout: Layout, args: argparse.Namespace) -> int:
    project = Path(args.project).resolve() if args.project else None
    values, origins, problems = ds_config.effective_config(layout, project)
    if problems:
        for p in problems:
            eprint("config problem: %s" % p)
        return EXIT_FAILURE
    if args.json:
        print_json({"config": values, "origins": origins})
    else:
        sys.stdout.write(ds_config.render(values, origins))
    return EXIT_OK


def cmd_config_init(layout: Layout, args: argparse.Namespace) -> int:
    target = (Path(args.project).resolve() if args.project else Path.cwd()) / ".design-sensei.yaml"
    if target.exists() and not args.force:
        return fail("%s already exists (use --force to overwrite)" % target)
    target.write_text(ds_config.template(layout), encoding="utf-8")
    print("wrote %s" % target)
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="design-sensei", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version", version="design-sensei %s" % __version__)
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    p = sub.add_parser("setup", help="prepare the local library (light by default, --full downloads every source)",
                       description="Create the local library, validate the catalog, optionally download sources and build the file index.")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--full", action="store_true", help="download every downloadable source (about 300 MB)")
    group.add_argument("--sources", metavar="ID,ID", help="download only these sources")
    p.add_argument("--offline", action="store_true", help="never use the network")
    p.add_argument("--jobs", type=int, default=4, metavar="N")
    p.add_argument("--min-free-mb", type=int, default=1024, metavar="MB")
    add_global_options(p)
    p.set_defaults(func=lambda a: run_with_layout(a, cmd_setup))

    sp = sub.add_parser("sources", help="list, download, inspect and update upstream sources", description="Manage the local source library.")
    ssub = sp.add_subparsers(dest="subcommand", metavar="COMMAND")
    ssub.required = True
    sync_sources.add_subcommands(ssub)

    ip = sub.add_parser("index", help="build the source file index and the pattern index", description="Build indexes.")
    isub = ip.add_subparsers(dest="subcommand", metavar="COMMAND")
    isub.required = True
    build_index.add_subcommands(isub)

    search_patterns.add_arguments(sub.add_parser("search", help="search patterns, knowledge notes and source files", description=search_patterns.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter))

    recommend.add_arguments(sub.add_parser("recommend", help="one-call recommendation: style, implementation patterns, licence gate, fallback, next steps", description=recommend.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter))

    read_doc.add_arguments(sub.add_parser("read", help="read only what you need of a note, reference, recipe or source file (card, toc, section, lines)", description=read_doc.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter))

    token_report.add_arguments(sub.add_parser("tokens", help="estimated token cost of SKILL.md, references, notes and command output (--budget-check enforces catalog/token-budgets.yaml)", description=token_report.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter))

    cp = sub.add_parser("catalog", help="validate catalog files and knowledge notes", description="Catalog tools.")
    csub = cp.add_subparsers(dest="subcommand", metavar="COMMAND")
    csub.required = True
    validate_catalog.add_subcommands(csub)

    lp = sub.add_parser("licenses", help="inspect licenses, keep the review ledger, generate attribution", description=check_licenses.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    lsub = lp.add_subparsers(dest="subcommand", metavar="COMMAND")
    lsub.required = True
    check_licenses.add_subcommands(lsub)

    doctor.add_arguments(sub.add_parser("doctor", help="diagnose the installation", description=doctor.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter))

    ep = sub.add_parser("config", help="show or create project configuration", description="Design Sensei configuration (.design-sensei.yaml).")
    esub = ep.add_subparsers(dest="subcommand", metavar="COMMAND")
    esub.required = True
    q = esub.add_parser("show", help="print the effective configuration and where each value comes from")
    q.add_argument("--project", metavar="DIR", help="project directory (default: current directory)")
    q.add_argument("--json", action="store_true")
    add_global_options(q)
    q.set_defaults(func=lambda a: run_with_layout(a, cmd_config_show))
    q = esub.add_parser("init", help="write a commented .design-sensei.yaml into a project")
    q.add_argument("--project", metavar="DIR", help="project directory (default: current directory)")
    q.add_argument("--force", action="store_true", help="overwrite an existing file")
    add_global_options(q)
    q.set_defaults(func=lambda a: run_with_layout(a, cmd_config_init))

    design_eval.add_arguments(sub.add_parser("eval", help="static design evaluation of a project or file", description=design_eval.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter))
    build_portable_skill.add_arguments(sub.add_parser("package-skill", help="assemble a self-contained skill folder (and zip) that can be copied anywhere", description=build_portable_skill.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter))
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        eprint("interrupted")
        return 130
    except catalog.CatalogError as exc:
        return fail(str(exc))
    except BrokenPipeError:
        return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
