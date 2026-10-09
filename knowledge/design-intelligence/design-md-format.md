---
title: "DESIGN.md format and tooling"
kind: guide
summary: "Guide to the DESIGN.md specification from Google Labs (alpha): YAML token front matter plus eight ordered prose sections, token types, the packages/cli linter and exporters, the three bundled examples, and how a coding agent should consume the file."
source_ids: [design-md, taste-skill]
pattern_ids: [design-md-spec, design-md-lint-and-export]
updated: "2026-10-09"
---

# DESIGN.md format and tooling

## What it is

DESIGN.md is a plain-text description of a visual identity for coding agents. A file has two layers: machine-readable design
tokens in YAML and human-readable rationale in Markdown. The spec calls the tokens "normative" and the prose their context
(`design-md:docs/spec.md`). The format is at version `alpha` and the README warns it will change (`design-md:README.md`). Upstream
is `google-labs-code/design.md` (Apache-2.0); the tooling ships as the npm package `@google/design.md` 0.4.0, Node 18 or newer
(`design-md:packages/cli/package.json`). Pinned commit `9bf8eae` is the 0.4.0 release (2026-07-27).

## Repository map

| Path | Contents |
| --- | --- |
| `design-md:README.md` | condensed spec, CLI reference, lint rule table |
| `design-md:PHILOSOPHY.md` | why prose leads, why specific references beat adjectives, negative constraints, how the format grows |
| `design-md:docs/spec.md` | the full spec, generated from `design-md:packages/cli/src/linter/spec-gen/spec.mdx` and `design-md:packages/cli/src/linter/spec-config.yaml` (sections, units, property lists, depth limits) |
| `design-md:packages/cli/` | TypeScript CLI and linter library (about 90 source files including tests) |
| `design-md:examples/` | three complete example systems |
| `design-md:.github/workflows/test.yml` | CI: lint, tests, build, a smoke lint of one example, tarball and Windows install smoke tests |
| `design-md:.agents/skills/` | four agent skills (CLI scoring scale, Ink terminal UI, TDD, typed service contracts) installed for working on the repo; not part of the format |

## File anatomy

- Optional YAML front matter, delimited by lines that are exactly `---`, then a Markdown body. An optional `#` title is not a
  section; sections are `##` headings.
- The parser accepts two embeddings: front matter, and fenced `yaml` or `yml` code blocks anywhere in the body
  (`design-md:packages/cli/src/linter/parser/handler.ts`). Blocks are merged; a top-level key defined in two blocks is rejected
  with the code `DUPLICATE_SECTION`. Spec and README only document front matter; the examples in `design-md:PHILOSOPHY.md` use code blocks.
- A file with no YAML does not fail: `design-md:packages/cli/src/linter/lint.ts` returns one warning.

## Token schema

| Key | Type | Notes |
| --- | --- | --- |
| `version` | string | optional, `alpha` |
| `name` | string | not marked optional in the schema (no lint rule enforces it); `description` is optional |
| `omitted` | list | optional; names (colors, typography, spacing, rounded, components) or `{section, reason}` entries that silence missing-section findings |
| `colors` | name to Color | `primary` should exist; common order primary, secondary, tertiary, neutral |
| `typography` | name to object | `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, `fontFeature`, `fontVariation` |
| `rounded` | level to Dimension | levels such as `sm`, `md`, `lg`, `full`; any key is valid |
| `spacing` | level to Dimension or number | unitless numbers allowed (column counts, ratios) |
| `components` | name to properties | `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width` |

Types: **Color** is any CSS colour (hex recommended; `oklch()`, `color-mix()` and others accepted; converted to sRGB for contrast
checks). **Dimension** is a number with `px`, `em` or `rem`. **Token reference** is `{path.to.token}`; outside `components` it must
point to a primitive, not a group, while component properties may reference a whole typography token. Variants are separate
entries with related names (`button-primary`, `button-primary-hover`). The model flattens nested groups under colors, rounded
and spacing to dotted names (`design-md:packages/cli/src/linter/model/handler.ts`); the limits are 20 nesting levels and 10
reference hops (`spec-config.yaml`).

## Sections

Sections may be omitted, but those present should follow this order. Unknown headings are preserved.

| # | Heading (alias) | Purpose | Token group |
| --- | --- | --- | --- |
| 1 | Overview (Brand & Style) | personality, audience, intended feeling; fallback guidance where no token applies | none |
| 2 | Colors | palettes and the role of each | `colors` |
| 3 | Typography | typical systems have 9-15 levels, named by role (headline, body, label...) | `typography` |
| 4 | Layout (Layout & Spacing) | grid or margin model, spacing scale | `spacing` |
| 5 | Elevation & Depth (Elevation) | how hierarchy is shown: shadows, tonal layers, borders | none |
| 6 | Shapes | corner and shape language | `rounded` |
| 7 | Components | buttons, chips, lists, tooltips, checkboxes, radios, inputs (marked as evolving) | `components` |
| 8 | Do's and Don'ts | guardrails | none |

## Philosophy in four points (paraphrased from `design-md:PHILOSOPHY.md`)

1. Prose carries the design; token values are reference numbers for it. Output quality depends more on how clearly intent is
   described than on value precision.
2. A specific reference (a named kind of object or era) evokes a whole world; "modern, clean, premium" lands in the middle of everything.
3. Naming the thing implies its negative constraints; keep a short, deliberate Do's and Don'ts list, not a long one.
4. Beyond the minimum categories, authors add their own sections and keys (the document's example is a `motion` group with
   durations and an easing).

Tension to note: the spec says tokens are normative, while PHILOSOPHY says token values are context, not rendering instructions.

## Tooling in `packages/cli` (read only; nothing here was run)

Commands (`design-md:packages/cli/src/index.ts`; file arguments accept a path or `-` for stdin; output defaults to JSON):

| Command | Does | Exit codes |
| --- | --- | --- |
| `lint` (`design-md:packages/cli/src/commands/lint.ts`) | parse, resolve tokens, run 11 rules, print `{findings, summary}` | 1 if any error, 2 if the file cannot be read |
| `diff` (`design-md:packages/cli/src/commands/diff.ts`) | lint two files, report added, removed and modified tokens per group and the finding delta | 1 on regression (more errors or warnings) |
| `export` (`design-md:packages/cli/src/commands/export.ts`) | `--format` of `json-tailwind` (alias `tailwind`), `css-tailwind`, `dtcg`, `css-vars` (`--prefix` optional) | 0 on success even with lint errors, 1 bad format or emitter error, 2 unreadable |
| `spec` (`design-md:packages/cli/src/commands/spec.ts`) | print the bundled spec; `--rules` or `--rules-only` for the rule table | 0 |

Lint rules (`design-md:packages/cli/src/linter/linter/rules/index.ts`):

| Rule | Severity | Checks |
| --- | --- | --- |
| `broken-ref` | error | component `{ref}` that does not resolve; warning for component properties outside the eight valid ones |
| `missing-primary` | warning | colours defined but no `primary` ("the agent will auto-generate key colors") |
| `contrast-ratio` | warning | component `backgroundColor`/`textColor` pair below 4.5:1 (WCAG 2.1 luminance; alpha is ignored) |
| `orphaned-tokens` | warning | colour never used by a component (runs only when components exist); Material-3-style families (primary, secondary, tertiary, error, surface, background, outline) exempt |
| `token-summary` | info | counts per group |
| `missing-sections` | info | no `spacing` or `rounded` while colours exist, unless omitted |
| `missing-typography` | warning | colours but no typography, unless omitted |
| `section-order` | warning | known headings out of canonical order (aliases resolved) |
| `unknown-key` | warning | top-level key within edit distance 2 of a schema key (typo such as `colours`) |
| `token-like-ignored` | warning | unknown top-level key whose value looks like tokens (hex, dimension, typography properties); exports drop it |
| `omitted-rules` | info | unknown or redundant `omitted` entries warn, declared omissions are info |

The model step (`design-md:packages/cli/src/linter/model/handler.ts`) adds errors for invalid colours, dimensions and units (only
px, rem, em are allowed in rounded and typography), a `fontFamily` that parses as a colour, non-numeric `fontWeight`, duplicate or
colliding token paths and excess nesting; unknown typography properties warn.

Exporters (all pure functions of the parsed model; none exports `components`):

| Format | Covers | Notes |
| --- | --- | --- |
| `json-tailwind` (`design-md:packages/cli/src/linter/tailwind/handler.ts`) | colors, fontFamily, fontSize (with lineHeight, letterSpacing, fontWeight), borderRadius, spacing | Tailwind v3 `theme.extend` JSON |
| `css-tailwind` (`design-md:packages/cli/src/linter/tailwind/v4/handler.ts`, `design-md:packages/cli/src/linter/tailwind/v4/serialize.ts`) | same categories | Tailwind v4 `@theme` block (`--color-*`, `--font-*`, `--text-*`, `--leading-*`, `--tracking-*`, `--font-weight-*`, `--radius-*`, `--spacing-*`); token names must be letters, digits and hyphens or the export fails |
| `dtcg` (`design-md:packages/cli/src/linter/dtcg/handler.ts`) | colour, spacing, rounded, typography | W3C Design Tokens 2025.10 shape |
| `css-vars` (`design-md:packages/cli/src/linter/css-vars/handler.ts`) | colours, spacing, rounded only | `:root` block (`design-md:packages/cli/src/linter/css-vars/serialize.ts`); dots in names become hyphens |

Library use: `import { lint } from '@google/design.md/linter'` returns `designSystem`, `findings`, `summary`, `tailwindConfig`,
`sections` and `documentSections`; `fixSectionOrder` is exported but not wired to any command (`design-md:packages/cli/src/linter/index.ts`).
Runtime dependencies: citty, yaml, zod and the unified/remark family (`design-md:packages/cli/package.json`).

Observed gaps between docs and code (from reading, not running):
- `css-vars` export exists in code but the README documents four formats; `lint` and `diff` also format `markdown`, while the README lists only `json`.
- The spec says a duplicate `##` heading rejects the file; no heading check exists in the linter.
- A parse failure (bad YAML, no YAML) is returned as one warning, so `lint` exits 0. Gate on warnings too.
- The model reads `fontSize`, `lineHeight` and `letterSpacing` only from strings, so a bare number such as `lineHeight: 1.1` (the
  spec's own example) appears to be dropped; the fixtures quote it (`design-md:packages/cli/src/linter/fixtures/HERITAGE.md`).
- README's sample contrast finding says "passes"; the code reports only failures. A `motion:` group like the PHILOSOPHY example
  would trigger `token-like-ignored`.
- The README says `diff` detects token-level and prose regressions; the code compares token maps and finding counts only, so
  prose edits are not diffed.

## Examples

Each folder holds `DESIGN.md`, `README.md`, a Tailwind v3 `tailwind.config.js` (components deliberately left out) and a
`design_tokens.json`. Their JSON includes component tokens, which the exporter above does not emit, so it was probably produced by
another tool or version (not verified).

| Example | Domain and style | Fonts |
| --- | --- | --- |
| `design-md:examples/atmospheric-glass/DESIGN.md` | weather app, dark glassmorphism, white surfaces at varying alpha | Inter |
| `design-md:examples/paws-and-paths/DESIGN.md` | pet-care platform, light, warm orange with blue | Plus Jakarta Sans |
| `design-md:examples/totality-festival/DESIGN.md` | eclipse music festival, dark, gold and cyan, glow | Space Grotesk, Inter |

All three carry 47 colour tokens in a Material-3-style role set, 6-8 typography levels, 6 rounding levels and 10 components,
use the aliases "Brand & Style" and "Layout & Spacing", and omit Do's and Don'ts. A prose-only counter-example is
`design-md:packages/cli/src/linter/fixtures/NO_FRONTMATTER.md`. The Taste Skill repo ships a different dialect:
`taste-skill:skills/stitch-skill/DESIGN.md` has numbered prose sections and no YAML tokens.

## How a coding agent should consume a DESIGN.md

Design Sensei guidance derived from the spec, README and linter messages (not upstream text):

1. Look for `DESIGN.md` in the project root first; if present it outranks catalog guidance.
2. Read both layers before writing UI. Treat Overview and Do's and Don'ts as constraints on every choice.
3. Resolve `{refs}` (front matter and fenced yaml blocks) and apply values exactly; do not round or "improve" them.
4. If prose and a token disagree, use the token for the value, the prose for the intent, and report the conflict.
5. Fill gaps from prose, then from the project's existing system, then record the assumption in your summary. Never invent a palette silently.
6. Treat `-hover` and `-active` entries as states of the base component; keep unknown properties as hints.
7. Map to the stack (Tailwind `@theme`, `theme.extend` or CSS variables); keep one source of truth; use letters, digits and
   hyphens in token names; compute contrast yourself for translucent colours.
8. Preserve unknown sections and keys; propose edits to DESIGN.md as a reviewable diff; note the `version` targeted.

## Strengths, limits and Design Sensei use

Strengths: small, human-readable, diffable; exporters to common token formats; a linter that catches broken references and
low contrast. Limits: alpha status; no light/dark mode mechanism, no elevation or motion tokens; components section still
evolving; the linter never compares prose with tokens; exporters drop components. Design Sensei treats it as a format to read
and offer (see `knowledge/implementation-recipes/write-a-design-md.md`), never as a dependency; the CLI is optional, needs npm
and network, and is only run with the user's consent.

## Licence

Apache-2.0 (`design-md:LICENSE`); source files carry "Copyright 2026 Google LLC" headers and no NOTICE file exists. Copying a file
means keeping the licence and notices and stating changes. This note paraphrases and quotes nothing.
