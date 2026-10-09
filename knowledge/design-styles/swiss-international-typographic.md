---
title: "Swiss / International Typographic Style"
kind: design-style
summary: "Grid-governed layout, flush-left sans-serif type, objective imagery and a tiny palette: hierarchy comes from scale, weight and position on an explicit grid, never from decoration. Guidance for building it on the web with CSS Grid."
source_ids: [astryx, taste-skill]
pattern_ids: [style-swiss-international-typographic]
updated: "2026-10-09"
---

# Swiss / International Typographic Style

The Swiss, or International Typographic, Style organises a page with an explicit grid, a single neo-grotesque sans-serif family, flush-left ragged-right text, objective photography and almost no colour. Everything that looks designed is a consequence of alignment and scale contrast. On the web it translates well because CSS Grid expresses the underlying logic directly.

## Visual characteristics
- A visible structure: modular columns and rows, strong alignment axes, text blocks pinned to cell edges.
- One sans-serif family in two or three weights; flush-left, ragged-right text; very large numerals or words against small, uniform text.
- Negative space treated as an active element, often asymmetric (heading in columns 1-5, text in 7-11).
- Black, white and one signal colour, traditionally red; photography is documentary and often monochrome.
- Hairline rules, numbered sections and small metadata labels instead of boxes and icons.

## When it fits, when it does not
- Fits: technical documentation and product sites, research and institutional sites, architecture and design studios, event programmes, any page with many parallel items to organise.
- Poor fit: warm or playful consumer brands, hospitality, entertainment, anything that depends on texture, ornament or emotional softness.
- Supporting influences that work: minimalism, editorial, generative-design, a restrained kinetic-typography. Do not mix with maximalism, skeuomorphism or vaporwave.

## Typography
- Family: a neo-grotesque (Helvetica Neue or Now, Neue Haas Grotesk, Akzidenz-Grotesk, Univers and Suisse are commercial; Inter, Archivo, Public Sans and IBM Plex Sans are free alternatives).
- Scale: pick one ratio between 1.25 and 1.5 and use few steps, for example 12 / 16 / 24 / 36 / 56 / 96 px. Fluid sizes via `clamp()` for the top steps only.
- Weights: two (400 and 500-700). Tracking -0.02 to -0.04em at 56 px and above, 0 for body, +0.04 to +0.08em for uppercase labels at 11-12 px.
- Leading: 1.05-1.15 for display, 1.4-1.5 for body, snapped to a 4 or 8 px baseline unit so neighbouring columns share rows.
- Use `font-variant-numeric: tabular-nums` for tables and counters. Never justify; turn hyphenation off in headings.

## Colour
- Black on white or off-white paper (#F4F4F0), plus one signal colour with one job (links, one status, one rule).
- Pure red #E30613 is 4.88:1 on white but 4.43:1 on #F4F4F0, which misses AA for small text; #D40511 gives 4.97:1 on that paper.
- No gradients, shadows or translucency. Depth comes from scale and position only.
- Dark variant: near-black (#0A0A0A) and white text with the same single accent; #FF2A2A on #0A0A0A is 5.3:1.
- Photography stays monochrome or uses one consistent duotone.

## Composition and layout
- 12 columns for wide layouts (6 for narrow), 16-32 px gutters, an 8 px baseline. Use CSS Grid with `subgrid` so nested items inherit the same tracks.
- Align everything to column edges and leave some modules empty on purpose. Large numerals may hang into the gutter.
- 1 px rules divide sections. A cheap way to draw them: a grid with `gap: 1px` whose parent and children have different backgrounds.
- Tables, lists and indexes are first-class components; images are sized to whole modules (3 by 4, 6 by 3).
- Responsive: reduce columns (12, 8, 4) while keeping the alignment logic. Do not scale type linearly with the viewport.

## Interaction and motion
- Crisp and short: 120-200 ms, ease-out or linear, fades and instant state changes. No bounce, overshoot or parallax.
- Hover inverts the cell (black fill, white text) or underlines. Focus rings are 2 px, offset 2 px, in black or the accent.
- If any entrance motion is wanted, draw the grid rules in at load (600 ms or less) or count numbers up, one effect at a time.
- Reduced motion: remove the entrance effects; every other state change is already instant.

## Accessibility cautions
- Tiny uppercase labels (10-11 px) are the usual failure. Keep 12 px or larger at 4.5:1 or better.
- Red must not be the only status cue; pair it with a word or icon.
- Dense multi-column tables break reflow at 320 CSS px (WCAG 1.4.10); give them a stacked-row layout on phones.
- Do not rely on alignment alone for grouping. Keep headings, lists and landmarks semantic.

## Common mistakes
- "Swiss" read as "clean": centred layouts, no grid, one font size.
- More than three weights or more than six sizes, which dissolves the system.
- Columns whose baselines differ by a few pixels because spacing is not tokenised.
- The accent colour used on five different things, so nothing is emphasised.
- Adding texture or soft shadows to make it friendlier; the style stops working.

## Typical mistakes of AI-generated versions
- Inter at arbitrary sizes, centred headings, three equal cards, gradients and drop shadows under a "Swiss" label.
- Decorative grid lines drawn on top of a layout that does not actually align to them.
- Section numbers (01, 02, 03) pasted as ornament with no structural meaning.

## How to build it
- Pattern: `style-swiss-international-typographic`. Write the grid as tokens first (columns, gutter, margin, baseline) and build every component on them.
- Spacing principle to follow: space and alignment establish groups before any card or border is added (`astryx:docs/design/spatial-hierarchy.md`, a draft design record).
- Role hierarchy and measure: `astryx:docs/design/typography-hierarchy.md`.
- A harsher cousin exists in the "Swiss Industrial Print" archetype of `taste-skill:skills/brutalist-skill/SKILL.md` (off-white substrate, heavy neo-grotesque, visible dividing lines, one red accent); read it as an opinionated variant, not as the baseline.

## Sources
Original guidance written for this project. astryx and taste-skill are MIT-licensed and cited as reference only.
