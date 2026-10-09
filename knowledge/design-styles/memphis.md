---
title: "Memphis"
kind: design-style
summary: "Playful 1980s postmodern graphics: squiggles, zigzags, confetti, terrazzo speckle and bold primitives in clashing but bounded colour. Covers calm-panel layout, decorative layers kept out of text, pattern recipes in CSS and the contrast of hot brights."
source_ids: []
pattern_ids: [style-memphis]
updated: "2026-10-09"
---

# Memphis

Memphis takes its name from a Milan design collective that launched in 1981 and deliberately broke with the restrained modernism that came before it. Furniture, ceramics and textiles were covered in laminate patterns, built from stacked primitives and coloured in combinations that were meant to look cheerful and slightly wrong. The graphic language that followed, and its many revivals, is built from the same parts: squiggles, zigzags, dots, confetti, triangles and half circles scattered over bright flat colour. On the web it is a decorative system. It works when the decoration sits around the content, and fails when it sits behind it.

## Visual characteristics
- Scattered primitives: squiggle lines, zigzags, plus signs, arcs, triangles, rings and half circles, at varied scales and slightly off axis.
- Black-and-white graphic patterns (stripes, checks, dots, terrazzo speckle) used as accents next to flat colour.
- A saturated palette of hot pink, turquoise, yellow, purple and orange, anchored by black outlines or fills.
- Flat colour and hard edges; thick black strokes or hard-offset shadows are optional but consistent.
- Asymmetric arrangement with overlaps, tilted elements and purposeful clutter around a calm core.
- Chunky display type and simple, friendly illustrations of objects, hands, plants and abstract figures.

## When it fits, when it does not
- Fits: festivals, music and club nights, student and youth brands, creative agency sites, event posters, children's creative products, retail campaigns, pop-up shops, and anything that celebrates a 1980s mood.
- Poor fit: banking, health, law, public services, dashboards, documentation and long-form reading. It is also a poor base for products that need to feel calm or premium.
- Supporting influences that work: maximalism, retro-vintage, y2k, neo-brutalism for outlines and hard shadows, a restrained kinetic-typography. Avoid minimalism, swiss-international-typographic, high-fashion-luxury, dark-technical-developer-tools and art-deco, which pull in the opposite direction.

## Typography
- Display: chunky, rounded or quirky faces such as Rubik, Lilita One, Bowlby One, Fredoka, Dela Gothic One or Syne ExtraBold at weight 700-900, set in short lines.
- Body: a plain geometric or humanist sans such as DM Sans, Work Sans or Nunito Sans at 400-500. Do not use the display face for paragraphs.
- Sizes: display `clamp(2.5rem, 8vw, 7rem)` with line-height 0.95-1.05; body 16-18 px at 1.5.
- A tilt of -2 to -5 degrees on one display word gives energy; keep paragraphs, forms and navigation upright.
- Limit to two families and three weights so the visual noise is carried by shapes, not type.

## Colour
- Core set: ink #161616, paper #FFF6E0, pink #FF6FB5, turquoise #2ED1C8, yellow #FFD93B, violet #5B35D5, orange #FF7A3D.
- Safe text pairs: ink on pink is 7.1:1, ink on turquoise 9.5:1, ink on yellow 13.1:1, ink on orange 7.0:1, ink on paper 16.8:1, white on violet 7.2:1, paper on violet 6.7:1, violet on yellow 5.2:1.
- Failing pairs: white on pink is 2.6:1, white on turquoise 1.9:1, ink on violet 2.5:1, pink on turquoise 1.35:1 (they vibrate), and pink, turquoise or yellow as text on paper (2.4:1, 1.8:1 and 1.3:1).
- Where a hot pink is needed as text on paper, use a deeper tone: #B8115E is 6.0:1 on paper and 6.4:1 on white. A deep teal #006F6A is 5.6:1 on paper.
- Rule of proportion: about 60% calm ground (paper or white), 30% two main colours, 10% pattern and accents. Four hues plus ink is the ceiling.
- Use black as the outline colour so adjacent brights are separated by line instead of vibrating against each other.

## Composition and layout
- Think of a calm core with a lively frame. Text, forms and tables sit on plain panels (white or paper with ink text); decoration lives in the margins, behind the panel edges and around headings.
- Anchor scattered shapes to a hidden grid or to the corners of cards, so the clutter reads as designed. Seed positions by hand or from a fixed list; random placement at runtime changes on every load and looks sloppy.
- Overlap generously, but never overlap the shape on top of body text or a control.
- Patterns in CSS: dots with `radial-gradient(var(--ink) 22%, transparent 24%) 0 0 / 18px 18px`; stripes with `repeating-linear-gradient(45deg, var(--ink) 0 3px, transparent 3px 11px)`; squiggles as inline SVG `path` elements with `stroke="currentColor"`.
- Keep decoration in a contained layer (`overflow: clip`, `isolation: isolate`, `pointer-events: none`) so it cannot cause horizontal scroll or block clicks.
- Responsive: reduce the number of scattered shapes at narrow widths and keep the largest two; keep text panels full width with 16-24 px padding.

## Interaction and motion
- Playful but bounded: a small wiggle or tilt on hover of a sticker or button (one or two cycles, under 500 ms), confetti shapes that drift slowly, a hard-edged shadow that shrinks when pressed.
- Press states: translate the element 3-4 px toward its hard shadow and reduce the shadow, with a 80-120 ms transition.
- Avoid flashing or rapid parallax. Nothing should blink more than three times a second, and loops should be slow (6-12 s).
- Reduced motion: no drifting, wiggle or parallax. Place the shapes statically and keep the press-state shift only if it is a single quick transition.
- Pause control: if decorative animation runs longer than five seconds, offer a way to stop it (WCAG 2.2.2), or keep it off by default.

## Accessibility cautions
- Never put a pattern or a gradient behind text. Busy patterns reduce legibility for many readers, especially those with dyslexia or attention differences. Keep a solid panel behind every paragraph and label.
- Adjacent saturated brights (pink next to turquoise, orange next to violet) vibrate. Separate them with black lines, gaps or paper.
- Decorative SVGs and CSS shapes need `aria-hidden="true"` or no markup at all; confetti elements must not enter the tab order or the accessibility tree.
- Forced-colors mode replaces your colours, but background images such as stripes and dots can remain visible while text is recoloured to system colours, which can hurt contrast. Hide the decorative layer with `display: none` there and give panels a real border.
- Do not use colour alone to distinguish states or categories; shape, text and icon should carry meaning too.
- Rotated text must stay readable, and tilts should stay under about 5 degrees on content that people must read.

## Common mistakes
- Using every colour, pattern and shape in the first screen; Memphis needs rest areas to feel intentional.
- Patterns as full-page backgrounds behind copy.
- Randomly generated shapes with no anchor, scale hierarchy or limited set.
- White text on pink or turquoise buttons.
- Smooth gradients, glows and glass, which belong to other styles and break the hard-edged flat character.
- Confusing it with vaporwave or y2k: Memphis is flat, print-like and pattern-driven, not glossy or neon.
- Many JavaScript-driven floating shapes that cost frames and ignore reduced motion.

## Typical mistakes of AI-generated versions
- A purple-pink gradient background with blobs and a few squiggles pasted over a centred card, with a glow shadow.
- Pastel versions of the palette (everything light pink and lilac) with grey text, which loses both the energy and the contrast.
- A random scatter of dozens of identical triangles and plus signs behind the headline, repeated in every section.
- White labels on pink and turquoise chips, and decorative shapes that are focusable or announced to screen readers.

## How to build it
- Pattern: `style-memphis`. No local source contains a Memphis implementation, so this recipe is original. Calm text panels, a contained decoration layer and one pattern at a time:

```css
:root { --ink: #161616; --paper: #FFF6E0; --pink: #FF6FB5; --teal: #2ED1C8; --yellow: #FFD93B; --violet: #5B35D5; }
body { background: var(--paper); color: var(--ink); font: 400 1.0625rem/1.5 "DM Sans", system-ui, sans-serif; }
h1 { font: 900 clamp(2.5rem, 8vw, 7rem)/1 Rubik, system-ui, sans-serif; transform: rotate(-3deg); }
.hero { position: relative; isolation: isolate; overflow: clip; background: var(--yellow); padding: 48px 24px; }
.hero::before, .hero::after { content: ""; position: absolute; z-index: -1; pointer-events: none; }
.hero::before { top: 0; right: 0; width: 160px; height: 120px; background: radial-gradient(var(--ink) 22%, transparent 24%) 0 0 / 18px 18px; }
.hero::after { bottom: 0; left: 0; width: 160px; height: 48px; background: repeating-linear-gradient(45deg, var(--ink) 0 3px, transparent 3px 11px); }
.panel { background: #fff; color: var(--ink); border: 3px solid var(--ink); padding: 24px;
  box-shadow: 6px 6px 0 var(--violet); max-width: 38rem; }
.sticker { background: var(--pink); color: var(--ink); font-weight: 800; border: 3px solid var(--ink);
  padding: 10px 18px; box-shadow: 4px 4px 0 var(--ink); transition: transform .1s, box-shadow .1s; }
.sticker:active { transform: translate(3px, 3px); box-shadow: 1px 1px 0 var(--ink); }
.sticker:focus-visible { outline: 3px solid var(--violet); outline-offset: 3px; }
@media (prefers-reduced-motion: no-preference) { .sticker:hover { animation: wiggle .4s ease-in-out 1; } }
@keyframes wiggle { 25% { transform: rotate(-3deg); } 75% { transform: rotate(3deg); } }
@media (max-width: 40rem) { .hero::before, .hero::after { display: none; } }
@media (forced-colors: active) { .hero::before, .hero::after { display: none; } .panel, .sticker { border-color: CanvasText; box-shadow: none; } }
```

- Pairs used: ink on the pink sticker is 7.1:1, ink on the white panel 18.1:1, and the violet focus ring is 7.2:1 on the white panel (5.2:1 if a control ever sits directly on the yellow).
- Add squiggles as inline SVG with `aria-hidden="true"` and `focusable="false"`, drawn with `stroke="currentColor"` so they follow the palette.
- Markup: `.hero > .panel > h1 + p + .sticker`. The heading and paragraphs sit inside the white panel, and the two pattern patches live only in the corners of the hero, outside the panel.

## Sources
Original guidance written for this project from general design history and computed contrast ratios. No third-party text or local source files are used.
