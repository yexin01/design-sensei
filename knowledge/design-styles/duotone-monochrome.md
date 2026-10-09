---
title: "Duotone and monochrome"
kind: design-style
summary: "Two inks or one hue: photographs mapped onto a shadow-to-highlight gradient, flat fields in the same pair, and single-hue tonal ramps for UI. Covers choosing pairs by luminance gap, the midtone text trap with computed ratios, an exact SVG gradient-map recipe, status without hue and reduced-motion colourway changes."
source_ids: [fancy, react-bits]
pattern_ids: [style-duotone-monochrome]
updated: "2026-10-09"
---

# Duotone and monochrome

Both approaches get their unity from restriction. Duotone maps the tonal range of a greyscale image onto a gradient between two colours, a shadow colour and a highlight colour, and then reuses the same pair for the flat areas around it, so photo, ground and type behave like one printed sheet. Monochrome builds a whole interface from one hue, using tints and shades for surfaces, borders, text and states. They suit work with inconsistent photography, strong shapes and a clear point of view. They fail where colour is the message: charts, status systems and products sold on true colour.

## Visual characteristics
- Photographs reduced to two colours, with deep shadows in one and bright highlights in the other; no stray hues.
- Flat fields in the same two colours around the picture, so edges dissolve into the page.
- Overprint effects where shapes overlap and a third tone appears (multiply-style mixing).
- One-hue ramps of six to ten steps from near-black to near-white for monochrome UI, with the hue held steady.
- Halftone, dither or grain to reinforce the print origin; type in the paper colour or the ink colour.
- Big silhouettes and strong scale contrast, since colour cannot separate things.

## When it fits, when it does not
- Fits: music and event posters, editorial features, campaigns that must unify mixed photography, portfolios, annual reports, single-brand dashboards (monochrome), mood imagery on product pages.
- Poor fit: maps, status dashboards that rely on red and green, multi-series charts, fashion, food, paint and other products sold on colour, medical imagery, user-submitted photos where skin tones and likeness matter.
- Supporting influences that work: editorial, grain-and-texture, retro-vintage (riso and screen-print logic), swiss-international-typographic, generative-design, minimalism. Avoid maximalism, y2k and skeuomorphism.

## Typography
- Type must hold itself up in a two-colour world: heavy, large display (Archivo, Anton, Inter Tight 800, or a sturdy serif such as Fraunces 700) in the lightest ink; body at weight 400 to 500 on a flat field.
- Display 64-160 px, leading 0.9 to 1.0, tracking -0.02em. Body 16-18 px, never directly over midtones.
- Monochrome UI cannot lean on hue for hierarchy, so use at least three clear steps of size and weight (for example 14, 16, 24 and 40 px at weights 400, 600 and 800).
- CJK: reversed-out (light on dark) text loses thin strokes, so use Noto Sans JP or SC at weight 500 to 700 rather than a light Mincho for small copy; bold weights survive halftone and dither.

## Colour
- Pick pairs for their luminance gap, not their hue. Indigo #1B1464 with amber #FFC857: indigo on amber is 10.3:1, white on indigo 15.8:1. Indigo with coral #FF5E78: coral on indigo is 5.4:1, and white on coral only 3.0:1, so type on coral must be indigo. Amber on white is 1.5:1, which is why amber never carries text on a light ground.
- The midtone trap: a gradient map from indigo to amber passes through #8D6E5E (a plain sRGB mix). White on it is 4.6:1, black 4.5:1, indigo 3.4:1 and amber 3.0:1, so only white or black text barely passes and nothing is comfortable. The indigo-to-coral midpoint #8D396E gives white 7.1:1 and amber 4.6:1. In every case, place text on a flat band or the shadow region, not on the picture's midtones.
- A monochrome blue ramp: #0B2A5B on #EAF1FF is 12.4:1, #2F5FA8 is 5.6:1 (usable for text), #4F7CC4 is 3.7:1 (strokes and large UI only) and #8FB0E6 is 1.9:1 (decoration). On the dark end, white on #0B2A5B is 14.0:1, #8FB0E6 6.4:1 and #4F7CC4 3.4:1.
- Paper-and-ink pairs behave well: #120F17 on #F4F1EA is 16.8:1.
- Without hue, status needs an icon, a label and a position. Keep one off-palette signal colour (an error red) for critical states.
- Grade the gradient map in sRGB deliberately; the linear-light default of SVG filters gives different, usually brighter midtones.

## Composition and layout
- Treat each picture as a printed plate: crop hard, work large, use one per section, and match the ground to the shadow colour so the image bleeds into the page.
- Use the two colours in blocks and stripes; let overlapping shapes multiply into a third tone for depth without a new hue.
- Choose images with strong silhouettes and a wide tonal range; fine detail and low-contrast photos turn to mud.
- Keep a full-colour version one click away where colour matters (product gallery, detail view).
- Monochrome UI: create elevation with tonal steps instead of shadows, put borders at a middle step, and use one inverted block (dark on light or the reverse) for emphasis.

## Interaction and motion
- Hover reveal: cross-fade a stacked full-colour image over the duotone one over 300-500 ms, or swap the two inks to flip the colourway. Cross-fade opacity; transitioning a `filter` on large images repaints every frame.
- Section transitions: let the background pair cross-fade over 400-800 ms between sections. Do not strobe between a light and a dark pair; large, rapid swaps approach flash limits (WCAG 2.3.1).
- Halftone or dither animation should be slow and paused when off-screen.
- Reduced motion: set the colourway statically, make hover reveals instant or focus-based, and freeze any dither drift.
- Performance: pre-render duotone versions of hero images at build time; keep live SVG or CSS filters for user-supplied or interactive images.

## Accessibility cautions
- When tone is the only difference (selected versus unselected, chart series, active tab), adjacent steps need at least 3:1 (WCAG 1.4.11); middle steps of a ramp are usually too close.
- Single-hue charts need direct labels, patterns or markers as well as lightness steps. Test the design in greyscale.
- Text over an image must pass at its worst region, not the average. Use a flat panel or a scrim; shadows alone do not change the underlying ratio.
- Duotone removes information carried by colour in a photo. Write useful alt text, and offer the original where the colour is the content.
- In forced-colors mode your palette is replaced; give text over images a solid Canvas-coloured backplate and borders a system colour.
- Pairs that differ in hue but not in lightness (a red and a green) collapse for colour-blind users; a large luminance gap is protective.

## Common mistakes
- Pairs with similar luminance, so the photograph has no tonal range and reads as a flat wash.
- Laying a 50 percent coloured overlay over a colour photograph instead of mapping a greyscale version.
- Duotoning an already low-contrast photo without adjusting levels first.
- Text on the midtones; three or four "duotone" pairs across one site.
- Turning faces and skin tones into odd hues without considering likeness and representation.
- Hiding the full-colour product from shoppers.

## Typical mistakes of AI-generated versions
- A purple-to-pink overlay with `mix-blend-mode` over a colour stock photo, white text on pink at 3:1, the same indigo-to-orange pair in every output, and `grayscale() sepia() hue-rotate()` chains that give a different tint for each image. Alt text and a full-colour fallback are usually missing.

## How to build it
- Pattern: `style-duotone-monochrome`. An exact gradient map with an SVG filter: luminance first, then a per-channel table from the shadow value to the highlight value. This recipe is original:

```html
<svg width="0" height="0" aria-hidden="true" focusable="false" style="position:absolute">
  <filter id="duo" color-interpolation-filters="sRGB">
    <feColorMatrix type="matrix" values="0.2126 0.7152 0.0722 0 0  0.2126 0.7152 0.0722 0 0  0.2126 0.7152 0.0722 0 0  0 0 0 1 0"/>
    <feComponentTransfer>
      <feFuncR type="table" tableValues="0.106 1"/>      <!-- #1B1464 to #FFC857 -->
      <feFuncG type="table" tableValues="0.078 0.784"/>
      <feFuncB type="table" tableValues="0.392 0.341"/>
    </feComponentTransfer>
  </filter>
</svg>
```

```css
.duo-wrap { position: relative; }
.duo { display: block; inline-size: 100%; filter: url(#duo); }
.duo-colour { position: absolute; inset: 0; inline-size: 100%; opacity: 0; transition: opacity 400ms; }  /* optional full-colour layer */
.duo-wrap:is(:hover, :focus-within) .duo-colour { opacity: 1; }
@media (prefers-reduced-motion: reduce) { .duo-colour { transition: none; } }
```

- Keep the filter SVG in the layout at zero size instead of using `display: none`, which breaks the reference in some engines. An approximation without SVG: show a greyscale image (`filter: grayscale(1) contrast(1.1)`) with `mix-blend-mode: multiply` on top of the highlight colour, then lay a shadow-colour layer over it with `mix-blend-mode: lighten`. It clips the darkest tones more than the table does.
- Local relatives:
  - `react-bits:src/tools/texture-lab/shaders.js` (`DUOTONE_FRAGMENT_SHADER`) takes luminance, applies a contrast uniform, mixes `u_shadowColor` to `u_highlightColor`, then blends with the original by an intensity uniform. It is the same gradient-map maths as the recipe above (described only, since react-bits is licence-restricted).
  - `react-bits:src/content/Animations/HalftoneReveal/HalftoneReveal.jsx` has `mono`, `duotone` and `color` modes and checks `prefers-reduced-motion`, keeping its pointer-driven reveal closed when the setting is on.
  - `react-bits:src/content/Animations/DitherVeil/DitherVeil.jsx` offers a `duotone` or `rgb` palette with ink (`#120f17`) and paper (`#f4f1ea`) defaults, and its `wander` motion is off under reduced motion.
  - `fancy:src/fancy/components/filter/gooey-svg-filter.tsx` shows the component pattern for hosting a hidden SVG `<filter>` and applying it through a CSS `filter: url(#id)` reference; a duotone filter can be wrapped the same way.

## Sources
Original guidance written for this project. fancy is MIT-licensed; react-bits is MIT with the Commons Clause and is described, not quoted. WCAG 2.2 criteria 1.4.11 and 2.3.1 are cited by number only.
