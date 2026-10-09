---
title: "Recipe: Lenis smooth scroll setup"
kind: recipe
summary: "Install Lenis, load its CSS, start it in vanilla JavaScript or React with reduced-motion handling and cleanup, lock scroll for modals, keep nested scrollers working, and optionally add section snap."
source_ids: [lenis]
pattern_ids: [smooth-scroll-lenis, lenis-react-provider, lenis-scroll-snap, lenis-nested-scroll-and-modals]
updated: "2026-10-09"
---

# Recipe: Lenis smooth scroll setup

## Goal

Smooth wheel scrolling that keeps native scroll semantics (sticky, anchors, keyboard, scrollbars), respects reduced
motion, cleans up after itself, and does not break modals or nested scroll areas.

## When to use, and when not

Use it on marketing, portfolio and editorial pages where scroll feel is part of the brand. Skip it for app-like UIs with
many nested scroll panes, documentation, iframe-heavy pages, or when `allowed_dependencies` forbids a new package. If you
only need smooth jumps to anchors, CSS `scroll-behavior: smooth` is enough.

## Prerequisites

- `lenis` 1.3.26 (`lenis:package.json`): `npm i lenis`. No runtime dependencies.
- Browser APIs used by the library: `matchMedia`, `ResizeObserver`, `requestAnimationFrame`.
- React 17 or newer only for the `lenis/react` entry; it is an optional peer dependency. The build adds a `"use client"`
  banner to that entry (`lenis:tsdown.config.ts`), so Next.js App Router layouts can render it.
- Do not set `scroll-behavior: smooth` on `html` while Lenis is active.

## Steps

### 1. Load the stylesheet once

Import `lenis/dist/lenis.css` (README, "Recommended CSS"). It makes `html.lenis` and its body `height: auto`, turns
`lenis-stopped` into `overflow: clip`, applies `overscroll-behavior: contain` to `data-lenis-prevent*` elements, disables
iframe pointer events while smooth-scrolling, and supports `autoToggle`. Remove app CSS that locks `html` or `body` to
`height: 100%` with `overflow: hidden`; it fights the page-level scroll that Lenis drives.

### 2. Vanilla controller with reduced-motion handling and cleanup

```js
// smooth-scroll.js
import Lenis from 'lenis'
import 'lenis/dist/lenis.css'

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)')

export function startSmoothScroll(options = {}) {
  let lenis = null

  const create = () => {
    if (lenis) return
    lenis = new Lenis({ autoRaf: true, anchors: true, ...options })
  }
  const remove = () => {
    lenis?.destroy()
    lenis = null
  }
  const apply = () => (reduceMotion.matches ? remove() : create())

  apply()
  reduceMotion.addEventListener('change', apply)

  return {
    get lenis() {
      return lenis
    },
    destroy() {
      reduceMotion.removeEventListener('change', apply)
      remove()
    },
  }
}
```

This is policy B: no Lenis at all while the visitor prefers reduced motion, native scroll instead, and it follows
live preference changes. Policy A is to always construct Lenis: with `respectReducedMotion` left at its default `true`
it disables smoothing and makes `scrollTo` instant by itself (`lenis:README.md`, Reduced motion). Prefer B for
`reduced_motion: static_first`, A when other code (ScrollTrigger sync, WebGL) needs the instance to exist.

### 3. Programmatic scrolling and anchors

```js
const scroller = startSmoothScroll()

export function scrollToSelector(selector, offset = 0) {
  if (scroller.lenis) scroller.lenis.scrollTo(selector, { offset })
  else document.querySelector(selector)?.scrollIntoView({ block: 'start' })
}
```

With `anchors: true`, same-page `href="#pricing"` links scroll smoothly. Put `scroll-margin-top` on targets (or
`scroll-padding-top` on `html`); Lenis subtracts both (`lenis:packages/core/src/lenis.ts`). The handler does not call
`preventDefault`, so the URL hash still updates. Move keyboard focus to the target yourself if it matters.

### 4. Modals and nested scrollers

```js
let locked = false

export function lockScroll() {
  if (locked) return
  locked = true
  if (scroller.lenis) scroller.lenis.stop()
  else document.documentElement.style.overflow = 'hidden'
}

export function unlockScroll() {
  if (!locked) return
  locked = false
  if (scroller.lenis) scroller.lenis.start()
  else document.documentElement.style.removeProperty('overflow')
}
```

```html
<div class="dialog" role="dialog" aria-modal="true" aria-labelledby="dialog-title" hidden>
  <div class="dialog__panel" data-lenis-prevent>
    <h2 id="dialog-title">Title</h2>
    <div class="dialog__body">Long content</div>
  </div>
</div>
```

`stop()` adds `lenis-stopped`, which the stylesheet turns into `overflow: clip`, and Lenis cancels wheel and touch
defaults. That would also block the dialog's own scrolling, so the scrollable panel carries `data-lenis-prevent`; the
nested-scroll check runs before the stopped check. Give the panel `max-height` with `overflow: auto`. Other nested
scrollers use the same attribute, or `allowNestedScroll: true` for automatic detection at a per-event DOM cost. This step
covers scroll only: focus trapping and Escape handling belong to `<dialog>` or your modal library. If the reduced-motion
preference can flip while a modal is open, re-apply the lock in `apply`.

### 5. React or Next.js

```tsx
// components/smooth-scroll.tsx
'use client'

import { useEffect, useState } from 'react'
import { ReactLenis } from 'lenis/react'

const QUERY = '(prefers-reduced-motion: reduce)'

function useReducedMotion() {
  const [reduced, setReduced] = useState(
    () => typeof window !== 'undefined' && window.matchMedia(QUERY).matches,
  )
  useEffect(() => {
    const query = window.matchMedia(QUERY)
    const update = () => setReduced(query.matches)
    update()
    query.addEventListener('change', update)
    return () => query.removeEventListener('change', update)
  }, [])
  return reduced
}

export function SmoothScroll() {
  const reduced = useReducedMotion()
  if (reduced) return null
  return <ReactLenis root options={{ autoRaf: true, anchors: true }} />
}
```

```tsx
// app/layout.tsx (a Server Component is fine)
import 'lenis/dist/lenis.css'
import { SmoothScroll } from '@/components/smooth-scroll'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <SmoothScroll />
        {children}
      </body>
    </html>
  )
}
```

`root` makes Lenis drive `<html>` and publishes the instance so `useLenis` works anywhere; with no children the component
renders nothing (`lenis:packages/react/src/provider.tsx`). Consume it:

```tsx
'use client'

import { useCallback, useEffect, useRef } from 'react'
import type Lenis from 'lenis'
import { useLenis } from 'lenis/react'

export function ScrollProgress() {
  const bar = useRef<HTMLDivElement>(null)
  // Stable identity: useLenis re-registers whenever the callback changes.
  const onScroll = useCallback((lenis: Lenis) => {
    bar.current?.style.setProperty('--progress', String(lenis.progress))
  }, [])
  useLenis(onScroll)
  return <div ref={bar} className="progress" aria-hidden="true" />
}

export function useScrollLock(locked: boolean) {
  const lenis = useLenis()
  useEffect(() => {
    if (!locked) return undefined
    if (lenis) {
      lenis.stop()
      return () => lenis.start()
    }
    const html = document.documentElement
    const previous = html.style.overflow
    html.style.overflow = 'hidden'
    return () => {
      html.style.overflow = previous
    }
  }, [locked, lenis])
}
```

Style the bar with `transform: scaleX(var(--progress, 0))` and `transform-origin: left`; writing a CSS variable avoids a
React render per frame. Function-valued options (`easing`, `prevent`) do not trigger instance recreation when they
change, because the wrapper compares options through JSON (`lenis:packages/react/src/provider.tsx`); define them once.

### 6. Optional: section snap

```js
import Snap from 'lenis/snap'

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)')

export function addSectionSnap(lenis, sections) {
  if (!lenis || reduceMotion.matches) return () => {}
  const snap = new Snap(lenis, {
    type: 'proximity',
    distanceThreshold: '30%',
    debounce: 300,
    duration: 0.9,
  })
  snap.addElements([...sections], { align: ['start'] })
  return () => snap.destroy()
}
```

Use `align: ['start', 'end']` for sections taller than the viewport so their content can be read. Snap reacts to Lenis
`virtual-scroll` events, so only wheel and touch input triggers it; keyboard scrolling is not snapped. Tear down with
`snap.destroy()` only: the unsubscribe function from `addElements` does not disconnect the elements' ResizeObservers
(`lenis:packages/snap/src/snap.ts`, `lenis:packages/snap/src/element.ts`). Skipping Snap under reduced motion is the
alternative defined here.

### 7. Teardown

Call `scroller.destroy()` (or unmount `SmoothScroll`) on route-level unmounts and hot-module disposal. `destroy()` removes
listeners, observers, the rAF loop and all `lenis*` classes from the root.

## Verification checklist

- [ ] Console is clean and a production build has no `window is not defined` error.
- [ ] `html` carries the `lenis` class after load and `lenis-smooth` while wheel-scrolling.
- [ ] Wheel scrolling is eased; Space, PageDown, Home, End and Tab to an off-screen link still scroll the page.
- [ ] Hash links scroll smoothly and clear a fixed header (`scroll-margin-top`).
- [ ] Rendering-panel emulation of `prefers-reduced-motion: reduce`: no smoothing, no stuck state; toggling it live works.
- [ ] Modal open: the page behind does not move and the panel scrolls; close: page scrolls again.
- [ ] A nested scroller scrolls on wheel without moving the page.
- [ ] Touch devices keep native momentum scrolling (`syncTouch` stays off unless you measured a need).
- [ ] Navigating or unmounting leaves no duplicate instance: `lenis` classes do not stack on `html`.
- [ ] Performance panel while scrolling: no long tasks from `scroll` listeners.
- [ ] Safari check: README documents a 60 fps cap and, on pre-M1 Macs, lag on `position: fixed` elements.

## Upstream references

`lenis:README.md`, `lenis:packages/core/src/lenis.ts`, `lenis:packages/core/lenis.css`, `lenis:packages/react/README.md`,
`lenis:packages/react/src/provider.tsx`, `lenis:packages/react/src/use-lenis.ts`, `lenis:packages/snap/README.md`,
`lenis:playground/core/test.ts`, `lenis:playground/react/app.tsx`. Overview note: `knowledge/animations/lenis.md`.

## Licence notes

Lenis is MIT licensed (`lenis:LICENSE`, copyright darkroom.engineering). The code above is original and only calls the
package's public API. Install Lenis from npm; if you ever copy upstream code, keep the licence notice.
