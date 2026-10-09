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
./bin/design-sensei package-skill --out dist --zip   # portable skill bundle (see below); fails on any stray secret/ignored file
git status                                  # nothing unexpected; sources/, .state/ and dist/ are ignored
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

## Portable skill bundle (GitHub release asset)

Not everyone installs a plugin or clones the repository. `package-skill` builds a self-contained skill folder and a zip of it, which a maintainer attaches to the GitHub release of the same tag (what users do with it: [Option B2](installation.md#option-b2---portable-bundle-copy-it-no-clone-needed)).

```bash
git checkout v0.1.0                                          # build from the tagged commit, with a clean work tree
./bin/design-sensei package-skill --out dist --zip
# dist/design-sensei/                         the skill folder
# dist/design-sensei-skill-0.1.0.zip          single top-level folder design-sensei/
# dist/design-sensei-skill-0.1.0.zip.sha256   "<hash>  <file>", sha256sum format
```

Check it before it is attached, from a plain copy and with `DESIGN_SENSEI_ROOT` unset:

```bash
rm -rf /tmp/ds-check && cp -R dist/design-sensei /tmp/ds-check
env -u DESIGN_SENSEI_ROOT /tmp/ds-check/scripts/design-sensei doctor --brief
env -u DESIGN_SENSEI_ROOT /tmp/ds-check/scripts/design-sensei catalog validate --strict
env -u DESIGN_SENSEI_ROOT /tmp/ds-check/scripts/design-sensei search "liquid glass"
```

Attach it (a maintainer runs this deliberately; nothing is uploaded automatically):

```bash
gh release create v0.1.0 dist/design-sensei-skill-0.1.0.zip dist/design-sensei-skill-0.1.0.zip.sha256 \
  --title "Design Sensei 0.1.0" --notes-file <release-notes.md>
# release already exists:  gh release upload v0.1.0 dist/design-sensei-skill-0.1.0.zip dist/design-sensei-skill-0.1.0.zip.sha256
```

Things to know:

* The version in the file name is `scripts/dslib/__init__.py` `__version__`; bump it with the other version fields (see Versioning) before building.
* The build is deterministic: sorted entries, timestamps fixed at 1980-01-01, normalised permissions. The same commit gives a byte-identical zip with the same Python and zlib; a different zlib can compress differently, so publish the `.sha256` of the file you actually upload.
* The build refuses to proceed (exit 1, nothing written) if it meets symbolic links, a secret-looking file (`.env*`, `*.pem`, `*.key`, `id_rsa*`, `credentials*.json`, `secrets.*`, `.netrc`, `.npmrc`), `sources/`, `.state/`, git data, `node_modules/`, anything matched by `.gitignore`, a dead relative link in the skill or the knowledge notes, or an incomplete tree. Caches (`__pycache__`, `.DS_Store`) are skipped silently.
* The bundle contains no upstream code, so there is no third-party source to notice beyond what `ATTRIBUTION.md` and `NOTICE` (both included) already say. Re-run `licenses report --check` first so the bundled `ATTRIBUTION.md` is current.
* Included: `skills/design-sensei/` (as the skill folder) and, under `toolkit/`, `catalog/`, `knowledge/`, `scripts/`, `docs/` (except this page), `examples/glass-hero/`, `LICENSE`, `ATTRIBUTION.md`, `CONTRIBUTING.md`, `SECURITY.md`. Everything else (`tests/`, `.claude-plugin/`, `bin/`, `sources/`, `.state/`) stays out. New Python modules under `scripts/` are picked up automatically; a new top-level folder the CLI needs has to be added to `TOOLKIT_DIRS` in `scripts/build_portable_skill.py`.

## CI

`.github/workflows/ci.yml` runs the test matrix, strict catalog validation, pattern-index and attribution freshness checks and JSON manifest checks. `.github/workflows/drift.yml` runs weekly and on demand: it downloads every source at its pinned commit and validates every file citation and license, so a rewritten or deleted upstream is noticed. These workflows have not been executed yet (no push has happened); their commands are the same ones listed above. There is **no release workflow**: the bundle zip is built and attached by hand as described above. CI does exercise the bundle indirectly, because `tests/unit/test_portable_skill.py` builds it, runs the launcher from a plain copy (doctor, search, strict catalog validation, eval) and checks that the zip is reproducible. If you later want automation, a workflow triggered by `release: published` would check out the tag, run `package-skill --out dist --zip` and `gh release upload ${{ github.event.release.tag_name }} dist/*.zip dist/*.sha256` (it needs `contents: write`); that job is intentionally not committed until a first release exists.

## After a release

Check `design-sensei sources status --check-upstream`, bump pins deliberately (`sources sync <id> --update --write-pins`), re-scan licenses, fix any citations the drift workflow reports, and release again.
