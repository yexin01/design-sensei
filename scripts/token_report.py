#!/usr/bin/env python3
"""Estimate how many tokens Design Sensei puts into Claude's context.

Reports the estimated size (characters / 4, rounded up: an ESTIMATE, not a tokenizer count) of

  * SKILL.md (what loads when the skill triggers) and each reference, pattern playbook, style note,
    command and agent file (read on demand);
  * the real output of `recommend` and `search` for four canned briefs at each detail level
    (brief / normal / full).

`--budget-check` compares the figures with catalog/token-budgets.yaml and exits 1 when a budget is exceeded.

Examples
  design-sensei tokens
  design-sensei tokens --json
  design-sensei tokens --budget-check
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import recommend
import search_patterns
from dslib import EXIT_FAILURE, EXIT_OK
from dslib import compact, yamlite
from dslib.cli import add_global_options, fail, print_json, run_with_layout
from dslib.paths import Layout

CANNED_BRIEFS = (
    "liquid glass hero for a fintech",
    "editorial scroll storytelling",
    "dark developer tool landing",
    "playful 3d product showcase",
)
CANNED_SEARCHES = ("liquid glass button", "smooth scroll", "text reveal", "shader gradient background")
SEARCH_LIMIT = 5
BUDGETS_FILE = "token-budgets.yaml"
MEASURE_HOME = "/ds-home"  # a library path that does not exist: nothing downloaded, no user configuration

# budget key -> (what is measured, how to read the measured value)
BUDGET_LABELS = {
    "skill_md_body": "SKILL.md body (loads when the skill triggers)",
    "recommend_normal": "recommend, normal detail (largest canned brief)",
    "recommend_brief": "recommend, brief detail (largest canned brief)",
    "search_normal": "search --limit %d, normal detail (largest canned query)" % SEARCH_LIMIT,
    "reference_max": "largest reference file",
    "playbook_max": "largest pattern playbook",
    "style_note_max": "largest design style note",
}


def tokens_of(path: Path) -> int:
    return compact.estimate_tokens(path.read_text(encoding="utf-8"))


def _group(directory: Path, pattern: str, root: Path, skip: Sequence[str] = ()) -> List[Dict[str, Any]]:
    items = []  # type: List[Dict[str, Any]]
    if directory.is_dir():
        for path in sorted(directory.glob(pattern)):
            if path.is_file() and path.name not in skip:
                items.append({"path": compact.rel_path(path, root), "tokens": tokens_of(path)})
    return items


def skill_report(layout: Layout) -> Dict[str, Any]:
    skill = layout.skill_dir / "SKILL.md"
    if not skill.is_file():
        return {"path": None, "total": 0, "frontmatter": 0, "body": 0}
    text = skill.read_text(encoding="utf-8")
    m = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
    front = m.group(0) if m else ""
    total, frontmatter = compact.estimate_tokens(text), compact.estimate_tokens(front)
    return {"path": compact.rel_path(skill, layout.root), "total": total, "frontmatter": frontmatter, "body": total - frontmatter}


def output_sizes(layout: Layout) -> Dict[str, Any]:
    """Real output size per canned brief / query and detail level (nothing is printed or written).

    Measured against a library with nothing downloaded and a fixed library path, so the numbers are the same on every machine
    (and are the worst case: download hints are included). Only the length of the toolkit root path varies.
    """
    layout = Layout(layout.root, Path(MEASURE_HOME), "token report")
    out = {"recommend": {}, "search": {}}  # type: Dict[str, Any]
    with tempfile.TemporaryDirectory(prefix="ds-tokens-") as tmp:  # an empty project: no .design-sensei.yaml or package.json leaks in
        for brief in CANNED_BRIEFS:
            rec = recommend.recommend(layout, brief, recommend.Options(project=Path(tmp)))
            out["recommend"][brief] = {d: compact.estimate_tokens(recommend.render_text(rec, d, layout.root, layout.home)) for d in compact.DETAILS}
    parser = argparse.ArgumentParser(add_help=False)
    search_patterns.add_arguments(parser)
    for query in CANNED_SEARCHES:
        ns = parser.parse_args([query, "--limit", str(SEARCH_LIMIT)])
        results, notes = search_patterns.run_search(layout, ns)
        out["search"][query] = {d: compact.estimate_tokens(search_patterns.render_results(results, notes, d, layout.root, layout.home)) for d in compact.DETAILS}
    return out


def build_report(layout: Layout) -> Dict[str, Any]:
    skill_dir = layout.skill_dir
    root = layout.root
    commands_dir = root / "commands"
    agents_dir = root / "agents"
    if not commands_dir.is_dir() and (skill_dir.parent / "commands").is_dir():
        commands_dir = skill_dir.parent / "commands"
    if not agents_dir.is_dir() and (skill_dir.parent / "agents").is_dir():
        agents_dir = skill_dir.parent / "agents"
    return {
        "note": "estimated tokens = ceil(characters / 4); a rough guide, not a tokenizer count",
        "skill": skill_report(layout),
        "references": _group(skill_dir / "references", "*.md", root),
        "playbooks": _group(skill_dir / "patterns", "*.md", root),
        "style_notes": _group(root / "knowledge" / "design-styles", "*.md", root, skip=("README.md",)),
        "commands": _group(commands_dir, "*.md", root),
        "agents": _group(agents_dir, "*.md", root),
        "outputs": output_sizes(layout),
    }


def measured(report: Dict[str, Any]) -> Dict[str, int]:
    """The value each budget key is checked against."""
    def biggest(group: str) -> int:
        return max([i["tokens"] for i in report[group]] or [0])

    out = report["outputs"]
    return {
        "skill_md_body": report["skill"]["body"],
        "recommend_normal": max([v["normal"] for v in out["recommend"].values()] or [0]),
        "recommend_brief": max([v["brief"] for v in out["recommend"].values()] or [0]),
        "search_normal": max([v["normal"] for v in out["search"].values()] or [0]),
        "reference_max": biggest("references"),
        "playbook_max": biggest("playbooks"),
        "style_note_max": biggest("style_notes"),
    }


def load_budgets(layout: Layout) -> Tuple[Dict[str, int], Optional[str]]:
    path = layout.catalog_dir / BUDGETS_FILE
    if not path.is_file():
        return {}, "no budgets file at %s" % path
    data = yamlite.load(path) or {}
    return {k: int(v) for k, v in data.items() if isinstance(v, int)}, None


def check_budgets(values: Dict[str, int], budgets: Dict[str, int]) -> List[str]:
    """One message per exceeded budget (empty list = all within budget)."""
    problems = []  # type: List[str]
    for key, limit in sorted(budgets.items()):
        have = values.get(key)
        if have is None:
            problems.append("budget %s is not a known measurement (known: %s)" % (key, ", ".join(sorted(values))))
        elif have > limit:
            problems.append("OVER BUDGET %s: %d tokens > budget %d (%s); trim it or raise the budget in catalog/%s on purpose" % (
                key, have, limit, BUDGET_LABELS.get(key, key), BUDGETS_FILE))
    return problems


def render_text(report: Dict[str, Any], values: Dict[str, int], budgets: Dict[str, int]) -> str:
    lines = ["Estimated tokens (characters / 4; an estimate, not a tokenizer count)", ""]
    skill = report["skill"]
    lines.append("SKILL.md: %d total (%d frontmatter, always loaded + %d body, loads on trigger)" % (skill["total"], skill["frontmatter"], skill["body"]))
    for title, group in (("references", "references"), ("playbooks (patterns/)", "playbooks"), ("commands", "commands"), ("agents", "agents")):
        items = report[group]
        lines.append("%s: %d file(s), %d total" % (title, len(items), sum(i["tokens"] for i in items)))
        lines.extend("  %5d  %s" % (i["tokens"], i["path"]) for i in sorted(items, key=lambda i: -i["tokens"]))
    notes = report["style_notes"]
    lines.append("style notes: %d file(s), %d total, largest 5:" % (len(notes), sum(i["tokens"] for i in notes)))
    lines.extend("  %5d  %s" % (i["tokens"], i["path"]) for i in sorted(notes, key=lambda i: -i["tokens"])[:5])
    lines.append("command output (brief / normal / full):")
    for kind in ("recommend", "search"):
        for key, sizes in report["outputs"][kind].items():
            lines.append("  %-9s %-34s %5d / %5d / %5d" % (kind, '"%s"' % key, sizes["brief"], sizes["normal"], sizes["full"]))
    if budgets:
        lines.append("budgets (measured / budget):")
        for key in sorted(budgets):
            have = values.get(key, 0)
            lines.append("  %-18s %5d / %5d  %s" % (key, have, budgets[key], "OVER" if have > budgets[key] else "ok"))
    return "\n".join(lines) + "\n"


def cmd_tokens(layout: Layout, args: argparse.Namespace) -> int:
    report = build_report(layout)
    values = measured(report)
    budgets, missing = load_budgets(layout)
    problems = check_budgets(values, budgets) if budgets else []
    if args.json:
        print_json({"report": report, "measured": values, "budgets": budgets, "violations": problems})
    else:
        sys.stdout.write(render_text(report, values, budgets))
        for p in problems:
            print(p)
    if args.budget_check:
        if missing:
            return fail(missing)
        return EXIT_FAILURE if problems else EXIT_OK
    return EXIT_OK


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    parser.add_argument("--budget-check", action="store_true", help="exit 1 when a budget in catalog/%s is exceeded" % BUDGETS_FILE)
    add_global_options(parser)
    parser.set_defaults(func=lambda a: run_with_layout(a, cmd_tokens))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="token_report.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arguments(parser)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
