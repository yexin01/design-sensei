---
title: "Futurism (digital sci-fi)"
kind: design-style
summary: "The contemporary future-tech look: dark cool stages, luminous accents used as light, HUD-style framing, spatial depth and precise motion. Written for product and launch sites, with guidance on contrast, one-canvas performance budgets and DOM text over WebGL."
source_ids: [react-bits, react-three-fiber, vengeance-ui]
pattern_ids: [style-futurism]
updated: "2026-10-09"
---

# Futurism (digital sci-fi)

In this catalogue "futurism" means the current future-tech interface look: a dark, cool stage, luminous accents that behave like light sources, thin HUD-style framing, spatial depth and exact, unhurried motion. It does not refer to the early twentieth-century Italian art movement. It overlaps with cyberpunk but is cleaner, more optimistic and more product-oriented.

## Visual characteristics
- A near-black, cool-tinted stage with one or two luminous accents (cyan, electric blue, white).
- Light behaves like light: rim glows, light trails and volumetric rays rather than decorative drop shadows.
- HUD framing: hairlines, corner brackets, tick marks, orbit rings, coordinates and readouts.
- Spatial depth: perspective grids, parallax, camera moves, particle fields, a single hero object.
- Monospace or extended type for data, with generous negative space around the focal object.

## When it fits, when it does not
- Fits: AI, robotics, aerospace and mobility products, hardware launches, games and esports, research labs, conferences, deep-tech start-ups.
- Poor fit: wellness, children's products, crafts, public services, text-heavy sites, audiences on low-power devices.
- Supporting influences that work: experimental-3d, generative-design, dark-technical-developer-tools, a restrained aurora-gradient-mesh, liquid-materials. Avoid retro-vintage, organic-tactile and art-deco.

## Typography
- Headlines: extended or geometric sans (Space Grotesk, Sora, Syne, Unbounded). Orbitron is overused. Text: a neutral grotesque (Inter, Geist). Data: mono (JetBrains Mono, IBM Plex Mono, Space Mono).
- Display 56-120 px at weight 500-700, tracking -0.02em. Uppercase labels at 12 px or larger with +0.1 to +0.2em tracking.
- Tabular numerals for readouts. Use weight 300 only at 32 px and above on dark.
- Never set paragraphs in mono or uppercase.

## Colour
- Cool near-black such as #05070D rather than #000, with surface steps four to six per cent lighter.
- Accent as light: cyan #22D3EE is 11.1:1 on #05070D. Muted text #7C8DA5 is 5.96:1; the tempting #5B6B7F is only 3.70:1.
- One primary glow hue and one secondary; white for focus. Do not rely on cyan versus blue to distinguish states.
- Large blurred glows lower the contrast of nearby text (halation). Keep glows on a few elements and text off them.

## Composition and layout
- A centred or offset hero object with asymmetric HUD labels around it. Frame panels with 1 px lines at 12-20% white and corner marks made from pseudo-elements.
- Perspective grid floors via WebGL or CSS 3D transforms; sections as panels with data modules.
- Real text stays in the DOM, layered over the canvas with `pointer-events: none` on the overlay container.
- Responsive: collapse HUD labels into a list on phones, shrink the stage and swap the canvas for a poster image.

## Interaction and motion
- Exact easings (ease-out expo), 400-900 ms; number tickers, scan lines and line-draw reveals; cursor parallax of two to four degrees; scroll-linked camera moves.
- One canvas per page. Pause it when off-screen and cap the pixel ratio.
- Reduced motion: show a static poster frame, disable parallax and tickers, display final values for readouts.
- Scan lines must stay slow and low in contrast; no flashing.

## Accessibility cautions
- Canvas content is invisible to assistive technology. Put all meaningful text in the DOM, mark the canvas `aria-hidden` and describe key visuals in text.
- Camera zooms and wide parallax can trigger vestibular symptoms; limit amplitude and offer a motion toggle.
- Thin glowing text under 14 px is a legibility risk. Use solid text colours beside the glow.
- Never encode status only in colour; add words or icons.

## Common mistakes
- Neon on everything and glow stacked on glow.
- A "sci-fi" display font used for body text.
- A full-screen WebGL canvas on every page, with no fallback and no pause.
- HUD clutter with invented numbers that mean nothing; fake data erodes trust.
- Auto-playing sound.

## Typical mistakes of AI-generated versions
- A purple-to-blue gradient, glowing orbs, glass cards and an Orbitron headline: the stereotypical "AI landing page".
- A rotating cube or sphere that has no relation to the product.
- Dashboards of random numbers presented as proof.

## How to build it
- Pattern: `style-futurism`. Build the stage (one hero object or shader) and the DOM text overlay first, then HUD framing with CSS, then motion.
- React Three Fiber provides the pieces for a safe stage: `fallback` for non-WebGL clients, `frameloop` (`always`, `demand`, `never`) and a `dpr` range defaulting to `[1, 2]` (`react-three-fiber:docs/API/canvas.mdx`), and the on-demand rendering and `invalidate` guidance in `react-three-fiber:docs/advanced/scaling-performance.mdx`.
- A worked example of pausing a canvas off-screen: `vengeance-ui:src/components/ui/liquid-ocean.tsx` switches `frameloop` between `always` and `never` from an IntersectionObserver, lowers geometry detail while hidden, fixes `dpr` at 1 and overlays DOM children with pointer events disabled. It has no reduced-motion or no-WebGL path, so add both.
- Star-field and light-trail backgrounds, described only because react-bits is licence-restricted: `react-bits:src/content/Backgrounds/Galaxy/Galaxy.jsx` (OGL shader with a `disableAnimation` prop) and `react-bits:src/content/Backgrounds/Hyperspeed/Hyperspeed.jsx` (three.js light trails with named presets).

## Sources
Original guidance written for this project. react-three-fiber and vengeance-ui are MIT-licensed; react-bits is MIT with the Commons Clause and is described, not quoted.
