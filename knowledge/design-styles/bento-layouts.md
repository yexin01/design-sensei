---
title: "Bento layouts"
kind: design-style
summary: "A modular grid of rounded tiles of different sizes, each holding one self-contained idea. Covers size-as-priority, responsive collapse, container queries, reading-order and motion-safety rules, with two verified local implementations."
source_ids: [react-bits, taste-skill, vengeance-ui]
pattern_ids: [style-bento-layouts]
updated: "2026-10-09"
---

# Bento layouts

A bento layout arranges content as tightly packed, rounded tiles of varied sizes, like the compartments of a lunch box. Each tile carries one idea: a statistic, a small interface fragment, a sentence and an image. Tile size signals priority, so the grid doubles as an overview and as a rhythm. It is common in product feature sections, dashboard overviews and portfolio indexes. It fails when the grid is filler for thin content.

## Visual characteristics
- Rounded rectangles (radius 16-28 px) in a tight grid with one uniform gap (8-20 px).
- Sizes follow importance: one hero tile (2 by 2), supporting tiles (2 by 1 or 1 by 2), small tiles (1 by 1).
- One surface language (a hairline border or a soft shadow) and one or two surface tones.
- Embedded micro-demos in tiles: a mini chart, a toggle, a stat, a UI fragment.
- A single accent per tile, with few tinted tiles in view at once.

## When it fits, when it does not
- Fits: feature overviews on product pages, dashboard summaries, portfolio and case-study indexes, about pages, app promotion pages, settings overviews.
- Poor fit: sequential content (steps, tutorials), long-form reading, catalogues whose items are uniform (use a regular grid), and any case where tile content is thin.
- Supporting influences that work: product-led-saas, minimalism, dark-technical-developer-tools, neo-brutalism, swiss-international-typographic, a restrained glassmorphism. Avoid pairing with editorial long reads.

## Typography
- Tile title 18-24 px at weight 600, one or two lines; tile body 14-16 px, three lines at most. The hero tile may carry a 40-72 px number or phrase at tracking -0.02em.
- One type scale for all tiles. If copy does not fit, shorten the copy instead of shrinking the type below 14 px.
- Tabular numerals for statistics. Use `line-clamp` only with an accessible way to expand.

## Colour
- Tile surfaces one or two steps from the page (for example #0F1115 page, #171A21 tile in dark; #F6F6F4 page, #FFFFFF tile in light).
- Hairline borders at 8-12% white are about 1.2-1.4:1 on a dark page: fine as tile edges, not as the boundary of an interactive control inside a tile.
- Gradients inside tiles must keep 4.5:1 under the text area; tint at most two tiles per viewport.

## Composition and layout
- Columns: four from 1024 px, two from 600 px, one below. This is exactly what the local MagicBento stylesheet does (cards with a 20 px radius, a 4 by 3 ratio and a 0.5 em gap).
- Spans: a hero 2 by 2, secondary 2 by 1, the rest 1 by 1; six to eight tiles per grid. Use `grid-auto-flow: dense` only if DOM order still matches the visual reading order.
- Use container queries so tiles adapt to their own width. The local research-bento-grid switches layout at a 840 px container width instead of a viewport width.
- Give tiles `min-height` rather than fixed height, and pin calls to action to the tile bottom so they align across a row.
- Collapse every span to one column on phones; do not scale a desktop mosaic down.

## Interaction and motion
- Hover: lift 2-4 px and shift the border or glow over 150-250 ms. A cursor spotlight is decoration only.
- Entrance: stagger 60-100 ms per tile over 400-600 ms, once. In-tile animations should start when visible and loop slowly.
- Reduced motion: no stagger, spotlight, tilt or particles; stop any autoplay; change state instantly.

## Accessibility cautions
- Keep DOM order equal to the intended reading order; `order` and `dense` flow can make keyboard order disagree with what is shown.
- A tile that is clickable should be one link or button with one accessible name, not a card containing several overlapping targets.
- Position-based spans (`nth-child`) break when content is reordered or filtered; prefer classes tied to tile role.
- Autoplay inside tiles (carousels, rotating demos) needs a pause control and must stop under reduced motion.

## Common mistakes
- Equal loudness: every tile has a gradient, glow and animation, so none leads.
- Random spans with no hierarchy, or more than eight tiles.
- Tiny text to fit fixed-height tiles; text clipped at narrow widths.
- Mobile layouts that keep two narrow columns.

## Typical mistakes of AI-generated versions
- A 3 by 2 grid of equal cards with an icon and a title, called bento.
- Gradient and glow on every tile, plus lorem-style copy and fake dashboards built from `div` rectangles.
- Spans keyed to child index with no rule for mobile.

## How to build it
- Pattern: `style-bento-layouts`. Start with the tile roles and priorities, then the grid, then the surface language, then in-tile content.
- `vengeance-ui:src/components/ui/research-bento-grid.tsx`: a twelve-column, two-row bento at 840 px container width and one column below it, with Framer Motion's `useReducedMotion` used to stop autoplay and animated loops. `vengeance-ui:src/components/ui/why-us-bento.tsx` is a simpler three-column version with `col-span-2` and `row-span-2` tiles.
- `react-bits:src/content/Components/MagicBento/MagicBento.jsx` and `.css` (described only; react-bits is licence-restricted): GSAP-driven spotlight, border glow, particles, tilt and magnetism per card. It disables effects through a `disableAnimations` prop and at widths of 768 px or less, but does not read `prefers-reduced-motion`, so pass the media query result into that prop.
- `taste-skill:skills/soft-skill/SKILL.md` describes an asymmetric bento archetype with a mandatory single-column collapse on phones.

## Sources
Original guidance written for this project. vengeance-ui and taste-skill are MIT-licensed; react-bits is MIT with the Commons Clause and is described, not quoted.
