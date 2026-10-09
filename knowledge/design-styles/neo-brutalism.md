---
title: "Neo-brutalism"
kind: design-style
summary: "The friendly, systematic cousin of brutalism: thick black outlines, hard offset shadows, flat saturated fills and chunky type, with physical press-down interactions. Includes colour-contrast rules for bright fills and a reduced-motion-safe button recipe."
source_ids: [astryx]
pattern_ids: [style-neo-brutalism]
updated: "2026-10-09"
---

# Neo-brutalism

Neo-brutalism keeps the exposed edges of brutalism but makes them cheerful and consistent. Elements get a heavy outline (2-4 px), a hard offset shadow with no blur, a flat bright fill and chunky type. Unlike raw brutalism it is a tidy system: every card shares one outline weight and one shadow offset, and buttons physically "press" into the page.

## Visual characteristics
- Heavy black (or very dark) outlines on every block, input and button.
- Hard offset shadows (4-8 px, blur 0) in the outline colour.
- Flat fills from a small saturated palette on a warm off-white or pale background; no gradients.
- Chunky sans type at weights 700-900, stickers, badges and tape-like labels.
- Small to medium radii (0-12 px) used consistently; occasional 1-3 degree tilts on decorative items.

## When it fits, when it does not
- Fits: tools and communities for creators, consumer start-ups, education, marketplaces for independents, playful landing pages, bento-style feature grids.
- Poor fit: formal enterprise, financial or medical products, luxury, quiet reading experiences. Dense data tables get heavy quickly with thick outlines.
- Supporting influences that work: bento-layouts, retro-vintage print references, kinetic-typography with chunky faces, product-led-saas for playful products. Avoid glassmorphism, neumorphism, art-deco and high-fashion-luxury.

## Typography
- Geometric or grotesque sans with personality: Space Grotesk, DM Sans, Lexend, Archivo (ExtraBold or Black), Poppins, Bricolage Grotesque. A mono for small labels.
- Headings 48-96 px at weight 700-900, tracking -0.02em, line-height 1.05-1.15. Body 16-18 px at 400-500; never light weights.
- Uppercase is common on buttons and tags; keep it to short strings.

## Colour
- Background warm off-white (#FFF4E0) or one pale tint; outlines and text in #000 or #111.
- Three to five flat fills used with meaning (category, status), not at random: for example yellow #FFD60A, pink #FF90E8, mint #7CF5C0.
- Text on a bright fill is black. Black on those three fills measures 14.9:1, 10.4:1 and 15.7:1, while white on mint is 1.34:1 and white on pink is 2.02:1.
- Dark mode needs its own rules: black outlines vanish, so switch to light outlines and light hard shadows rather than inverting the page.

## Composition and layout
- Card grids and bento tiles with identical outline weight and shadow offset; generous inner padding (24-32 px).
- Stickers, badges and thick dividers as structure; tilt only decorative pieces, never body text.
- Chunky controls: 48-56 px tall buttons and inputs with 3 px outlines. Drop to 2 px outlines and 4 px shadows on phones.
- Keep a clear single focal block per section; colour alone does not create hierarchy when every block is loud.

## Interaction and motion
- The signature is the press: on hover the element lifts (translate -2 px, shadow grows), on active it moves down by the shadow offset and the shadow collapses to zero. Durations 80-120 ms, ease-out.
- Toggles and tabs snap rather than slide. Optional tape-style marquees; make them pausable.
- Animate `transform` on small controls; on large grids move a shadow pseudo-element instead of repainting big shadows.
- Reduced motion: keep the static pressed state (the shadow collapse still communicates it) and remove the transitions.

## Accessibility cautions
- Heavy outlines help non-text contrast (3:1), which is a real advantage of the style. Make sure the focus ring is visibly different from the normal outline (3 px ring with a 3 px offset, in a contrasting colour).
- Never put white text on pastel fills. Check every fill and text pair.
- Adjacent saturated fills (yellow against pink) can vibrate; separate them with the outline and a neutral gap.
- Tilted text is harder to read and to select; limit tilt to icons, stickers and short labels.

## Common mistakes
- Blur shadows mixed with hard outlines, which reads as an unfinished system.
- Inconsistent outline weights and shadow offsets between components.
- Five or more fill colours with no meaning, so nothing signals status.
- No pressed or disabled state; the whole point of the style is the tactile mapping.
- Black outlines carried into dark mode unchanged.

## Typical mistakes of AI-generated versions
- A 1 px border, a soft `shadow-lg` and a pastel gradient labelled "neo-brutalist".
- Large bubbly radii (16-24 px) with offset shadows, producing a toy look instead of a system.
- Every card tilted and every colour used once, with no press interaction.

## How to build it
- Pattern: `style-neo-brutalism`. Tokens: `--outline: 3px solid #000`, `--shadow: 6px 6px 0 #000`, `--radius: 8px`, four fills.
- Closest local reference is the Astryx y2k theme: periwinkle body, dark charcoal borders in light mode (its own comment calls this the heavy-outline look), zero element radii and pastel category fills paired with dark text (`astryx:packages/themes/y2k/src/y2kTheme.ts`). It is not neo-brutalist in full: its borders are mostly 1 px and its shadows are soft. Raise the outline width and swap its `--shadow-*` tokens for hard offsets to get closer.
- A button that presses (original code):

```css
.nb-button { border: 3px solid #000; background: #FFD60A; color: #000; box-shadow: 6px 6px 0 #000;
  transition: transform 100ms ease-out, box-shadow 100ms ease-out; }
.nb-button:hover { transform: translate(-2px, -2px); box-shadow: 8px 8px 0 #000; }
.nb-button:active { transform: translate(6px, 6px); box-shadow: 0 0 0 #000; }
@media (prefers-reduced-motion: reduce) { .nb-button { transition: none; } }
```

## Sources
Original guidance written for this project. astryx is MIT-licensed and cited as reference only.
