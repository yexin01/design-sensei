---
title: "R3F product showcase scene"
kind: recipe
summary: "A rotating, draggable product viewer in React Three Fiber built from documented primitives: GLTF loading with useLoader, a fitted turntable, studio lighting from a three.js room environment, on-demand rendering with controls, and a pause control."
source_ids: [react-three-fiber, img2threejs]
pattern_ids: [r3f-product-showcase-scene, r3f-gltf-loading-suspense, r3f-frame-loop-animation]
updated: "2026-10-09"
---

# R3F product showcase scene

## Goal

Show one product model on a page: it turns slowly, the visitor can drag to inspect it, rendering stops when nothing moves, and motion can be paused or is off for visitors who prefer reduced motion. The code uses R3F and plain three.js add-ons only; drei is not required.

## When to use

- A single hero object or product detail view where 3D adds information (shape, finish, scale).
- Not when the model is unavailable or very heavy for the audience's devices: use a photo, a turntable video or a poster. Not for configurators with many variants without a loading and memory plan.

## Prerequisites

- Everything in `knowledge/implementation-recipes/r3f-canvas-in-a-page-with-fallback.md`: R3F 9.x, React `>=19 <19.4`, `three >=0.156`. Use that recipe's shell for lazy loading, the WebGL check, the error boundary and the poster, and its `usePrefersReducedMotion` hook.
- A `.glb` or `.gltf` file served from your site. Without one the viewer shows a placeholder knot.
- Import paths: the docs use `three/addons/...` (`react-three-fiber:docs/API/hooks.mdx`, `react-three-fiber:docs/tutorials/loading-models.mdx`); the example app uses `three/examples/jsm/...` (`react-three-fiber:example/src/demos/Gltf.tsx`). Both forms appear in the sources; use the one your bundler and three version support.
- Helpers used and where the docs show them: `useLoader` with `GLTFLoader` and `<primitive>` (`loading-models.mdx`), `extend(OrbitControls)` as a component (`react-three-fiber:docs/tutorials/v9-migration-guide.mdx`), controls plus `invalidate` under `frameloop="demand"` (`react-three-fiber:docs/advanced/scaling-performance.mdx`). `RoomEnvironment` and `PMREMGenerator` are three.js; the same pattern appears in the img2threejs generator output (`img2threejs:forge/stage3_build/generate_threejs_factory.py`).

## Steps

**1. Imports and controls.** The OrbitControls `change` event is forwarded to `invalidate`, as the docs do. Damping is left off: in three.js it needs `update()` every frame, which would defeat on-demand rendering.

```tsx
import { Suspense, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { Canvas, extend, useFrame, useLoader, useThree } from '@react-three/fiber'
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js'
import { usePrefersReducedMotion } from './guards' // from the canvas recipe

const Controls = extend(OrbitControls)

function ViewerControls() {
  const camera = useThree((s) => s.camera)
  const gl = useThree((s) => s.gl)
  const invalidate = useThree((s) => s.invalidate)
  const ref = useRef<OrbitControls>(null!)
  useEffect(() => {
    const controls = ref.current
    const onChange = () => invalidate()
    controls.addEventListener('change', onChange)
    return () => controls.removeEventListener('change', onChange)
  }, [invalidate])
  return (
    <Controls
      ref={ref}
      args={[camera, gl.domElement]}
      enablePan={false}
      enableZoom={false} // avoid taking over page scrolling; enable if zoom matters
      minPolarAngle={Math.PI / 4}
      maxPolarAngle={(Math.PI * 3) / 4}
    />
  )
}
```

**2. Studio lighting.** A neutral room environment gives reflections to metal and glossy materials; one weak directional light adds a highlight. Values are starting points. The environment texture is disposed on cleanup.

```tsx
function Studio() {
  const gl = useThree((s) => s.gl)
  const scene = useThree((s) => s.scene)
  const invalidate = useThree((s) => s.invalidate)
  useEffect(() => {
    const pmrem = new THREE.PMREMGenerator(gl)
    const envMap = pmrem.fromScene(new RoomEnvironment(), 0.04).texture
    pmrem.dispose()
    scene.environment = envMap
    invalidate()
    return () => { scene.environment = null; envMap.dispose() }
  }, [gl, scene, invalidate])
  return <directionalLight position={[2, 3, 4]} intensity={0.6} />
}
```

**3. The model, fitted without mutating the cached asset.** `useLoader` caches by URL and suspends. Scaling and centring happen on a wrapper group, so the cached `gltf.scene` stays untouched. If the same URL is shown in two places, clone the scene first because an object can only live in one place (`react-three-fiber:docs/API/objects.mdx`).

```tsx
function GltfProduct({ url, size = 1.6 }: { url: string; size?: number }) {
  const gltf = useLoader(GLTFLoader, url)
  const { scale, position } = useMemo(() => {
    const box = new THREE.Box3().setFromObject(gltf.scene)
    const dims = box.getSize(new THREE.Vector3())
    const scale = size / (Math.max(dims.x, dims.y, dims.z) || 1)
    return { scale, position: box.getCenter(new THREE.Vector3()).multiplyScalar(-scale) }
  }, [gltf, size])
  return (
    <group scale={scale} position={position}>
      <primitive object={gltf.scene} />
    </group>
  )
}

function Placeholder() {
  return (
    <mesh>
      <torusKnotGeometry args={[0.5, 0.17, 160, 24]} />
      <meshStandardMaterial color="#b08d57" metalness={0.85} roughness={0.28} />
    </mesh>
  )
}
```

For Draco-compressed files, the docs configure the loader through the third argument of `useLoader` (`react-three-fiber:docs/API/hooks.mdx`, "Loader extensions"). Other compression formats are not covered by the docs.

**4. Turntable and the viewer.** Rotation uses a clamped `delta`, not `clock.elapsedTime`, because switching `frameloop` resets the clock (`react-three-fiber:packages/fiber/src/core/store.ts`). The `frameloop` prop is `always` only while spinning, so a paused or reduced-motion viewer renders on demand.

```tsx
function Turntable({ spin, children }: { spin: boolean; children: ReactNode }) {
  const group = useRef<THREE.Group>(null!)
  useFrame((_, delta) => {
    if (spin) group.current.rotation.y += Math.min(delta, 0.1) * 0.5
  })
  return <group ref={group}>{children}</group>
}

export default function ProductViewer({ modelUrl, active = true }: { modelUrl?: string; active?: boolean }) {
  const reducedMotion = usePrefersReducedMotion()
  const [paused, setPaused] = useState(false)
  const spin = active && !reducedMotion && !paused
  return (
    <div style={{ position: 'relative', width: '100%', height: 480 }}>
      <Canvas
        frameloop={spin ? 'always' : 'demand'}
        dpr={[1, 1.5]}
        camera={{ position: [0, 0.35, 3.2], fov: 35 }}
        role="img"
        aria-label="Interactive 3D view of the product. Drag to rotate.">
        <Studio />
        <Suspense fallback={null}>
          <Turntable spin={spin}>{modelUrl ? <GltfProduct url={modelUrl} /> : <Placeholder />}</Turntable>
        </Suspense>
        <ViewerControls />
      </Canvas>
      {!reducedMotion && (
        <button type="button" onClick={() => setPaused((p) => !p)} style={{ position: 'absolute', right: 12, bottom: 12 }}>
          {paused ? 'Resume rotation' : 'Pause rotation'}
        </button>
      )}
    </div>
  )
}
```

Pass `active` from the shell's in-view flag. The 1.6-unit fitted size and the camera distance of 3.2 at 35 degrees leave a margin around the model.

**5. Tune.**

- Colour: `Canvas` applies ACES filmic tone mapping by default and `flat` switches it off (`react-three-fiber:docs/API/canvas.mdx`). Compare both against the real product photo if brand colours matter.
- Pixels: raise `dpr` to `[1, 2]` for crisper edges on dense screens at higher fill cost; see `knowledge/animations/r3f-animation-and-performance.md`.
- Shadows: the `shadows` prop exists but adds a shadow pass; contact shadows from drei are not verified here.
- Many models: `useLoader.clear(GLTFLoader, url)` evicts a cache entry (present in `react-three-fiber:packages/fiber/src/core/hooks.tsx`, undocumented); dispose geometry and materials of evicted assets yourself.

## Verification checklist

- Responsive: the model is fully visible and centred at 360 px and 1440 px.
- Reduced motion: no rotation and no pause button; dragging still re-renders.
- Pause: after pausing, the performance panel shows no continuous rendering.
- Console: no errors when the model URL is missing or fails (wrap in the canvas recipe's boundary); no leaked contexts on route changes.
- Touch: dragging the canvas on a phone behaves acceptably next to page scrolling (OrbitControls touch and wheel behaviour is three.js behaviour, not verified in these sources).
- Performance: test the real model on a mid-range phone; check file size and texture sizes.
- Accessibility: the label states the interaction, the pause button is reachable by keyboard, and the page offers the information shown only in 3D as text.

## Upstream references

`react-three-fiber:docs/tutorials/loading-models.mdx`, `react-three-fiber:docs/API/hooks.mdx`, `react-three-fiber:docs/API/objects.mdx`, `react-three-fiber:docs/advanced/scaling-performance.mdx`, `react-three-fiber:docs/tutorials/v9-migration-guide.mdx`, `react-three-fiber:example/src/demos/Gltf.tsx`, `react-three-fiber:example/src/demos/Activity.tsx` (a `<primitive>` model with an environment).

## Licence notes

The code above is original and covered by this repository's MIT licence; it calls public APIs of React Three Fiber (MIT, Copyright (c) 2019-2025 Poimandres) and three.js. Do not reuse the example app's models (`react-three-fiber:example/public/`): their licences are not stated. Use models you have the right to publish.
