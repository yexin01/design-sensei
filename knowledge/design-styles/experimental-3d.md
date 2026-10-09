---
title: "Experimental 3D"
kind: design-style
summary: "Real-time 3D scenes as the primary experience: product stages, scroll-driven camera journeys and material showpieces built with three.js and React Three Fiber. Covers art direction, one-canvas budgets, DOM text over WebGL, keyboard access, fallbacks and reduced motion."
source_ids: [img2threejs, react-bits, react-three-fiber, vengeance-ui]
pattern_ids: [style-experimental-3d]
updated: "2026-10-09"
---

# Experimental 3D

Experimental 3D puts a real-time scene at the centre of the page: a product on a lit stage, a camera that travels as the visitor scrolls, a material or object studied up close. On the web it means WebGL through three.js, usually driven from React with React Three Fiber (R3F). The craft is half art direction (light, material, camera, restraint) and half engineering (asset weight, frame budget, fallbacks, accessibility). Without a reason tied to the product, a 3D scene is only a slow, heavy decoration.

## Visual characteristics
- A stage with one hero object (or a small set), lit by a controlled environment, with fog or a plain backdrop.
- The camera as narrator: slow orbits, scroll-linked dolly moves, cuts between sections.
- Physically based materials (metal, glass, ceramic) with environment reflections; post effects such as bloom or vignette used lightly.
- DOM text and UI layered over the canvas; space left around the subject.
- A restrained palette so material and light carry the scene.

## When it fits, when it does not
- Fits: product launches and configurators (hardware, vehicles, furniture, footwear), immersive portfolios, exhibitions, educational explainers, data landscapes, games.
- Poor fit: content-heavy and SEO-critical pages, low-power or mobile-first audiences without a lite mode, forms and other critical flows, scenes with no link to what is being sold or explained.
- Supporting influences that work: motion-led-storytelling, liquid-materials, futurism, minimalism (as the stage), high-fashion-luxury for a single product, dark-technical-developer-tools for viewer UI. Avoid dense editorial layouts and brutalism.

## Typography
- Real text lives in the DOM over the canvas, for legibility, selection and search. Use 3D text meshes only for one display word, and mirror it in the DOM.
- Overlay headings 40-96 px with high contrast; specifications in mono at 14-16 px.
- Load fonts before the first frame so overlay text does not reflow under a running canvas.

## Colour
- R3F renders with sRGB output and ACES filmic tone mapping by default; the `flat` prop turns tone mapping off when flat brand colours must stay exact (`react-three-fiber:docs/API/canvas.mdx`).
- Reflective materials need a neutral, pre-filtered HDR environment; add one or two accent lights for mood. Colour textures are sRGB; roughness, normal and similar data maps are not (`img2threejs:docs/materials/THREEJS_MATERIAL_REFERENCE.md`).
- Overlay text sits over changing content. Reserve text zones with a fixed gradient scrim or a solid panel and check the worst frame.
- Match the page background and the canvas background, or keep the canvas transparent (R3F creates a translucent renderer by default).

## Composition and layout
- One `Canvas` per page, fixed behind scrolling sections or inline in a section, with camera keyframes mapped to scroll progress. The Design Sensei defaults allow one WebGL canvas.
- Treat assets as a budget: compressed GLB with Draco or Meshopt and KTX2 textures; reuse geometries and materials, use instancing for repeats and level of detail for distant parts (all covered in `react-three-fiber:docs/advanced/scaling-performance.mdx`).
- Provide a rendered poster image for first paint, loading feedback, and a fallback for non-WebGL clients.
- Phones: cap the pixel ratio near 1.5, drop shadows and post effects, use a simpler model or a static image, and avoid capturing page scroll inside the canvas.

## Interaction and motion
- Damped orbit controls with angle and zoom limits; idle rotation of 0.1-0.3 rad/s only while visible and stopped by interaction. Camera moves 600-1200 ms.
- Render on demand for static scenes (`frameloop="demand"` with `invalidate()` when something mutates outside React) and stop the loop when off-screen.
- Reduced motion: no auto-rotation or camera drift; show a fixed pose with manual controls, and replace scroll-linked camera moves with a still image per section.
- Never strobe light or flash the camera.

## Accessibility cautions
- Canvas content is not accessible. Give the canvas an `aria-label` (or `aria-hidden` if decorative), keep the same information in the DOM, and offer a skip link past it.
- Orbit controls are usually mouse-only. Make the viewer focusable and add keyboard rotation and zoom. `vengeance-ui:src/components/ui/model-viewer.tsx` shows the minimum: `tabIndex`, a descriptive `aria-label`, arrow keys rotating in 15 degree steps, and a visible focus ring.
- Fast zooms, fly-throughs and strong parallax trigger vestibular symptoms; offer a pause or reduce-motion control.
- Weight is access: provide a lite mode for weak devices and slow networks.

## Common mistakes
- Uncompressed models and 4K textures, blocking first paint, no poster.
- A spinning shape with no connection to the message.
- State updates inside the frame loop, remounting scenes instead of toggling visibility, and creating objects every frame (see `react-three-fiber:docs/advanced/pitfalls.mdx`).
- More than one canvas, or a loop that keeps running off-screen.
- Hijacking scroll inside the canvas on touch devices.

## Typical mistakes of AI-generated versions
- A rotating wireframe torus knot or glass blob with `OrbitControls`, a stock environment preset and bloom, whatever the product.
- Extra helper libraries installed for one cube; 3D text for every heading; no fallback, no mobile mode, no reduced-motion branch.

## How to build it
- Pattern: `style-experimental-3d`. Order: art direction (light, material, camera), asset pipeline, scene, scroll mapping, performance, fallback, accessibility.
- Install per the R3F readme: `three`, `@types/three` and `@react-three/fiber`; fiber 8 pairs with React 18 and fiber 9 with React 19 (`react-three-fiber:readme.md`).
- `Canvas` props worth setting deliberately: `fallback`, `frameloop`, `dpr` (default `[1, 2]`), `flat`, `gl`; wrap it in an error boundary for GPU context crashes (`react-three-fiber:docs/API/canvas.mdx`).
- Pausing off-screen: `vengeance-ui:src/components/ui/liquid-ocean.tsx` toggles `frameloop` from an IntersectionObserver.
- Material starting values (polished chrome around metalness 1 and roughness 0.12; use `transmission` rather than low opacity for glass) are tabulated in the img2threejs material reference above; it also describes code-only procedural models in `img2threejs:README.md`.
- A glass-lens, bar and cube scroll scene with `MeshTransmissionMaterial` is `react-bits:src/content/Components/FluidGlass/FluidGlass.jsx`, described only because react-bits is licence-restricted.

## Sources
Original guidance written for this project. react-three-fiber, img2threejs (Apache-2.0) and vengeance-ui are permissively licensed; react-bits is MIT with the Commons Clause and is described, not quoted.
