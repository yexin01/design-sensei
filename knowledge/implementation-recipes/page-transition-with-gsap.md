---
title: "Recipe: Page transition with GSAP"
kind: recipe
summary: "Original curtain transition for a fetch-and-swap router: GSAP cover and reveal timelines, per-page gsap.context cleanup, Lenis stop and reset, focus and title announcement, and an instant swap under reduced motion."
source_ids: [gsap, lenis]
pattern_ids: [page-transition-gsap]
updated: "2026-10-09"
---

# Recipe: Page transition with GSAP

## Goal

Internal links cover the page with a curtain, swap the content while it is covered, then reveal the new page. Scroll resets,
focus moves, the title updates, per-page animation is torn down and rebuilt, and visitors who prefer reduced motion get an
instant swap. The design is original; GSAP supplies the timing.

## When to use, and when not

Use it on small multi-page marketing or portfolio sites where all pages share one stylesheet and one layout shell. Do not use
it for apps whose pages depend on inline scripts, per-page `<head>` assets, forms with redirects or authentication
flows. Frameworks with their own router (Next.js, Nuxt, Astro) should keep the transition module and page lifecycle but
let the framework swap content; how to intercept exits in each router is not covered by the cloned sources and is not
verified here. The browser's native cross-document view transitions are an alternative worth evaluating; they are also
not covered here, so check support before relying on them.

## Prerequisites

- `gsap` 3.15.0 (`gsap:package.json`). Custom licence: see `knowledge/animations/gsap.md` and https://gsap.com/standard-license.
- Optional `lenis` 1.3.26 (`lenis:package.json`) for the scroll reset. Without it the code uses `window.scrollTo`.
- The shared `lib/gsap` registration module (see `gsap-text-reveal-and-stagger`) and a page helper that builds animations,
  such as its `revealCards`.
- Server-rendered pages that each contain the same outlet element, for example `<main id="main">`.

## Steps

### 1. Markup and CSS

```html
<div class="curtain" aria-hidden="true"></div>
<div id="route-announcer" class="visually-hidden" aria-live="polite"></div>
<main id="main" tabindex="-1" data-page="home">...</main>
```

```css
.curtain {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: var(--curtain-color, #111);
  pointer-events: none;
  visibility: hidden; /* GSAP reveals it, parked below the viewport, once script runs */
}
#main:focus { outline: none; } /* focus is moved here by script, not by the visitor */
.visually-hidden {
  position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap;
}
```

The curtain deliberately has no CSS `transform`. GSAP reads existing transforms and would add them to its own, so the
parked offset is set only by GSAP (`yPercent`). Without script the curtain stays hidden and links navigate normally.

### 2. Transition module (cover and reveal)

```js
// transition.js
import { gsap } from './lib/gsap'

const reduceQuery = window.matchMedia('(prefers-reduced-motion: reduce)')

export function createTransition(curtain) {
  const park = () => gsap.set(curtain, { yPercent: 100, autoAlpha: 1 })
  park()

  return {
    async leave() {
      if (reduceQuery.matches) return // instant swap: no curtain at all
      await gsap.fromTo(curtain, { yPercent: 100 }, { yPercent: 0, duration: 0.3, ease: 'power3.inOut' })
    },
    async enter() {
      if (reduceQuery.matches) return
      await gsap.to(curtain, { yPercent: -100, duration: 0.3, ease: 'power3.inOut' })
      park()
    },
  }
}
```

Awaiting a tween works because GSAP animations expose `then` (`gsap:types/animation.d.ts`); it resolves when the tween
finishes. Total motion is 0.6 s, which fits `motion_intensity` 7 in the budget table (600 ms); scale both phases down for
lower levels, for example 0.2 s each at level 5 (400 ms). The preference is read at call time, so a change applies to the next link.

### 3. Page lifecycle with `gsap.context`

```js
// pages.js
import { gsap } from './lib/gsap'
import { revealCards } from './reveal-cards.js'

let ctx = null

export const page = {
  mount(root) {
    ctx = gsap.context(() => {
      revealCards(root) // matchMedia and ScrollTriggers created here are recorded by the context
    }, root)
  },
  unmount() {
    ctx?.revert()
    ctx = null
  },
}
```

`ctx.revert()` restores inline styles, kills the ScrollTriggers and tears down nested `matchMedia` objects created inside
(`gsap:types/gsap-core.d.ts`, `gsap:src/gsap-core.js`). Without it every navigation would stack triggers.

### 4. Router: intercept, fetch, swap

```js
// router.js
import { ScrollTrigger } from './lib/gsap'

export function startRouter({ transition, page, getLenis = () => null, outlet = '#main' }) {
  const announcer = document.getElementById('route-announcer')
  let busy = false
  let current = new URL(location.href)

  history.scrollRestoration = 'manual'
  page.mount(document.querySelector(outlet))

  async function load(url) {
    const response = await fetch(url, { headers: { Accept: 'text/html' } })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    return new DOMParser().parseFromString(await response.text(), 'text/html')
  }

  function resetScroll() {
    const lenis = getLenis()
    if (lenis) lenis.scrollTo(0, { immediate: true, force: true })
    else window.scrollTo(0, 0)
  }

  async function go(url, { push = true } = {}) {
    if (busy) return
    busy = true
    getLenis()?.stop()

    try {
      const [next] = await Promise.all([load(url), transition.leave()])
      const incoming = next.querySelector(outlet)
      if (!incoming) throw new Error('Outlet missing in response')

      page.unmount()
      document.querySelector(outlet).replaceWith(incoming)
      document.title = next.title
      if (push) history.pushState({}, '', url)
      current = new URL(url, location.href)

      resetScroll()
      page.mount(incoming)
      requestAnimationFrame(() => ScrollTrigger.refresh())

      incoming.setAttribute('tabindex', '-1')
      incoming.focus({ preventScroll: true })
      if (announcer) announcer.textContent = next.title

      await transition.enter()
    } catch {
      window.location.assign(url) // anything unexpected: fall back to a normal navigation
    } finally {
      busy = false
      getLenis()?.start()
    }
  }

  document.addEventListener('click', (event) => {
    if (event.defaultPrevented || event.button !== 0) return
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
    const link = event.target.closest('a[href]')
    if (!link || link.target || link.hasAttribute('download') || 'noTransition' in link.dataset) return
    const url = new URL(link.href, location.href)
    if (url.origin !== location.origin) return
    if (url.pathname === current.pathname && url.search === current.search) return // same page or hash only
    event.preventDefault()
    go(url.href)
  })

  window.addEventListener('popstate', () => {
    const next = new URL(location.href)
    if (next.pathname === current.pathname && next.search === current.search) {
      current = next // hash-only change: let the browser and Lenis handle it
      return
    }
    go(next.href, { push: false })
  })
}
```

Wire it up once, after load: `const scroller = startSmoothScroll()` from `lenis-smooth-scroll-setup`, then
`startRouter({ transition: createTransition(document.querySelector('.curtain')), page, getLenis: () => scroller.lenis })`.

Notes on the Lenis calls (`lenis:packages/core/src/lenis.ts`): `stop()` freezes input during the transition; `scrollTo` is
ignored while stopped unless `force: true`; `immediate: true` jumps without animation and clears inertia. Hash-only
links are left to the browser and, if enabled, Lenis' `anchors` option.

### 5. Limits you must handle

- Scripts in the fetched HTML do not run (`DOMParser` leaves them inert). Page-specific code belongs in `page.mount`.
- Only the title is synchronised from the new `<head>`. Keep one global stylesheet or extend the swap.
- Send analytics page views yourself after each swap.
- The curtain colour should come from the design tokens and keep contrast with both pages' content edges.

## Verification checklist

- [ ] Clicking an internal link covers, swaps, reveals; the URL and title update; Back and Forward work.
- [ ] Modifier clicks, middle clicks, `target`, `download`, external and hash-only links behave natively.
- [ ] Reduced motion emulated: instant swap, no curtain, still scrolled to the top with focus on `main`.
- [ ] A screen reader announces the new title; keyboard focus lands on `main`; Tab continues from there.
- [ ] Scroll resets to the top, Lenis resumes with no leftover momentum, and wheel scrolling works again once the transition ends.
- [ ] `ScrollTrigger.getAll().length` matches the new page's own triggers after every navigation (it must not grow).
- [ ] Double-clicking a link does not navigate twice; a failed fetch falls back to a normal page load.
- [ ] No layout shift when content swaps; the whole transition stays inside the project's motion budget.

## Upstream references

`gsap:types/gsap-core.d.ts` (`context`, `matchMedia`, `set`, `to`, `fromTo`), `gsap:types/animation.d.ts` (`then`),
`gsap:src/gsap-core.js`, `lenis:packages/core/src/lenis.ts` (`stop`, `start`, `scrollTo`), `lenis:README.md`.
Notes: `knowledge/animations/gsap.md`, `knowledge/animations/lenis.md`, `knowledge/animations/motion-principles-for-ui.md`.

## Licence notes

Original code that calls the public API of the `gsap` npm package (custom licence; `catalog/licenses.yaml` status
`needs_human_review`) and, optionally, of `lenis` (MIT). Nothing from either source is copied or quoted. Read
https://gsap.com/standard-license before shipping. This is not legal advice.
