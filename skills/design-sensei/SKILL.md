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

Make interfaces that look decided, not generated. Work in five steps: **inspect, art-direct, discover, implement,
verify**. Do not skip step 2: generic output comes from jumping straight to code.

In this file `design-sensei` means the command `${CLAUDE_SKILL_DIR}/scripts/design-sensei` (quote the path if it contains
spaces). The Bash tool does not keep shell state between calls, so always write the full command.

## 0. Check the toolkit (once per task)

```bash
${CLAUDE_SKILL_DIR}/scripts/design-sensei doctor --brief
${CLAUDE_SKILL_DIR}/scripts/design-sensei config show --project .
```

- `doctor` reports where the catalog and the local source library live and how many upstream sources are downloaded.
  The catalog (patterns, notes, licence data) is always available; upstream **source code** is optional and fetched on demand.
- `config show` prints the effective settings: `design_variance`, `motion_intensity`, `visual_density`,
  `preferred_frameworks`, `allowed_dependencies`, `performance_budget`, `webgl_enabled`, `reduced_motion`,
  `source_acquisition_mode`. Defaults are sensible; never ask the user to fill in a questionnaire. Use
  `design-sensei config init` only if the user wants a `.design-sensei.yaml`.
- If the command is unavailable, read `${CLAUDE_SKILL_DIR}/../../knowledge/pattern-index/by-category.md` and
  `${CLAUDE_SKILL_DIR}/../../catalog/patterns.yaml` directly and work from those.
- If `source_acquisition_mode` is `offline`, never run `sources sync`; use only what is already downloaded.

## 1. Inspect the project

Look before designing. Record a short project brief (keep it in your notes, not in the repo):

| Question | Where to look |
| --- | --- |
| Framework, runtime, router | `package.json`, framework config, `app/` or `pages/`, `index.html` |
| Styling system | Tailwind config, CSS modules, StyleX, vanilla CSS, CSS-in-JS |
| Design tokens / DESIGN.md | `tailwind.config.*`, `:root` custom properties, `theme`, `DESIGN.md` |
| Existing components | `components/`, `ui/`, a shadcn `components.json`, a design system package |
| Installed motion/3D libs | `gsap`, `lenis`, `motion`/`framer-motion`, `three`, `@react-three/fiber` |
| Build, test, lint commands | `package.json` scripts, CI config |
| Constraints | browser support, performance budget, SSR, CMS, accessibility requirements |

Rules: extend the existing component and token system instead of adding a second one. Prefer libraries already installed.
Respect `allowed_dependencies`. If the project already has a `DESIGN.md` or style guide, it outranks anything below.

## 2. Establish art direction before code

Decide, in writing, with a one-line reason each (template in [references/art-direction.md](references/art-direction.md)):

1. **Audience and emotion**: who uses it, what they should feel in the first five seconds.
2. **Style direction**: pick one primary style and at most one supporting influence.
   `design-sensei search "<mood words>" --category design-style --scope patterns` then read the style note.
3. **Typography**: display + text (+ mono) families, scale, weights, line length. See [references/typography.md](references/typography.md).
4. **Colour**: tokens for background, surface, text, accent and states, with contrast checked. See [references/color-systems.md](references/color-systems.md).
5. **Layout and spacing**: grid, spacing scale, rhythm, hierarchy. See [references/layout-composition.md](references/layout-composition.md).
6. **Surfaces and imagery**: radius, borders, shadows or glass, image treatment.
7. **Motion language** and **interaction patterns**: tempo, easing, what moves and why. See [references/motion-design.md](references/motion-design.md).

Dial the ambition with the configuration (defaults 6 / 5 / 5):

| Dial | 1-3 | 4-7 | 8-10 |
| --- | --- | --- | --- |
| `design_variance` | familiar layouts, proven patterns | distinctive but usable | experimental composition, unusual grids |
| `motion_intensity` | hover/focus states only | purposeful transitions, a few scroll moments | cinematic, motion-led; every effect needs a reduced-motion alternative |
| `visual_density` | airy, one idea per screen | balanced | dense, information-rich |

Avoid the generic tells: default indigo-to-violet gradients, one typeface everywhere, centered hero over three identical
cards, glass or glow on everything, stock-icon rows, effects that do not serve the message. If you recognise your
direction as the default, change one major decision deliberately.

## 3. Discover source material

Start with one call: `${CLAUDE_SKILL_DIR}/scripts/design-sensei recommend "<mood and goal words>" --project .` (add
`--framework react|nextjs|vue`, `--max-gpu low`, `--reduced-motion-safe`, `--no-webgl`, `--allowed-deps gsap,lenis`,
`--limit 5`, `--json` as needed). It applies `.design-sensei.yaml` and returns a primary style (plus at most one supporting
style) with its note path and pairs-well-with / avoid hints, up to three implementation patterns (reuse class, licence
status, GPU cost, dependencies, reduced-motion alternative, doc, recipe, first three source files with downloaded state),
a LICENSE GATE line, a FALLBACK line when the top pattern is GPU-heavy or needs dependencies outside
`allowed_dependencies`, and NEXT STEPS. Honour the gate and the fallback. Use `search` to dig deeper (patterns carry source
ids, licence status, reuse class and real file paths):

```bash
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "liquid glass button"
${CLAUDE_SKILL_DIR}/scripts/design-sensei search scroll --framework react --max-gpu low --reduced-motion-safe
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "text reveal" --scope all --limit 5
${CLAUDE_SKILL_DIR}/scripts/design-sensei search --facets      # vocabulary: categories, tags, frameworks, sources
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "uniform u_time" --content   # grep downloaded source files
```

Filters: `--category`, `--tag`, `--framework`, `--source`, `--dependency`, `--use-case`, `--max-gpu none|low|medium|high`,
`--reduced-motion-safe`, `--webgl` / `--no-webgl`, `--license-status`, `--redistribution`, `--status`.

Then:

1. Read the pattern's `knowledge_doc` and `recipe` (absolute paths are printed). Read the playbook for the pattern family
   in [patterns/](patterns/) (table below).
2. Open the real implementation files listed under `file:`. If a source is "not downloaded" and the mode allows it:
   `${CLAUDE_SKILL_DIR}/scripts/design-sensei sources sync <id>` (needs network and git; asks permission). Check first with
   `design-sensei sources show <id>`.
3. Compare two or three candidates against the art direction, the project's stack, dependency cost, GPU cost, accessibility
   and licence class. Choose the one that serves the design. Impressive is not a criterion.
4. **Licence gate** (shown as `reuse` in results; details in [references/source-usage.md](references/source-usage.md)):

| reuse | Meaning |
| --- | --- |
| `copy_with_attribution` | permissive licence: adapt freely, keep copyright and licence notice in the project |
| `license_review_required` | custom terms (for example react-bits, gsap): use as a dependency per its terms, never bundle or republish; read the review in `design-sensei sources show <id>` |
| `reimplement_only` | no licence granted: learn the idea, write your own code |
| `reference_only` | links and descriptions only: do not copy anything |
| `verify_first` | licence not verified: treat as reference only |
| `original` | project-authored guidance: free to use |

## 4. Implement

- Build the foundation first: tokens, type scale, layout grid, base components; then page sections; motion last.
- Adapt a pattern instead of rewriting it, but integrate it into the project's component, styling and animation systems.
  One animation system per project (for example do not mix GSAP, Motion and CSS keyframes for the same job).
- Dependencies: follow `allowed_dependencies`; justify each new one and list it in your summary. Prefer a CSS or native
  solution when it gives the same result.
- Progressive enhancement: semantic static HTML first, enhancement second. Every WebGL effect gets a static fallback
  and a `prefers-reduced-motion` path. Lazy-load heavy code, pause offscreen work, clean up listeners, animation frames and
  GPU resources.
- When adapting MIT or Apache code, keep the upstream notice and add the project to `THIRD_PARTY_NOTICES.md`. Never copy code
  from sources whose reuse class forbids it.
- Never run install scripts or other code from downloaded upstream repositories.

Open the reference you need, not all of them:

| Need | Read |
| --- | --- |
| Principles, hierarchy, spacing | [references/design-principles.md](references/design-principles.md) |
| Choosing between libraries/components | [references/component-selection.md](references/component-selection.md) |
| Animation, scroll, choreography | [references/motion-design.md](references/motion-design.md) |
| Shaders, GLSL, WebGL backgrounds | [references/shaders-and-webgl.md](references/shaders-and-webgl.md) |
| 3D scenes, React Three Fiber | [references/three-dimensional-design.md](references/three-dimensional-design.md) |
| Breakpoints and fluid layouts | [references/responsive-design.md](references/responsive-design.md) |
| Accessibility rules | [references/accessibility.md](references/accessibility.md) |
| Performance budgets | [references/performance.md](references/performance.md) |
| Review and QA protocol | [references/design-qa.md](references/design-qa.md) |

Pattern playbooks (condensed how-tos with pattern ids): [hero sections](patterns/hero-sections.md),
[navigation](patterns/navigation.md), [typography effects](patterns/typography-effects.md),
[cards and grids](patterns/cards-and-grids.md), [microinteractions](patterns/microinteractions.md),
[scroll storytelling](patterns/scroll-storytelling.md), [background shaders](patterns/background-shaders.md),
[liquid glass](patterns/liquid-glass.md), [3D scenes](patterns/three-dimensional-scenes.md),
[product showcases](patterns/product-showcases.md), [image to 3D](patterns/image-to-3d.md),
[cursor interactions](patterns/cursor-interactions.md), [page transitions](patterns/page-transitions.md),
[data visualization](patterns/data-visualization.md), [responsive layouts](patterns/responsive-layouts.md).

## 5. Verify before saying done

1. Run the project's own build, type-check, lint and tests; fix what you broke.
2. Static check: `${CLAUDE_SKILL_DIR}/scripts/design-sensei eval <project-dir>` (heuristic lint for accessibility, motion,
   performance, responsiveness, typography and provenance; it cannot judge taste).
3. For a scored second opinion, delegate to the `design-reviewer` agent (read-only; give it screenshot paths and the
   art-direction brief) or run `/design-sensei:review`.
4. Look at it. With a browser tool (Playwright, Chrome DevTools, a headless browser skill) load the page and:
   screenshot at 375, 768, 1280 and 1920 px; read the console and network for errors and failed assets;
   emulate `prefers-reduced-motion: reduce`; tab through with the keyboard; check WebGL fallback by disabling WebGL if
   possible; measure LCP/CLS/JS size if tooling exists. Compare against the art-direction brief and fix issues.
5. If no browser tool is available, **say so explicitly** and list what could not be verified.
6. Score the result with the rubric in [references/design-qa.md](references/design-qa.md): art direction, differentiation,
   typography and hierarchy, layout consistency, responsive behaviour, motion quality, accessibility, performance,
   provenance, technical correctness. Report evidence, not superlatives.

### Completion checklist

- [ ] Project inspected; existing system extended, no duplicate component or animation system
- [ ] Art-direction brief written and visible in the result (tokens, type, colour, motion)
- [ ] Every borrowed pattern traced to a source id; licence class respected; notices kept
- [ ] New dependencies within `allowed_dependencies` and listed in the summary
- [ ] Reduced-motion alternative and no-WebGL fallback for every animated or GPU effect
- [ ] Keyboard, focus, contrast, semantics, alt text checked
- [ ] Build/tests pass; no console errors or failed assets; responsive widths inspected
- [ ] Limitations stated (for example visual inspection unavailable, sources not downloaded)

## Commands

| Command | Purpose |
| --- | --- |
| `design-sensei doctor [--brief] [--online]` | diagnose installation, catalog, library, config |
| `design-sensei setup [--full \| --sources a,b]` | prepare the local library (light by default) |
| `design-sensei sources list \| show <id> \| status \| sync <id...>` | inspect and download upstream sources (pinned commits) |
| `design-sensei recommend <brief> [filters]` | one call: style, patterns, licence gate, fallback, next steps |
| `design-sensei search <words> [filters]` | find patterns, notes (`--scope docs`) and files (`--scope files`) |
| `design-sensei index build [--docs]` | rebuild the file index (and the browsable pattern index) |
| `design-sensei catalog validate [--strict]` | validate catalog, notes and file references |
| `design-sensei licenses check \| scan \| report` | licence inspection and attribution report |
| `design-sensei config show \| init` | effective settings / create `.design-sensei.yaml` |
| `design-sensei eval <path>` | static design evaluation |
| `design-sensei package-skill [--out DIR] [--zip]` | build a self-contained, copyable skill bundle |

Plugin entry points (plugin install only): `/design-sensei:brief` (art-direction brief, no code), `/design-sensei:style`
(2-3 style options with a recommendation), `/design-sensei:review` (scored review), `/design-sensei:sources` (download and
licence state), and the `design-reviewer` agent.

Exit codes: 0 ok, 1 failure, 2 usage error, 3 partial success, 4 required tool or network unavailable.
Full documentation: `docs/` in the Design Sensei repository (installation, source management, licensing).
