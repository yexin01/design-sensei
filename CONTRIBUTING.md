# Contributing to Design Sensei

Thank you for helping. The project is small and strict about two things: **truthfulness** (every claim traces to a real source file or says it is unverified) and **licensing** (upstream code is never committed here).

## Quick start

```bash
git clone https://github.com/yexin01/design-sensei.git && cd design-sensei
./bin/design-sensei doctor
./bin/design-sensei setup --full            # optional: download the upstream sources (about 300 MB)
python3 -m unittest discover -s tests -t .  # whole suite, no network needed
./bin/design-sensei catalog validate --strict
```

Requirements: Python 3.9+ (standard library only; do not add dependencies) and git. Keep code compatible with Python 3.9: no `match`, no `X | Y` types evaluated at runtime, no `str.removeprefix` tricks that differ by version.

## What to contribute

| Kind | Where | Guide |
| --- | --- | --- |
| A new pattern or design style | `catalog/patterns.d/<topic>.yaml` + a note under `knowledge/` | [docs/contributing.md](docs/contributing.md) |
| A new upstream source | `catalog/sources.yaml` | [docs/source-management.md](docs/source-management.md) |
| Fix a wrong fact | the note or catalog entry, with the file path that proves it | cite `source-id:path` |
| Tooling, tests, docs | `scripts/`, `tests/`, `docs/` | tests first for bugs |

## Rules

1. **No upstream code, media or large files in commits.** `sources/` and `.state/` are git-ignored and a test enforces it. Quote at most about eight lines from permissively licensed sources, always with a citation; quote nothing from sources whose reuse class is `license_review_required`, `reimplement_only`, `reference_only` or `verify_first`.
2. **Verify before you write.** Read the source file. Do not invent props, options, versions, compatibility claims or license facts. If you could not verify something, write "not verified".
3. **Cite paths** as `` `source-id:path/in/source` ``. `design-sensei catalog validate` checks them against the pinned commit.
4. **Keep provenance honest**: `provenance: original | upstream | mixed` on patterns, `source_ids` in note front matter.
5. **Accessibility is part of the pattern**: set `accessibility.motion` truthfully and write the reduced-motion alternative in the recipe before setting `reduced_motion_alternative: true`.
6. **No secrets, no machine-specific paths.** A hygiene test scans tracked files.
7. **Generated files are generated**: `knowledge/pattern-index/` (`design-sensei index build --docs`) and `ATTRIBUTION.md` (`design-sensei licenses report`). CI fails if they are stale.

## Before opening a pull request

```bash
python3 -m unittest discover -s tests -t .
./bin/design-sensei catalog validate --strict
./bin/design-sensei index build --docs-only && ./bin/design-sensei index build --check
./bin/design-sensei licenses report --check
claude plugin validate . --strict          # if you changed plugin or skill metadata
```

Describe what you verified and how. Pull requests that add sources must include the license review (`licenses scan --write`) and a note on anything that needs human review.

## Conduct

Be kind, assume good faith, and keep discussions about the work. Report security problems privately, see [SECURITY.md](SECURITY.md).
