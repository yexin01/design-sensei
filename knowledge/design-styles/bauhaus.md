---
title: "Bauhaus"
kind: design-style
summary: "Function-first geometry from the 1919-1933 German school: primary colours with black and paper, circles, squares and triangles, diagonal asymmetry, geometric sans-serif type and rule bars. Covers colour contrast of the primaries, shape-based layout in CSS and how to avoid clip-art Bauhaus."
source_ids: []
pattern_ids: [style-bauhaus]
updated: "2026-10-09"
---

# Bauhaus

Bauhaus was a German school of art, craft and design, founded in 1919 and closed under political pressure in 1933. Its graphic and product work shaped modern design by treating form as the result of purpose: basic geometry, a few primary colours, sans-serif letters and an asymmetric but carefully balanced page. On the web the style works when it behaves like a system, with shapes, colours and type each doing a job. It fails when circles and triangles are sprinkled over a page as decoration.

## Visual characteristics
- A palette of red, yellow and blue with black and a warm paper white; colours are flat, saturated and used in large fields.
- Three basic shapes (circle, square, triangle) used as structure, masks and counters, not as clip-art.
- Asymmetric balance, with diagonals and a strong horizontal and vertical armature of thick bars and rules.
- Geometric sans-serif letters, often lowercase, in bold weights, sometimes rotated 90 degrees along an edge.
- Photomontage and cut-out images placed on or across colour fields; overlaps are crisp, with no soft edges.
- No ornament, no gradients, no shadows; hierarchy by scale, position and colour contrast.

## When it fits, when it does not
- Fits: design schools, museums and exhibitions, architecture and furniture studios, event and festival posters, education and workshop programmes, product brands that value utility and craft, and portfolios of designers or makers.
- Poor fit: healthcare and wellness that need softness, luxury brands that rely on restraint and ornament, long legal or reference text, and dashboards that need a neutral frame for many data colours.
- Supporting influences that work: swiss-international-typographic, minimalism, editorial, flat-design, retro-vintage. Avoid glassmorphism, aurora-gradient-mesh, vaporwave, skeuomorphism and high-fashion-luxury.

## Typography
- Geometric sans-serifs with circular bowls: Jost, Josefin Sans, Outfit, Poppins, League Spartan, or Futura where licensed. Use a neutral system sans for body text if the display face is too distinctive for reading.
- Display: weight 700-800, `clamp(3rem, 9vw, 8rem)`, line height 0.95, tracking -0.02em. Lowercase headings are a legitimate Bauhaus move (the school explored a single-case alphabet); keep sentences and body copy in normal case, and set `lang` correctly.
- Body 17-18 px at 1.5, measure 55-65 characters, flush left and ragged right.
- Rotated labels via `writing-mode: vertical-rl` are good for margin captions of three or four words; never for paragraphs.
- Use two weights, 400 and 800. Avoid novelty fonts that merely reference the period.

## Colour
- Core set: paper #F3ECDD, ink #111111, red #C8200E, yellow #F2B705, blue #0B3D91.
- Safe text pairs: ink on paper is 16.1:1, ink on yellow 10.4:1, white on blue 10.0:1, paper on blue 8.5:1, blue on paper 8.5:1, white on red 5.7:1, paper on red 4.9:1, blue on yellow 5.5:1.
- Unsafe pairs: ink on red is 3.3:1 (large text at most), ink on blue 1.9:1, red on blue 1.75:1 (and the edge visibly vibrates), red on yellow 3.1:1, and yellow on paper 1.55:1, so yellow can never carry text, a thin rule or an input border on a paper ground.
- A brighter red #D62718 gives only 4.3:1 as text on paper; use #C8200E or darker when red is used as a text colour.
- Assign roles: red for the one action or focal shape, blue for structure and links, yellow for highlights and backgrounds, black for type and rules. Do not add green, orange or pastel variants; the discipline is the style.
- Proportions: roughly 60% paper, 20% black, 20% colour fields, with the three primaries in unequal amounts.

## Composition and layout
- Build on a modular grid (12 columns, 8 px unit) and then break it deliberately with one dominant diagonal, a rotated block or a shape that crosses the margin.
- Use heavy bars and rules as dividers, with thicknesses from a fixed set (4, 8, 16 px) so they feel designed.
- Shapes carry structure: a circle as a portrait mask or call-to-action badge, a square as a text panel, a triangle as an arrow or a corner cut. In CSS: `border-radius: 50%` with `aspect-ratio: 1`, `clip-path: polygon(0 100%, 100% 100%, 50% 0)`, and `transform: rotate()` for decoration only.
- Keep reading text horizontal and in DOM order. Diagonals belong to shapes, bars and large display words, not to paragraphs.
- Place text on a solid, uncluttered field with one of the safe pairs above; avoid text across the seam between two colours.
- Responsive: collapse to a single column and keep one hero shape and one bar; remove diagonal overlaps below 40 rem instead of shrinking them.

## Interaction and motion
- Motion is mechanical and economical: shapes slide along an axis, rotate in quarter turns or swap fill colour. 120-250 ms, linear or ease-out, with no bounce.
- Hover swaps the fill (paper to yellow, blue to ink) rather than adding shadows; pressed states can shift an element by 2-4 px.
- Focus rings: 3 px solid ink with a 3 px offset on paper; on red or blue fields use a white or paper ring.
- Reduced motion: remove slide, rotate and parallax movement; keep the colour swap and a static composition.

## Accessibility cautions
- Pure saturated red beside blue vibrates and tires readers; keep them separated by black, paper or a gap, and never put one behind the other as text.
- Do not use colour alone to distinguish primaries in charts; add labels or hatching, and test red-yellow-blue figures for colour-vision difference.
- Rotated and oversized type must stay real text in a sensible reading order; check 200% zoom and 320 CSS pixel reflow (WCAG 1.4.10) because fixed shapes and absolute positions often overflow.
- Decorative shapes should be `aria-hidden` or CSS-only. Informative shapes (a diagram, a status) need text equivalents.
- Forced-colors mode replaces background colours, so shape fields can vanish and text can land on a different ground. Give shapes and bars a border so they remain visible, and never put text over a shape that only exists as a background.
- Lowercase-only headings are fine for sighted readers, but do not apply `text-transform` to acronyms or proper names that screen readers or translators might need intact.

## Common mistakes
- Treating "primary colours plus circles" as the whole style; the structure and asymmetry are the point.
- Symmetric, centred layouts with a row of three equal feature cards.
- Adding gradients, soft shadows or rounded rectangles that contradict the flat geometry.
- Using a Bauhaus-named novelty typeface instead of a plain geometric sans.
- Mixing in extra hues or pastels, which turns it into generic playful design or Memphis.
- Confusing it with De Stijl (a strict orthogonal grid with no diagonals or circles) or with Swiss style (neutral palette, no shapes as images).
- Overlapping shapes on top of headings so the text becomes unreadable.

## Typical mistakes of AI-generated versions
- A red circle, a yellow triangle and a blue square scattered at random behind a centred headline, with pastel tones and a drop shadow.
- A "Bauhaus" colour scheme of beige, terracotta and sage that has none of the primaries or any geometry.
- Gradients inside the shapes and rounded buttons in every colour.
- Red headings on a blue block, and ink text on red buttons that fall below 4.5:1.

## How to build it
- Pattern: `style-bauhaus`. No local source contains a Bauhaus implementation, so this recipe is original. Start with tokens, then position a few shapes on a grid and keep text on the paper or on a safe colour field:

```css
:root { --paper: #F3ECDD; --ink: #111111; --red: #C8200E; --yellow: #F2B705; --blue: #0B3D91; --u: 8px; }
body { background: var(--paper); color: var(--ink); font: 400 1.0625rem/1.5 Jost, Futura, "Century Gothic", system-ui, sans-serif; }
h1 { font-weight: 800; font-size: clamp(3rem, 9vw, 8rem); line-height: .95; letter-spacing: -.02em; text-transform: lowercase; }
.poster { display: grid; grid-template-columns: repeat(12, 1fr); gap: var(--u); padding: calc(var(--u) * 3); }
.panel { grid-column: 1 / span 6; background: var(--blue); color: #fff; padding: calc(var(--u) * 4); }
.disc { grid-column: 8 / span 4; background: var(--red); border-radius: 50%; aspect-ratio: 1; }
.wedge { grid-column: 7 / span 2; background: var(--yellow); clip-path: polygon(0 100%, 100% 100%, 50% 0); aspect-ratio: 1; }
.bar { grid-column: 1 / -1; height: calc(var(--u) * 2); background: var(--ink); }
a { color: var(--blue); text-decoration-thickness: .12em; text-underline-offset: .2em; }
a:focus-visible { outline: 3px solid var(--ink); outline-offset: 3px; }
@media (max-width: 40rem) { .poster > * { grid-column: 1 / -1; } .wedge { display: none; } }
@media (forced-colors: active) { .panel, .disc, .wedge, .bar { border: 2px solid CanvasText; } }
@media (prefers-reduced-motion: no-preference) { .disc { transition: transform .2s ease-out; } .disc:hover { transform: translateX(8px); } }
```

- Check the pairs: white on the blue panel is 10.0:1, link blue on paper is 8.5:1, and the ink focus ring is 16.1:1 against paper.
- Mark purely decorative `.disc`, `.wedge` and `.bar` elements `aria-hidden="true"` in the markup.

## Sources
Original guidance written for this project from general design history and computed contrast ratios. No third-party text or local source files are used.
