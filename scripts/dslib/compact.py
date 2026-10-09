"""Token-efficient output helpers shared by `recommend`, `search` and `tokens`.

Detail levels: brief (ids and one-liners), normal (default: today's facts without the waste),
full (the verbose legacy layout, absolute paths allowed).
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import Any, Optional, Sequence

from . import config as ds_config
from .paths import Layout

DETAILS = ("brief", "normal", "full")
DEFAULT_DETAIL = "normal"
SUMMARY_LIMIT = 140  # characters of summary kept in brief/normal text output
MAX_FILES = 3

# Cheap-read suggestions. `design-sensei read` is built elsewhere; adjust the wording here only.
READ_STYLE_CMD = "design-sensei read {slug} --card"
READ_PATTERN_CMD = "design-sensei read {id} --section <name>"


def estimate_tokens(text: str) -> int:
    """Rough token estimate: characters / 4, rounded up (an estimate, not a tokenizer)."""
    return int(math.ceil(len(text) / 4.0))


def add_detail_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--detail", choices=DETAILS, default=None,
                        help="text output size: brief (ids, one line each), normal (default, relative paths, trimmed), full (verbose, absolute paths); "
                             "default from output_detail in the configuration; --json is unaffected")


def resolve_detail(cli_value: Optional[str], layout: Layout, project: Optional[Path] = None) -> str:
    """CLI flag wins over the ``output_detail`` configuration key, which wins over the built-in default."""
    if cli_value:
        return cli_value
    try:
        values, _, _ = ds_config.effective_config(layout, project)
    except Exception:  # configuration trouble must never block a search
        return DEFAULT_DETAIL
    value = values.get("output_detail")
    return value if value in DETAILS else DEFAULT_DETAIL


LIB_PREFIX = "@lib/"


def rel_path(path: Any, root: Path, home: Optional[Path] = None) -> str:
    """``path`` relative to ``root`` (posix separators). Paths under the library ``home`` (when it lives outside root) read ``@lib/...``."""
    if not path:
        return "-"
    for base, prefix in ((root, ""), (home, LIB_PREFIX)):
        if base is None:
            continue
        try:
            return prefix + Path(str(path)).relative_to(base).as_posix()
        except ValueError:
            continue
    return str(path)


def root_header(root: Path, home: Optional[Path]) -> str:
    """The single ``root:`` line (plus ``lib:`` only when the library lives outside the toolkit)."""
    if home is None or str(home) == str(root) or str(home).startswith(str(root) + "/"):
        return "root: %s" % root
    return "root: %s | %s = %s" % (root, LIB_PREFIX, home)


def clip(text: str, limit: int = SUMMARY_LIMIT) -> str:
    """Whitespace-collapsed text cut at a sentence end (preferred) or a word boundary, never mid-word."""
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= limit:
        return text
    window = text[:limit]
    ends = [m.end() for m in re.finditer(r"[.!?](?=\s)", window)]
    if ends and ends[-1] >= limit * 0.5:
        return window[: ends[-1]].rstrip()
    cut = window.rfind(" ")
    if cut < limit * 0.5:
        cut = limit
    return window[:cut].rstrip(" ,;:-") + "…"


def more(total: int, shown: int) -> str:
    return " +%d more" % (total - shown) if total > shown else ""


def style_slug_of(pattern_id: str) -> str:
    return pattern_id[len("style-"):] if pattern_id.startswith("style-") else pattern_id


def read_style(slug: str) -> str:
    return "`%s`" % READ_STYLE_CMD.format(slug=slug)


def read_pattern(pid: str) -> str:
    return "`%s`" % READ_PATTERN_CMD.format(id=pid)


def split_common_dir(paths: Sequence[str]) -> "tuple":
    """(prefix, short names): the directory shared by all paths (with trailing slash, or "") and the paths below it."""
    import os
    if not paths:
        return "", []
    dirs = [os.path.dirname(p) for p in paths]
    try:
        prefix = os.path.commonpath([d or "." for d in dirs]) if len(paths) > 1 else dirs[0]
    except ValueError:
        prefix = ""
    prefix = "" if prefix in (".", "/", "") else prefix.rstrip("/") + "/"
    return prefix, [p[len(prefix):] if prefix and p.startswith(prefix) else p for p in paths]
