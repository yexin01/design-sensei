---
title: "Generative design"
kind: design-style
summary: "Visuals produced by rules, parameters and seeded randomness: noise fields, contours, cells, particles, dithering and procedural geometry. Covers authoring the system (palette, constraints, seed), reproducibility, performance limits and static fallbacks, with verified local references."
source_ids: [fancy, img2threejs, liquid-logo, react-bits]
pattern_ids: [style-generative-design]
updated: "2026-10-09"
---

# Generative design

In generative design the designer authors a system (a palette, a set of constraints, a seed) and the machine produces instances. Typical building blocks are noise and flow fields, contour bands, cell and Voronoi structures, particles, signed-distance shapes, ordered dithering and procedural 3D geometry. On the web it serves hero backgrounds, per-item covers and avatars, data art, loaders and identity systems that need endless variation under one look.

## Visual characteristics
- Repetition with variation: each output is recognisably a member of one family.
- Algorithmic structure: fields, contours, grids of cells, dither patterns, orbits, wave interference.
- A constrained palette of three to five colours, so variety stays coherent.
- Fine detail and mathematical rhythm; often monochrome or duotone.
- Either slow evolving motion (time-based noise) or a frozen frame treated like a print.

## When it fits, when it does not
- Fits: identities that vary per event, album or user, report covers, studio and lab backgrounds, AI and developer-tool branding, loaders, creative-coding portfolios, personalised share images.
- Poor fit: work that must show a specific subject, products where exact frame reproducibility matters but seeds are not controlled, audiences on low-power devices, medical or legal imagery.
- Supporting influences that work: swiss-international-typographic, minimalism (the generative layer as the only ornament), grain-and-texture, aurora-gradient-mesh, futurism, liquid-materials. Avoid skeuomorphism.

## Typography
- Let the generated layer carry interest and keep type neutral: a grotesque (Inter, Space Grotesk) with mono labels (JetBrains Mono, IBM Plex Mono).
- Expose the system: small mono captions such as `seed 4172 / density 0.62` at 11-13 px with tabular numerals make the origin explicit.
- Place text on calm areas. Mask quiet zones in the generated layer or use a solid panel.
- Display sizes 48-120 px; do not apply the generative effect to the text itself unless a legible fallback exists.

## Colour
- Define palettes as data (three to five colours plus a background) and let the algorithm choose only from them. Random HSL hues produce muddy or neon results.
- Interpolate ramps in OKLCH (`color-mix(in oklch, ...)` or gradient interpolation) for smoother transitions.
- Constrain luminance so any combination passes contrast under overlay text, or reserve a scrim.
- Ordered dithering hides banding in gradients; the local Dither background exposes `colorNum` (default 4) and `pixelSize` (default 2).

## Composition and layout
- Treat the piece as an object with a frame: a full-bleed background behind a calm text panel, or a "specimen" tile in a grid.
- Seed everything. The same seed must give the same output, so URLs, screenshots and server rendering agree. Derive the seed from the item id.
- Reserve the box with `aspect-ratio`; the canvas fills it and never decides the layout.
- Ship a pre-rendered SVG or PNG of a fixed seed as the poster and no-JavaScript fallback.
- Budget per frame: aim for about 16 ms or render once. Scale particle counts with area, start low and cap them on phones.

## Interaction and motion
- Useful inputs: slow time-based drift, pointer attraction or repulsion, scroll-linked parameter change, an explicit "reseed" action.
- Loop hygiene: pause when the element is off-screen and when the tab is hidden, cap ambient pieces at 30 fps, use time rather than frame counts.
- Reduced motion: render one frame with a fixed time value, switch pointer influence off; an explicit reseed button can stay.
- Any control must be keyboard operable.

## Accessibility cautions
- Decorative output gets `aria-hidden` (or empty alt text); data art needs a text or table equivalent.
- Fast-changing fine patterns (animated dither, strobing dots) and high-frequency moire can cause visual stress; keep temporal change slow and spatial contrast soft behind text.
- Heavy loops drain batteries; offer a static render where data-saver or low-power signals are detectable.

## Common mistakes
- Unseeded `Math.random()` during render, which causes hydration mismatches in server-rendered apps and unreproducible screenshots.
- Unbounded particle counts and full-screen 60 fps canvases on every device.
- No poster or fallback image.
- Randomness without design constraints; no curation of good seeds.
- Text laid over high-frequency detail.

## Typical mistakes of AI-generated versions
- Floating particles joined by thin lines, in random colours, running forever on a full-screen canvas.
- Positions drawn from `Math.random()` on every render, no seed, no parameters exposed, no poster.
- Presenting the output as "AI-generated art" with no design system behind it.

## How to build it
- Pattern: `style-generative-design`. Choose the system, write its parameters and palette as data, use a seeded generator (the public-domain mulberry32 algorithm, below), render to canvas or SVG, add pause and a poster.

```js
function mulberry32(a) { return function () { let t = (a += 0x6D2B79F5); t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
```

- `liquid-logo:fragment-shader.glsl` is a noise-driven flow field with uniforms such as `u_speed`, `u_iterations`, `u_scale` and `u_noiseIntensity`; `liquid-logo:presets.js` ships it as ten named parameter sets (Glow, Wisp, Smoke, Oil Slick, Chrome and others), a good model for exposing a generative family.
- `fancy:src/fancy/components/background/animated-gradient-with-svg.tsx` positions blurred circles with `Math.random()` during render; replace that with seeded values before using it in a server-rendered page.
- `img2threejs:README.md` describes code-only procedural 3D models built from primitives and procedural shaders.
- Described only because react-bits is licence-restricted: `react-bits:src/tools/shape-magic/liquid.js` with `sdf.js` and `marchingSquares.js` fuse rectangles into one smooth SVG path (a smooth-union distance field traced by marching squares, then smoothed), so the output is plain SVG; `react-bits:src/content/Backgrounds/Dither/Dither.jsx` applies 8 by 8 Bayer dithering to a wave field (`disableAnimation` stops it); `react-bits:src/content/Backgrounds/Topography/Topography.jsx` draws noise contour bands and pauses off-screen.

## Sources
Original guidance written for this project. fancy, img2threejs (Apache-2.0) and liquid-logo are permissively licensed; react-bits is MIT with the Commons Clause and is described, not quoted.
