# Cards and grids playbook

Choose and build card collections, bento layouts, pointer-lit cards and stacked or staggered card sections that keep reading order, hierarchy and mobile layout intact.

In this file `design-sensei` means `${CLAUDE_SKILL_DIR}/scripts/design-sensei`.

## When to use / when not

- Use for feature sections, option pickers, galleries, metric tiles and case-study indexes.
- Not for sequential content (steps, tutorials), long reading, or uniform catalogues where a plain grid or table is better. Use a section, not a card, to group a page region (the Astryx guidance behind [[astryx-card-and-grid-collections]]).
- The most common failure is a grid of equal cards with an icon and a title. Decide tile roles and priority first.

## Pick the approach

| Situation | Pick | Reuse class | Notes |
| --- | --- | --- | --- |
| Layout language for varied-size tiles | [[style-bento-layouts]] | license_review_required | Style note; hero tile 2 by 2, secondary 2 by 1, six to eight tiles, one column on phones. |
| App UI: items, navigation targets, pick-one options | [[astryx-card-and-grid-collections]] with [[astryx-responsive-layout-primitives]] | copy_with_attribution | Card, ClickableCard, SelectableCard in an intrinsic `Grid`. React 19, pre-1.0. |
| Animated bento in a Tailwind and framer-motion project | [[vengeance-ui-bento-grids]] | copy_with_attribution | `research-bento-grid` honours reduced motion; others do not. `expandable-bento-grid` has no dialog role or focus trap. Replace default avatars. |
| Bento, masonry or colour-reveal grid from a library | [[react-bits-bento-and-card-grids]] | license_review_required | MagicBento content is hard-coded in the file; no ARIA or reduced-motion check in the three. Pass `disableAnimations`. |
| Spotlight, tilt or border-glow on one card | [[react-bits-pointer-lit-cards]] | license_review_required | Decorative; pointer only. SpotlightCard checks reduced motion, the others do not. |
| Cards that stack as the page scrolls | [[fancy-stacking-cards]] | copy_with_attribution | Sticky plus scale. Sticky fails under an ancestor with overflow other than visible. Recipe drops scaling under reduced motion. |
| Staggered reveal of a card row | [[gsap-stagger-reveal]] | license_review_required | `ScrollTrigger.batch`, step about 70 ms, cap about 8 items. Without GSAP use IntersectionObserver ([[motion-principles]]). |
| Reorder, filter or expand cards with animation | [[gsap-flip-layout-transition]] | license_review_required | No recipe yet. Under reduce apply the change immediately; keep focus on the same logical element. |
| KPI tiles above a chart | [[astryx-kpi-stat-row]] | copy_with_attribution | See [data visualization](data-visualization.md). |
| Idea: stepped feature card with timed cross-fades | [[skiper-ui-stepped-feature-card]] | reimplement_only | No licence granted. Read the note for the idea, write your own code and assets. |
| 3D or ring image carousel | [[vengeance-ui-3d-image-carousels]] | copy_with_attribution | See [product showcases](product-showcases.md). |

Dials: `visual_density` 1-3 means two or three large cards per row with generous gaps; 8-10 allows dense tiles with 14 px minimum text. `design_variance` low means a regular grid; high allows a bento with a clear lead tile. `motion_intensity` at most hover lift and one once-only entrance below level 5.

## Search commands

```bash
design-sensei search "bento grid" --category card-grid,design-style
design-sensei search "card hover" --category card-grid --reduced-motion-safe --max-gpu low
design-sensei search "stagger reveal" --category animation,scroll
design-sensei search "card grid layout" --scope docs
```

## Implementation steps

1. List the items and rank them. Assign roles (lead, support, small) before choosing a layout. Write real content; thin content is a reason not to use a bento.
2. Build the grid with CSS Grid and `minmax()` or container queries. Typical breakpoints from the [bento note](../../../knowledge/design-styles/bento-layouts.md): four columns from 1024 px, two from 600 px, one below. Collapse every span to one column on phones; do not scale a desktop mosaic down.
3. Keep DOM order equal to reading order. Avoid `grid-auto-flow: dense` and `order` unless keyboard order still matches. Key spans to classes for the tile role, not `nth-child`.
4. A clickable card is one link or button with one accessible name. Do not overlay several targets; if nested actions exist, follow the ClickableCard approach where inner links and buttons work independently.
5. One surface language (hairline border or soft shadow), one radius system, tabular numerals for stats, `min-height` rather than fixed height, calls to action pinned to the tile bottom.
6. Add motion last: hover lift 2-4 px over 150-250 ms; entrance stagger 60-100 ms per tile over 400-600 ms, once. Pointer effects only under `(hover: hover) and (pointer: fine)`.
7. If installing from a library, use the recipes: [Vengeance install](../../../knowledge/implementation-recipes/vengeance-ui-install-and-verify-component.md), [React Bits install](../../../knowledge/implementation-recipes/react-bits-choose-variant-and-install.md). Replace placeholder images and avatars with licensed assets.

## Accessibility and performance gates

- Text 4.5:1 inside tiles including gradient areas; tint at most two tiles per viewport. Hairline borders at 8-12 percent alpha are not control boundaries.
- Autoplay inside a tile (carousel, rotating demo) over 5 s needs a pause control and must stop under reduced motion.
- Truncated text needs an accessible way to expand; do not shrink type below 14 px to fit a fixed height.
- Reduced motion: no stagger, spotlight, tilt or particles; state changes instantly.
- CLS at most 0.1: fixed `aspect-ratio` on images, reserved heights, no hidden-until-JS cards above the fold (they also delay LCP).
- Drive pointer effects with `transform`, `opacity` or CSS variables, not layout properties. The agent-style bento with many simultaneous animations is unmeasured: profile it.

## Common mistakes

- Three identical cards with icon, heading and text; every tile with a glow, a gradient and an animation so none leads.
- Spans that only work at one width; more than eight tiles; copy that does not fit and gets clipped.
- Expanding cards that open an overlay with no dialog role or focus management (`expandable-bento-grid` has none and also resets `document.body.style.overflow` on every change).
- Using MagicBento-style hard-coded content without editing it for the product.
- Copying React Bits or Skiper UI files (licence gate: React Bits is use-in-app only; Skiper UI has no licence, ideas only).

## Where to read more

- Notes: [bento layouts](../../../knowledge/design-styles/bento-layouts.md), [Astryx](../../../knowledge/components/astryx.md), [Vengeance UI](../../../knowledge/components/vengeance-ui.md), [React Bits catalog](../../../knowledge/components/react-bits-catalog.md), [Fancy components](../../../knowledge/components/fancy.md), [Skiper UI](../../../knowledge/components/skiper-ui.md).
- Recipes: [stacking cards on scroll](../../../knowledge/implementation-recipes/fancy-stacking-cards-scroll.md), [GSAP text reveal and stagger](../../../knowledge/implementation-recipes/gsap-text-reveal-and-stagger.md), [motion-safe wrapper](../../../knowledge/implementation-recipes/vengeance-ui-motion-safe-wrapper.md).
- Related playbooks: [microinteractions](microinteractions.md), [data visualization](data-visualization.md), [cursor interactions](cursor-interactions.md), [responsive layouts](responsive-layouts.md), [product showcases](product-showcases.md).
- References: [layout composition](../references/layout-composition.md), [responsive design](../references/responsive-design.md), [component selection](../references/component-selection.md).
