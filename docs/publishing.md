# Publishing and releasing

This repository is both a Claude Code plugin and a one-plugin marketplace, so publishing means making the git repository reachable and tagging releases. **Nothing here is pushed automatically**; a maintainer runs these steps deliberately.

## Pre-release checklist

```bash
python3 -m unittest discover -s tests -t .                  # also with the oldest and newest supported Python
./bin/design-sensei catalog validate --strict --require-sources
./bin/design-sensei index build --docs-only && ./bin/design-sensei index build --check
./bin/design-sensei licenses scan --write && ./bin/design-sensei licenses report
./bin/design-sensei licenses check
claude plugin validate . --strict
claude plugin validate skills --strict      # skill front matter
git status                                  # nothing unexpected; sources/ and .state/ are ignored
```

Review `ATTRIBUTION.md` and the items marked `needs_human_review` in `catalog/licenses.yaml` before announcing a release.

## Versioning

* Bump `version` in `.claude-plugin/plugin.json` (Claude Code uses it to decide whether users get an update; if it is unchanged, installed copies do not update).
* Update `CHANGELOG.md` and `skills/design-sensei/SKILL.md` `metadata.version`, and `scripts/dslib/__init__.py` `__version__`.
* Tag: `git tag -a v0.1.0 -m "Design Sensei 0.1.0"`.

## Publish

1. Create the public GitHub repository and push the default branch and tags (a maintainer does this; it is not part of any script).
2. Users install with `/plugin marketplace add <owner>/design-sensei` and `/plugin install design-sensei@design-sensei` (see [installation.md](installation.md)).
3. Optional: submit to Anthropic's plugin directory following the Claude Code publishing documentation.

## CI

`.github/workflows/ci.yml` runs the test matrix, strict catalog validation, pattern-index and attribution freshness checks and JSON manifest checks. `.github/workflows/drift.yml` runs weekly and on demand: it downloads every source at its pinned commit and validates every file citation and license, so a rewritten or deleted upstream is noticed. These workflows have not been executed yet (no push has happened); their commands are the same ones listed above.

## After a release

Check `design-sensei sources status --check-upstream`, bump pins deliberately (`sources sync <id> --update --write-pins`), re-scan licenses, fix any citations the drift workflow reports, and release again.
