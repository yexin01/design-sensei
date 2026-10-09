---
title: "Recipe: Lenis and GSAP ScrollTrigger sync"
kind: recipe
summary: "Drive Lenis from GSAP's ticker, keep ScrollTrigger updated on every Lenis scroll event, register plugins safely, refresh after layout changes, handle reduced motion and teardown, in vanilla JavaScript and React."
source_ids: [lenis, gsap]
pattern_ids: [lenis-gsap-scrolltrigger-sync]
updated: "2026-10-09"
---

# Recipe: Lenis and GSAP ScrollTrigger sync

## Goal

One frame clock, one scroll position. Lenis smooths wheel input, ScrollTrigger reads the same position, and scrubbed or
pinned animations stay glued to the page with no jitter.

## When to use, and when not

Use it when scroll-linked GSAP animation (scrub, pin, scroll triggers) is combined with Lenis. ScrollTrigger alone needs
none of this, and Lenis alone does not need GSAP. If the project forbids new dependencies, drop both and use CSS plus
IntersectionObserver (`knowledge/animations/motion-principles-for-ui.md`).

## Prerequisites

- `lenis` 1.3.26 (`lenis:package.json`) and `gsap` 3.15.0 (`gsap:package.json`); ScrollTrigger ships inside the `gsap`
  package. `npm i lenis gsap`.
- GSAP has a custom licence. This recipe installs it from npm and never copies its code. Read
  `knowledge/animations/gsap.md` (Licence and handling) and https://gsap.com/standard-license first.
- Client-side code only: both libraries touch `window`.

## The approach, and why

The method below follows the README of Lenis (GSAP ScrollTrigger section) and its React, Vue and Nuxt examples.

| Piece | Reason | Evidence |
|---|---|---|
| `autoRaf: false` | GSAP's ticker is the single clock. Two drivers feed `raf` unrelated times. | `lenis:packages/core/src/lenis.ts` |
| `lenis.on('scroll', ScrollTrigger.update)` | ScrollTrigger re-reads the scroll position on Lenis' frame. `update` takes no meaningful argument. | `gsap:types/scroll-trigger.d.ts`, `gsap:src/ScrollTrigger.js` |
| `gsap.ticker.add(t => lenis.raf(t * 1000))` | Ticker time is in seconds, Lenis wants milliseconds. A ticker listener also keeps GSAP's ticker from auto-sleeping. | `gsap:types/gsap-core.d.ts`, `gsap:src/gsap-core.js` |
| `gsap.ticker.lagSmoothing(0)` | GSAP otherwise shortens long frames, so animation time slips against scroll. | `lenis:README.md` |
| No `scrollerProxy` | Lenis writes the real window scroll position. | `gsap:types/scroll-trigger.d.ts` |

## Steps

### 1. Register GSAP plugins in one shared client module

```ts
// lib/gsap.ts
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

if (typeof window !== 'undefined') gsap.registerPlugin(ScrollTrigger)

export { gsap, ScrollTrigger }
```

Registering at module scope matters in React: child effects run before parent effects, so a registration inside a parent
`useEffect` would come too late. `registerPlugin` is safe to repeat.

### 2. The engine (vanilla JavaScript)

```js
// scroll-engine.js
import Lenis from 'lenis'
import 'lenis/dist/lenis.css'
import { gsap, ScrollTrigger } from './lib/gsap'

let engine = null

export function startScrollEngine(options = {}) {
  if (engine) return engine

  const lenis = new Lenis({ autoRaf: false, anchors: true, ...options })

  const offScroll = lenis.on('scroll', ScrollTrigger.update)

  const tick = (seconds) => lenis.raf(seconds * 1000)
  gsap.ticker.add(tick)
  gsap.ticker.lagSmoothing(0)

  engine = {
    lenis,
    refresh() {
      lenis.resize()
      ScrollTrigger.refresh()
    },
    destroy() {
      offScroll()
      gsap.ticker.remove(tick)
      gsap.ticker.lagSmoothing(500, 33) // GSAP's own defaults, as read in gsap-core.js
      lenis.destroy()
      engine = null
    },
  }
  return engine
}
```

Reduced motion: Lenis keeps `respectReducedMotion: true` by default, so under `prefers-reduced-motion: reduce` it stops
smoothing and the sync stays valid. If you prefer no Lenis at all under `reduce`, skip constructing it and let
ScrollTrigger read native scroll; then none of the glue above is needed.

### 3. Build scroll animation inside `gsap.matchMedia`

```js
import { gsap } from './lib/gsap'
import { startScrollEngine } from './scroll-engine.js'

const engine = startScrollEngine()
const mm = gsap.matchMedia()

mm.add('(prefers-reduced-motion: no-preference)', () => {
  gsap.to('[data-parallax]', {
    yPercent: -12,
    ease: 'none',
    scrollTrigger: {
      trigger: '[data-parallax-section]',
      start: 'top bottom',
      end: 'bottom top',
      scrub: 0.5,
    },
  })
})

document.fonts.ready.then(() => engine.refresh())
```

Under `reduce` the callback never runs, so the content stays in its authored position. GSAP does not read the preference
itself, so this branch is yours to write. ScrollTrigger already refreshes on `load` and `resize`; call `engine.refresh()`
after fonts, lazy images or injected content change the layout.

### 4. React or Next.js

```tsx
'use client'

import { useEffect, useRef } from 'react'
import { ReactLenis, useLenis, type LenisRef } from 'lenis/react'
import { gsap, ScrollTrigger } from '@/lib/gsap'

export function ScrollEngine() {
  const lenisRef = useRef<LenisRef>(null)

  useEffect(() => {
    const tick = (seconds: number) => lenisRef.current?.lenis?.raf(seconds * 1000)
    gsap.ticker.add(tick)
    gsap.ticker.lagSmoothing(0)
    return () => {
      gsap.ticker.remove(tick)
      gsap.ticker.lagSmoothing(500, 33)
    }
  }, [])

  // Same function identity every render, so the hook registers once.
  useLenis(ScrollTrigger.update)

  return <ReactLenis root ref={lenisRef} options={{ autoRaf: false, anchors: true }} />
}
```

Mount `ScrollEngine` once in the root layout and import `lenis/dist/lenis.css` there. Components that animate use
`gsap.context` so route changes clean up:

```tsx
'use client'

import { useEffect, useRef } from 'react'
import { gsap } from '@/lib/gsap'

export function Reveal({ children }: { children: React.ReactNode }) {
  const root = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      const mm = gsap.matchMedia()
      mm.add('(prefers-reduced-motion: no-preference)', () => {
        gsap.from('[data-reveal]', {
          autoAlpha: 0,
          y: 24,
          duration: 0.7,
          ease: 'power3.out',
          stagger: 0.08,
          scrollTrigger: { trigger: root.current, start: 'top 80%', once: true },
        })
      })
    }, root)
    return () => ctx.revert()
  }, [])

  return <div ref={root}>{children}</div>
}
```

`ctx.revert()` also reverts the nested `matchMedia` and the ScrollTriggers created inside, and survives React Strict Mode's
double effect run. For Vue and Nuxt see the GSAP examples in `lenis:packages/vue/README.md` and
`lenis:playground/nuxt/app.vue`; the principle is identical.

### 5. Development drift check

```js
// development only
lenis.on('scroll', ({ animatedScroll }) => {
  const drift = Math.abs(animatedScroll - window.scrollY)
  if (drift > 1.5) console.warn('Lenis and native scroll differ by', drift)
})
```

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Pinned or scrubbed elements jitter | `autoRaf: true` plus the ticker, or `ScrollTrigger.update` not wired | One driver, wire the listener. |
| Start and end positions wrong after load | Fonts, images or injected content changed layout | `engine.refresh()` after they settle. |
| Anchors land off target | Triggers created after the anchor position was computed | Refresh, then scroll. |
| Animations stack after navigation | No `gsap.context` revert | Build inside a context; revert on unmount. |
| `window is not defined` | Constructed during server rendering | Create inside an effect or `onMounted`. |

## Verification checklist

- [ ] `lenis.options.autoRaf` is `false` and only the ticker calls `raf` (add a temporary counter if unsure).
- [ ] With `markers: true` on one trigger, markers stay fixed to the page while flicking and while scrollbar-dragging.
- [ ] A pinned section does not jitter at slow, medium and fast wheel speeds.
- [ ] Reload in the middle of the page; resize the window; rotate a device: positions recover.
- [ ] Rendering-panel emulation of `prefers-reduced-motion: reduce`: no scroll-linked motion, content visible.
- [ ] After a route change or unmount, `ScrollTrigger.getAll().length` is 0 and `destroy()` ran.
- [ ] Drift check stays quiet; Performance panel shows no long tasks from scroll callbacks.
- [ ] Remove `markers` before shipping.

## Upstream references

`lenis:README.md`, `lenis:packages/react/README.md`, `lenis:packages/vue/README.md`, `lenis:playground/nuxt/app.vue`,
`lenis:packages/core/src/lenis.ts`, `gsap:types/scroll-trigger.d.ts`, `gsap:types/gsap-core.d.ts`,
`gsap:src/ScrollTrigger.js`, `gsap:src/gsap-core.js`. Notes: `knowledge/animations/lenis.md`,
`knowledge/animations/gsap.md`, `knowledge/animations/scroll-storytelling.md`.

## Licence notes

Lenis is MIT (`lenis:LICENSE`). GSAP is under its own no-charge licence: the recipe uses the published npm package and
original glue code only; no GSAP source is copied or quoted. The approach itself is described in the Lenis README, which
is MIT licensed. Check the current GSAP terms before shipping, and see `catalog/licenses.yaml` for the project's review
status. This is not legal advice.
