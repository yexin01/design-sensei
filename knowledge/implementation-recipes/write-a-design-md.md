---
title: "Write and validate a DESIGN.md"
kind: recipe
summary: "Step-by-step recipe to create a DESIGN.md for a project from the verified spec: inspect the project, write tokens and the eight prose sections, validate by hand or with the optional CLI, and wire the file into agent workflows."
source_ids: [design-md]
pattern_ids: [design-md-spec, design-md-lint-and-export]
updated: "2026-10-09"
---

# Write and validate a DESIGN.md

## Goal

One `DESIGN.md` at the project root that gives a coding agent exact token values and the intent behind them, and that
validates without errors. Format background: `knowledge/design-intelligence/design-md-format.md`.

## When to use, when not to

Use it when a project has no written design system, when tokens are scattered across config and CSS, before a redesign, or when
several agents or sessions must produce consistent UI. Do not use it for a one-off page. If another system (Figma variables,
Style Dictionary) is the single source of truth for tokens, write the prose sections only and list the skipped groups under
`omitted`, saying where the tokens live.

## Prerequisites

- Read access to the project (Tailwind config, CSS custom properties, theme files, components) and a short brief.
- Nothing to install to write the file. Optional validation uses Node 18 or newer and the npm package `@google/design.md`
  0.4.0 (`design-md:packages/cli/package.json`); that needs network access, so ask the user first.
- The spec is version `alpha` (`design-md:docs/spec.md`); details may change.

## Steps

1. **Inspect, read only.** Collect existing colours, fonts, spacing and radius scales and component styles. Existing tokens
   win; record gaps instead of inventing a second palette.
2. **Write a five-line brief**: product and audience; the feeling in the first seconds; one specific reference (an object,
   publication or era) instead of adjectives; spacious or dense; hard constraints (brand fonts, accessibility, performance).
3. **Copy the skeleton below** into `DESIGN.md` and replace every value. Keep the section order.
4. **Colours.** Name roles `primary`, `secondary`, `tertiary`, `neutral` plus `on-*`, `surface` and `error` as needed. In prose,
   give each role one bullet: what it is for and where it is never used. Refer to token names so prose and values cannot drift.
5. **Typography.** Start with four levels (display, headline, body, label); mature systems use 9-15. Always write units on
   `fontSize` and `letterSpacing`, `fontWeight` as a number, and `lineHeight` as a dimension or a quoted unitless string
   (the model code reads these three only from strings; see the format note).
6. **Layout and spacing.** Base unit, scale, gutter, maximum width in `spacing`; prose for the grid or margin model.
7. **Elevation and depth.** Prose only; the spec has no tokens for it. Say whether hierarchy comes from tonal layers, borders or shadows.
8. **Shapes.** A `rounded` scale plus the rule for which radius goes where.
9. **Components.** Start with `page`, `button-primary`, its hover variant and `card`; reference tokens as `"{group.name}"`; add
   `input` and others as the product needs. Variants are separate entries.
10. **Do's and Don'ts.** Three to eight specific rules tied to a token or behaviour; delete vague ones ("be modern").
11. **Extensions (optional).** Motion, iconography or voice as prose. A token-like top-level group (for example `motion`
    holding values such as `120ms`) is accepted but, by the linter code as read, warns that exporters drop it.
12. **Validate** (next section), fix, repeat.
13. **Wire it in.** Mention `DESIGN.md` in the project's agent instructions and decide the source of truth: DESIGN.md, or the
    code tokens generated from it. Never hand-edit both.

## Skeleton

Original template; the values are placeholders that parse and pass the checks below, so replace them with the project's own.

```markdown
---
version: alpha
name: Example Product
description: One sentence naming the product, its audience and the feeling the interface should give.
colors:
  primary: "#16324F"
  primary-hover: "#0F2438"
  on-primary: "#FFFFFF"
  secondary: "#5B6B7A"
  tertiary: "#B54708"
  on-tertiary: "#FFFFFF"
  neutral: "#F6F4EF"
  surface: "#FFFFFF"
  on-surface: "#1B1F24"
  error: "#B3261E"
typography:
  display:
    fontFamily: Work Sans
    fontSize: 56px
    fontWeight: 700
    lineHeight: "1.05"
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Work Sans
    fontSize: 28px
    fontWeight: 600
    lineHeight: "1.2"
  body-md:
    fontFamily: Work Sans
    fontSize: 16px
    fontWeight: 400
    lineHeight: "1.6"
  label-sm:
    fontFamily: IBM Plex Mono
    fontSize: 12px
    fontWeight: 500
    lineHeight: "1.3"
    letterSpacing: 0.08em
rounded:
  sm: 4px
  md: 8px
  full: 9999px
spacing:
  base: 8px
  sm: 8px
  md: 16px
  lg: 32px
  xl: 64px
  gutter: 24px
components:
  page:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
    textColor: "{colors.on-primary}"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: "{spacing.lg}"
---

## Overview

Who uses the product, in what situation, and what they should feel in the first seconds. Name one concrete reference.

## Colors

- **Primary ({colors.primary}):** what it is used for and, as importantly, where it is never used.

## Typography

Which family carries which job, and how sizes step between levels.

## Layout

Grid or margin model, the spacing scale and its base unit.

## Elevation & Depth

How hierarchy is shown: shadows, tonal layers or borders.

## Shapes

The corner language, with the rule for when each radius applies.

## Components

Buttons, inputs, cards and the states that matter.

## Do's and Don'ts

- Do keep one accent for the single most important action on a screen.
- Don't introduce a second accent colour.
```

Quote every colour (a bare `#` starts a YAML comment) and every `{reference}` (a bare `{` starts a flow mapping).

## Validation

Manual checklist (mirrors the lint rules in `design-md:packages/cli/src/linter/linter/rules/index.ts`):

- [ ] Front matter is fenced by lines that are exactly `---` and parses as YAML.
- [ ] Top-level keys are schema keys only (a typo such as `colours` is flagged).
- [ ] `primary` and at least one typography token exist; `spacing` and `rounded` exist or are listed under `omitted`.
- [ ] Every `{reference}` resolves and points to a primitive (components may point to a typography token).
- [ ] Units are px, em or rem; `fontWeight` is numeric; token names use letters, digits and hyphens (Tailwind v4 export needs this).
- [ ] Each component text and background pair reaches 4.5:1; for translucent colours composite over the real background first,
      because the linter ignores alpha.
- [ ] No unintended orphan colours; `##` headings follow the spec order with no duplicates (the spec rejects duplicates, the linter does not check).
- [ ] Prose names and values agree with the tokens.

Optional tool check, with the user's consent (this downloads from npm; run it on your own file, never on code under `sources/`):

```bash
npx @google/design.md lint DESIGN.md
npx @google/design.md export --format css-tailwind DESIGN.md > theme.css
npx @google/design.md diff DESIGN.md DESIGN-new.md
```

`lint` prints JSON and exits 1 on errors, but a YAML parse failure is reported as one warning with exit 0, so read every
warning. `export` supports `json-tailwind`, `css-tailwind`, `dtcg` and `css-vars`, never emits components, and exits 0 even
when the source has lint errors. `diff` exits 1 when the new file has more errors or warnings.

## Verify after use

- Generate a sample page from the file and grep it for hard-coded colours, fonts or radii that are not in DESIGN.md.
- Check 375, 768 and 1280 px widths, console errors, keyboard focus, and contrast on real backgrounds.
- If the file documents motion, confirm a `prefers-reduced-motion` alternative exists for every animated element.
- Load only the fonts the file names, with `font-display: swap`, to keep the performance budget.
- Compare the result with the Do's and Don'ts and report conflicts instead of resolving them silently.

## Upstream references

Format: `design-md:docs/spec.md`, `design-md:README.md`, `design-md:PHILOSOPHY.md`. Complete examples:
`design-md:examples/paws-and-paths/DESIGN.md`, `design-md:examples/atmospheric-glass/DESIGN.md`. Tooling:
`design-md:packages/cli/src/commands/export.ts`.

## Licence notes

The upstream project is Apache-2.0 (`design-md:LICENSE`). The skeleton above is original; the upstream examples are not, so
keep their notices if you copy any of them.
