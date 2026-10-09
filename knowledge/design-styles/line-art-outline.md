---
title: "Line art and outline"
kind: design-style
summary: "Interfaces drawn with strokes of one consistent weight instead of fills: outlined icons, contour illustrations, hairline rules and outlined display type. Covers stroke discipline, 3:1 contrast for thin lines, draw-on motion with stroke-dashoffset, forced-colors handling and the weak affordance of outline-only controls."
source_ids: [vengeance-ui]
pattern_ids: [style-line-art-outline]
updated: "2026-10-09"
---

# Line art and outline

Line art builds the interface from strokes instead of masses of colour: contour illustrations, outlined icons, hairline dividers, diagrams, ghost buttons and large outlined words. It trades weight for precision, so everything depends on discipline. One stroke weight, one cap and join style and one construction grid make a set read as designed; mixed weights read as a pile of clip art. The same technique can feel technical (blueprints, schematics), editorial (engraving, contour portraits) or friendly (a hand-drawn wobble), depending on how the line is drawn. It is related to neo-brutalism only on the surface: neo-brutalism wants thick outlines, flat fills and offset shadows, while line art wants fine, even strokes and empty space.

## Visual characteristics
- A uniform stroke width, for example 1.5 to 2 px on a 24 px icon grid and 1 to 2 px for rules, with caps and joins (round or butt, mitred or round) chosen once.
- Little or no fill; the page ground does the filling. When fills appear they are flat spot colours, sometimes deliberately offset from their outline.
- Contour drawings of objects, buildings, maps and people, including continuous-line drawings made from one unbroken path.
- Outlined display type, hairline borders and ghost (outline) buttons.
- Technical variants: blueprint (pale lines on a deep blue), isometric wireframes, dimension lines and dashed construction lines. Organic variants: sketchy, doodled, slightly wobbling strokes.

## When it fits, when it does not
- Fits: icon systems, onboarding and product-education illustration, architecture, design and craft brands, stationery, documentation and diagrams, analytics and fintech with a light tone, portfolios.
- Poor fit: dense tables and charts where fills encode values, loud promotional pages that need mass and appetite, products sold on true colour, small mobile text, audiences with low vision who need strong affordances.
- Supporting influences that work: minimalism, editorial, swiss-international-typographic, generative-design, retro-vintage (engraving), japanese-minimalism. Avoid skeuomorphism, glassmorphism, claymorphism, y2k and neo-brutalism.

## Typography
- Match the text to the line. A monoline sans such as Jost, Outfit, DM Sans or Work Sans has stems close to a 1.5 px icon stroke at 16 px; a heavy slab beside hairline icons looks like two systems.
- Outlined display words only large (64 px and up), weight 700 or more, with a 1.5 to 2 px stroke. At body sizes the outline closes up. Variable fonts show their internal overlapping contours when stroked, so use a static instance, or fill and stroke the text in the same colour.
- Body text stays filled. Use a handwritten face (Caveat, Kalam) only for short annotations.
- CJK: dense glyphs fill in when outlined, so keep outlined CJK above about 48 px, and keep body weight at 400 or more. A monoline gothic such as Noto Sans JP, or a round one such as Zen Maru Gothic, pairs well with a geometric Latin face. Put the Latin family first in `font-family` so Latin letters come from it and kana and kanji fall through.

## Colour
- Thin lines look lighter than their colour value, because anti-aliasing mixes them with the ground. WCAG 1.4.11 asks for 3:1 against adjacent colours for graphics needed to understand the content, and 4.5:1 applies to text.
- On paper #FAF7F0: ink #1A1A1A is 16.3:1, grey #595959 6.6:1, #6E6E6E 4.8:1 and blue #2B4FD8 6.1:1. A pale grey #B8B8B8 is 1.9:1 and #E8E4DA is 1.2:1, so use those for decoration only.
- On white: #767676 is 4.5:1, #8A8A8A is 3.5:1 (fine for non-text strokes, not for text) and #CFCFCF is 1.6:1.
- Use one line colour and at most one accent. Gradient strokes and glow undermine the precision that is the point.
- Dark mode: recompute with light strokes on a dark ground; do not just invert.

## Composition and layout
- Draw icons and illustration on a grid (24 or 48 px with 2 px padding). Use the same stroke width across sizes by setting it per size, or with `vector-effect: non-scaling-stroke` when scaling SVG.
- Build hierarchy from line weight and density, not fill: 2 to 3 px for primary shapes, 1 px for detail, dashes for construction, disabled or secondary states.
- Use hairline rules for sections and tables instead of filled bands. Place 1 px horizontal and vertical lines on half-pixel positions, or the lines blur.
- Combine with one photograph or one flat filled shape per page so the layout does not look like an unfinished wireframe.
- Give drawn illustrations room; crowded contours turn to noise.

## Interaction and motion
- Draw-on: animate `stroke-dashoffset` over 600 to 1200 ms, once, when a drawing enters view. Link underlines that draw in over 300 to 400 ms are an inexpensive variant.
- Hover on outline controls: fill with the ink colour and invert the label, or deepen the stroke from 1.5 to 2 px.
- Keep the finished drawing as the default state and add the draw-on with a class, so a failed script never leaves it invisible.
- Animate only `stroke-dashoffset`, `transform` and `opacity`, and limit simultaneous long paths; many animated complex paths are costly to paint.
- Reduced motion: show the finished drawing immediately and keep colour changes.

## Accessibility cautions
- Pale 1 px borders around inputs, cards and icons are the commonest failure. Anything needed to identify a control, state or focus position needs 3:1.
- Outline-only buttons have weak affordance. Use them for secondary actions; make the primary action filled, with a 3:1 border and 4.5:1 label.
- Decorative drawings are `aria-hidden="true"` and `focusable="false"`. Icons that carry meaning need a name, and icon-only buttons need an accessible label. Keep at least a 24 px target (WCAG 2.5.8), preferably 44 px on touch, even if the glyph is 20 px.
- Forced-colors mode adapts system-visible properties, not every hard-coded SVG paint. Use `currentColor` for strokes and set `CanvasText` or `LinkText` explicitly there. Display words with a transparent fill and a text stroke can vanish, so restore the fill.
- Dashes and weight must not be the only signal of a disabled or selected state.

## Common mistakes
- Mixed stroke widths, caps and corner radii in one set, or icons from two libraries side by side.
- Scaling an SVG so strokes end up at 0.5 px or 5 px.
- Pale grey hairlines for everything, including the focus ring.
- Outlined text at body size; stroked variable fonts with visible overlaps.
- Ghost buttons for every action so nothing has weight.
- Decorative lines that animate forever.

## Typical mistakes of AI-generated versions
- Icons from different sets with different weights; corporate-blob line illustrations with broken or self-crossing paths; gradient strokes with glow; `1px solid #E5E7EB` on every box described as "clean line art"; outline buttons with pale text; "continuous line" art that is several disconnected paths.

## How to build it
- Pattern: `style-line-art-outline`. Fix the weight, caps and joins once, draw on a grid, use `currentColor`. This recipe is original:

```html
<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
  <path class="draw" pathLength="1" d="M8 34C14 14 26 12 40 14C36 26 26 36 8 34Z"/>
</svg>
```

```css
/* the drawing is complete by default; a script adds .is-drawing (for example from an IntersectionObserver) */
.is-drawing .draw { stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw 900ms cubic-bezier(.7, 0, .3, 1) forwards; }
@keyframes draw { to { stroke-dashoffset: 0; } }
.outline-word { -webkit-text-stroke: 1.5px currentColor; -webkit-text-fill-color: transparent; }
@media (prefers-reduced-motion: reduce) { .is-drawing .draw { animation: none; stroke-dashoffset: 0; } }
@media (forced-colors: active) { svg { stroke: CanvasText; } .outline-word { -webkit-text-fill-color: CanvasText; } }
```

- Closest local relative: `vengeance-ui:src/components/ui/line-hover-link.tsx` draws SVG arc and scribble underlines on a `pathLength="1"` path by animating `stroke-dashoffset` from 1 to 0 (0.4 s for the arc, 0.6 s for the scribble) on hover and `:focus-visible`, and it ships a `prefers-reduced-motion` block that turns animation off. It is a link effect, not a full line-art system, but the dash technique is the same one used above. Check round caps in your target browsers for a stray dot at the start of a path.

## Sources
Original guidance written for this project. vengeance-ui is MIT-licensed and cited as reference only. WCAG 2.2 criteria 1.4.11 and 2.5.8 are cited by number only.
