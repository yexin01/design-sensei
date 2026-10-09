# Layout and composition

Grid systems, asymmetry, whitespace, bento, deliberate grid-breaking, section rhythm, hero composition and image treatment, tuned by `design_variance` and `visual_density`.

## When to load this

Load it when deciding page structure (step 2) and when building sections (step 4). Breakpoints and fluid behaviour are covered in [responsive design](responsive-design.md);
grouping, spacing scale and hierarchy in [design principles](design-principles.md). Values are starting points unless labelled as a standard.

## Decisions to make

| Decision | Options | Dial influence |
| --- | --- | --- |
| Grid | symmetric 12-column, asymmetric spans (7/5, 8/4), fractional (`2fr 1fr 1fr`), modular tiles | `design_variance` 1-3 symmetric; 4-7 asymmetric; 8-10 fractional or off-grid |
| Hero | centred, 50/50, asymmetric split, full-bleed image, product-led | variance low: centred or 50/50; mid and high: asymmetric or image-led |
| Section layouts | 2-3 (low), 3-4 per 8 sections (mid), 4+ with none repeated back to back (high) | `design_variance` |
| Containers | space and hairlines (low density), cards for related groups (mid), dividers and tonal bands (high) | `visual_density` |
| Whitespace | section padding 80-160 px (airy), 64-96 px (balanced), 24-48 px (dense) | `visual_density` |
| Grid-breaking | none, one planned break, coordinated breaks | `design_variance` |

Conflicts: variance 8-10 with density 8-10, keep data regions on a plain grid (variance 5 or lower) and spend the experiment on the header, imagery and empty states.
Variance 4 or higher requires a stated one-column order under 768 px.

## Grid systems

- Define the grid as tokens first: columns (12 wide, 8 tablet, 4 narrow), gutter (16-32 px), outer margin, max container width (1100-1280 px for content pages), baseline (4 or 8 px).
- Use CSS Grid, not floats or percentage hacks. Let content decide column count with intrinsic sizing where tiles are interchangeable:

```css
.grid { display: grid; gap: var(--space-6);
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr)); }   /* equal tiles, no breakpoints */
.page { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); column-gap: var(--space-6); }
.page > .lead  { grid-column: 1 / span 7; }
.page > .aside { grid-column: 9 / span 4; }   /* column 8 left empty on purpose */
@media (max-width: 47.99rem) { .page > * { grid-column: 1 / -1; } }
```

- Use `subgrid` (where supported) so nested items share parent tracks; fall back to the same explicit tracks if not.
- Use container queries (`container-type: inline-size`) so components adapt to their own width, not the viewport. The bento notes use a 840 px container breakpoint.
- Use `minmax(0, 1fr)` rather than `1fr` for text columns so long words cannot blow out the track. Use `min-height: 100dvh` for viewport-tall sections, not `100vh`.
- Astryx offers a worked primitive set: Stack, Grid with intrinsic columns, Layout (five-slot page topology), Section, with one numeric spacing scale and theme width points
  `sm` 640, `md` 768, `lg` 1024, `xl` 1280, `2xl` 1536 ([[astryx-responsive-layout-primitives]], [Astryx note](../../../knowledge/components/astryx.md)). It has no hero or marketing sections:
  compose those yourself.

## Asymmetry and whitespace

- Asymmetric splits (7/5, 8/4, 5/7 alternating) create direction; put the heading in columns 1-5 and the text in 7-11 for an editorial offset ([[style-editorial]], [[style-swiss-international-typographic]]).
- Whitespace is structure. Macro space (between sections) says "new idea", micro space (inside groups) says "related". Keep micro < group < section (see
  `astryx:docs/design/spatial-hierarchy.md`).
- Empty modules on a grid are intentional: leave a column empty rather than filling it with a decorative element.
- Constrain text to its measure (about 60-70 characters, see [typography](typography.md)) inside a wider container; the text column is usually 640-720 px.
- Do not centre-align content-heavy pages. Centre one short statement per section at most.

## Bento

Use for 6 to 8 self-contained ideas where size signals priority ([[style-bento-layouts]], [note](../../../knowledge/design-styles/bento-layouts.md)).

| Rule | Value |
| --- | --- |
| Columns | 4 from 1024 px, 2 from 600 px, 1 below (container queries preferred) |
| Spans | one hero tile 2x2, secondary 2x1, the rest 1x1; tile count equals content count, no filler |
| Gap and radius | one gap 8-20 px; radius 16-28 px, one value |
| Surface | one edge language, one or two tone steps from the page; at most two tinted tiles in view |
| Order | DOM order equals reading order; avoid `grid-auto-flow: dense` unless they still match; key spans to tile role, not `nth-child` |
| Mobile | collapse every span to one column; do not scale the mosaic down |
| Interactivity | a clickable tile is one link or button with one accessible name |

Starting points: [[vengeance-ui-bento-grids]] (copy_with_attribution; check each grid for reduced-motion handling), [[astryx-card-and-grid-collections]] (copy_with_attribution),
[[react-bits-bento-and-card-grids]] (license_review_required: use as a dependency per its terms, do not republish; pass the reduced-motion preference into its disable-animation prop).
Avoid the stereotype: a 3x2 grid of equal icon cards called bento.

## Breaking the grid on purpose

1. Build the aligned layout first. Break it after, with a written reason (emphasis, tension, rhythm).
2. Break in one place per section: an image bleeding past the container, a heading overlapping a photo by about 24 px (mid) up to 64 px (high), an element hanging into the gutter.
3. Keep an invisible structure: broken elements still align to a column edge, baseline or shared offset somewhere.
4. Never break text legibility or reading order. DOM order stays the reading order; use CSS placement, not `order`, to move things visually, and test the keyboard sequence.
5. Plan the mobile layout of every break (usually remove it). Overlaps and negative margins collapse to a clean single column.
6. Maximalist or brutalist layouts still need a hidden grid and rest areas ([[style-maximalism]], [[style-brutalism]]).

## Section rhythm

- Vary section layout, background tone and density so the page has a pulse: dense proof strip after an airy hero, a full-bleed image or colour block every three to five screens of text.
- Heuristics from the notes: at most two consecutive zigzag (image left, image right) sections; 3-4 distinct layouts per 8 sections at mid variance, 4+ at high; do not repeat a layout back to back at high variance.
- Product pages typically follow: header with primary action, hero, proof strip, 3-5 feature sections, a deep-dive on the main workflow, testimonials with real names, pricing, FAQ, final call to action, footer
  ([[style-product-led-saas]]). Adapt the order to the brief; keep one primary action visible.
- Section padding is a token (`--section-pad`, see [design principles](design-principles.md)); vary it deliberately, not randomly.
- Keep one rhythm of vertical spacing multiples; break it only with a stated reason.

## Hero composition

- The hero answers three questions in the first viewport: what is this, why should I care, what do I do next. Headline of 12 words or fewer, one sentence of support, one primary and at most one secondary action.
- One idea of visual weight: a product shot, a photograph, a type statement or a background field, not all four.
- Archetypes: product-led split (headline left, real interface right), image-led (full-bleed photo with a text panel or scrim), type-led (display type 8-20vw, [[style-kinetic-typography]]), atmospheric
  ([[style-aurora-gradient-mesh]] behind a short headline, text on the calm region), object-led (3D or product viewer, with a static fallback).
- Fit the hero to the viewport with `min-height: 100dvh` (or less if the next section should peek); keep the navigation to one line.
- Centred hero over a gradient is the default tell. If you choose it, justify it by `design_variance` 1-3 or a single short statement and change one other major element.
- Text over imagery needs a scrim or a reserved text area, tested on the busiest region of the image.
- Mobile: keep the primary action above the fold, compress the visual instead of dropping it, preserve the kicker-headline-support order.

## Image treatment

| Topic | Rule |
| --- | --- |
| Ratio and layout shift | give every image width, height or `aspect-ratio`; `object-fit: cover` inside a fixed box; use `<figure>` and `<figcaption>` for editorial images |
| Loading | LCP image eager with `fetchpriority="high"`; below-fold images `loading="lazy"`; responsive `srcset` and `sizes`; modern formats where supported |
| Consistency | one grade (temperature, contrast, grain) across all photos; do not tint with CSS filters to fake it |
| Crops | choose crops on purpose (full-bleed, tight, inset with caption); use `<picture>` for art-directed mobile crops |
| Text on image | scrim 35-55% or solid panel; measure the worst region (see [colour](color-systems.md)) |
| Hover and motion | zoom at most 1.03 inside an `overflow: hidden` frame; parallax a few percent only; none under reduced motion |
| Alt text | describe what the image shows or its purpose; empty `alt` for decoration; screenshots describe the interface |
| Real content | real screenshots and photographs, not `div` rectangles posing as a dashboard; label placeholders as placeholders |

For image-to-model and gallery treatments see [[r3f-product-showcase-scene]] and [[vengeance-ui-3d-image-carousels]]; both need a static fallback.

## Checklist before saying done

- [ ] Grid tokens defined and used; elements align to column edges or a shared offset
- [ ] Hero passes the three-question test in one viewport at 375 and 1280 px
- [ ] Section layouts vary per the dial band; no unintended repetition
- [ ] Every break from the grid has a reason, an alignment anchor and a mobile plan
- [ ] DOM order equals reading and keyboard order; one-column order stated under 768 px
- [ ] No horizontal scroll at 320 CSS px (WCAG 1.4.10 reflow); no clipped text at 200% zoom
- [ ] Images have dimensions or aspect ratio, correct loading hints, alt text and a consistent grade
- [ ] CLS at most 0.1 and LCP at most 2.5 s on the hero (budget defaults)

## Common mistakes

- Everything centred, three equal cards, repeated for every section.
- A grid drawn as decoration over a layout that does not align to it.
- Bento with filler tiles, equal loudness, or desktop spans that survive on phones.
- Overlaps and negative margins with no mobile plan, causing overflow.
- `order` or dense flow changing visual order away from the DOM and keyboard order.
- Hero taller than the viewport with the action below the fold; hero text over the brightest part of a photo.
- Uniform section padding everywhere, so the page has no pulse; or random padding with no scale.
- Images without dimensions, causing layout shift.

## Related

Patterns: [[astryx-responsive-layout-primitives]], [[astryx-card-and-grid-collections]], [[style-bento-layouts]], [[vengeance-ui-bento-grids]], [[fancy-stacking-cards]],
[[style-editorial]], [[style-swiss-international-typographic]], [[style-product-led-saas]].
Notes: [bento layouts](../../../knowledge/design-styles/bento-layouts.md), [editorial](../../../knowledge/design-styles/editorial.md),
[Swiss style](../../../knowledge/design-styles/swiss-international-typographic.md), [product-led SaaS](../../../knowledge/design-styles/product-led-saas.md),
[Astryx](../../../knowledge/components/astryx.md), [dials recipe](../../../knowledge/implementation-recipes/art-direction-brief-from-dials.md),
[stacking cards recipe](../../../knowledge/implementation-recipes/fancy-stacking-cards-scroll.md).
References: [art-direction.md](art-direction.md), [design-principles.md](design-principles.md), [typography.md](typography.md), [color-systems.md](color-systems.md),
[responsive-design.md](responsive-design.md), [performance.md](performance.md).
