# Contributor guide: patterns, notes, recipes

[CONTRIBUTING.md](../CONTRIBUTING.md) has the rules. This page shows the formats and the workflow.

## 1. Add a pattern

Create or extend a file in `catalog/patterns.d/` (one file per topic keeps diffs small; ids must be unique across all pattern files). Schema: `catalog/schemas/patterns.schema.json`.

```yaml
schema_version: 1
patterns:
  - id: smooth-scroll-lenis                 # kebab-case, globally unique
    title: Smooth scroll with Lenis
    category: scroll                        # see the enum in the schema
    summary: Inertia-based smooth scrolling that keeps native scroll semantics intact.
    provenance: upstream                    # upstream | original | mixed
    tags: [smooth-scroll, inertia]
    source_ids: [lenis]
    frameworks: [javascript, react]
    dependencies: [lenis]                   # packages verified in the source's package.json/README
    implementation_status: recipe_available # reference_only | recipe_available | verified_example
    use_cases: [marketing site, scroll storytelling]
    performance:
      gpu_intensity: none                   # none | low | medium | high | unknown
      fallback_required: false
    accessibility:
      motion: moderate                      # none | subtle | moderate | intense
      reduced_motion_alternative: true      # true only if your recipe/note defines it
    source_paths:                           # source-id:path, verified against the pinned commit
      - lenis:packages/core/src/lenis.ts
    knowledge_doc: knowledge/animations/lenis.md
    recipe: knowledge/implementation-recipes/lenis-smooth-scroll-setup.md
```

Do not add `license_status`; it is derived from the sources (and validated if present).
`implementation_status` values: `reference_only` (pointer to upstream), `recipe_available` (a recipe in this repository), `verified_example` (a recipe that was built and checked as an example under `examples/`).

## 2. Write a knowledge note

Notes live under `knowledge/<area>/<slug>.md` and start with front matter checked by `catalog/schemas/knowledge-doc.schema.json`:

```markdown
---
title: "Lenis smooth scroll"
kind: animation        # design-style | component-library | shader | animation | website-reference | recipe | guide | index
summary: "What the note covers, in one or two sentences (20-400 characters)."
source_ids: [lenis]
pattern_ids: [smooth-scroll-lenis]
updated: "2026-10-09"
---
```

Quote values that contain `: ` and always quote dates (the catalog YAML dialect rejects ambiguous plain scalars). Cite upstream files as `` `lenis:packages/core/src/lenis.ts` ``; `catalog validate` resolves each citation when the source is downloaded. A note with a citation of a source that is not listed in its `source_ids` produces a warning.

Section guides by kind are in the recipe/note files themselves; the common thread: say what is verified, say when **not** to use it, give the performance and accessibility cost, and end with licence/reuse guidance.

## 3. Write a recipe

A recipe (`kind: recipe`) is original step-by-step guidance: goal, when to use, prerequisites with versions read from the source's `package.json`, numbered steps with **your own** code, a verification checklist (responsive widths, `prefers-reduced-motion`, console errors, performance) and upstream references. Recipes may call a library's public API; they must not reproduce code from sources whose reuse class is not `copy_with_attribution`.

## 4. Verify

```bash
./bin/design-sensei catalog validate --strict --require-sources   # needs `setup --full`
python3 -m unittest discover -s tests -t .
./bin/design-sensei index build --docs-only                       # regenerate knowledge/pattern-index/
./bin/design-sensei search "<words from your pattern>"            # does it come up?
```

Without the sources downloaded, `catalog validate` still checks structure and cross references, and reports how many file citations it could not check.

## 5. Promote a recipe to `verified_example`

Build the recipe as a small project under `examples/<name>/`, run `design-sensei eval examples/<name>`, inspect it in a real browser at several widths with reduced motion on and off, and describe what you checked in the example's README. Only then set `implementation_status: verified_example`.
