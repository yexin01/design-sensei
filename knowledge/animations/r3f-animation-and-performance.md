---
title: "R3F animation loop and performance checklist"
kind: animation
summary: "How the React Three Fiber frame loop works, how to animate without React state, when to render on demand, and how DPR, antialiasing, instancing and disposal change cost. A practical checklist drawn from the upstream docs, source and tests."
source_ids: [react-three-fiber]
pattern_ids: [r3f-frame-loop-animation, r3f-on-demand-rendering, r3f-adaptive-resolution-performance, r3f-instancing-and-resource-reuse]
updated: "2026-10-09"
---

# R3F animation loop and performance checklist

## Concept

R3F runs one shared render loop for every `Canvas` on the page. Components subscribe with `useFrame` and animate by mutating three.js objects, not React state. Cost is controlled on three axes: how often frames render (`frameloop`), how many pixels each frame has (`dpr`, antialiasing) and how much each frame draws (draw calls, materials, instancing). Disposal decides what stays in GPU memory.

## How the upstream implements it

- **Loop** (`react-three-fiber:packages/fiber/src/core/loop.ts`). `loop()` requests the next animation frame, runs "before" global effects, then updates every root that is active and either in `always` mode or has `internal.frames > 0`, then runs "after" effects. When no root asks for another frame the loop cancels itself and runs "tail" effects. `update()` reads `clock.getDelta()`, calls each `useFrame` subscriber with `(state, delta, xrFrame)` in priority order, and renders unless a positive-priority subscriber took over. `invalidate()` sets the frame counter and restarts the loop. Calling it from inside a `useFrame` callback requests an additional frame (source comment; not in the docs). `advance()` drives `frameloop="never"`.
- **Subscriptions** (`react-three-fiber:packages/fiber/src/core/store.ts`, `react-three-fiber:packages/fiber/src/core/hooks.tsx`). `useFrame` subscribes in a layout effect and unsubscribes on unmount. Subscribers sort ascending by priority. Any priority above 0 switches off automatic rendering; negative priorities only reorder (`react-three-fiber:docs/API/hooks.mdx`).
- **Any change invalidates.** The store subscribes to itself and calls `invalidate`; the reconciler invalidates on prop updates and removals (`react-three-fiber:packages/fiber/src/core/reconciler.tsx`). That is why `demand` mode renders when React state changes something in the scene.
- **Configuration** (`react-three-fiber:packages/fiber/src/core/configuration.ts`). Defaults: `frameloop="always"`, `dpr=[1, 2]`. A runtime change to frameloop or `gl.shadowMap` lasts until its prop changes. The pixel ratio is the exception: it is re-resolved on every re-render and on browser zoom or display change.
- **Teardown** (`react-three-fiber:packages/fiber/src/core/root.tsx`, `react-three-fiber:packages/fiber/src/core/renderer.ts`). Unmounting a root unmounts the React tree (which disposes declarative objects), calls `dispose` on the scene's own properties such as a background or environment texture, and releases the renderer: R3F-built renderers are disposed and then lose their context. A renderer instance you pass in is not disposed, but its render lists are released and its context is lost (v9).

## Key parameters (verified)

| Option | Default | Effect |
|---|---|---|
| `frameloop` | `always` | `demand` renders only after an invalidation; `never` needs `advance()` |
| `dpr` | `[1, 2]` | pixel ratio = `devicePixelRatio` clamped into the range (`calculateDpr` in `react-three-fiber:packages/fiber/src/core/utils.tsx`) |
| `performance` | current 1, min 0.5, max 1, debounce 200 ms | `regress()` drops `current` to `min`, then back to `max` after `debounce` unless called again; nothing changes unless your code reads `current` |
| `gl` | antialias on, `powerPreference: 'high-performance'` | constructor options; the renderer is created once per root, so set them on the first render |
| `shadows` | `false` | enables the shadow map; the docs give no cost figures |
| `useFrame(cb, priority)` | priority 0 | positive priority means you must call `gl.render` yourself |

## Integration steps

**1. Animate with refs and clamped deltas.** Original code:

```tsx
function Spinner({ speed = 0.6 }: { speed?: number }) {
  const ref = useRef<THREE.Mesh>(null!)
  useFrame((_, delta) => {
    // Use the delta, never a fixed step; clamp it so a pause cannot cause a jump.
    ref.current.rotation.y += Math.min(delta, 0.1) * speed
  })
  return <mesh ref={ref}>{/* geometry and material */}</mesh>
}
```

Lerp or damp toward targets inside the callback, fetch fast external state non-reactively (for example `store.getState()`), and avoid `new THREE.Vector3()` per frame (`react-three-fiber:docs/advanced/pitfalls.mdx`). A spring library that animates outside React is also acceptable per the docs.

**2. Pick a regime.** Idle scenes use `frameloop="demand"`. Anything that mutates the scene outside React (controls, imperative tweens) calls `invalidate()`:

```tsx
const invalidate = useThree((s) => s.invalidate)
useEffect(() => {
  const onChange = () => invalidate()
  controls.addEventListener('change', onChange)
  return () => controls.removeEventListener('change', onChange)
}, [controls, invalidate])
```

`invalidate()` is a flag, so a synchronous animation that starts in the same tick can jump; the docs schedule a frame first and start the animation on the next one (`react-three-fiber:docs/advanced/scaling-performance.mdx`). To animate only while visible, drive the `frameloop` prop from state (`always` when visible, `demand` otherwise); the docs confirm the prop updates apply (`react-three-fiber:docs/API/canvas.mdx`).

**3. Cap pixels.** Use `dpr={[1, 1.5]}` or similar to bound fill cost on high-density screens. Turning antialiasing off (`gl={{ antialias: false }}`, shown in `canvas.mdx`) is worth testing at an effective DPR of 2 or more; that policy is this catalog's guidance, not an upstream recommendation, and it is unbenchmarked. For adaptive quality, call `performance.regress()` while the user moves the camera and scale resolution from `performance.current`; the docs show a small component for this and mention a drei `PerformanceMonitor`. In 9.8.1 a runtime `setDpr` is reset by the next `Canvas` re-render (`react-three-fiber:packages/fiber/tests/dpr.test.tsx`, "the prop wins over setDpr"), although `canvas.mdx` says otherwise. Safer: hold the ratio in React state and pass it as the `dpr` prop.

**4. Reuse and instance.** Share geometries and materials, load assets with `useLoader` (cached by URL), and instance repeats. The docs treat each mesh as a draw call and say to stay well under 1000, ideally a few hundred. Original instancing sketch:

```tsx
function Dots({ count = 2000 }) {
  const ref = useRef<THREE.InstancedMesh>(null!)
  useLayoutEffect(() => {
    const m = new THREE.Matrix4()
    for (let i = 0; i < count; i++) {
      m.setPosition(Math.random() * 4 - 2, Math.random() * 4 - 2, Math.random() * 4 - 2)
      ref.current.setMatrixAt(i, m)
    }
    ref.current.instanceMatrix.needsUpdate = true
  }, [count])
  return (
    <instancedMesh ref={ref} args={[undefined, undefined, count]}>
      <sphereGeometry args={[0.03, 8, 8]} />
      <meshStandardMaterial />
    </instancedMesh>
  )
}
```

**5. Dispose deliberately.** Declarative objects are disposed on unmount, scheduled at idle priority on a real GPU and immediately in a test environment (`disposeOnIdle` in `react-three-fiber:packages/fiber/src/core/reconciler.tsx`). Put `dispose={null}` on a group to protect shared assets for its whole subtree. `<primitive>` objects are never disposed; dispose them yourself (`react-three-fiber:docs/API/objects.mdx`). `useLoader.clear(Loader, url)` evicts a cache entry; it exists in `hooks.tsx` but is undocumented.

**6. Reduced motion.** R3F does not read `prefers-reduced-motion`. Gate motion yourself: skip the mutation in `useFrame`, set `frameloop="demand"`, keep user-driven interaction working through `invalidate()`, and offer a pause control. The recipes `knowledge/implementation-recipes/r3f-canvas-in-a-page-with-fallback.md` and `knowledge/implementation-recipes/r3f-product-showcase-scene.md` implement this.

## Performance and fallbacks

| Situation | Choice | Fallback |
|---|---|---|
| Static or rarely changing scene | `demand` | none needed |
| Continuous animation on screen | `always` plus a clamp on delta | switch to `demand` when off-screen |
| Heavy post-processing or many lights | `performance.regress()` on interaction | lower `dpr` |
| Many identical meshes | `instancedMesh` | LOD (the docs use drei `Detailed`) |
| Large models | `useLoader` with nested `Suspense`, low-quality first | static poster |
| No WebGL or context loss | detect and use an error boundary | static image (see the canvas recipe) |

The docs also note that canvases use React concurrent mode, so `startTransition` can defer expensive updates (`react-three-fiber:docs/advanced/pitfalls.mdx`).

## Pitfalls

- **Delta spikes.** `loop.ts` passes the raw clock delta and the clock keeps running between on-demand frames, so the first frame after a long idle period can carry seconds of delta. Clamp it.
- **Frameloop changes reset time.** `setFrameloop` stops the clock and zeroes `elapsedTime` (`react-three-fiber:packages/fiber/src/core/store.ts`). Do not key animation to `clock.elapsedTime` if you toggle `frameloop`; accumulate deltas instead.
- **A positive `useFrame` priority stops automatic rendering.** Add one for post-processing only if you will render the scene yourself.
- **Mutation is invisible to `demand`.** Forgetting `invalidate()` after mutating outside React leaves a stale frame.
- **Docs and source disagree on the loop.** `react-three-fiber:docs/tutorials/how-it-works.mdx` describes `setAnimationLoop`; `loop.ts` uses `requestAnimationFrame` outside XR.
- **Each `Canvas` owns a WebGL context.** Prefer one canvas with several views for many 3D widgets (`react-three-fiber:example/src/demos/ViewTracking.tsx`).

## Practical checklist

1. Mutate refs inside `useFrame`; no `setState` in loops or fast events.
2. Use `delta`, clamp it, and never depend on `elapsedTime` across frameloop changes.
3. Allocate vectors and matrices once, outside the callback.
4. Choose `demand` for idle scenes and `invalidate()` after outside mutation.
5. Pause rendering when the canvas is off-screen or the user prefers reduced motion.
6. Bound `dpr`; test antialiasing off on dense screens; verify on a mid-range phone.
7. Share geometry and materials; cache loads with `useLoader`; instance repeats.
8. Toggle `visible` instead of remounting heavy subtrees.
9. Protect shared assets with `dispose={null}`; dispose `primitive` objects manually.
10. Keep to one `Canvas` per page where possible and give it a parent with a fixed height.
11. Check idle CPU and GPU in the browser performance panel after the scene settles.
12. Provide a static fallback for no-WebGL and reduced-data cases.

## Related patterns

`r3f-frame-loop-animation`, `r3f-on-demand-rendering`, `r3f-adaptive-resolution-performance`, `r3f-instancing-and-resource-reuse`. Library overview: `knowledge/components/react-three-fiber.md`. Licence: MIT, Copyright (c) 2019-2025 Poimandres (`react-three-fiber:LICENSE`); code above is original and covered by this repository's MIT licence.
