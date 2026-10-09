---
title: "Aurora and gradient mesh"
kind: design-style
summary: "Soft multi-colour gradients that drift like light: blurred colour blobs, mesh gradients and shader-driven aurora backgrounds. Covers three implementation tiers from static CSS to WebGL, palette discipline, banding, text contrast over the worst region and freeze-frame fallbacks."
source_ids: [fancy, react-bits, shadergradient, vengeance-ui]
pattern_ids: [style-aurora-gradient-mesh]
updated: "2026-10-09"
---

# Aurora and gradient mesh

Aurora and gradient-mesh backgrounds fill a hero or section with soft colour that blends and slowly moves, like northern lights or a lava lamp. They make a plain layout feel atmospheric without imagery. They are also the most overused effect on AI-flavoured sites, so the value lies in a deliberate palette, controlled motion and a text-safe layout.

## Visual characteristics
- Three or four colour regions blended with large soft transitions; no visible edges.
- Slow drift, with cycles of 20-60 seconds, or a still frame used as a poster.
- Often paired with grain to remove banding and add warmth.
- Always a background: the content sits on top in a simple, high-contrast layer.

## When it fits, when it does not
- Fits: hero backgrounds behind a short headline, AI and software launches, wellness and meditation, event pages, section transitions, brand moments.
- Poor fit: behind dense text, data visualisation (colour confusion), low-power devices, pages that need a neutral reading ground.
- Supporting influences that work: glassmorphism, minimalism, grain-and-texture, product-led-saas, liquid-materials, futurism. Avoid brutalism, swiss-international-typographic and flat retro looks.

## Typography
- Simple, heavy-enough sans at large sizes: headline 48-96 px, weight 600-700; body at 18 px or larger when it sits near the gradient.
- Keep text on a calm part of the field, or on a panel. Do not use thin weights over colour transitions.

## Colour
- Pick an analogous or split palette with similar lightness so blends stay clean; interpolate in OKLCH (`in oklch` gradient interpolation) to avoid grey, muddy midpoints.
- Avoid the default indigo-to-violet-to-pink sweep; start from the brand hue and add one neighbour and one contrast.
- Check text against the lightest and the most saturated region. White on violet #5227FF is 6.79:1, but white on lime #7CFF67 is 1.28:1.
- Add a scrim (dark at 35-55%) or a solid text panel when the field varies.
- Dither or add faint grain (2-6%) to prevent banding on 8-bit displays.

## Composition and layout
- Position the brightest area away from the headline; fade the field out with a mask toward the content and the footer.
- One background per page section; do not stack several.
- Use `position: absolute; inset: 0; z-index: -1` inside a clipped container, with `pointer-events: none`.

## Interaction and motion
- Drift speed low enough to be felt rather than seen. Optional pointer influence at 5% or less.
- Pause when off-screen or the tab is hidden; cap the pixel ratio; one WebGL canvas per page.
- Reduced motion: freeze the animation at a good frame (or swap in the static CSS gradient) and disable pointer influence.
- Animating `filter: blur()` on large layers is expensive; blur once and animate position or opacity.

## Accessibility cautions
- Text contrast over moving colour changes continuously; design for the worst frame or put text on a panel.
- Large saturated animation in peripheral vision can distract readers with attention difficulties; keep amplitude small and offer a pause beyond five seconds (WCAG 2.2.2).
- Mark the layer `aria-hidden`; provide the static fallback for no-WebGL and print.

## Common mistakes
- The same purple-blue-pink gradient on every site.
- Text over the busiest region; thin type over transitions.
- Animated multi-layer blur on mobile; several canvases.
- No grain, so banding appears on large smooth fields; no static fallback.

## Typical mistakes of AI-generated versions
- Three blurred circles in violet, blue and pink behind a centred headline and glass cards, animated forever.

## How to build it
- Pattern: `style-aurora-gradient-mesh`. Tier 1, static CSS: layered `radial-gradient()` backgrounds with `in oklch` interpolation and an optional grain overlay. Tier 2, CSS or SVG motion: blurred coloured shapes. Tier 3, WebGL shader.
- Tier 2 example: `fancy:src/fancy/components/background/animated-gradient-with-svg.tsx` renders blurred SVG circles with CSS keyframes (`colors`, `speed` in seconds, `blur` of light, medium or heavy). It positions circles with `Math.random()` during render, so seed them for server-rendered pages. `vengeance-ui:src/components/ui/aurora-hero.tsx` is a pure-CSS striped aurora using repeating gradients, a blur filter and a background-position animation.
- Tier 3, described only because shadergradient and react-bits are licence-restricted: `shadergradient:packages/shadergradient/src/ShaderGradientCanvas.tsx` lazy-mounts the canvas when visible (`lazyLoad` default true) with `pixelDensity` defaulting to 1; `shadergradient:packages/shadergradient/src/ShaderGradient/Mesh/Materials.tsx` advances the time uniform only while `animate` is `on`, so setting it to `off` gives a still frame for reduced motion; props such as `type` (plane, sphere, waterPlane), `color1` to `color3`, `uSpeed`, `uStrength`, `grain` and `grainBlending` are listed in `shadergradient:packages/shadergradient/src/types.ts`.
- `react-bits:src/content/Backgrounds/Aurora/Aurora.jsx` (OGL; `colorStops`, `amplitude`, `blend`, `speed`) and `react-bits:src/content/Backgrounds/Grainient/Grainient.jsx` (grain props including `grainAnimated`; pauses off-screen and when the tab is hidden). Aurora runs its loop continuously, so add visibility handling.

## Sources
Original guidance written for this project. fancy and vengeance-ui are MIT-licensed; shadergradient declares MIT without a licence file and react-bits is MIT with the Commons Clause, so both are described and referenced by path only.
