# Component selection

A decision procedure for choosing among the catalog's libraries and components, plus a factual summary of the 15 downloadable sources and 3 reference sites.

Load this at step 3 (discover) when two or more candidates could do the job, when the user asks "which library", and before adding any dependency. Impressive is not a criterion. Fit with the art direction and the project is.

## Decision procedure

1. **Restate the job** in one line (for example "animated hero background, calm, behind text") and the art-direction constraints (style, motion tempo, density).
2. **Check what the project already has** (SKILL.md step 1): component system, animation library, styling system. An existing solution that does the job wins over a new one.
3. **Shortlist two or three candidates**: `design-sensei search "<job words>" --framework <fw> --max-gpu <level> --reduced-motion-safe`, then read each pattern's note and recipe. Include a native CSS option when one exists.
4. **Filter by hard gates** in this order; any failure removes the candidate:
   - Licence class permits your use ([source usage](source-usage.md)). `reimplement_only`, `reference_only`, `verify_first` cannot supply code.
   - `allowed_dependencies` allows it (none: CSS/native only; existing: already-installed packages; minimal: justify each; any/list).
   - `webgl_enabled` is true if it needs a canvas.
   - Stack fit: framework, React/Tailwind/StyleX version, SSR.
5. **Score the rest** (table below). Prefer the lowest cost that meets the brief.
6. **Prove the fallback**: static layer, reduced-motion path, no-WebGL path. A candidate without one needs a wrapper; count that work.
7. **Write the choice down** with the comparison table and the reason for each rejection; list new dependencies in the summary.

### Criteria

| Criterion | What to check | Where to read it |
| --- | --- | --- |
| Art-direction fit | Mood, tempo, density and shape language match the brief; it does not force a second visual language | style note, pattern summary |
| Stack fit | Framework, styling system, router coupling, SSR, install path | note "Install" and "Pitfalls" sections |
| Dependency cost | New packages, bundle weight, overlap with existing libraries (two animation systems is a defect) | pattern `dependencies`, note |
| GPU cost | `gpu_intensity` in the pattern; canvases, shader loops, DPR, offscreen pause | pattern `performance`, [performance](performance.md) |
| Accessibility | Reduced-motion branch, keyboard, names, focus styles, contrast, canvas alternative | note "Accessibility observations"; [accessibility](accessibility.md) |
| Maintenance signals | Pre-1.0 or deprecation windows, pinned version, `last_checked` date, whether upstream accepts contributions, planned a11y work, stale docs | `design-sensei sources show <id>`, note pitfalls |
| Licence class | Reuse class and any restrictions | `sources show`, [source usage](source-usage.md) |

Maintenance signals come only from the notes and registry: pinned commit, last-checked date, version in the note, changelog findings. Do not guess popularity. `design-sensei sources status --check-upstream` shows whether upstream moved since the pin.

### How the dials change the choice

| Setting | Effect |
| --- | --- |
| `design_variance` high | Accept less conventional components, but only with a mobile composition ([responsive design](responsive-design.md)) |
| `motion_intensity` 1-3 | CSS transitions; no animation library |
| `motion_intensity` 4-7 | One animation system (existing one first); few scroll moments |
| `motion_intensity` 8-10 | GSAP/Lenis/R3F allowed, each effect with a reduced-motion alternative; budget accordingly |
| `visual_density` high | Prefer a design system with tables, forms and charts (Astryx-like) over decorative effect libraries |
| `allowed_dependencies: none` | Reimplement from the idea with CSS/native APIs; copy-in components count as code you maintain |
| `reduced_motion: static_first` | Prefer components with a built-in reduced-motion branch, or wrap and default off |
| `performance_budget.max_webgl_canvases` | One live canvas by default; a second needs a reason |

## Comparison table template

Fill one row per candidate, including "native CSS".

```markdown
| Candidate | Pattern / source | Art fit | Stack fit | New deps | GPU | A11y / reduced motion | Maintenance | Reuse class | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| native CSS gradient | - | medium: no depth | yes | none | none | trivial | none | original | fallback layer |
| <pattern-id> | <source-id> | high: <why> | yes | <pkg> | low | wrapper needed | v0.x, pin | copy_with_attribution | chosen |
| <pattern-id> | <source-id> | high | no: Vue | - | high | none | - | license_review_required | rejected: stack |
```

## The sources at a glance

Reuse class is what search shows: `copy_with_attribution` needs notice kept; `license_review_required` means read the licence review first; `reimplement_only` and `reference_only` supply ideas, not code ([source usage](source-usage.md)). Facts below come from the notes linked in each row's source note column and `catalog/sources.yaml`.

### 15 downloadable sources

| Source | Use it for | Caveats | Reuse class |
| --- | --- | --- | --- |
| `taste-skill` | Anti-generic UI rules and the three dials; method, not a dependency ([note](../../../knowledge/design-intelligence/taste-skill.md)) | v2 labelled experimental; sponsor logos are not covered by MIT | copy_with_attribution |
| `design-md` | DESIGN.md token format and linter ([note](../../../knowledge/design-intelligence/design-md-format.md)) | Alpha specification | copy_with_attribution (Apache-2.0: keep NOTICE, state changes) |
| `awesome-opus-videos` | Mining prompt vocabulary ([note](../../../knowledge/design-intelligence/awesome-opus-videos.md)) | Mostly video/animation prompts, about ten for web pages; entries are third-party | copy_with_attribution |
| `liquid-logo` | Liquid-metal logo shader as a technique ([note](../../../knowledge/shaders/liquid-metal-logo.md)) | A browser tool, not a library; no WebGL fallback or reduced motion; big drawing buffer; demo logos are third-party marks | copy_with_attribution |
| `skiper-ui` | Ideas only: theme-toggle view transition, coverflow carousel, stepped feature card ([note](../../../knowledge/components/skiper-ui.md)) | Unofficial clone with no licence | reimplement_only |
| `vengeance-ui` | Copy-in animated landing components via shadcn-style registry; agent skill/MCP ideas ([note](../../../knowledge/components/vengeance-ui.md)) | 7 of 76 components honour reduced motion; 41 of 76 have no ARIA/role/key handling; imports whole GSAP and three; media in `public/` not reusable | copy_with_attribution |
| `fancy` | Text effects, cursor trails, physics, marquees ([note](../../../knowledge/components/fancy.md)) | One component checks reduced motion; marquees have no pause; Matter-based gravity can leak listeners; Tailwind tokens in demos | copy_with_attribution |
| `react-bits` | Large catalog of animated React components, strong GPU backgrounds ([note](../../../knowledge/components/react-bits.md), [catalog](../../../knowledge/components/react-bits-catalog.md)) | MIT + Commons Clause; 53 GPU backgrounds, 26 with neither visibility nor tab gating; uneven accessibility; variants not twins | license_review_required |
| `astryx` | Application design system: tokens, themes, app shell, charts, accessibility contracts ([note](../../../knowledge/components/astryx.md)) | Pre-1.0 (0.6.6), canary packages pinned exactly, global reset, no marketing sections, React only | copy_with_attribution |
| `react-three-fiber` | Declarative three.js scenes, on-demand rendering ([note](../../../knowledge/components/react-three-fiber.md)) | No reduced-motion or a11y handling; React only; heavy bundle; do not set state in the frame loop | copy_with_attribution |
| `liquid-glass-js` | WebGL refraction glass for one hero element ([note](../../../knowledge/shaders/liquid-glass.md)) | Elements are `div`s without keyboard support; one WebGL context per element; per-fragment cost high (about 770 texture reads by the note's count); no destroy method | copy_with_attribution |
| `shadergradient` | Animated gradient backgrounds, React and Vue ([note](../../../knowledge/shaders/shadergradient.md)) | MIT declared but no LICENSE file; no WebGL detection, context-loss or reduced-motion handling; always-on render loop; three.js peers | license_review_required |
| `img2threejs` | Image-to-procedural-3D workflow ([note](../../../knowledge/components/img2threejs.md)) | Procedural output only; typecheck gates need a showcase checkout; scores mislead on photographs | copy_with_attribution (Apache-2.0) |
| `lenis` | Smooth scroll, native touch by default ([note](../../../knowledge/animations/lenis.md)) | Non-passive listeners; v2 roadmap renames options (pin version); Safari frame cap | copy_with_attribution |
| `gsap` | Timelines, ScrollTrigger, SplitText ([note](../../../knowledge/animations/gsap.md)) | Custom licence (not OSI); does not read reduced motion; needs cleanup in frameworks | license_review_required |

### 3 reference sites (links only)

| Source | What it offers | Handling | Reuse class |
| --- | --- | --- | --- |
| `refero-styles` | Real website styles with DESIGN.md files ([note](../../../knowledge/website-references/refero-styles.md)) | Its robots.txt disallows AI crawlers: do not fetch or scrape; the user may browse it themselves | reference_only |
| `uxplanet-50-design-styles` | Article on design-style vocabulary ([note](../../../knowledge/website-references/uxplanet-50-design-styles.md)) | Inspection blocked; nothing reproduced; use the original taxonomy in [design styles](../../../knowledge/design-styles/README.md) | reference_only |
| `animmaster-lib` | Commercial animated component library ([note](../../../knowledge/website-references/animmaster-lib.md)) | Paid; redistribution prohibited; link only | reference_only |

## Rules against a second component system

- Detect first: `components.json` (shadcn), a design-system package, `components/ui/`, Tailwind theme, StyleX config, existing motion/GSAP/Lenis dependencies. Extend them.
- Copy-in components (React Bits, Vengeance UI, Fancy) are source you adopt: restyle them with the project's tokens, remove unused variants and demo content, and place them where the project keeps components. Do not leave a parallel `vendor-ui` tree.
- Never add Astryx (own theme, reset and StyleX) to a project that already has a design system; use it only for a new application UI or as a reference for tokens and accessibility ([[astryx-theme-token-system]]).
- One animation system per job: if GSAP is installed, do not add Motion for the same reveals; if Lenis exists, do not accept a component that creates its own (React Bits ScrollStack does).
- One smooth-scroll layer, one theme attribute owner (`Theme` in Astryx writes `data-theme` on `<html>`), one icon set, one font pairing.
- Prefer a native CSS answer for simple hover, focus, transitions and gradients.
- When combining sources (a text effect from one, a background from another), reconcile tokens, easing and reduced-motion handling so they read as one system.

## Checklist before saying done

- [ ] Shortlist compared in a table, including a native option; rejections explained
- [ ] Hard gates passed: licence class, `allowed_dependencies`, `webgl_enabled`, stack
- [ ] Chosen component restyled with project tokens; demo content, remote placeholder images and unused variants removed
- [ ] Static fallback, reduced-motion path and (for GPU) no-WebGL path in place
- [ ] No second component, theme or animation system introduced
- [ ] New dependencies and borrowed source ids listed in the summary; notices added where required

## Common mistakes

- Picking the most visually dramatic candidate and then wrapping it in fallbacks the brief did not need.
- Assuming a popular library handles reduced motion or keyboard access (most do not; see the counts above).
- Installing a design system into an app that has one.
- Treating the sample code in a note as permission to copy it; only the reuse class decides.
- Stacking three GPU backgrounds because each is "light" on its own.
- Reusing upstream media (photos, logos, models, fonts) because the code is MIT.

## Related

Patterns: [[react-bits-self-pausing-shader-backgrounds]], [[shader-gradient-background]], [[liquid-glass-css-fallback]], [[astryx-design-system-react]], [[vengeance-ui-registry-copy-paste-install]], [[lenis-gsap-scrolltrigger-sync]], [[r3f-lazy-canvas-webgl-fallback]].
Notes: [pattern index by source](../../../knowledge/pattern-index/by-source.md), [by category](../../../knowledge/pattern-index/by-category.md), [React Bits background budget](../../../knowledge/implementation-recipes/react-bits-heavy-background-budget.md), [Vengeance install and verify](../../../knowledge/implementation-recipes/vengeance-ui-install-and-verify-component.md).
References: [source usage](source-usage.md), [accessibility](accessibility.md), [performance](performance.md), [design principles](design-principles.md).
