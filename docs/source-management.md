# Source management

`catalog/sources.yaml` is the canonical registry of upstream material. This page explains what each field means, what `sources sync` does and refuses to do, and how to add or update a source.

## What is in a normal clone

| Included in this repository | Never included |
| --- | --- |
| catalog (YAML + JSON Schemas), license policy and review ledger | upstream source code, assets, media |
| project-authored knowledge notes, recipes, playbooks, reference documents | clones of upstream repositories |
| scripts, plugin, skill, tests, docs | the generated file index, lock file, caches |

Upstream code is cloned on each user's machine into the *source library* (`sources/` in a checkout, `~/.design-sensei/sources/` otherwise). The repository's `.gitignore` excludes it, and a test fails if anything under `sources/` other than its README becomes tracked.

## Fields of `catalog/sources.yaml`

Validated by `catalog/schemas/sources.schema.json` and by `design-sensei catalog validate`.

| Field | Meaning |
| --- | --- |
| `id` | stable kebab-case identifier used everywhere (`lenis`, `react-bits`) |
| `name`, `url`, `type` | `git_repository`, `website`, `article` or `documentation_site` |
| `category` | `design_intelligence`, `ui_components`, `graphics_3d`, `animation` |
| `acquisition_method` | `git_shallow` (depth-1 clone), `git_sparse` (depth-1, only `sparse_paths`), `reference_only` (never downloaded) |
| `sparse_paths` | directories to check out for `git_sparse`; files in the repository root are always included |
| `default_branch` | branch used by `--update` |
| `pinned_commit` | exact commit the catalog was verified against; what `sync` checks out |
| `license`, `license_status`, `redistribution_status` | see [licensing.md](licensing.md) |
| `attribution` | credit line used in `ATTRIBUTION.md` |
| `local_path` | folder name inside the library |
| `frameworks`, `tags`, `npm_packages` | search metadata, only values seen in the source |
| `last_checked` | date the facts above were last verified |
| `inspection_status` | `inspected_local` (cloned and read), `inspected_remote` (HTTP or metadata only), `blocked` (reason in notes), `pending` |
| `notes` | what was observed, caveats, why a source is reference-only |

Anything not verified is marked `pending_verification`, `unknown` or `not_found`; never guessed.

## Commands

```bash
design-sensei sources list [--category C] [--present|--missing]
design-sensei sources show <id>                 # catalog facts, license review, local state, patterns using it
design-sensei sources status [--check-upstream] # local commit vs pin (vs upstream tip)
design-sensei sources sync <id...> | --all      # download or update to the pinned commit
design-sensei sources sync <id> --update --write-pins   # move the pin to the upstream branch tip
design-sensei sources sync --all --offline      # report what is present, use no network
design-sensei sources sync --all --dry-run
```

Options: `--jobs N` (parallel downloads, default 4), `--retries N` (transient network failures, default 3), `--min-free-mb MB` (refuse to start below this free space, default 1024).

### Exit codes

| Code | Meaning |
| --- | --- |
| 0 | everything requested succeeded (including "already up to date" and reference-only) |
| 1 | the operation failed |
| 2 | usage error (unknown id, bad flag combination) |
| 3 | partial: some sources succeeded, others failed or were skipped |
| 4 | a required tool or the network was unavailable (git missing, offline with missing sources) |

## What sync guarantees

* **Pinned and reproducible.** A fresh download checks out `pinned_commit` (fetched by hash, depth 1). Without a pin it resolves the default branch tip. `--update` moves to the tip; `--write-pins` records the new hash and today's date in `sources.yaml` by editing only those lines (comments and layout are preserved).
* **Non-destructive.** A checkout with modified tracked files, a directory that is not a git checkout, or a clone whose `origin` differs from the catalog is reported as `blocked` and left exactly as it is. Untracked files you add survive updates. There is no `--force`.
* **Atomic.** Downloads go to a hidden temporary directory and are renamed into place only on success, so an interrupted sync leaves no half-initialised source.
* **Safe.** Only `https://` URLs are cloned. No hook, install script, submodule or LFS download from an upstream repository is ever run. Symlinks in sources are never followed by the indexer.
* **Resilient.** Transient network errors are retried with back-off; permission, not-found and policy failures are not. Missing git, offline mode, no disk space and unreachable remotes each give a specific message and exit code. One failing source never stops the others.
* **Honest about state.** `.state/lock.json` (in the library home, never committed) records what was downloaded and when.

## Adding a source

1. Inspect it first: read the README, find the license file at the commit you will pin, check how big it is.
2. Add an entry to `catalog/sources.yaml` with `pinned_commit: null`, `license_status: pending_verification`, `redistribution_status: pending_verification`, `inspection_status: pending`.
3. `design-sensei sources sync <id> --update --write-pins` (pins the current tip).
4. `design-sensei licenses scan <id> --write` records the license files, hashes and copyright lines in `catalog/licenses.yaml`; read the license text yourself and then set `license`, `license_status` and `redistribution_status` accordingly.
5. For big repositories choose `git_sparse` and list only the directories that matter.
6. Write at least one knowledge note and one pattern that cite real files (`<id>:path`), then run `design-sensei catalog validate --strict`. The coverage rule makes the strict run fail for a source nothing refers to.
7. Regenerate derived files: `design-sensei index build --docs` and `design-sensei licenses report`.

## Updating pins

```bash
design-sensei sources status --check-upstream     # which upstreams moved
design-sensei sources sync lenis --update --write-pins
design-sensei licenses scan lenis --write          # license text may have changed
design-sensei catalog validate --strict --require-sources   # every cited file still exists
```

If validation reports a missing file, update the pattern or note that cited it. A scheduled workflow (`.github/workflows/drift.yml`) runs this check against the pinned commits.

## Sizes (measured on 2026-10-09)

The 15 downloadable sources need about 300 MB: astryx 43 MB (sparse; the full repository is about 1.2 GB), shadergradient 88 MB, react-bits 33 MB (sparse), vengeance-ui 46 MB, the rest under 25 MB each. Download time with `--jobs 4` was about 16 seconds on a fast connection.
