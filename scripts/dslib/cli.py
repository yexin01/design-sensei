"""Small helpers shared by every command: global options, layout, output."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Iterable, List, Sequence

from . import EXIT_FAILURE
from .paths import Layout, LayoutError, resolve_layout


def add_global_options(parser: argparse.ArgumentParser) -> None:
    """Options accepted by every command (kept after the sub-command so they can be used anywhere)."""
    group = parser.add_argument_group("global options")
    group.add_argument("--home", metavar="DIR", default=None, help="library home holding sources/ and .state/ (default: see docs/installation.md)")
    group.add_argument("--root", metavar="DIR", default=None, help=argparse.SUPPRESS)


def layout_from_args(args: argparse.Namespace) -> Layout:
    return resolve_layout(root=getattr(args, "root", None), home=getattr(args, "home", None))


def print_json(data: Any) -> None:
    json.dump(data, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")


def eprint(*parts: Any) -> None:
    print(*parts, file=sys.stderr)


def fail(message: str, code: int = EXIT_FAILURE) -> int:
    eprint("error: %s" % message)
    return code


def run_with_layout(args: argparse.Namespace, fn) -> int:
    """Resolve the layout and call ``fn(layout, args)``; layout problems become clean errors."""
    try:
        layout = layout_from_args(args)
    except LayoutError as exc:
        return fail(str(exc))
    return fn(layout, args)


def format_table(rows: Sequence[Sequence[str]], headers: Sequence[str] = ()) -> str:
    """Left-aligned fixed-width table (no colors, safe for logs)."""
    table = [list(map(str, r)) for r in rows]
    if headers:
        table.insert(0, list(headers))
    if not table:
        return ""
    widths = [max(len(r[i]) for r in table) for i in range(len(table[0]))]
    lines = []
    for idx, row in enumerate(table):
        lines.append("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip())
        if headers and idx == 0:
            lines.append("  ".join("-" * w for w in widths).rstrip())
    return "\n".join(lines)


def short(sha: Any) -> str:
    return str(sha)[:7] if sha else "-"


def csv_list(value: str) -> List[str]:
    return [v.strip() for v in value.split(",") if v.strip()]
