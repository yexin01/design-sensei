---
title: "Grain and texture"
kind: design-style
summary: "Tactile surface treatment through film grain, paper, halftone and dither: how to add warmth and remove gradient banding cheaply, keep text legible, avoid full-screen blend-mode jank and freeze the effect under reduced motion. Draws on verified local grain implementations."
source_ids: [react-bits, shadergradient, taste-skill]
pattern_ids: [style-grain-and-texture]
updated: "2026-10-09"
---

# Grain and texture

Grain and texture put a physical surface under digital shapes: film grain, paper fibre, risograph speckle, halftone dots, ordered dither. A faint grain warms flat colour, hides gradient banding and unifies images from different sources. It is a finishing layer more than a style of its own, which is why it combines with nearly everything. The cost is legibility and rendering performance if it is applied carelessly.

## Visual characteristics
- Fine noise at 2-12% strength over flat colour and gradients; coarse grain for a deliberately analogue look.
- Paper, canvas or dust overlays; halftone or dither patterns for print and bitmap looks.
- Occasional film artefacts: scratches, vignette, light leaks, scanlines.
- Muted contrast and slightly lifted blacks.

## When it fits, when it does not
- Fits: editorial, luxury, retro, organic and gradient-heavy designs, photography and portfolio sites, music and culture projects.
- Poor fit: data-dense tools, small text at low contrast, very low-power devices if applied as large animated layers.
- Supporting influences that work: editorial, aurora-gradient-mesh, retro-vintage, high-fashion-luxury, organic-tactile, vaporwave. Use sparingly with minimalism; avoid with precise swiss-international-typographic layouts.

## Typography
- Grain lowers perceived contrast, so favour sturdy text: weight 400 or more, 16 px or larger, no hairline serifs below 28 px.
- Keep text above the texture layer in z-order; never place text beneath a multiply or overlay layer that tints it.
- Distressed fonts only for display words.

## Colour
- Use warm or neutral grain; coloured noise shifts hue and looks like a compression artefact.
- Opacity 3-8% suits UI; up to about 12% for posters. A neutral grain at 12% over body text can drop contrast by one or more steps, so re-measure (a #767676 caption on #F7F3EA is already only 4.1:1).
- Blend modes: `overlay` and `soft-light` preserve highlights; `multiply` darkens; `difference` and `screen` shift colour.
- Dither with a small colour count (four levels in the local Dither background) gives an intentional bitmap look; use grain or dither at 2-6% to break gradient banding.

## Composition and layout
- Apply grain to surfaces, not content: a hero background, a section tint, a card face.
- For a global overlay use one fixed, pointer-events-none layer above the page background and below text, not a layer attached to a scrolling container.
- Tile a small texture (128-256 px) instead of shipping a large image.
- Match grain scale across elements; mixed grain sizes make composites look pasted.

## Interaction and motion
- Static grain is usually enough. If animated, jump the tile offset at 12-24 fps rather than regenerating noise each frame.
- Pause when off-screen; no flicker (keep flicker amplitude at zero).
- Reduced motion: stop animation and keep the static tile. Honour the preference even for subtle effects.

## Accessibility cautions
- Grain over text reduces contrast and can hamper readers with low vision; measure with the texture present.
- Animated noise and flicker can cause discomfort; no strobing.
- Mark overlays `aria-hidden` and `pointer-events: none`; make sure they do not intercept focus or clicks.
- High-frequency halftone or dither behind text creates moire-like vibration; keep text on flat panels.

## Common mistakes
- Full-viewport blend-mode layers on scrolling content, causing repaint jank.
- Opacity of 20% or more; grain on top of text; coloured noise.
- Regenerating noise on a canvas every frame.
- Using texture to hide low-quality imagery.

## Typical mistakes of AI-generated versions
- An SVG noise overlay at heavy opacity across the entire page including text, with `mix-blend-mode` on a large scrolling wrapper, and animated by JavaScript every frame.

## How to build it
- Pattern: `style-grain-and-texture`. Cheapest first: a tiled noise PNG or SVG `feTurbulence` data URI in a fixed `::before`; then canvas or shader only if you need animation or control.
- Described only because react-bits and shadergradient are licence-restricted. `react-bits:src/content/Animations/Noise/Noise.jsx` paints a 256 px noise tile once, then shifts its background position at a configurable `fps` (default 24) instead of regenerating it; it offers `opacity`, `blendMode`, `contrast`, `colored`, `dust`, `scratches`, `scanlines`, `flicker` and `fixed`, stops animating under `prefers-reduced-motion` and is `aria-hidden`.
- `react-bits:src/content/Backgrounds/Grainient/Grainient.jsx` bakes grain into a shader gradient (`grainAmount`, `grainScale`, `grainAnimated`) and pauses when off-screen or the tab is hidden.
- `react-bits:src/tools/texture-lab/types.js` lists a wide effect vocabulary: noise, grain, halftone, Bayer dither, paper and film-grain overlays, scanlines, duotone, light leak.
- `shadergradient:packages/shadergradient/src/types.ts` shows `grain` (on or off) and `grainBlending` options on a gradient.
- `taste-skill:skills/soft-skill/SKILL.md` advises applying grain only to fixed, pointer-events-none layers and never to scrolling containers.

## Sources
Original guidance written for this project. taste-skill is MIT-licensed; shadergradient declares MIT without a licence file and react-bits is MIT with the Commons Clause, so both are described and referenced by path only.
