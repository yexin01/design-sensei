# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- 12 design-style notes: flat design, material design, Bauhaus, Memphis, isometric and 3D illustration, hand-drawn and doodle, collage and cutout, pixel art and 8-bit, glitch, line art and outline, duotone and monochrome, Japanese minimalism (40 styles in total).
- `design-sensei recommend`: one call returns a primary and supporting style, up to three patterns, a licence gate, a fallback and next steps.
- Plugin entry points: `/design-sensei:brief`, `:style`, `:review`, `:sources` and a read-only `design-reviewer` agent.
- `design-sensei package-skill [--zip]`: self-contained skill bundle that works when copied, with a launcher that finds `<skill>/toolkit` and a library kept under `~/.design-sensei`.
- `evals/`: trigger query set (24 queries), authored behavioural evals and results.

### Changed
- Skill description rewritten after a trigger evaluation: should-trigger queries fired in 29 of 36 runs (was 13 of 36), with no false triggers on near-miss queries. See `evals/results-trigger.md` for caveats.

## [0.1.0] - 2026-10-09

### Added
- Claude Code plugin and single-plugin marketplace (`.claude-plugin/`), validated with `claude plugin validate --strict`.
- The `design-sensei` skill: inspect, art-direct, discover, implement, verify workflow with on-demand references and pattern playbooks.
- Source registry for all 18 requested upstream sources (15 git repositories, 3 websites/articles) with exact pinned commits, license status and redistribution status.
- `design-sensei` command line: `setup`, `sources list|sync|status|show`, `index build`, `search`, `catalog validate`, `licenses check|scan|report`, `doctor`, `config show|init`, `eval`.
- Non-destructive, resumable source sync with pinning, sparse checkout, retries, offline mode and disk-space guard.
- Deterministic file index of downloaded sources, ranked search over patterns, notes and files, license-aware results.
- License detection heuristics, review ledger (`catalog/licenses.yaml`) and generated `ATTRIBUTION.md`.
- Knowledge base: design-style taxonomy, component, shader and animation notes, implementation recipes and a generated pattern index.
- Static design evaluator (`eval`) and evaluation rubric.
- Test suite (unit and integration, local git repositories, no network) and GitHub Actions workflows.
