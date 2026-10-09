---
name: design-sensei
description: >-
  Use this skill whenever the task is to make a web interface look, feel or move better, especially anything
  involving motion or graphics code. Trigger for: designing, redesigning or art-directing a site, landing
  page, dashboard or component so it feels distinctive rather than templated; and for implementing visual or
  interactive effects such as page and route transitions, shared-element morphs, GSAP/ScrollTrigger and Lenis
  smooth scrolling, parallax and pinned scroll sections, animated shader or gradient backgrounds, WebGL,
  Three.js / React Three Fiber scenes, 3D product viewers (GLB models, orbit controls, lighting), liquid
  glass, cursor effects and kinetic typography. Includes performance-conscious tuning of these effects on
  mobile. Provides an inspect, art-direct, search, implement, verify workflow with a catalog of styles and
  open-source code patterns, plus licence guidance. Skip for backend, tests, copywriting, non-visual refactors
  and generic performance debugging.
license: MIT
compatibility: Claude Code. Needs python3 3.9+; git only when downloading upstream sources; a browser tool is optional for visual checks.
allowed-tools:
  - Bash(${CLAUDE_SKILL_DIR}/scripts/design-sensei search *)
  - Bash(${CLAUDE_SKILL_DIR}/scripts/design-sensei recommend *)
  - Bash(${CLAUDE_SKILL_DIR}/scripts/design-sensei read *)
  - Bash(${CLAUDE_SKILL_DIR}/scripts/design-sensei doctor *)
  - Bash(${CLAUDE_SKILL_DIR}/scripts/design-sensei sources list *)
  - Bash(${CLAUDE_SKILL_DIR}/scripts/design-sensei sources show *)
  - Bash(${CLAUDE_SKILL_DIR}/scripts/design-sensei sources status *)
  - Bash(${CLAUDE_SKILL_DIR}/scripts/design-sensei config show *)
  - Bash(${CLAUDE_SKILL_DIR}/scripts/design-sensei eval *)
metadata:
  version: "0.1.0"
  repository: https://github.com/yexin01/design-sensei
---

# Design Sensei

Make interfaces that look decided, not generated. Five steps: **inspect, art-direct, discover, implement, verify**.
Never skip step 2: generic output comes from jumping straight to code. Spend ambition on the design, not on reading:
fetch only what the current decision needs (see Reading cheaply).

`design-sensei` below means `${CLAUDE_SKILL_DIR}/scripts/design-sensei` (quote it if the path has spaces; write the full
command every call, Bash keeps no state). If it is missing, work from `${CLAUDE_SKILL_DIR}/../../knowledge/pattern-index/by-category.md`.
If `source_acquisition_mode` is `offline`, never run `sources sync`. Settings come from `.design-sensei.yaml` (defaults are
fine; never quiz the user): `design_variance`, `motion_intensity`, `visual_density`, `preferred_frameworks`,
`allowed_dependencies`, `performance_budget`, `webgl_enabled`, `reduced_motion`, `output_detail`.

## 1. Inspect the project

Record a short brief in your notes, not the repo: framework and router; styling system; tokens or `DESIGN.md`; existing
components (`components/`, shadcn `components.json`); installed motion/3D libs (`gsap`, `lenis`, `motion`, `three`,
`@react-three/fiber`); build/test/lint scripts; constraints (browsers, performance budget, SSR, accessibility).
Extend the existing component and token system; never add a second one. Prefer installed libraries; respect
`allowed_dependencies`. A project `DESIGN.md` or style guide outranks everything here.

## 2. Establish art direction before code

Decide in writing, one-line reason each (template: [references/art-direction.md](references/art-direction.md)):
1. **Audience and emotion**: who, and what they feel in five seconds.
2. **Style**: one primary, at most one supporting (from `recommend` below).
3. **Typography**: display + text (+ mono), scale, weights, measure ([typography](references/typography.md)).
4. **Colour**: background, surface, text, accent, state tokens, contrast checked ([colour](references/color-systems.md)).
5. **Layout and spacing**: grid, scale, rhythm, hierarchy ([layout](references/layout-composition.md)).
6. **Surfaces and imagery**: radius, borders, shadow or glass, image treatment.
7. **Motion and interaction**: tempo, easing, what moves and why ([motion](references/motion-design.md)).

| Dial (default) | 1-3 | 4-7 | 8-10 |
| --- | --- | --- | --- |
| `design_variance` (6) | familiar, proven | distinctive but usable | experimental composition |
| `motion_intensity` (5) | hover/focus only | purposeful, a few scroll moments | cinematic; every effect needs a reduced-motion path |
| `visual_density` (5) | airy | balanced | dense |

Generic tells to avoid: indigo-violet gradients, one typeface everywhere, centered hero over three identical cards,
glass or glow on everything, stock-icon rows, effects that do not serve the message. If your direction is the default,
change one major decision on purpose.

## 3. Discover source material

Start with one call: `design-sensei recommend "<mood and goal words>" --project .` (optional `--framework`, `--max-gpu low`,
`--reduced-motion-safe`, `--no-webgl`, `--allowed-deps gsap,lenis`, `--limit 5`). It applies `.design-sensei.yaml` and
returns a primary and supporting style, up to three patterns with reuse class, GPU cost, dependencies and files, a LICENSE
GATE, a FALLBACK when the top pattern is heavy, and NEXT steps. Honour the gate and fallback. Dig deeper with
`design-sensei search <words> [--category --tag --framework --source --max-gpu --reduced-motion-safe --webgl|--no-webgl
--scope docs|files|all --content --facets]`.

`--detail brief|normal|full` (or `output_detail`): normal is default; brief (about 300 tokens) triages candidates;
use full only when normal omits something you need (an absolute path, an untrimmed summary). `--json` ignores it.

**Reading cheaply** (`read` instead of Read; nothing creative is cut, you just choose the part):
- `design-sensei read <target>` prints a ~400-token card. `--toc` lists headings with token costs; `--section "Colour,Typography"`
  fetches parts; `--max-tokens N` cuts at a section boundary; `--full` is the whole file, only when you truly need it.
- Targets: a style (`glassmorphism`), a pattern id (`--recipe` for its recipe), `ref:typography`, `playbook:hero-sections`,
  `recipe:<slug>`, `note:lenis`, or code as `<source>:<path> --lines 1:60` (its header shows the licence class first).
- For the chosen style always add `--section "Common mistakes,Typical mistakes"` (the card omits them; they prevent generic output).
- Take the card, then the sections the current decision needs: Colour before choosing a palette, Accessibility cautions
  before shipping, the recipe before implementing. Ambiguous names list candidates (exit 2).

Then: compare two or three candidates against the art direction, stack, dependency and GPU cost, accessibility and
licence; pick what serves the design, not what impresses. If a source is not downloaded and the mode allows, check
`design-sensei sources show <id>` then `design-sensei sources sync <id>` (needs network, git; asks permission).

**Licence gate** (`reuse` in results; details [references/source-usage.md](references/source-usage.md)):

| reuse | Meaning |
| --- | --- |
| `copy_with_attribution` | permissive: adapt, keep copyright and licence notice |
| `license_review_required` | custom terms (react-bits, gsap): use as a dependency per its terms, never bundle or republish; read `sources show <id>` |
| `reimplement_only` | no licence granted: learn the idea, write your own code |
| `reference_only` / `verify_first` | links only / unverified: copy nothing |
| `original` | project-authored guidance: free to use |

## 4. Implement

- Foundation first: tokens, type scale, grid, base components; then sections; motion last.
- Adapt a pattern into the project's component, styling and animation systems. One animation system per project.
- New dependencies: within `allowed_dependencies`, justified, listed in your summary. Prefer CSS or native when equal.
- Static semantic HTML first. Every WebGL effect gets a static fallback and a `prefers-reduced-motion` path. Lazy-load heavy
  code, pause offscreen work, clean up listeners, frames and GPU resources.
- Keep upstream MIT/Apache notices and add them to `THIRD_PARTY_NOTICES.md`. Never copy from sources whose class forbids it.
- Never run install scripts or code from downloaded upstream repositories.

Open only the reference you need (use `read ref:<name> --toc` first for the long ones): principles
[design-principles](references/design-principles.md), library choice [component-selection](references/component-selection.md),
[motion-design](references/motion-design.md), [shaders-and-webgl](references/shaders-and-webgl.md),
[three-dimensional-design](references/three-dimensional-design.md), [responsive-design](references/responsive-design.md),
[accessibility](references/accessibility.md), [performance](references/performance.md), [design-qa](references/design-qa.md).
Playbooks in [patterns/](patterns/) (`read playbook:<name>`): hero-sections, navigation, typography-effects, cards-and-grids,
microinteractions, scroll-storytelling, background-shaders, liquid-glass, three-dimensional-scenes, product-showcases,
image-to-3d, cursor-interactions, page-transitions, data-visualization, responsive-layouts.

## 5. Verify before saying done

1. Run the project's build, type-check, lint, tests; fix what you broke.
2. `design-sensei eval <project-dir>`: heuristic lint (accessibility, motion, performance, responsiveness, typography,
   provenance); cannot judge taste.
3. For a scored second opinion, delegate to the `design-reviewer` agent (read-only, separate context; pass screenshot paths
   and the brief) or run `/design-sensei:review`.
4. Look at it with a browser tool: screenshots at 375 and 1280 first, 768 and 1920 at the end; console and network errors;
   `prefers-reduced-motion: reduce`; keyboard tab-through; WebGL fallback; LCP/CLS if tooling exists. Fix against the brief.
5. No browser tool: **say so** and list what was not verified.
6. Score with the rubric in [references/design-qa.md](references/design-qa.md); report evidence, not superlatives.

- [ ] Project inspected; no duplicate component or animation system
- [ ] Art-direction brief written and shown (tokens, type, colour, motion)
- [ ] Every borrowed pattern traced to a source id; licence class respected; notices kept
- [ ] Dependencies within `allowed_dependencies` and listed
- [ ] Reduced-motion path and no-WebGL fallback for every animated or GPU effect
- [ ] Keyboard, focus, contrast, semantics, alt text checked
- [ ] Build/tests pass; no console errors or failed assets; widths inspected
- [ ] Limitations stated

## Commands

`design-sensei <cmd> --help` documents all options. Main: `recommend`, `search`, `read`, `eval`, `sources list|show|status|sync`,
`config show|init`, `doctor`, `setup`, `index build`, `catalog validate`, `licenses check|scan|report`, `tokens` (cost report),
`package-skill` (portable bundle). Plugin extras: `/design-sensei:brief` (art-direction brief, no code), `:style` (2-3 style
options), `:review` (scored review), `:sources`, and the `design-reviewer` agent. Exit codes: 0 ok, 1 failure, 2 usage,
3 partial, 4 tool or network unavailable. Docs: `docs/` in the repository.
