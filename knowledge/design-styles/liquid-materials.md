---
title: "Liquid materials"
kind: design-style
summary: "Surfaces that behave like molten metal, oil, gel or water: shader-driven chrome and iridescence, goo and metaball shapes, physically based glass and metal in 3D. Covers the four implementation families, fragment-cost limits, static and reduced-motion fallbacks and legibility."
source_ids: [fancy, img2threejs, liquid-logo, react-bits, vengeance-ui]
pattern_ids: [style-liquid-materials]
updated: "2026-10-09"
---

# Liquid materials

Liquid materials make an interface surface look like it flows: mercury and chrome, oil-slick iridescence, gel, water, or glass that bends what is behind it. Four implementation families exist. A fragment shader over a logo or image texture. A background shader on a full-screen quad. Physically based materials in a 3D scene. And 2D SVG techniques (goo filters, metaball paths). The material is the message, which makes it powerful for a logo or a hero object and harmful as general decoration.

## Visual characteristics
- Continuous flowing surfaces with hard reflection bands, fresnel rims and specular highlights.
- Silver or monochrome bases with tinted accents; oil-slick hue shifts from thin-film colour.
- Blobby merging shapes (metaballs, goo) and edge-aware flow that follows a logo contour.
- Slow, viscous motion and damped pointer ripples.

## When it fits, when it does not
- Fits: logo and identity animation, hero objects for product launches, AI, music and fashion brands, loaders, posters, short brand moments.
- Poor fit: dense UI, long reading, low-power devices, sober brands, body-copy treatments, pages that already contain other animated surfaces.
- Supporting influences that work: experimental-3d, futurism, y2k, high-fashion-luxury, a single object in a minimalism layout, aurora-gradient-mesh. Avoid swiss-international-typographic, brutalism and retro-vintage.

## Typography
- Keep text outside the liquid. Use a neutral grotesque or serif at high contrast beside the effect.
- If a wordmark is rendered inside the shader, use heavy, simple letterforms (weight 700-900, 80-200 px) and three to eight letters; thin strokes disintegrate in the flow. Keep a DOM or alt-text equivalent.
- Put body copy on solid panels next to the effect, never over it.

## Colour
- Chrome is low-chroma greys with hard-edged light and dark bands; tint with one accent covering about a third of the surface at most.
- Use near-black or very light backgrounds. Mid-grey backgrounds make chrome disappear.
- Mid-tones inside the effect cut text contrast; verify the silhouette against the background in the static frame (3:1 or better).
- Capture a pleasing frame as the poster and pick the fallback colours from it.

## Composition and layout
- One liquid element per view, with negative space around it; calls to action stay outside the effect.
- Size the canvas to its box with `aspect-ratio`. Mask to a logo shape with an alpha texture. Full-screen only when it is the hero.
- Liquid effects are soft, so render at 0.5-0.75 of device resolution and scale up.
- Always include a poster image and a `<noscript>` or no-WebGL alternative.

## Interaction and motion
- Speed around 0.3-0.7 with 6-15 noise iterations; the local liquid-logo presets span speeds of 0.34 to 1.42 and iterations of 6 to 15. Pointer interaction as damped ripples or attraction.
- Cost is pixels times iterations. Cap the pixel ratio at 1-1.5, lower iterations on phones, pause when off-screen or hidden, and use one canvas.
- Fallbacks: a poster still, or a short muted looping video exported from the tool (liquid-logo exports PNG and MP4), or an SVG goo filter or gradient where WebGL is unavailable.
- Reduced motion: show the poster frame or freeze the time uniform, and turn off pointer ripples.

## Accessibility cautions
- Decorative layers are `aria-hidden`; a logo rendered on a canvas still needs a text alternative.
- Continuous motion in peripheral vision needs a pause control beyond five seconds (WCAG 2.2.2); avoid specular glints that flicker.
- Chrome edge shading can lower edge definition for low-vision users; check the static frame.
- Heavy GPU use drains batteries; offer the static version when low-power or data-saver signals are present.

## Common mistakes
- A full-screen, always-on, 60 fps shader behind the whole site.
- Chrome text for headings and navigation.
- Several liquid, glass and aurora effects competing on one page.
- Low-resolution or non-transparent logo textures, giving jagged flow; no static fallback; unbounded pixel ratio on large screens.

## Typical mistakes of AI-generated versions
- A "chrome blob" or a blurred white card called "liquid glass", plus metallic CSS gradients on headlines.
- A pasted full-screen mercury shader at 60 fps with no pause, no poster and no reduced-motion path.
- The same pink-and-blue iridescent gradient on every output.

## How to build it
- Pattern: `style-liquid-materials`. Choose a family, set a frame-cost budget, build the poster and fallback first, then the live version.
- `liquid-logo:fragment-shader.glsl` is a simplex-noise flow field that follows the edges of a logo texture, driven by uniforms such as `u_speed`, `u_iterations`, `u_scale`, `u_noiseIntensity` and `u_logoInteractStrength`. `liquid-logo:presets.js` holds ten named parameter sets, `liquid-logo:shaders.js` loads and compiles the shader pair, and `liquid-logo:main.js` runs the `requestAnimationFrame` loop. The README documents PNG and MP4 export and client-side processing (`liquid-logo:README.MD`).
- For 3D, `img2threejs:docs/materials/THREEJS_MATERIAL_REFERENCE.md` gives starting values (polished chrome at metalness 1 and roughness 0.12, clear glass at roughness 0.05 with transmission 1, frosted glass at 0.52 and 0.85) and the rules to use `transmission` rather than low opacity and to provide a pre-filtered environment.
- 2D goo: `fancy:src/fancy/components/filter/gooey-svg-filter.tsx` (blur with a `strength` prop, default 10, then an alpha-contrast colour matrix and composite). `vengeance-ui:src/components/ui/liquid-metal.tsx` wraps the `LiquidMetal` shader of the `@paper-design/shaders-react` package with `colorBack`, `colorTint`, `speed`, `repetition` and `distortion` props.
- Described only because react-bits is licence-restricted: `react-bits:src/content/Backgrounds/LiquidChrome/LiquidChrome.jsx` (`baseColor`, `speed`, `amplitude`, `frequencyX`, `frequencyY`, `interactive`), `react-bits:src/content/Animations/MetallicPaint/MetallicPaint.jsx` (a WebGL2 shader over an image with `liquid`, `refraction`, `speed`, `tintColor`) and `react-bits:src/tools/shape-magic/liquid.js` (liquid SVG paths without WebGL).

## Sources
Original guidance written for this project. fancy, img2threejs (Apache-2.0), liquid-logo and vengeance-ui are permissively licensed; react-bits is MIT with the Commons Clause and is described, not quoted.
