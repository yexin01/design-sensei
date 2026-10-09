---
title: "Art Deco"
kind: design-style
summary: "1920s-30s geometric glamour: strict symmetry, sunbursts, fans and stepped forms, gold on black, navy or emerald, tall display lettering and ornamental borders. Gives CSS techniques, palette contrast numbers and ways to avoid kitsch."
source_ids: []
pattern_ids: [style-art-deco]
updated: "2026-10-09"
---

# Art Deco

Art Deco celebrates machine-age elegance: symmetrical compositions, radiating sunbursts, fans, chevrons and stepped silhouettes, rich dark grounds with metallic accents, and tall geometric lettering. On the web it signals glamour, heritage and ceremony. It needs discipline: ornament is structural and repeated, never scattered. This note is fully original; the local sources contain no Art Deco implementation.

## Visual characteristics
- Bilateral symmetry and strong vertical emphasis; centred layouts with framed panels.
- Geometric ornament: sunbursts, scallops, fans, concentric arcs, stepped corners, parallel lines.
- Black, deep navy or emerald grounds with gold, brass or champagne line work; ivory as the light alternative.
- Tall, high-contrast or geometric capitals with generous tracking.
- Thin double rules and borders that frame sections.

## When it fits, when it does not
- Fits: cocktail bars, hotels, galas and weddings, jewellery, film and theatre, period fiction, premium spirits, boutique heritage brands.
- Poor fit: tools, dense information, tech and developer products, playful consumer apps, anything needing a modern neutral tone.
- Supporting influences that work: high-fashion-luxury, editorial, retro-vintage, grain-and-texture, skeuomorphism for brass and enamel. Avoid y2k, neo-brutalism and brutalism.

## Typography
- Display: geometric or stylised capitals (Poiret One, Limelight, Josefin Sans in caps, Marcellus, Cinzel, Bodoni Moda). 40-96 px, tracking +0.08 to +0.2em for caps, weight 400-600 with one or two ornamental faces maximum.
- Body: a calm serif or humanist sans (Cormorant Garamond at 18-20 px, Libre Baskerville, Lato) with leading 1.6; do not set paragraphs in display faces.
- Thin-stroke faces below 28 px disappear on dark grounds; step up to a sturdier cut.

## Colour
- Gold on dark works: #D4AF37 is 9.36:1 on #0B0B0B, 7.98:1 on navy #0B1D3A and 5.80:1 on emerald #0B3D2E. Gold on white is only 2.10:1, so on light grounds use a deep bronze such as #8A6D1F (4.90:1) or ink.
- Ivory text (#F5F0E6) on those grounds is above 15:1.
- Use gold sparingly as line work and accents; faux-metal gradients on text and buttons look cheap and lower legibility.

## Composition and layout
- Centre axis, symmetrical grids, framed panels with stepped or chamfered corners (`clip-path` or SVG borders), sunburst headers built from `repeating-conic-gradient`.
- Vertical rhythm with ornamental dividers; narrow centred text columns (about 60 characters).
- Keep ornament in SVG or CSS; it scales crisply and weighs little.
- On phones reduce frames to single rules and keep the sunburst as a header motif.

## Interaction and motion
- Ceremonial and slow: line-draw reveals using SVG `stroke-dashoffset` (600-1000 ms), a single shimmer sweep over a gold rule, curtain-like fades.
- Hover on links: underline growth or a gold rule extending. No bounce.
- Reduced motion: show the lines fully drawn and skip the shimmer.

## Accessibility cautions
- Thin gold lines on dark are decorative; text must meet 4.5:1 separately.
- Wide-tracked all-caps hurts reading beyond a few words.
- Ornamental SVG is `aria-hidden`; frames made from images need no alt text.
- Keep focus rings visible against gold and dark.

## Common mistakes
- Ornament overload, so the page becomes pastiche.
- Gold gradients on all text; script fonts mixed in.
- Light weights for body on dark; gold text on white.
- Asymmetric layouts that break the style's logic.

## Typical mistakes of AI-generated versions
- Black page, gold gradient headline, a serif font and random geometric shapes without symmetry or a repeating motif.

## How to build it
- Pattern: `style-art-deco`. Tokens: black, navy or emerald ground, gold, ivory, one display face, one text face, a stroke weight for rules.

```css
.sunburst { background: repeating-conic-gradient(from 0deg at 50% 100%, #D4AF37 0 2deg, transparent 2deg 8deg); mask-image: linear-gradient(to top, #000, transparent 85%); }
.frame { border: 1px solid #D4AF37; outline: 1px solid #D4AF37; outline-offset: 6px; }
```

- Draw dividers and corner ornaments as inline SVG with `currentColor`, so they follow theme tokens and work in forced-colors mode.

## Sources
Fully original guidance written for this project; no local source files are cited.
