# 3D scenes playbook

Add a real-time 3D scene (three.js, React Three Fiber) only where it carries information, and ship it lazy-loaded, capped, pausable and with a static fallback.

## When to use / when not

- Use for a hero object or product detail where shape, finish or scale matters; immersive portfolios, explainers, data landscapes.
- Do not use for content-heavy or SEO-critical pages, forms and checkout, low-power-first audiences without a lite mode, or a spinning shape with no tie to the message. A CSS or video background, a photo or a turntable video often does the job.
- Gate by dials: `webgl_enabled: false` means do not build it (poster, video or CSS only). `allowed_dependencies` none/existing: no `three`/R3F unless installed. `motion_intensity` <= 3: static pose with manual drag only. `performance_budget` (initial JS, LCP, CLS, `max_webgl_canvases`) outranks the effect; default allows one canvas.
- Typical AI output to avoid: a rotating wireframe torus knot or glass blob with `OrbitControls`, a stock environment preset and bloom, whatever the product.

## Pick the approach

| Situation | Pattern | Reuse class | Notes |
| --- | --- | --- | --- |
| Mount a scene in a React/Next page | [[r3f-canvas-setup]] | copy_with_attribution (MIT) | Canvas fills its parent: give the parent a fixed height. |
| Lazy chunk, WebGL check, poster, error boundary | [[r3f-lazy-canvas-webgl-fallback]] | copy_with_attribution | Start here for every R3F section. `Canvas fallback` is not a WebGL detector; use a boundary. |
| Load a glTF/GLB model | [[r3f-gltf-loading-suspense]] | copy_with_attribution | `useLoader` + `Suspense` + `<primitive>`; Draco via loader extensions. |
| Product on a stage | [[r3f-product-showcase-scene]] | copy_with_attribution | Details in [product showcases](product-showcases.md). |
| Idle scene should cost nothing | [[r3f-on-demand-rendering]] | copy_with_attribution | `frameloop="demand"` and `invalidate()` after outside mutation. |
| Continuous animation | [[r3f-frame-loop-animation]] | copy_with_attribution | Mutate refs in `useFrame` with a clamped delta; no `setState`. |
| High-DPI cost control | [[r3f-adaptive-resolution-performance]] | copy_with_attribution | `dpr` range, antialias off test, `performance.regress()`. |
| Many repeated meshes | [[r3f-instancing-and-resource-reuse]] | copy_with_attribution | Instance, share geometry/material, dispose deliberately. |
| Click/hover on meshes | [[r3f-pointer-events-interaction]] | copy_with_attribution | `stopPropagation`, `onPointerMissed`. Add keyboard equivalents yourself. |
| Packaged scenes (scroll shader dissolve, image particles, 3D books, wave grid, GLB viewer, ocean) | [[vengeance-ui-three-js-scenes]] | copy_with_attribution (MIT; GPU cost high) | Wrap in a motion-safe wrapper; check the dependencies list, it can omit packages. Model viewer has labelled arrow-key rotation. |
| Heavy 3D backgrounds with post-processing or simulation | [[react-bits-three-r3f-backgrounds]] | license_review_required (MIT + Commons Clause) | GPU cost high; some never pause offscreen; budget recipe is mandatory. |
| Art direction for the whole page | [[style-experimental-3d]], [[style-futurism]] | copy_with_attribution / license_review_required | Style notes, no code. |
| Scene built from a reference image | [[image-to-3d-img2threejs-pipeline]] | copy_with_attribution (Apache-2.0) | See [image to 3D](image-to-3d.md). |
| Animated shader backdrop instead of geometry | see [background shaders](background-shaders.md) | | Cheaper than a full scene. |

Defaults: R3F with plain three.js add-ons (OrbitControls, RoomEnvironment) so drei is not required; the recipes use no drei. One `Canvas` per page; several tracked views from a single canvas if more are needed.

## Search commands

```bash
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "r3f canvas" --category three-scene
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "performance" --category three-scene --framework r3f
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "scene" --category three-scene --max-gpu medium --reduced-motion-safe
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "three" --webgl --license-status verified
```

## Implementation steps

1. Art direction first: the one object, its light (neutral pre-filtered environment plus one or two accents), material, camera, restrained palette. DOM text sits over the canvas, never 3D text for headings (one display word at most, mirrored in the DOM). Reserve text zones with a scrim and check the worst frame.
2. Asset budget: compressed GLB (Draco or Meshopt, KTX2 textures where supported), a poster image from the same camera and aspect ratio (avoids visual jump), models you may publish (example-app models in R3F are not cleared).
3. Shell from the [canvas recipe](../../../knowledge/implementation-recipes/r3f-canvas-in-a-page-with-fallback.md): poster on server and first render; `hasWebGL()` probe; `IntersectionObserver`; `React.lazy` chunk; error boundary; context-loss handler returning to the poster. Mark the wrapper `role="img"` with an `aria-label`, or `aria-hidden` if decorative.
4. Scene: `dpr={[1, 1.5]}` (default is `[1, 2]`), `frameloop="demand"` unless something animates, refs plus clamped `delta` in `useFrame`, vectors allocated once, shared geometry/material, `visible` toggles instead of remounting heavy subtrees. `dispose={null}` on groups of shared assets; `<primitive>` is never auto-disposed.
5. Reduced motion: R3F does not read it. Skip mutation in `useFrame`, `frameloop="demand"`, keep drag working via `invalidate()`, offer a pause control; replace scroll-linked camera moves with a still per section.
6. Interaction: damped controls need per-frame `update()`, which defeats `demand` mode; leave damping off or accept `always`. Disable wheel zoom unless needed so page scroll is not captured; do not hijack scroll on touch. Make the viewer focusable with keyboard rotation (arrow keys) and a visible focus ring.
7. Phones: lower `dpr` cap, drop shadows and post effects, simpler model or the static image (heuristic: treat width <= 900 px, four or fewer cores or `saveData` as low power, as one upstream component does).
8. Test: [R3F test renderer](../../../knowledge/components/react-three-fiber.md) can unit-test scene graphs without WebGL ([[r3f-test-renderer-unit-tests]]).

## Accessibility and performance gates

- [ ] Poster with meaningful alt/label; same information available as DOM text; no keyboard trap; viewer reachable and operable by keyboard.
- [ ] Reduced motion emulated: no auto-rotation or camera drift; pause control present when motion runs.
- [ ] WebGL disabled: poster stays, no uncaught error. Context loss recovered.
- [ ] 3D chunk is not downloaded until the section nears the viewport; LCP candidate is the poster; LCP <= 2.5 s, CLS <= 0.1 (reserve height), INP <= 200 ms.
- [ ] Idle scene: Performance panel shows no rendering work off-screen or after settling.
- [ ] Only one live WebGL context in view; no "too many contexts" warnings across route changes.
- [ ] Test on a real mid-range phone with the chosen `dpr` cap; check model and texture sizes.
- [ ] Flicker, flashes and fast zooms avoided; strong parallax offered with a reduce option.
- [ ] Licence gate: R3F/three are MIT (keep notice when copying code); react-bits custom terms; vengeance-ui MIT; only models you may publish.

## Common mistakes

- `setState` in `useFrame` or fast pointer events; `new THREE.Vector3()` per frame; fresh objects as props (rebuilds them).
- Forgetting `invalidate()` after mutating outside React under `frameloop="demand"` (stale frame); keying animation to `clock.elapsedTime` when toggling frameloop (it resets); unclamped delta after idle.
- A positive `useFrame` priority silently stops automatic rendering.
- Mounting several `Canvas` elements; loop running off-screen; uncompressed models and 4K textures; no poster; `Canvas fallback` mistaken for WebGL detection.
- Overlay text over a changing scene without a scrim; fonts loading after first frame.
- Mixing colour spaces on custom materials (colour textures sRGB, data maps not).

## Where to read more

- [React Three Fiber note](../../../knowledge/components/react-three-fiber.md), [R3F animation and performance](../../../knowledge/animations/r3f-animation-and-performance.md), [experimental 3D style](../../../knowledge/design-styles/experimental-3d.md)
- [Canvas with fallback recipe](../../../knowledge/implementation-recipes/r3f-canvas-in-a-page-with-fallback.md), [product showcase recipe](../../../knowledge/implementation-recipes/r3f-product-showcase-scene.md), [motion-safe wrapper](../../../knowledge/implementation-recipes/vengeance-ui-motion-safe-wrapper.md), [heavy background budget](../../../knowledge/implementation-recipes/react-bits-heavy-background-budget.md)
- [three-dimensional-design reference](../references/three-dimensional-design.md), [performance](../references/performance.md), [accessibility](../references/accessibility.md); related playbooks [product showcases](product-showcases.md), [image to 3D](image-to-3d.md), [background shaders](background-shaders.md)
