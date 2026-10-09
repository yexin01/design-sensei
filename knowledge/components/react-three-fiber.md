---
title: "React Three Fiber (R3F)"
kind: component-library
summary: "React renderer for three.js: declarative scenes inside a Canvas, hooks for the frame loop, asset loading and state, pointer events, on-demand rendering and automatic disposal. Covers install, repo map, documented pitfalls, SSR notes and MIT reuse terms."
source_ids: [react-three-fiber]
pattern_ids: [r3f-canvas-setup, r3f-lazy-canvas-webgl-fallback, r3f-frame-loop-animation, r3f-on-demand-rendering, r3f-adaptive-resolution-performance, r3f-instancing-and-resource-reuse, r3f-gltf-loading-suspense, r3f-pointer-events-interaction, r3f-product-showcase-scene, r3f-test-renderer-unit-tests]
updated: "2026-10-09"
---

# React Three Fiber (R3F)

## What it is and who maintains it

- A React renderer for three.js. Lowercase JSX elements are three.js classes: `<mesh />` creates a `THREE.Mesh`, props are assigned to the instance, and `args` carries constructor arguments (`react-three-fiber:docs/getting-started/your-first-scene.mdx`, `react-three-fiber:docs/tutorials/how-it-works.mdx`).
- Package `@react-three/fiber`, version 9.8.1 at the pinned commit, MIT, maintained by the Poimandres collective (`react-three-fiber:packages/fiber/package.json`).
- v9 pairs with React 19 and v8 paired with React 18 (`react-three-fiber:docs/getting-started/introduction.mdx`). The intro banner says v10 is in alpha (WebGPU, new frame-loop scheduler) with separate docs. This note describes the v9 behaviour found at the pin.
- Targets the DOM and React Native (`@react-three/fiber/native`, expo-gl). Native is out of scope here (`react-three-fiber:docs/getting-started/installation.mdx`).

## Install and minimal usage

- Install as documented: `npm install three @react-three/fiber`. TypeScript projects also add `@types/three` (`react-three-fiber:docs/getting-started/installation.mdx`, `react-three-fiber:readme.md`).
- Peer ranges at the pin: `react >=19 <19.4`, `three >=0.156`, `react-dom` optional (`react-three-fiber:packages/fiber/package.json`). The installation page also says "compatible with React v18 and v19", which conflicts with those peers; trust the manifest of the release you install.
- Smallest scene, quoted from the docs (`react-three-fiber:docs/getting-started/your-first-scene.mdx`):

```jsx
<Canvas>
  <mesh>
    <boxGeometry />
    <meshStandardMaterial />
  </mesh>
</Canvas>
```

- Add `ambientLight` and `directionalLight` children to see shading. A component joins the frame loop with `useFrame((state, delta) => ...)` and mutates a ref (see the animation note).
- `Canvas` fills its parent, so the parent needs a real height. The root is only created once the measured box has non-zero width and height (`react-three-fiber:packages/fiber/src/web/Canvas.tsx`).

## Canvas, hooks and events

| Canvas prop | Default | Notes (`react-three-fiber:docs/API/canvas.mdx`, `react-three-fiber:packages/fiber/src/core/configuration.ts`) |
|---|---|---|
| `frameloop` | `always` | `always`, `demand`, `never` |
| `dpr` | `[1, 2]` | clamps `devicePixelRatio` into the range; a number fixes it |
| `camera` | perspective, fov 75, near 0.1, far 1000, z = 5 | props object or your own camera; `orthographic` switches type |
| `gl` | `{}` | constructor options, a renderer instance, or a sync/async factory. Built-in defaults: antialias, alpha, `powerPreference: 'high-performance'` (`react-three-fiber:packages/fiber/src/core/renderer.ts`) |
| `shadows` | `false` | `true` selects soft PCF; strings or an object configure `gl.shadowMap` |
| `flat`, `linear`, `legacy` | `false` | ACES tone mapping and sRGB output are on by default. `flat` removes tone mapping, `linear` switches off sRGB output, `legacy` disables `THREE.ColorManagement` (per `configuration.ts`; the `canvas.mdx` table words `legacy` the other way round) |
| `performance` | min 0.5, max 1, debounce 200 | movement regression state (`react-three-fiber:packages/fiber/src/core/store.ts`) |
| `fallback` | none | see pitfalls: it becomes the content of the `<canvas>` element |

Other props: `resize`, `events`, `eventSource`, `eventPrefix`, `onCreated`, `onPointerMissed`; extra HTML attributes (`style`, `className`, `aria-*`) go to the wrapper `div`.

- **Hooks** (`react-three-fiber:docs/API/hooks.mdx`, `react-three-fiber:packages/fiber/src/core/hooks.tsx`): `useThree(selector?)` returns renderer, scene, camera, size, viewport, clock, pointer, `invalidate`, `setDpr`, `setFrameloop` and more. `useFrame(callback, priority?)` runs before each render with `(state, delta, xrFrame)`. `useLoader(Loader, url | urls, extend?, onProgress?)` suspends and caches by URL, with `useLoader.preload`. `useGraph(object)` returns `{ nodes, materials }`. Hooks throw outside a `Canvas` subtree.
- **Other exports** (`react-three-fiber:docs/API/additional-exports.mdx`): `extend`, `createRoot`, `createPortal`, `invalidate`, `advance`, `addEffect`, `addAfterEffect`, `addTail`, `flushSync`, `applyProps`, `events`.
- **Objects** (`react-three-fiber:docs/API/objects.mdx`): `args` for constructors, `set`-style props (`color="hotpink"`, `position={[1, 2, 3]}`), `scale={1}` through `setScalar`, dash-case piercing (`rotation-x`), `attach` (materials and geometries attach automatically), `<primitive object={...} />` for existing objects, `extend` for third-party classes.
- **TypeScript** (`react-three-fiber:docs/API/typescript.mdx`, `react-three-fiber:docs/tutorials/v9-migration-guide.mdx`): type refs with `useRef<Mesh>(null!)`, spread props with `ThreeElements['mesh']`, add custom elements through the `ThreeElements` interface or the `extend(Class)` factory form. v9 removed the old `MeshProps`-style exports.
- **Events** (`react-three-fiber:docs/API/events.mdx`, `react-three-fiber:packages/fiber/src/core/events.ts`): `onClick`, `onContextMenu`, `onDoubleClick`, `onWheel`, `onPointerUp/Down/Over/Out/Enter/Leave/Move`, `onPointerMissed` (the docs say enter and leave behave like over and out). Events reach every intersected object nearest first; `stopPropagation()` also blocks objects behind. Pointer capture is added to the hit test rather than replacing it.

## Performance regimes (documented)

| Regime | How | Cost and caveat |
|---|---|---|
| Continuous | default `frameloop="always"` | one render per display frame; drains battery when the scene is idle |
| On demand | `frameloop="demand"` | renders on prop changes or `invalidate()`; mutation outside React (controls) must invalidate |
| Manual | `frameloop="never"` plus `advance()` | you drive time |
| Resolution | `dpr`, `performance.regress()` | fewer pixels while moving |
| Draw calls | instancing, shared geometry and materials | docs: stay well under 1000 meshes, ideally a few hundred |

Details, code and a checklist: `knowledge/animations/r3f-animation-and-performance.md`. Source: `react-three-fiber:docs/advanced/scaling-performance.mdx`.

## Directory map

| Path | Contents |
|---|---|
| `react-three-fiber:docs/` | MDX docs: `getting-started/`, `API/`, `tutorials/`, `advanced/`, `development/CORE.md` (module boundaries) |
| `react-three-fiber:packages/fiber/src/core/` | platform-neutral core: `root.tsx`, `configuration.ts`, `store.ts`, `loop.ts`, `hooks.tsx`, `events.ts`, `reconciler.tsx`, `renderer.ts`, `portal.tsx`, `extend.ts` |
| `react-three-fiber:packages/fiber/src/web/` | DOM `Canvas.tsx` and pointer-event adapter `events.ts` |
| `react-three-fiber:packages/fiber/src/native/` | React Native `Canvas` and polyfills |
| `react-three-fiber:packages/fiber/tests/` | jest suites for canvas, events, hooks, renderer, dpr |
| `react-three-fiber:packages/test-renderer/` | `@react-three/test-renderer` 9.1.1 |
| `react-three-fiber:packages/eslint-plugin/` | `@react-three/eslint-plugin` 0.1.2 |
| `react-three-fiber:example/src/demos/` | 28 lazy-loaded demos (portals, multi-view, GLTF, shaders, Suspense errors) |

## Notable modules

| Module | What it does | File | Pattern |
|---|---|---|---|
| Canvas | measures the parent, builds the root, wraps children in an error boundary and Suspense | `react-three-fiber:packages/fiber/src/web/Canvas.tsx` | `r3f-canvas-setup` |
| Root and renderer | `createRoot`, async renderer readiness, ownership and release of the renderer | `react-three-fiber:packages/fiber/src/core/root.tsx` | `r3f-lazy-canvas-webgl-fallback` |
| Frame loop | one shared `requestAnimationFrame` loop, `invalidate`, `advance`, global effects | `react-three-fiber:packages/fiber/src/core/loop.ts` | `r3f-on-demand-rendering` |
| Hooks | `useFrame`, `useThree`, `useLoader` | `react-three-fiber:packages/fiber/src/core/hooks.tsx` | `r3f-frame-loop-animation`, `r3f-gltf-loading-suspense` |
| Configuration and store | prop diffing, dpr clamp, `performance`, size | `react-three-fiber:packages/fiber/src/core/configuration.ts` | `r3f-adaptive-resolution-performance` |
| Reconciler | attach, prop application, disposal on removal | `react-three-fiber:packages/fiber/src/core/reconciler.tsx` | `r3f-instancing-and-resource-reuse` |
| Events | raycasting, hover, capture | `react-three-fiber:packages/fiber/src/core/events.ts` | `r3f-pointer-events-interaction` |
| Test renderer | scene-graph tests without WebGL | `react-three-fiber:packages/test-renderer/src/index.tsx` | `r3f-test-renderer-unit-tests` |

## Pitfalls the docs and source warn about

- **No `setState` in loops.** Do not set state in `useFrame`, fast pointer events or intervals; mutate refs with deltas (`react-three-fiber:docs/advanced/pitfalls.mdx`).
- **Hooks outside `Canvas` crash** because they need its context (`react-three-fiber:docs/API/hooks.mdx`).
- **Changing `args` rebuilds the object.** Passing fresh `new THREE.Vector3()` or geometry instances as props recreates them every render (`react-three-fiber:docs/API/objects.mdx`).
- **Mutation is invisible under `demand`.** Controls that mutate the camera need `invalidate()`; it only sets a flag and does not render immediately (`react-three-fiber:docs/advanced/scaling-performance.mdx`).
- **Do not mount and unmount heavy subtrees.** Materials compile and geometries upload on mount; toggle `visible` instead (`react-three-fiber:docs/advanced/pitfalls.mdx`).
- **Allocation in `useFrame`** feeds the garbage collector; the repo ships lint rules `no-new-in-loop` and `no-clone-in-loop` (`react-three-fiber:packages/eslint-plugin/docs/rules/no-new-in-loop.md`).
- **Disposal.** R3F calls `dispose()` on unmounted objects. Use `dispose={null}` for shared assets. `<primitive>` objects are never disposed and must not be added twice; clone them (`react-three-fiber:docs/API/objects.mdx`, `react-three-fiber:packages/fiber/src/core/reconciler.tsx`).
- **`useLoader` assets are cached by URL.** Mutating or disposing them affects every user (`react-three-fiber:docs/API/hooks.mdx`).
- **Colour management.** Materials created outside the Canvas need `THREE.ColorManagement.enabled = true`; v9 stopped converting texture colour spaces, so annotate colour textures for custom materials (`react-three-fiber:docs/advanced/scaling-performance.mdx`, `react-three-fiber:docs/tutorials/v9-migration-guide.mdx`).
- **`fallback` is not a WebGL detector.** The docs describe it as shown "in case GL is not supported", but `Canvas.tsx` renders it as the children of the `<canvas>` element. A failed renderer throws out of `Canvas`, so use an error boundary (a test covers a rejected async `gl` factory reaching the nearest boundary: `react-three-fiber:packages/fiber/tests/canvas.test.tsx`).
- **StrictMode and hiding.** In v9 a parent `<StrictMode>` applies inside the canvas, so effects run twice in development; create and release resources symmetrically (`react-three-fiber:docs/tutorials/v9-migration-guide.mdx`). Hiding a canvas with React `<Activity>` keeps its renderer and scene state and pauses frame subscriptions (`react-three-fiber:packages/fiber/CHANGELOG.md`, 9.8.1).
- **One `Canvas` is one WebGL context**, and browsers cap live contexts (comment in `react-three-fiber:packages/fiber/src/core/renderer.ts`). `react-three-fiber:example/src/demos/ViewTracking.tsx` renders several DOM-tracked views from a single canvas.
- **Docs versus source at the pin:** `how-it-works.mdx` says the default camera sits at the origin and the loop uses `setAnimationLoop`; `Canvas.tsx`, `configuration.ts` and `loop.ts` show z = 5 and `requestAnimationFrame` (XR sessions switch to `setAnimationLoop`). `scaling-performance.mdx` illustrates `performance.min` as 0.1, the store default is 0.5. `canvas.mdx` says an unchanged `dpr` range preserves a runtime `setDpr`, but `react-three-fiber:packages/fiber/tests/dpr.test.tsx` ("the prop wins over setDpr") and `configuration.ts` re-resolve the prop on every re-render and display change.

## Next.js and SSR

- Next.js 13.1 or later: add `three` to `transpilePackages` in `next.config.js` if you meet untranspiled add-ons; older versions used `next-transpile-modules`. The docs also point to an official starter, `create-r3f-app next` (`react-three-fiber:docs/getting-started/installation.mdx`, `react-three-fiber:docs/getting-started/introduction.mdx`).
- A test server-renders `Canvas` with `renderToString`: the output contains the `<canvas>` and its fallback content and no renderer is created (`react-three-fiber:packages/fiber/tests/canvas.test.tsx`).
- The docs do not cover App Router `'use client'`, dynamic imports or hydration. See `knowledge/implementation-recipes/r3f-canvas-in-a-page-with-fallback.md` for an original approach that never renders the scene on the server.

## drei and the ecosystem

`@react-three/drei` is a separate package ("useful helpers, this is an ecosystem in itself" in the docs) and is not part of this repository. The docs and demos use it for `OrbitControls`, `Environment`, `useGLTF`, `useTexture`, `Html`, `useProgress`, `PerformanceMonitor` and `Detailed`; `react-three-fiber:example/package.json` depends on `@react-three/drei` `^9.105.5`. The docs state that drei's controls call `invalidate` for you. This catalog has not read drei's source, so its recipes use plain three.js add-ons and flag any drei use. Other packages listed in the intro: gltfjsx, postprocessing, rapier, xr, leva, a11y, react-spring (`react-three-fiber:docs/getting-started/introduction.mdx`).

## Testing and lint packages

- `@react-three/test-renderer` renders to a scene graph without WebGL: `create(element)`, `scene`, `toGraph()`, `toTree()`, `fireEvent()`, `advanceFrames(frames, delta)`, `update()`, `unmount()`, `act()`. It forces `frameloop: 'never'` and no events by default (`react-three-fiber:packages/test-renderer/README.md`, `react-three-fiber:packages/test-renderer/markdown/rttr.md`, `react-three-fiber:packages/test-renderer/src/index.tsx`). Install and walkthrough: `react-three-fiber:docs/API/testing.mdx`.
- `@react-three/eslint-plugin` enables `no-clone-in-loop` and `no-new-in-loop` in its `recommended` config (`react-three-fiber:packages/eslint-plugin/src/configs/recommended.ts`).

## Accessibility and performance observations

- R3F has no reduced-motion or accessibility handling in its source; the docs list `@react-three/a11y` as an ecosystem package that this catalog has not reviewed. Reduced motion, a static alternative and a pause control are the integrator's job (see the recipes).
- The docs claim there is no overhead compared with plain three.js. This catalog did not measure that.
- The default loop renders continuously. The only measurements in the docs are an external scheduler benchmark quoted in `react-three-fiber:docs/advanced/scaling-performance.mdx`; this catalog did not re-run it.

## Licence and reuse

MIT, Copyright (c) 2019-2025 Poimandres (`react-three-fiber:LICENSE`). Attribution: React Three Fiber by the Poimandres collective. Keep the notice when copying substantial code. Binary assets under `react-three-fiber:example/public/` and the docs images carry no licence statement in the repo and are not cleared for reuse here; the tutorials credit their own models and CC0 textures (`react-three-fiber:docs/tutorials/loading-models.mdx`, `react-three-fiber:docs/tutorials/loading-textures.mdx`).

## Related patterns

`r3f-canvas-setup`, `r3f-lazy-canvas-webgl-fallback`, `r3f-frame-loop-animation`, `r3f-on-demand-rendering`, `r3f-adaptive-resolution-performance`, `r3f-instancing-and-resource-reuse`, `r3f-gltf-loading-suspense`, `r3f-pointer-events-interaction`, `r3f-product-showcase-scene`, `r3f-test-renderer-unit-tests`. Recipes: `knowledge/implementation-recipes/r3f-canvas-in-a-page-with-fallback.md`, `knowledge/implementation-recipes/r3f-product-showcase-scene.md`.
