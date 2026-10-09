# Three-dimensional design

Decide whether real-time 3D earns its cost, then build it with React Three Fiber (R3F) so it loads late, renders only when needed, stays within budget and falls back to a poster. Load this before adding a three.js or R3F scene, a product viewer, or an image-to-3D model.

Claims about R3F come from the [R3F note](../../../knowledge/components/react-three-fiber.md) and the [R3F animation and performance note](../../../knowledge/animations/r3f-animation-and-performance.md) (v9.8.1 at the pin; read the manifest of the release you install). Thresholds marked heuristic are Design Sensei guidance, not measurements. The art-direction side lives in the [experimental 3D style note](../../../knowledge/design-styles/experimental-3d.md).

## Does 3D earn its cost?

3D costs JavaScript, GPU, battery, assets and accessibility work. Require a reason tied to the product.

| Situation | Choice |
| --- | --- |
| Shape, finish or scale is the product (hardware, footwear, furniture, vehicle) | R3F product viewer: [[r3f-product-showcase-scene]] |
| Decorative depth, abstract object | Image, video or CSS 3D transform; not R3F |
| Scroll-driven camera journey | Only at `motion_intensity` 7+, one canvas, a still image per section for reduced motion |
| Photo of an object, no GLB available, approximate result acceptable | Image-to-3D, see below |
| Exact geometry or CAD fidelity needed | Supplied GLB via `useLoader`, [[r3f-gltf-loading-suspense]] |
| Content-heavy, SEO-critical, forms, checkout, low-power or mobile-first audience | No 3D, or a lite mode with a poster |
| Several small 3D widgets | One canvas with several views, not several canvases |

Config gates:

| Setting | Effect |
| --- | --- |
| `webgl_enabled: false` | No 3D at all. Use images or video. |
| `max_webgl_canvases` (default 1) | Ceiling. One `Canvas` is one WebGL context; browsers cap live contexts. |
| `initial_js_kb` (default 200, gzipped) | three.js plus R3F must be lazy-loaded; they will not fit in the initial bundle. |
| `allowed_dependencies` | `none`/`existing`: no new `three` or `@react-three/fiber`; use a poster or CSS. `minimal`: add `three` and `@react-three/fiber` only; justify drei separately. |
| `motion_intensity` 1-4 | Static pose, user-driven rotation only. 5-6: slow idle rotation while visible. 7+: camera moves of 600-1200 ms (heuristic from the style note). |
| `reduced_motion` | R3F has no reduced-motion handling; you gate it. Fixed pose, manual controls, no auto-rotation or camera drift. |
| `preferred_frameworks` | Match the project's framework; v9 pairs with React 19, v8 with React 18. |

## R3F setup

1. Install `three` and `@react-three/fiber` (plus `@types/three` for TypeScript). Check the peer range of the release: the note records `react >=19 <19.4` and `three >=0.156` at the pin. Next.js: add `three` to `transpilePackages` if untranspiled add-ons appear.
2. `Canvas` fills its parent and creates its root only once the parent has non-zero size: give the wrapper an explicit height.
3. Never render the scene on the server. Pattern [[r3f-lazy-canvas-webgl-fallback]]: the poster is the initial output; a lazy chunk mounts after effects confirm WebGL support and the section is near the viewport. Wrap in an error boundary, because a failed renderer throws out of `Canvas` and `Canvas`'s `fallback` prop is not a WebGL detector. Recipe: [canvas with fallback](../../../knowledge/implementation-recipes/r3f-canvas-in-a-page-with-fallback.md).
4. Pattern [[r3f-canvas-setup]] for the declarative scene.

## Frame loop: always versus on demand

| Scene | Setting | Notes |
| --- | --- | --- |
| Static or user-driven viewer | `frameloop="demand"` | Controls that mutate the camera must call `invalidate()`. Damping needs `update()` every frame, so leave it off in demand mode. [[r3f-on-demand-rendering]] |
| Continuous animation on screen | `frameloop="always"` | Switch to `demand` when offscreen or paused (drive the prop from state). |
| Pause on reduced motion | `demand`, skip the mutation in `useFrame` | Keep drag/orbit working through `invalidate()`; offer a pause control. |

- Animate by mutating refs in `useFrame`, never `setState` in loops or fast pointer events ([[r3f-frame-loop-animation]]).
- Use `delta`, clamp it (about 0.1 s) because the first frame after idle can carry seconds of delta, and never key animation to `clock.elapsedTime` if you toggle `frameloop` (it resets).
- Allocate vectors and matrices once, outside the callback.
- Toggle `visible` instead of unmounting heavy subtrees; materials compile and geometries upload on mount.

## Scene composition, light, material

- One hero object on a stage. Leave space around it for DOM text; real text stays in the DOM over the canvas, with a scrim or solid panel for contrast. Use a 3D text mesh for at most one display word and mirror it in the DOM.
- Restraint: one neutral pre-filtered environment for reflections, plus one or two accent lights. Skip bloom and depth of field unless the art direction needs them; they are hero-render features, not defaults.
- R3F defaults to sRGB output and ACES filmic tone mapping. Use `flat` if flat brand colours must stay exact. Colour textures are sRGB; data maps (roughness, normal) are not. Materials created outside the Canvas need `THREE.ColorManagement.enabled = true`.
- Shadows are off by default; enable only where they ground the object, and drop them on phones.
- Match canvas and page backgrounds, or keep the canvas transparent.
- Avoid the generic 3D tell: a rotating wireframe torus knot or glass blob with orbit controls, stock environment and bloom, regardless of product.

## Camera and controls UX

- Orbit with damping, angle limits and zoom limits so the object cannot be lost. Idle rotation 0.1-0.3 rad/s, only while visible, stopped by interaction (heuristic).
- Do not capture page scroll on touch devices: one-finger drag rotating the object competes with scrolling. Prefer a visible "interact" affordance or restrict wheel zoom.
- Keyboard: orbit controls are usually mouse-only. Make the viewer focusable (`tabIndex`), add arrow-key rotation (15 degree steps is a workable default), keep a visible focus ring, and a descriptive `aria-label`.
- Frame the object from its bounding box instead of hard-coding the camera; recompute on resize.
- Pointer events on meshes: [[r3f-pointer-events-interaction]].

## Asset and performance budgets

| Concern | Rule |
| --- | --- |
| Draw calls | The docs say stay well under 1000 meshes, ideally a few hundred. Instance repeats: [[r3f-instancing-and-resource-reuse]]. |
| Geometry/materials | Share them; cache loads with `useLoader`; protect shared assets with `dispose={null}`; dispose `<primitive>` objects yourself. |
| Models | Compressed GLB (Draco or Meshopt), KTX2 textures, low-quality first with nested `Suspense`. Triangle budget set up front (img2threejs tiers: up to 6,000 low, up to 60,000 standard). |
| Resolution | `dpr={[1, 1.5]}` or similar; test antialiasing off at DPR 2+ (catalog guidance, unbenchmarked); adaptive: [[r3f-adaptive-resolution-performance]]. Hold a dynamic ratio in React state and pass it as the `dpr` prop. |
| Phones | Cap DPR near 1.5, no shadows or post effects, simpler model or the poster (heuristic). |
| Loading | Poster for first paint, loading feedback, lazy chunk. The poster is the LCP candidate, not the canvas. |
| Idle | After the scene settles, check idle CPU and GPU in the performance panel. |
| Count | Canvases within `max_webgl_canvases`; loop stops offscreen. |

## Fallbacks

Poster `img` with real alt text (or `role="img"` plus `aria-label` on the canvas wrapper), shown when: WebGL missing, renderer throws, context lost, `webgl_enabled` false, data-saver, small or coarse-pointer device by policy, or reduced-motion visitors who do not opt in to interaction. Keep the same information in the DOM and offer a skip link past the viewer. Under reduced motion show a fixed pose with manual controls, or the poster.

## Image-to-3D with img2threejs

Use when a site needs a stylized 3D hero or prop from one reference image, approximate is acceptable, the project can afford a long agent session (the docs estimate roughly 80k-180k model tokens per object, an estimate not a measurement) and a browser or screenshot tool exists. Not for exact geometry, photoreal people, smoke, liquid, caustics or lace, scenes, or when no screenshot tooling exists; use a supplied GLB or a static image instead.

Workflow, in order: confirm the object suits the suitability rubric (pass, conditional or reject); install the img2threejs skill (needs Node 18+, Git, Python 3.10+); run the staged pipeline with strict quality and the locked build passes; judge each pass by looking at the reference-versus-render comparison sheet; mount the generated `create<Name>Model` factory in R3F as a `<primitive>` created in an effect (it uses DOM canvases, so never on the server), dispose it yourself, and put it inside the lazy shell above with a poster. Use `frameloop="demand"`. The generated `LookDev` lights use a 4096 px shadow map: prefer your own lights in production. Do not present the result as an exact copy.

Patterns: [[image-to-3d-img2threejs-pipeline]], [[image-to-3d-review-gates-and-correction-loop]]. Playbook and steps: [recipe](../../../knowledge/implementation-recipes/image-to-3d-with-img2threejs.md), [img2threejs note](../../../knowledge/components/img2threejs.md). Licences: img2threejs is Apache-2.0 (`copy_with_attribution`): keep the licence text, mark modified files and keep copyright notices; the licensing of generated output is not stated upstream (not verified), so keep the reference image's rights in mind. R3F is MIT. The licence gate is in `source-usage.md`.

## Checklist before saying done

- [ ] A reason tied to the product justifies 3D; a poster alternative exists.
- [ ] `webgl_enabled` and `allowed_dependencies` respected; three.js and R3F in a lazy chunk, outside `initial_js_kb`.
- [ ] One canvas (or within `max_webgl_canvases`); `frameloop` chosen deliberately; stops offscreen.
- [ ] No `setState` in `useFrame`; deltas clamped; no per-frame allocation.
- [ ] DPR bounded; assets compressed; draw calls and triangles logged and within budget.
- [ ] WebGL-missing, renderer-error, context-lost and reduced-motion paths tested by hand.
- [ ] Keyboard access, focus ring, `aria-label`, contrast of overlay text on the worst frame.
- [ ] Disposal verified across mount, unmount and route change.
- [ ] `design-sensei eval` clean for PERF-004, PERF-005, PERF-006, MOT-001, MOT-006.

## Common mistakes

- Uncompressed models or 4K textures; no poster; blocking first paint.
- Rendering the canvas during SSR; hooks used outside `Canvas`.
- Fresh `new THREE.Vector3()` or geometry passed as props every render, rebuilding objects.
- Remounting scenes instead of toggling `visible`; a loop running while offscreen.
- More than one canvas; scroll hijacked on touch.
- Treating `Canvas fallback` as WebGL detection.
- Judging generated models by the similarity score alone instead of a three-quarter render.

## Related

- Patterns: [[r3f-canvas-setup]], [[r3f-lazy-canvas-webgl-fallback]], [[r3f-on-demand-rendering]], [[r3f-frame-loop-animation]], [[r3f-adaptive-resolution-performance]], [[r3f-instancing-and-resource-reuse]], [[r3f-gltf-loading-suspense]], [[r3f-product-showcase-scene]], [[image-to-3d-img2threejs-pipeline]], [[style-experimental-3d]], [[vengeance-ui-three-js-scenes]].
- Recipes: [product showcase scene](../../../knowledge/implementation-recipes/r3f-product-showcase-scene.md), [canvas with fallback](../../../knowledge/implementation-recipes/r3f-canvas-in-a-page-with-fallback.md), [image to 3D](../../../knowledge/implementation-recipes/image-to-3d-with-img2threejs.md).
- Other references: `performance.md`, `motion-design.md`, `shaders-and-webgl.md`, `accessibility.md`, `source-usage.md`.
