---
title: "Budget and fall back for heavy React Bits backgrounds"
kind: recipe
summary: "Ship GPU-driven React Bits backgrounds (WebGL, WebGPU) safely: choose by cost, mount lazily, pause offscreen, cap resolution, gate on reduced motion, touch, data-saver and GPU support, and always render a static layer underneath."
source_ids: [react-bits]
pattern_ids:
  - react-bits-ogl-shader-backgrounds
  - react-bits-self-pausing-shader-backgrounds
  - react-bits-three-r3f-backgrounds
  - react-bits-webgpu-backgrounds
  - react-bits-canvas-grid-backgrounds
  - react-bits-webgl-cursor-trails
  - react-bits-3d-image-galleries
  - react-bits-glass-surfaces
updated: "2026-10-09"
---

# Budget and fall back for heavy React Bits backgrounds

## Goal

Use a shader or WebGL React Bits component as a hero or section backdrop without wrecking load time, battery, accessibility or the page when WebGL is missing. The result is a small wrapper that decides whether the effect may run, loads it only near the viewport, releases it when it is far away, and shows a designed static layer in every other case.

## When to use

- Any row marked WebGL or WebGPU in `knowledge/components/react-bits-catalog.md`: the 53 GPU-driven backgrounds, plus GPU cursor trails, 3D galleries and glass components.
- You want a background on a marketing page and cannot test on low-end phones.
- Do not use it for DOM-only components (text, menus, cards); `knowledge/implementation-recipes/react-bits-choose-variant-and-install.md` covers their reduced-motion gate.
- Do not add a GPU background behind dense reading text or inside a modal that mounts and unmounts constantly.

## What the source gives you (and what it does not)

A regular-expression scan of the 53 GPU-driven backgrounds (TS + Tailwind files, approximate):

| Engine (count) | Offscreen pause (IntersectionObserver) | Reduced motion | DPR cap | `paused` prop |
|---|---|---|---|---|
| OGL (34) | 17 | 4 | 21 | 7 |
| three.js (10) | 5 | 1 | 9 | 1 |
| three via R3F (3: Beams, Silk, Dither) | 0 | 0 | 2 | 0 |
| raw WebGL (4) | 3 | 3 | 3 | 2 |
| WebGPU via vgpu (2) | 2 | 2 | 2 | 2 |

26 of the 53 neither observe visibility nor listen for tab changes, including `react-bits:src/ts-tailwind/Backgrounds/Aurora/Aurora.tsx`, `react-bits:src/ts-tailwind/Backgrounds/DarkVeil/DarkVeil.tsx`, `react-bits:src/ts-tailwind/Backgrounds/Beams/Beams.tsx` and `react-bits:src/ts-tailwind/Backgrounds/Silk/Silk.tsx` (the last two force an always-on frame loop). Most create their renderer with no user-facing failure path. Treat all of them as "always on, no fallback" unless the notes below say otherwise.

Components with real safeguards worth preferring when the look fits:

- `react-bits:src/ts-tailwind/Backgrounds/Plasma/Plasma.tsx`: props for internal render scale (default 0.55), max device pixel ratio (1.5), target frame rate (30) and iteration count; pauses offscreen and in hidden tabs; paints one static frame under reduced motion; handles context loss.
- `react-bits:src/ts-tailwind/Backgrounds/AeroShards/AeroShards.tsx` and `react-bits:src/ts-tailwind/Backgrounds/ShapeWaves/ShapeWaves.tsx`: WebGPU, `paused` and `onError` props, observer and tab gating, reduced-motion freeze; AeroShards also chooses a quality tier from device memory, core count and canvas width and lowers it when frames run long.
- `react-bits:src/ts-tailwind/Backgrounds/PatternWaves/PatternWaves.tsx`, `react-bits:src/ts-tailwind/Backgrounds/MicroSlats/MicroSlats.tsx`, `react-bits:src/ts-tailwind/Backgrounds/GhostFibers/GhostFibers.tsx`: observer and tab gating, reduced-motion handling, `paused` prop.
- `react-bits:src/ts-tailwind/Backgrounds/LightPillar/LightPillar.tsx`: low, medium and high tiers (lower iteration counts and pixel ratio on mobile user agents or four cores or fewer) and a visible unsupported-WebGL state. `react-bits:src/ts-tailwind/Backgrounds/DarkVeil/DarkVeil.tsx` has a resolution-scale prop and a pixel ratio cap of 2.
- Avoid or strip: `react-bits:src/ts-tailwind/Backgrounds/PixelBlast/PixelBlast.tsx` (its offscreen-pause flag is never updated), `react-bits:src/ts-tailwind/Backgrounds/GridScan/GridScan.tsx` (downloads face-detection weights from a public CDN even with the webcam off), `react-bits:src/ts-tailwind/Animations/SplashCursor/SplashCursor.tsx` (no cleanup).

Upstream's own advice (`react-bits:src/docs/Introduction.jsx`): at most two or three animated components per page, static placeholders instead of heavy effects on mobile, test beyond your own device. The docs site gates its previews the same way (`react-bits:src/hooks/usePreviewMediaAllowed.js`, `react-bits:src/utils/renderGate.js`).

## Budget rules (original guidance, adjust per project)

| Concern | Rule |
|---|---|
| Count | one live GPU canvas in view, two mounted at most |
| Resolution | cap pixel ratio at 1.5 for full-viewport raymarch or fluid shaders, 2 for the rest; use the component's own scale prop when it has one |
| Frame rate | 30 fps is enough for slow ambient motion where a target-fps prop exists |
| Offscreen and hidden tab | pause, or better unmount; do not rely on the component |
| Touch and narrow screens | static layer below 768 px or without a fine pointer (policy choice; AeroShards only lowers quality below 640 px) |
| Reduced motion, data-saver | static layer, no GPU work |
| No WebGL or WebGPU, or a thrown error | static layer |
| LCP | the static layer is the LCP candidate; load the effect after it |

## Steps

1. **Pick by cost.** Prefer a self-pausing component (Plasma, PatternWaves, MicroSlats, GhostFibers, AeroShards) for always-visible heroes. Use older single-file shaders only behind the slot below.
2. **Install** the component as in `knowledge/implementation-recipes/react-bits-choose-variant-and-install.md`.
3. **Add the effect-mode hook** (original code). It starts as `static` so nothing heavy runs before the client knows the device.

   ```ts
   'use client';

   import { useEffect, useState } from 'react';

   export type EffectMode = 'live' | 'static';

   export interface EffectModeOptions {
     /** Below this viewport width (px) the effect stays static. */
     minWidth?: number;
     /** Also require a mouse-like pointer (hover and fine). Use it for cursor effects. */
     requireFinePointer?: boolean;
   }

   type NetworkInfo = { saveData?: boolean; effectiveType?: string };

   const REDUCED = '(prefers-reduced-motion: reduce)';
   const FINE_POINTER = '(hover: hover) and (pointer: fine)';

   function decide(minWidth: number, requireFinePointer: boolean): EffectMode {
     const reduced = window.matchMedia(REDUCED).matches;
     const wide = window.matchMedia(`(min-width: ${minWidth}px)`).matches;
     const fine = window.matchMedia(FINE_POINTER).matches;
     const net = (navigator as Navigator & { connection?: NetworkInfo }).connection;
     const saver = Boolean(net?.saveData) || net?.effectiveType === 'slow-2g' || net?.effectiveType === '2g';
     if (reduced || saver || !wide) return 'static';
     if (requireFinePointer && !fine) return 'static';
     return 'live';
   }

   export function useEffectMode({ minWidth = 768, requireFinePointer = false }: EffectModeOptions = {}): EffectMode {
     // Static on the server and on the first client render: no hydration mismatch, no GPU work before we know.
     const [mode, setMode] = useState<EffectMode>('static');

     useEffect(() => {
       const update = () => setMode(decide(minWidth, requireFinePointer));
       const queries = [REDUCED, `(min-width: ${minWidth}px)`, FINE_POINTER].map((q) => window.matchMedia(q));
       update();
       queries.forEach((q) => q.addEventListener('change', update));
       return () => queries.forEach((q) => q.removeEventListener('change', update));
     }, [minWidth, requireFinePointer]);

     return mode;
   }
   ```

4. **Add the slot** (original code). It always renders the static layer, mounts the effect only when the mode is live, the GPU API exists and the slot is near the viewport, unmounts it again when it leaves (which frees the GL context), and falls back on any render-time error or an `onError` callback.

   ```tsx
   'use client';

   import { Component, Suspense, useEffect, useRef, useState, type ReactNode } from 'react';
   import { useEffectMode } from './use-effect-mode';

   /** True when a WebGL context can be created. The probe context is released immediately. */
   function canUseWebGL(): boolean {
     try {
       const canvas = document.createElement('canvas');
       const gl = canvas.getContext('webgl2') ?? canvas.getContext('webgl');
       gl?.getExtension('WEBGL_lose_context')?.loseContext();
       return gl != null;
     } catch {
       return false;
     }
   }

   class GpuBoundary extends Component<{ onFail: () => void; children: ReactNode }, { failed: boolean }> {
     state = { failed: false };
     static getDerivedStateFromError() {
       return { failed: true };
     }
     componentDidCatch() {
       this.props.onFail();
     }
     render() {
       return this.state.failed ? null : this.props.children;
     }
   }

   interface GpuSlotProps {
     /** Static layer that is always rendered underneath: CSS gradient, poster image. */
     fallback: ReactNode;
     /** Returns the lazy-loaded React Bits element. Call fail() from an onError callback if the component has one. */
     effect: (api: { fail: () => void }) => ReactNode;
     /** Which API the effect needs. WebGPU components such as AeroShards need 'webgpu'. */
     api?: 'webgl' | 'webgpu';
     /** Start loading this far before the slot scrolls into view. */
     rootMargin?: string;
     /** Unmount the effect again when the slot leaves the viewport, which frees its GPU memory. */
     releaseWhenFar?: boolean;
     /** Must size and position the slot, for example "absolute inset-0 -z-10". */
     className?: string;
   }

   export function GpuSlot({
     fallback,
     effect,
     api = 'webgl',
     rootMargin = '200px',
     releaseWhenFar = true,
     className = 'relative h-full w-full',
   }: GpuSlotProps) {
     const mode = useEffectMode();
     const hostRef = useRef<HTMLDivElement>(null);
     const [near, setNear] = useState(false);
     const [supported, setSupported] = useState(false);
     const [failed, setFailed] = useState(false);

     useEffect(() => {
       setSupported(api === 'webgpu' ? 'gpu' in navigator : canUseWebGL());
     }, [api]);

     useEffect(() => {
       const host = hostRef.current;
       if (!host || mode !== 'live') {
         setNear(false);
         return;
       }
       const observer = new IntersectionObserver(
         ([entry]) => setNear((prev) => (releaseWhenFar ? entry.isIntersecting : prev || entry.isIntersecting)),
         { rootMargin },
       );
       observer.observe(host);
       return () => observer.disconnect();
     }, [mode, rootMargin, releaseWhenFar]);

     const live = mode === 'live' && supported && near && !failed;
     const fail = () => setFailed(true);

     return (
       <div ref={hostRef} className={`overflow-hidden ${className}`} aria-hidden="true">
         <div className="absolute inset-0">{fallback}</div>
         {live && (
           <div className="absolute inset-0">
             <GpuBoundary onFail={fail}>
               <Suspense fallback={null}>{effect({ fail })}</Suspense>
             </GpuBoundary>
           </div>
         )}
       </div>
     );
   }
   ```

5. **Use it**, with the component lazy-loaded so its chunk (and `ogl`, `three` or `vgpu`) is fetched only when the slot goes live. Plasma's props below were read from its TS file; the static layer is a plain CSS gradient chosen to match the effect's palette.

   ```tsx
   'use client';

   import { lazy } from 'react';
   import { GpuSlot } from '@/lib/gpu-slot';

   const Plasma = lazy(() => import('@/components/Plasma'));
   const AeroShards = lazy(() => import('@/components/AeroShards'));

   const staticLayer = (
     <div
       className="h-full w-full"
       style={{ background: 'radial-gradient(60% 60% at 50% 0%, #4c1d95 0%, transparent 70%), #0b0b12' }}
     />
   );

   export function PlasmaBackdrop() {
     return (
       <GpuSlot
         className="absolute inset-0 -z-10"
         fallback={staticLayer}
         effect={() => (
           <Plasma color="#7c3aed" speed={0.5} mouseInteractive={false} renderScale={0.5} maxDpr={1.5} targetFps={30} />
         )}
       />
     );
   }

   export function ShardsBackdrop() {
     return (
       <GpuSlot
         api="webgpu"
         className="absolute inset-0 -z-10"
         fallback={staticLayer}
         effect={({ fail }) => <AeroShards backgroundColor="#0b0b12" onError={fail} />}
       />
     );
   }
   ```

   Put the slot in a `relative isolate overflow-hidden` section and the page content in a `relative z-10` sibling. Backgrounds fill 100 percent of their parent, so the parent needs a real height. In Next.js the file is already a client component; keep the lazy import inside it.

6. **Tune.** If frames still drop on a throttled CPU, lower the component's scale or quality prop, raise `minWidth`, or switch to the static layer for that route. For components without a resolution prop, wrap them in the slot and accept all-or-nothing.

## Verification checklist

- [ ] Reduced motion emulated in DevTools: no canvas element in the DOM, static layer visible.
- [ ] Scroll the hero out of view by more than the root margin: the canvas element disappears and the Performance panel shows no animation-frame callbacks from it.
- [ ] Narrow window (below 768 px) and touch emulation: static layer only.
- [ ] Force `canUseWebGL` to return false (or `'gpu' in navigator` to be false) in a dev build: the page still looks designed.
- [ ] Throw inside the effect once: the error boundary swaps in the static layer and the rest of the page survives.
- [ ] Performance panel with 4x CPU throttling: no long tasks from the effect during scroll; LCP is the static layer or real content, not the canvas.
- [ ] No more than two GPU canvases are mounted at once (Elements panel).

## Upstream references

- Backgrounds named above, all under `react-bits:src/ts-tailwind/Backgrounds/`, plus `react-bits:src/ts-tailwind/Animations/SplashCursor/SplashCursor.tsx`.
- Gating examples used by the docs site: `react-bits:src/hooks/usePreviewMediaAllowed.js`, `react-bits:src/utils/renderGate.js`.
- Upstream performance advice: `react-bits:src/docs/Introduction.jsx`.
- Counts and per-component facts: `knowledge/components/react-bits.md`.

## Licence notes

Install components with the upstream CLI into your own app; never copy them into a library, template or registry (`react-bits:LICENSE.md`, `knowledge/implementation-recipes/react-bits-license-safe-usage.md`). The slot and hook above are original and work with any lazy-loaded component. GSAP, three, ogl and vgpu are separate packages with their own licences.
