---
title: "R3F canvas in a page with lazy loading and fallback"
kind: recipe
summary: "Mount a React Three Fiber Canvas in a React or Next.js page only when it is near the viewport and WebGL works, idle it when off-screen or under reduced motion, and show a static poster when WebGL is missing or the context fails."
source_ids: [react-three-fiber]
pattern_ids: [r3f-canvas-setup, r3f-lazy-canvas-webgl-fallback, r3f-on-demand-rendering]
updated: "2026-10-09"
---

# R3F canvas in a page with lazy loading and fallback

## Goal

A 3D section that costs almost nothing until it is needed: the three.js and R3F code is a separate chunk fetched only when the section is near the viewport and the browser can create a WebGL context; rendering idles when the section is off-screen or the user prefers reduced motion; and a static poster covers every failure path.

## When to use

- Marketing sections, hero objects and product teasers where 3D enhances the page.
- Not for a page whose core content is the 3D scene (no static equivalent), nor for several canvases on one page: each `Canvas` owns a WebGL context and browsers cap live contexts. Use one canvas with several tracked views instead (`react-three-fiber:example/src/demos/ViewTracking.tsx`).
- Not when a CSS or video background would do.

## Prerequisites

| Item | Version or note | Source |
|---|---|---|
| `@react-three/fiber` | 9.x; install with `npm install three @react-three/fiber` | `react-three-fiber:docs/getting-started/installation.mdx` |
| `react`, `react-dom` | `>=19 <19.4` at the pinned release | `react-three-fiber:packages/fiber/package.json` |
| `three` | `>=0.156`; add `@types/three` for TypeScript | `react-three-fiber:packages/fiber/package.json` |
| Next.js | add `three` to `transpilePackages` if an add-on is untranspiled | `react-three-fiber:docs/getting-started/installation.mdx` |

`matchMedia`, `IntersectionObserver`, `canvas.getContext` and the `webglcontextlost` event are standard web APIs and are not covered by the R3F sources. Verify versions on npm at install time.

## Steps

**1. Guards** (no three.js import, so they stay in the page bundle). Original code:

```ts
import { useEffect, useState } from 'react'

export function hasWebGL(): boolean {
  try {
    const canvas = document.createElement('canvas') // discarded after the probe
    return Boolean(canvas.getContext('webgl2') ?? canvas.getContext('webgl'))
  } catch {
    return false
  }
}

export function usePrefersReducedMotion() {
  const [reduced, setReduced] = useState(false) // false on the server and first render
  useEffect(() => {
    const query = window.matchMedia('(prefers-reduced-motion: reduce)')
    const update = () => setReduced(query.matches)
    update()
    query.addEventListener('change', update)
    return () => query.removeEventListener('change', update)
  }, [])
  return reduced
}

export function useInView(rootMargin = '200px') {
  const [node, setNode] = useState<Element | null>(null)
  const [inView, setInView] = useState(false)
  useEffect(() => {
    if (!node) return
    const observer = new IntersectionObserver(([e]) => setInView(e.isIntersecting), { rootMargin })
    observer.observe(node)
    return () => observer.disconnect()
  }, [node, rootMargin])
  return [setNode, inView] as const
}
```

**2. Error boundary.** A failed renderer is thrown out of `Canvas` (`configure(...).catch(setError)` then rethrow in `Canvas.tsx`; a test covers a rejected async `gl` factory reaching the nearest boundary in `react-three-fiber:packages/fiber/tests/canvas.test.tsx`). The docs recommend guarding against context crashes (`react-three-fiber:docs/API/canvas.mdx`).

```tsx
import { Component, type ReactNode } from 'react'

export class SceneBoundary extends Component<{ fallback: ReactNode; children: ReactNode }, { failed: boolean }> {
  state = { failed: false }
  static getDerivedStateFromError() { return { failed: true } }
  componentDidCatch(error: unknown) { console.warn('3D scene failed, showing the poster.', error) }
  render() { return this.state.failed ? this.props.fallback : this.props.children }
}
```

**3. The scene (lazy chunk).** This is the only file that imports three.js and R3F. `frameloop` is toggled from props; the docs state that prop changes apply (`canvas.mdx`, "Updating configuration"). The spin uses `delta` because changing `frameloop` resets `clock.elapsedTime` (`react-three-fiber:packages/fiber/src/core/store.ts`), and clamps it because on-demand frames can follow a long idle period.

```tsx
import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import type { Mesh } from 'three'

type SceneProps = { active: boolean; reducedMotion: boolean; label: string; onContextLost: () => void }

function Spinner({ spin }: { spin: boolean }) {
  const mesh = useRef<Mesh>(null!)
  useFrame((_, delta) => {
    if (spin) mesh.current.rotation.y += Math.min(delta, 0.1) * 0.6
  })
  return (
    <mesh ref={mesh}>
      <icosahedronGeometry args={[1, 1]} />
      <meshStandardMaterial color="#6d8cff" flatShading />
    </mesh>
  )
}

export default function Scene({ active, reducedMotion, label, onContextLost }: SceneProps) {
  const spin = active && !reducedMotion
  return (
    <Canvas
      frameloop={spin ? 'always' : 'demand'}
      dpr={[1, 1.5]}
      camera={{ position: [0, 0, 4], fov: 45 }}
      role="img"
      aria-label={label}
      onCreated={({ gl }) => gl.domElement.addEventListener('webglcontextlost', onContextLost)}>
      <ambientLight intensity={Math.PI / 2} />
      <directionalLight position={[3, 4, 5]} intensity={2} />
      <Spinner spin={spin} />
    </Canvas>
  )
}
```

`role` and `aria-label` reach the wrapper `div` because `CanvasProps` extends the div attributes (`react-three-fiber:packages/fiber/src/web/Canvas.tsx`). A `Canvas` fills its parent and only creates its root once the parent has a non-zero size, so the shell below fixes the height.

**4. The shell.** It never renders the scene on the server: the poster is the initial output, and the lazy scene mounts only after effects have confirmed WebGL and visibility. The `Suspense` also covers asset loading inside the canvas, because `Canvas` suspends its DOM parent while its own `Suspense` is pending (`Block` in `react-three-fiber:packages/fiber/src/core/utils/react.tsx`; the docs' "Nested loading" example relies on this).

```tsx
'use client' // Next.js App Router: needed for hooks. Not covered by the R3F docs.
import { lazy, Suspense, useEffect, useState } from 'react'
import { hasWebGL, useInView, usePrefersReducedMotion } from './guards'
import { SceneBoundary } from './SceneBoundary'

const Scene = lazy(() => import('./Scene')) // three.js and R3F are fetched only when this renders

export function SceneShell({ poster, label, height = 420 }: { poster: string; label: string; height?: number }) {
  const [setNode, inView] = useInView()
  const reducedMotion = usePrefersReducedMotion()
  const [webgl, setWebgl] = useState<boolean | null>(null)
  const [wanted, setWanted] = useState(false)
  const [lost, setLost] = useState(false)

  useEffect(() => setWebgl(hasWebGL()), [])
  useEffect(() => { if (inView) setWanted(true) }, [inView]) // keep mounted after the first view

  const posterEl = (
    <img src={poster} alt={label} style={{ display: 'block', width: '100%', height: '100%', objectFit: 'cover' }} />
  )
  const show3d = webgl === true && wanted && !lost

  return (
    <div ref={setNode} style={{ position: 'relative', width: '100%', height }}>
      {show3d ? (
        <SceneBoundary fallback={posterEl}>
          <Suspense fallback={posterEl}>
            <Scene active={inView} reducedMotion={reducedMotion} label={label} onContextLost={() => setLost(true)} />
          </Suspense>
        </SceneBoundary>
      ) : posterEl}
    </div>
  )
}
```

**5. Use it.** Render `<SceneShell poster="/hero.webp" label="Rotating faceted sphere" />` from any page. Make the poster a screenshot of the scene at the same aspect ratio to avoid a visual jump. For Next.js, dynamic imports and `ssr: false` are alternatives that the R3F docs do not cover. `React.lazy` with `Suspense` is the pattern the upstream example app uses for its demos (`react-three-fiber:example/src/demos/index.tsx`).

## Behaviour

| State | Result |
|---|---|
| server render, first client render | poster only |
| WebGL missing, or not yet near the viewport | poster; the 3D chunk is not downloaded |
| in view, WebGL available | lazy chunk, then the canvas |
| scrolled away | canvas stays mounted, `frameloop="demand"` so it idles |
| reduced motion | canvas renders a static frame; no spin |
| renderer throws, or context lost | poster |

Note on `fallback`: if you pass `<Canvas fallback={...}>` it becomes the content inside the `<canvas>` element (`Canvas.tsx` calls it "similar to img's alt prop"). It does not replace the canvas when WebGL fails; the boundary above does that job.

## Verification checklist

- Responsive: 360 px, 768 px and 1440 px widths; no layout shift when the poster swaps for the canvas.
- Reduced motion: emulate `prefers-reduced-motion: reduce` in the browser devtools; the sphere stays still.
- No WebGL: disable WebGL in the browser or run with GPU acceleration off; the poster stays and no uncaught error appears (browsers may still log their own warning).
- Network: the scene chunk loads only after the section approaches the viewport.
- Idle: with the section scrolled away, the performance panel shows no rendering work.
- Console: no errors on mount, unmount or route changes; no warnings about too many WebGL contexts.
- Accessibility: poster has meaningful alt text; the canvas wrapper has `role="img"` and a label; no keyboard traps.
- Mobile: test on a real mid-range phone with the chosen `dpr` cap.

## Upstream references

`react-three-fiber:docs/API/canvas.mdx` (props, defaults, fallbacks, ownership), `react-three-fiber:packages/fiber/src/web/Canvas.tsx` (wrapper, measuring, error flow), `react-three-fiber:packages/fiber/src/core/root.tsx` (async renderer, teardown), `react-three-fiber:docs/advanced/scaling-performance.mdx` (on-demand rendering).

## Licence notes

The code above is original and covered by this repository's MIT licence. It calls the public API of React Three Fiber (MIT, Copyright (c) 2019-2025 Poimandres); keep that notice if you copy upstream code rather than only calling it.
