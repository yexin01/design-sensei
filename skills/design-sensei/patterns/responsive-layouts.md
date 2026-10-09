# Responsive layouts playbook

Pick a layout approach for each page region, write it mobile-first, and verify from 320 to 1920 px, including the heavy effects that must degrade on small devices.

The rules and values live in the [responsive design reference](../references/responsive-design.md); this playbook maps situations to patterns and steps. Only one catalog pattern is in the `responsive-layout` category (Astryx), so most guidance here is original CSS practice plus the neighbouring patterns below.

## When to use / when not

- Use for every new section, page shell, card collection or adapted effect. Load the reference when writing CSS for a new section.
- If the project already has a grid, breakpoint tokens or a design system (shadcn, Astryx, Tailwind config), extend it; do not add a second one.
- Do not treat shrinking the desktop layout as "responsive". Dials: `design_variance` 8-10 needs a deliberate mobile composition; `visual_density` 8-10 needs real mobile information design (tabs, disclosure, tables that reflow); `motion_intensity` above 5 gives phones about two points less (heuristic from the scroll guide).

## Pick the approach

| Region or situation | Approach | Pattern / reuse class | Notes |
| --- | --- | --- | --- |
| Card or tile collection | Intrinsic grid: `repeat(auto-fit, minmax(min(100%, 16rem), 1fr))`; Astryx `Grid columns={{minWidth, max}}` if installed | [[astryx-card-and-grid-collections]], [[astryx-responsive-layout-primitives]] (copy_with_attribution) | No breakpoints needed; `min(100%, ...)` prevents narrow-container overflow. |
| Feature overview with priority | Bento: four columns from about 1024 px, two from about 600 px, one below (heuristic from the style note) | [[style-bento-layouts]] (license_review_required), [[vengeance-ui-bento-grids]] (copy_with_attribution), [[react-bits-bento-and-card-grids]] (license_review_required) | Collapse every span on phones; DOM order = reading order; container queries for tiles. See [cards and grids](cards-and-grids.md). |
| App with sidebar | Shell with side nav that becomes a drawer below a width point | [[astryx-app-shell-navigation]] (copy_with_attribution) | Drawer is a modal dialog with focus trap; see [navigation](navigation.md). |
| Reusable widget in sidebar and main | `@container` queries on the component | [[astryx-responsive-layout-primitives]] for tokens and width points sm 640 / md 768 / lg 1024 / xl 1280 / 2xl 1536 | Components size to their slot; page structure still uses media queries. |
| Strict grid, editorial or Swiss composition | CSS Grid with named columns, fluid top type steps only | [[style-swiss-international-typographic]], [[style-editorial]] (copy_with_attribution) | Define the narrow-screen reorder explicitly; avoid `order` that breaks keyboard order. |
| Type scale and spacing | `clamp()` with a `rem` term for display; fixed `rem` for body | [[astryx-typography-scale]] (copy_with_attribution), [[astryx-theme-token-system]] | See [typography](../references/typography.md). |
| Scroll effects by viewport | `gsap.matchMedia()`: pinned only for wide + fine pointer; stacked reveals below | [[gsap-match-media-reduced-motion]], [[gsap-scrolltrigger-pin-scrub]] (license_review_required) | See [scroll storytelling](scroll-storytelling.md). |
| WebGL/R3F on phones | Static layer, lower `dpr`, lazy mount | [[r3f-lazy-canvas-webgl-fallback]], [[r3f-adaptive-resolution-performance]], [[webgl-effect-fallback-and-reduced-motion]] | See [3D scenes](three-dimensional-scenes.md), [background shaders](background-shaders.md). |
| Glass surfaces on small devices | Plain CSS glass; no WebGL refraction | [[liquid-glass-css-fallback]] | See [liquid glass](liquid-glass.md). |
| Hover-driven effects | Mount only under `(hover: hover) and (pointer: fine)` | [[fancy-cursor-proximity-text]] | See [cursor interactions](cursor-interactions.md). |

Default when nothing else is specified: mobile-first CSS Grid/flex with `gap`, intrinsic auto-fit grids, fluid display type, container queries only for reusable widgets, media queries for page structure.

## Search commands

```bash
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "responsive layout grid" --category responsive-layout
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "bento grid" --category card-grid --reduced-motion-safe
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "mobile navigation drawer" --category navigation
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "matchMedia reduced motion" --scope all --limit 5
${CLAUDE_SKILL_DIR}/scripts/design-sensei eval .     # RESP-001..003, A11Y-005, PERF-001, PERF-006, TYPO-002
```

## Implementation steps

1. Inventory the existing breakpoints, spacing tokens, container widths and layout components; reuse them.
2. Write the 375 px layout first: single column, readable measure (about 45-75 characters, `max-width: 65ch`, heuristic), `gap` for spacing, logical properties (`margin-inline`, `padding-block`) so RTL works.
3. Add a breakpoint only where the layout breaks (content-driven), named as a token. Check the awkward 768 px state: no orphan cards or over-wide text.
4. Fluid type: `clamp(min, rem + vw term, max)` always keeping a `rem` part so browser zoom works; keep the largest within roughly 2.5 times the smallest (heuristic). Body stays fixed `rem`.
5. Heights: `svh` when content must always fit (pinned stages, full-screen heroes), `dvh` to track the visible area, with a `vh` fallback line before. Avoid `100vw` for full-width elements when a scrollbar exists.
6. Media: `width`/`height` or `aspect-ratio` on every image; `srcset`/`sizes`; `<picture>` for art-directed crops; never lazy-load the LCP image; replace remote placeholder images.
7. Touch: no hover-only information; targets >= 24x24 CSS px (44 recommended); inputs at 16 px or more; cap sticky bars and test with the keyboard open.
8. Gate heavy effects with `matchMedia` for width, pointer and reduced motion (plus `saveData` where available) and keep a static layer; one live canvas at most.
9. Screenshots at 375, 768, 1280, 1920, plus 320 px and 200% zoom, a short landscape height and a reduced-motion pass. Detect overflow with `document.documentElement.scrollWidth > document.documentElement.clientWidth`.

## Accessibility and performance gates

- [ ] Viewport meta present, zoom allowed (no `user-scalable=no`); `viewport-fit=cover` plus `env(safe-area-inset-*)` on notched devices.
- [ ] Reflow at 320 CSS px and 400% zoom without two-axis scrolling (WCAG 1.4.10); long words and URLs wrap.
- [ ] Reading order = DOM order after every reorder, `order` or dense grid flow.
- [ ] Targets and contrast: 24x24 minimum, 44 recommended; 4.5:1 / 3:1.
- [ ] Reduced motion at 375 and 1280: static stacked layout, nothing hidden.
- [ ] CLS <= 0.1 (sized media, `min-height` not fixed heights), LCP <= 2.5 s on mobile, INP <= 200 ms; heavy libraries lazy-loaded within `performance_budget`.
- [ ] No horizontal scroll at any inspected width; eval has no RESP errors.

## Common mistakes

- Designing 1280 px first and squeezing; breakpoints copied from device lists.
- `font-size` in `vw` alone, or `clamp()` without a `rem` term.
- Bare `100vh` heroes cut off by mobile browser bars; fixed-height text containers.
- A bento or three-column grid kept at two narrow columns on phones; `nth-child` spans that break on reorder.
- Pinned sequences, cursor effects or full-viewport shaders shipped to touch devices.
- Hover menus with no tap path; tooltips as the only label.
- Verifying only at one desktop width; trusting DevTools throttling as a phone test.

## Where to read more

- [Responsive design reference](../references/responsive-design.md), [layout composition](../references/layout-composition.md), [performance](../references/performance.md), [accessibility](../references/accessibility.md), [design QA](../references/design-qa.md)
- [Astryx note](../../../knowledge/components/astryx.md), [Bento layouts](../../../knowledge/design-styles/bento-layouts.md), [Swiss style](../../../knowledge/design-styles/swiss-international-typographic.md), [scroll storytelling mobile strategy](../../../knowledge/animations/scroll-storytelling.md), [heavy background budget](../../../knowledge/implementation-recipes/react-bits-heavy-background-budget.md)
- Related playbooks: [cards and grids](cards-and-grids.md), [navigation](navigation.md), [hero sections](hero-sections.md)
