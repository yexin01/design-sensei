# Design Sensei

Design intelligence for [Claude Code](https://code.claude.com): a skill, a searchable catalog of design styles and implementation patterns, and a local library of real open-source implementations (React Three Fiber, GSAP, Lenis, shader and component libraries) that Claude can read before it writes your interface.

It exists to stop interfaces that look generated. The skill makes Claude **inspect the project, decide the art direction in writing, find real implementations, adapt them without adding a second system, and verify the result in a browser**, while respecting accessibility, performance and the license of every source it borrows from.

* **149 patterns and 92 knowledge notes** (40 design styles, component libraries, shaders, animation, recipes) covering all 18 requested upstream sources, every file reference verified against pinned commits.
* **Works offline and locally**: Python 3.9+ standard library only, no server, no API key, no embeddings.
* **License-aware**: every search result shows the source's license status and a reuse class (`copy_with_attribution`, `license_review_required`, `reimplement_only`, `reference_only`, ...). Upstream code is never committed here.

> Status: version 0.1.0, developed on macOS with Python 3.9 and 3.13. The GitHub Actions workflows are written but have not run yet, and Linux and Windows are untested. See [Limitations](#limitations).

## Quick start

```bash
git clone https://github.com/yexin01/design-sensei.git
claude plugin marketplace add ./design-sensei
claude plugin install design-sensei@design-sensei
```

Then open Claude Code in any project and ask for UI work ("give the pricing page a distinctive editorial look with a restrained scroll animation"). The skill loads automatically, or run `/design-sensei:design-sensei`.

Without installing anything you can also use the command line from the clone:

```bash
cd design-sensei
./bin/design-sensei doctor
./bin/design-sensei search "liquid glass button"
./bin/design-sensei search scroll --framework react --max-gpu low --reduced-motion-safe
```

Full instructions (plugin, skill-only, CLI, locations, removal): [docs/installation.md](docs/installation.md).

## Plugin vs source library

| | What | Size | Needs git/network |
| --- | --- | --- | --- |
| **Plugin / clone** | skill, catalog, knowledge notes, scripts | a few MB of text | no |
| **Source library** (optional) | shallow clones of the 15 upstream repositories at pinned commits, outside the plugin directory (`~/.design-sensei/sources`, or `sources/` in a checkout) | about 300 MB | yes |

Installing the plugin does **not** download the library. `design-sensei setup` creates it empty; `design-sensei setup --full` or `design-sensei sources sync <id>` fills it. The catalog, notes and recipes work without it; with it, search results point at real files you can read.

## Commands

```text
design-sensei setup [--full | --sources a,b] [--offline]   prepare the local library (light by default)
design-sensei sources list | show <id> | status | sync <id...|--all> [--update --write-pins] [--offline] [--dry-run]
design-sensei index build [--docs] [--check]                 file index of sources; browsable pattern index
design-sensei recommend <brief> [filters] [--json]              style + patterns + licence gate + fallback in one call
design-sensei read <target> [--toc|--section A,B|--full]           read part of a note, reference, recipe or source file
design-sensei tokens [--budget-check]                        estimated token cost of the skill and its outputs
design-sensei search <words> [filters] [--scope patterns|docs|files|all] [--json]
design-sensei catalog validate [--strict] [--require-sources]
design-sensei licenses check | scan [--write] | report [--check]
design-sensei doctor [--brief] [--online]
design-sensei config show | init
design-sensei eval <project-dir|file>                        static design evaluation (heuristic)
design-sensei package-skill [--out DIR] [--zip]               self-contained skill bundle (works when copied)
```

`design-sensei <command> --help` documents every option. Exit codes: `0` ok, `1` failure or validation errors, `2` usage error, `3` partial success, `4` required tool or network unavailable.

### Recommending

```bash
design-sensei recommend "liquid glass hero for a fintech" --framework react --max-gpu medium
```

Returns a primary style (and at most one supporting style), up to three implementation patterns with their licence class, a licence gate line, a lower-GPU fallback when needed, and next steps. Use `search` to dig deeper.

### Token efficiency

Quality first, tokens second: nothing is removed from the catalog; the tools just let Claude read the part it needs. `design-sensei read glassmorphism` prints a ~400-token card instead of the whole note (`--toc`, `--section "Colour"`, `--full` for more). `recommend` and `search` take `--detail brief|normal|full` (default `normal`). `design-sensei tokens` reports the estimated cost of every part of the skill and enforces budgets.

### Plugin entry points

With the plugin installed: `/design-sensei:brief <goal>` writes an art-direction brief before any code, `/design-sensei:style <mood>` compares style options, `/design-sensei:review` scores the result with the QA rubric (via the read-only `design-reviewer` agent), and `/design-sensei:sources` shows what is downloaded and under which licence. See [docs/plugin-entrypoints.md](docs/plugin-entrypoints.md).

### Searching

```bash
design-sensei search "kinetic typography" --framework react
design-sensei search --category design-style "editorial"     # style notes
design-sensei search "text reveal" --scope all --limit 5     # patterns + notes + downloaded files
design-sensei search "uniform u_time" --content              # grep downloaded source files
design-sensei search --facets                                # categories, tags, frameworks, sources
```

Filters: `--category`, `--tag`, `--framework`, `--source`, `--dependency`, `--use-case`, `--status`, `--max-gpu`, `--reduced-motion-safe`, `--webgl`/`--no-webgl`, `--license-status`, `--redistribution`. Ranking is deterministic: weighted fields, inverse document frequency, light stemming and a small synonym table. Browsable views: [knowledge/pattern-index/](knowledge/pattern-index/README.md).

### Project configuration

`design-sensei config init` writes a commented `.design-sensei.yaml` into your project. Every key is optional.

| Key | Default | Meaning |
| --- | --- | --- |
| `design_variance` | 6 | 1 familiar ... 10 experimental |
| `motion_intensity` | 5 | 1 static ... 10 cinematic |
| `visual_density` | 5 | 1 airy ... 10 dense |
| `preferred_frameworks` | `[]` | prefer these when several fit; empty follows the project |
| `allowed_dependencies` | `minimal` | `none`, `existing`, `minimal`, `any`, or a list |
| `performance_budget` | 200 KB JS, LCP 2500 ms, CLS 0.1, 1 WebGL canvas | checked by `eval` |
| `webgl_enabled` | `true` | `false` forbids WebGL/3D |
| `reduced_motion` | `respect` | or `static_first` |
| `source_acquisition_mode` | `on_demand` | or `full`, `offline` |

## The sources

15 git repositories (cloned on demand) and 3 reference-only sites. Full detail and per-source handling: [ATTRIBUTION.md](ATTRIBUTION.md), [docs/licensing.md](docs/licensing.md).

| Group | Sources |
| --- | --- |
| Design intelligence | taste-skill, design.md, awesome-opus5-5-videos, Refero Styles (link only), UX Planet article (link only; inspection blocked) |
| UI components and effects | liquid-logo, skiper-ui (unlicensed: ideas only), VengeanceUI, fancy, react-bits (MIT + Commons Clause), Animmaster Lib (paid, link only), astryx |
| 3D, shaders, rendering | react-three-fiber, liquid-glass-js, shadergradient (MIT declared, no LICENSE file), img2threejs |
| Animation and scroll | lenis, gsap (custom "no charge" license) |

## Repository layout

```text
.claude-plugin/        plugin.json, marketplace.json
bin/design-sensei      command on PATH while the plugin is enabled
skills/design-sensei/  SKILL.md, references/ (14), patterns/ (15 playbooks), scripts/ launcher, config/
catalog/               sources.yaml, patterns.yaml + patterns.d/, licenses.yaml, schemas/
knowledge/             design-styles, components, shaders, animations, design-intelligence,
                       website-references, implementation-recipes, pattern-index (generated)
scripts/               CLI modules; dslib/ holds the YAML parser, schema validator, git wrapper
tests/                 unit, integration, design-evaluations (no network needed)
examples/              glass-hero (verified example) and usage walkthrough
docs/                  installation, architecture, source-management, licensing, contributing,
                       publishing, troubleshooting
sources/               local clones go here (git-ignored); only README.md is tracked
```

Patterns live in `catalog/patterns.yaml` and `catalog/patterns.d/*.yaml` (one file per topic keeps contributions merge-friendly; ids are unique across all of them).

## How the skill works

1. **Inspect** the project: stack, tokens, components, installed libraries, constraints.
2. **Art direction** before code: audience, style, typography, color, layout, surfaces, motion, interaction, tuned by the three dials.
3. **Discover**: search the catalog, read notes and the real upstream files, compare candidates, pass the license gate.
4. **Implement**: adapt into the existing system; static first; fallbacks and reduced motion for every effect.
5. **Verify**: project build and tests, `design-sensei eval`, browser inspection at several widths with reduced motion and console checks, or an explicit statement of what could not be verified.

Evaluation rubric and protocol: [skills/design-sensei/references/design-qa.md](skills/design-sensei/references/design-qa.md), automated checks and manual scenarios: [tests/design-evaluations/](tests/design-evaluations/README.md).

## Development

```bash
python3 -m unittest discover -s tests -t .      # unit, integration (local git repositories), design evaluations
./bin/design-sensei catalog validate --strict   # add --require-sources after `setup --full`
./bin/design-sensei doctor
```

Tests that need the real network are skipped unless `DESIGN_SENSEI_NETWORK_TESTS=1`. Contribution rules: [CONTRIBUTING.md](CONTRIBUTING.md), formats: [docs/contributing.md](docs/contributing.md), releasing: [docs/publishing.md](docs/publishing.md), design: [docs/architecture.md](docs/architecture.md), problems: [docs/troubleshooting.md](docs/troubleshooting.md).

## License

Original work in this repository: MIT, see [LICENSE](LICENSE). Upstream projects are not included, keep their own licenses, and are listed with their status in [ATTRIBUTION.md](ATTRIBUTION.md). License detection in this project is heuristic and is not legal advice; items marked "needs human review" in `catalog/licenses.yaml` need a person to read the upstream terms.

## Limitations

* Verified: macOS (Apple silicon), Python 3.9.6 and 3.13, git 2.53, Claude Code 2.1.295 (`claude plugin validate --strict`, local marketplace install). Not verified: Linux, Windows, other Python versions, installing from a published GitHub repository, running the skill in an interactive session end to end.
* Knowledge notes were written by reading the pinned source files; recipe code was type-checked or run in jsdom/headless Chrome only where each note says so. Nothing was tested on real GPUs or in other browsers.
* The UX Planet article could not be inspected (Cloudflare 403) and Refero forbids AI crawlers, so neither is summarized; Animmaster Lib is a paid library and only its public categories are recorded.
* Source facts can drift after the pinned commits; the weekly drift workflow is meant to catch that once the repository is published.
* `design-sensei eval` is a static linter. It cannot judge contrast, composition or taste.
