---
title: "Hand-drawn and doodle"
kind: design-style
summary: "Wobbly outlines, marker underlines, arrows, sticky notes and handwriting accents that make an interface feel made by a person. Covers where to keep the human touch and where to keep the machine, pen-colour contrast numbers, CSS and SVG wobble techniques and static fallbacks for line-boil motion."
source_ids: []
pattern_ids: [style-hand-drawn-doodle]
updated: "2026-10-09"
---

# Hand-drawn and doodle

Hand-drawn design borrows the look of a notebook, whiteboard or sketchpad: uneven outlines, felt-tip underlines, circled words, arrows that point at what matters, stars and squiggles in the margins, sticky notes and graph-paper grounds. It signals warmth, informality and a person behind the product. The discipline is to be imperfect on purpose in a few controlled places (borders, accents, annotations) while the layout, type and controls underneath stay precise and readable. This note is fully original; the local sources contain no hand-drawn implementation.

## Visual characteristics
- Outlines of 2-3 px in a pen colour with slightly irregular corners, open joins and rounded caps; shapes that do not quite close.
- Marker highlights behind words, wavy or double underlines, circles and arrows drawn around key items, small stars, sparks and squiggles.
- Paper grounds: warm off-white, lined, dotted or graph paper; torn-notebook edges; sticky notes and index cards in pastel with a small rotation.
- Hard offset shadows in pen colour, never soft blurred ones; fills as loose colour blocks that miss the outline slightly.
- Illustrations in a single line weight, often two or three flat colours, with characters or objects drawn as if with a marker.

## When it fits, when it does not
- Fits: education and children's products, creative and whiteboarding tools, indie products, personal sites and portfolios, newsletters and blogs, onboarding and empty states, community and non-profit pages, explanatory annotation on top of an otherwise clean product.
- Poor fit: banking, healthcare, legal or compliance flows where the hand-drawn tone undermines trust; dense data tables; precise technical tools; premium or formal brands.
- Supporting influences that work: organic-tactile, grain-and-texture, retro-vintage, editorial, neo-brutalism (the hard offset shadow is shared), claymorphism for softer products, collage-cutout. Avoid swiss-international-typographic, dark-technical-developer-tools, futurism and isometric-illustration.

## Typography
- Handwriting faces for display only: Caveat, Kalam, Patrick Hand, Gaegu, Shadows Into Light. Many have a small x-height, so set them 20-24 px or larger and give lines generous leading (1.3-1.4).
- Body copy stays in a robust text face (a humanist sans or a sturdy serif) at 16-18 px with leading 1.5. Handwritten paragraphs slow reading, particularly for people with dyslexia or readers in a second language.
- Keep handwritten strings short: a kicker, an annotation, a label on an arrow. Never use them for form labels, error messages, prices or legal text.
- Headings 32-64 px; tracking 0; an occasional wavy underline (`text-decoration-style: wavy`) in an accent pen colour.

## Colour
- Paper and pens: graphite #2D2A26 on paper #FBF7EC is 13.34:1; ballpoint blue #2447A8 is 7.72:1; raspberry #B3224F is 6.02:1; marker orange #C2410C is 4.84:1; marker green #1E7A4E is 4.97:1.
- Pencil grey is the trap. #8A857B on paper is 3.43:1, which fails for text but is acceptable for a decorative or non-text border (3:1). Text in pencil grey should be #6B665C (5.33:1).
- Highlighter yellow #FFE45E on paper is 1.19:1, so it can only be a background shape. Dark text on it is excellent: graphite 11.23:1, blue 6.50:1.
- Sticky-note pastels take graphite comfortably (on #FFF1A8 it is 12.51:1, on #BFE3F5 10.55:1, on #FFD0DC 10.41:1). Orange on #FFF1A8 drops to 4.54:1, barely passing.
- Three pen colours plus two highlighter tints are enough. Input borders should use #7A756B or darker (about 4.3:1) so fields are visible against the paper.

## Composition and layout
- Keep a real grid underneath. Cards may rotate between -1.5 and 1.5 degrees, but alignment, spacing and the reading order are exact.
- Use doodles as annotations that earn their place: an arrow from a headline to the call to action, a circle around a price, a squiggle under a key phrase. Decorating every heading destroys the signal.
- Draw containers with irregular border radii or an SVG outline on a decorative layer, and keep the content inside simple rectangles.
- Paper effects (lined or dotted backgrounds) sit on the page ground, not behind body text; dots at 8-24 px spacing with a faint tone.
- Responsive: scale rotation and doodle size down on phones, drop margin doodles first, never let a decoration overlap a tap target.

## Interaction and motion
- Draw-on strokes (`stroke-dashoffset`, 500-900 ms) for underlines and arrows when they enter the viewport; a gentle wiggle of 1-2 degrees on hover for cards or stickers over 150-250 ms.
- Line boil: alternating two or three slightly different versions of a shape at 3-6 frames per second gives the classic hand-animated shimmer. Use it on one or two illustrations at most, and implement it by swapping prepared SVG paths or sprite frames rather than recalculating filters every frame.
- Controls still behave like controls: instant, clearly pressed states; no wobble on buttons while they are being clicked.
- Reduced motion: show every stroke already drawn, remove wiggle and boil, keep a colour or underline change for hover.

## Accessibility cautions
- Scribbles, arrows and stars are decoration: `aria-hidden="true"` on the SVG, no meaning carried by them alone. If an arrow points at the key action, the action also has a text label.
- Rotated elements still need logical focus and reading order; do not rotate text blocks that people must read at length, and never rotate form labels.
- Focus indicators must be plain and strong (solid 3 px, not sketchy or pencil grey). Pen-colour hover states need a non-colour cue.
- Forced-colors mode replaces border, text and background colours with system colours, so marker highlights and squiggles drawn as backgrounds may be dropped or recoloured. Add a real `border` or `text-decoration` that survives, and let SVG decoration use `currentColor`.
- Handwriting fonts at 200% zoom and large system text sizes need room; test that nothing clips. Provide a plain-font toggle for pages heavy in handwritten text.

## Common mistakes
- Chaotic rotation of every element, including text, buttons and inputs; wobble filters applied to whole text blocks so letters blur.
- Everything doodled at once (borders, icons, headings, dividers, background) until nothing stands out.
- Handwriting font in body copy, tables, forms or error messages.
- Applying `feTurbulence` displacement to large containers (slow repaints) or animating the filter every frame.
- Clip-art sticker packs that do not share a line weight, colour set or hand.

## Typical mistakes of AI-generated versions
- A script font on every string, a pencil-grey caption on cream that fails contrast, random rotation on all cards and buttons, a generic hand-drawn arrow pasted next to every heading, and a "sketch" look made by a blurry filter over the entire page that also blurs the text.

## How to build it
- Pattern: `style-hand-drawn-doodle`. No hand-drawn implementation exists in the local sources, so this recipe is original. Tokens: paper, graphite, two pen colours, a highlighter tint, one line weight (2.5 px), one rotation limit, one offset-shadow size.

```css
.doodle-card { background: #FFFFFF; color: #2D2A26; padding: 1rem 1.25rem; border: 2.5px solid #2D2A26;
  border-radius: 14px 22px 12px 26px / 24px 12px 22px 14px; box-shadow: 4px 5px 0 #2D2A26; transform: rotate(-.8deg); }
.marker { background: linear-gradient(transparent 58%, #FFE45E 58% 92%, transparent 92%); }
.squiggle { text-decoration: underline wavy #B3224F; text-decoration-thickness: 3px; text-underline-offset: 6px; }
.doodle-card:hover { transform: rotate(.6deg) translateY(-2px); transition: transform .2s; }
@media (prefers-reduced-motion: reduce) { .doodle-card:hover { transform: rotate(-.8deg); transition: none } }
@media (forced-colors: active) { .doodle-card { border-color: CanvasText; box-shadow: none } .marker { text-decoration: underline } }
```

- Wobble for an extra-sketchy edge: put the outline on a decorative `::before` layer and apply a small SVG filter to it only (`feTurbulence` `baseFrequency` about 0.03 with `feDisplacementMap` `scale` 2-3 and a fixed `seed`), never to the text container. For hand-placed arrows and circles, draw the paths once in a vector editor, or generate jittered paths at build time, then ship them as static inline SVG with `stroke-linecap: round` and `fill: none`.
- Arrow or underline draw-on: set `pathLength="1"`, `stroke-dasharray: 1`, animate `stroke-dashoffset` from 1 to 0, and set it to 0 outright when reduced motion is requested.

## Sources
Original guidance written for this project; no local source files are cited.
