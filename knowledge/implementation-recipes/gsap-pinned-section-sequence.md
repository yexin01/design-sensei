---
title: "Recipe: GSAP pinned section sequence"
kind: recipe
summary: "Build a pinned, scroll-scrubbed section whose beats cross-fade on one timeline, with gsap.matchMedia branches for wide screens, compact screens and reduced motion, plus clean teardown."
source_ids: [gsap, lenis]
pattern_ids: [gsap-scrolltrigger-pin-scrub, gsap-match-media-reduced-motion]
updated: "2026-10-09"
---

# Recipe: GSAP pinned section sequence

## Goal

A stage that stays fixed in the viewport while several beats change, driven by scroll position and smoothed by `scrub`.
On narrow or touch screens and under reduced motion, the same content is an ordinary stacked section.

## When to use, and when not

Use for three to six steps that explain one process or product, on desktop-class screens. Do not use for content people
need to read at their own pace, for forms, or for anything long. Keep total pinned travel under about 6 viewport heights
(`knowledge/animations/scroll-storytelling.md`). Skip it when `motion_intensity` is below 5: the budget table in
`knowledge/animations/motion-principles-for-ui.md` allows no pinned sequences there.

## Prerequisites

- `gsap` 3.15.0 (`gsap:package.json`) with ScrollTrigger (`gsap/ScrollTrigger`). GSAP's licence is custom: see
  `knowledge/animations/gsap.md` and https://gsap.com/standard-license.
- The shared registration module `lib/gsap` from `gsap-text-reveal-and-stagger`, with ScrollTrigger registered.
- Optional Lenis smoothing. Lenis keeps native scroll, so pinning works unchanged once the sync from
  `lenis-gsap-scrolltrigger-sync` is in place (`lenis:README.md`).

## Steps

### 1. Markup and CSS: stacked by default, pinned only when script says so

```html
<section class="story" data-story aria-labelledby="story-title">
  <h2 id="story-title">How it works</h2>
  <div class="story__stage" data-stage>
    <ol class="story__beats">
      <li class="beat" data-beat><h3>Capture</h3><p>Short copy.</p></li>
      <li class="beat" data-beat><h3>Review</h3><p>Short copy.</p></li>
      <li class="beat" data-beat><h3>Ship</h3><p>Short copy.</p></li>
    </ol>
    <div class="story__visual" data-visual></div>
  </div>
</section>
```

```css
.story__stage { display: grid; gap: 3rem; }
.beat { max-width: 40ch; }

/* Added and removed by script, so CSS and JavaScript never disagree about the mode. */
.story.is-pinned .story__stage {
  min-height: 100svh;
  grid-template-columns: 1fr 1fr;
  align-items: center;
}
.story.is-pinned .story__beats { display: grid; }
.story.is-pinned .beat { grid-area: 1 / 1; } /* all beats share one cell and cross-fade */
```

### 2. Branch with `gsap.matchMedia`

```js
// story.js
import { gsap, ScrollTrigger } from './lib/gsap'

const HOLD = 1 // timeline units a beat stays readable
const SWAP = 0.5 // timeline units for a cross-fade

export function initStory(section) {
  const stage = section.querySelector('[data-stage]')
  const visual = section.querySelector('[data-visual]')
  const beats = gsap.utils.toArray('[data-beat]', section)
  if (!stage || beats.length < 2) return null

  const mm = gsap.matchMedia()

  mm.add(
    {
      motion: '(prefers-reduced-motion: no-preference)',
      pinned:
        '(min-width: 900px) and (min-height: 640px) and (pointer: fine) and (prefers-reduced-motion: no-preference)',
    },
    (ctx) => (ctx.conditions.pinned ? buildPinned(section, stage, visual, beats) : revealStacked(beats)),
  )

  document.fonts?.ready.then(() => ScrollTrigger.refresh())
  return mm
}
```

Nothing matches under `reduce`, so the callback never runs: the stacked layout stays, with all text visible. If the
visitor changes the preference or resizes across a breakpoint, `matchMedia` reverts the old branch, runs its cleanup
function and re-runs the callback (`gsap:types/gsap-core.d.ts`: `MatchMedia`, `Context`; behaviour in `gsap:src/gsap-core.js`).
Conditions also include a minimum height so a short window does not pin a stage that cannot fit.

### 3. The pinned branch

```js
function buildPinned(section, stage, visual, beats) {
  section.classList.add('is-pinned')

  const tl = gsap.timeline({
    defaults: { ease: 'none' }, // scroll distance maps linearly to progress
    scrollTrigger: {
      trigger: stage,
      start: 'top top',
      end: () => `+=${beats.length * 100}%`, // one viewport height per beat
      scrub: 0.6,
      pin: true,
      anticipatePin: 1,
      invalidateOnRefresh: true,
    },
  })

  tl.to({}, { duration: HOLD }) // the first beat is readable on arrival
  beats.slice(1).forEach((beat, k) => {
    const label = `beat-${k + 1}`
    tl.addLabel(label)
      .to(beats[k], { opacity: 0, yPercent: -8, duration: SWAP }, label)
      .fromTo(beat, { opacity: 0, yPercent: 8 }, { opacity: 1, yPercent: 0, duration: SWAP }, `${label}+=0.15`)
    if (visual) tl.to(visual, { scale: 1 + 0.06 * (k + 1), duration: SWAP }, label)
    tl.to({}, { duration: HOLD }) // hold: an empty tween that only takes time
  })

  return () => section.classList.remove('is-pinned')
}
```

What the options do, from `gsap:types/scroll-trigger.d.ts` and `gsap:src/ScrollTrigger.js`:

- `end: '+=100%'`-style values resolve against the scroller height, so `beats.length * 100` percent is one viewport per beat.
- `scrub: 0.6` is the length of a catch-up tween on the timeline's progress; `true` would lock it to the scrollbar.
- `pin: true` wraps the stage in a spacer element (class `pin-spacer`) that supplies the extra scroll length.
- `anticipatePin: 1` pins slightly early based on scroll velocity to reduce the jump on fast flicks.
- `invalidateOnRefresh: true` re-reads layout-dependent values when ScrollTrigger refreshes.
- Hidden beats use `opacity`, not `autoAlpha`: `autoAlpha` would set `visibility: hidden` and remove inactive beats from
  the accessibility tree. Keep interactive elements out of beats and keep DOM order equal to reading order.

### 4. The compact branch

```js
function revealStacked(beats) {
  gsap.set(beats, { autoAlpha: 0, y: 24 })
  ScrollTrigger.batch(beats, {
    start: 'top 85%',
    once: true,
    onEnter: (batch) =>
      gsap.to(batch, { autoAlpha: 1, y: 0, duration: 0.6, ease: 'power3.out', stagger: 0.1, overwrite: true }),
  })
}
```

Narrow and touch layouts get one-time reveals with no pin, which also avoids scrub-heavy work on phones. Under `reduce`
there is no motion at all.

### 5. Mount and tear down

```tsx
// React
'use client'
import { useEffect, useRef } from 'react'
import { initStory } from '@/lib/story'

export function Story({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLElement>(null)
  useEffect(() => {
    const mm = ref.current ? initStory(ref.current) : null
    return () => mm?.revert()
  }, [])
  return (
    <section ref={ref} className="story" data-story aria-labelledby="story-title">
      {children}
    </section>
  )
}
```

In plain JavaScript call `initStory(document.querySelector('[data-story]'))` after load and `mm.revert()` on teardown.
`revert()` restores inline styles, kills the ScrollTriggers, removes the pin spacer and calls the returned cleanup, so the
`is-pinned` class disappears too.

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Large blank gap after the section | Layout changed after pinning (fonts, images) | `ScrollTrigger.refresh()`; reserve media size. |
| Stage content clipped | Stage taller than the viewport | Add a `min-height` media condition, shorten copy, or fall back to stacked. |
| Pin jitters on fast scroll | Lenis not synced, or no `anticipatePin` | Use `lenis-gsap-scrolltrigger-sync`; keep `anticipatePin: 1`. |
| Beats unreadable by screen readers | `autoAlpha` used on beats | Use `opacity`. |
| Wrong breakpoints after rotation | Condition mismatch | Test portrait and landscape; adjust the pinned query. |
| Double scroll movement | ScrollTrigger `snap` plus Lenis snap | Use only one snapping mechanism per range. |

## Verification checklist

- [ ] Wide window, mouse, motion allowed: the stage pins, beats cross-fade in order, scrolling back reverses cleanly.
- [ ] No jump on pin or unpin; no blank gap below the section; markers (development only) match the visual start and end.
- [ ] Narrow window or a touch device: no pin, no `.pin-spacer` in the DOM, beats reveal once.
- [ ] `prefers-reduced-motion: reduce` emulated at both sizes: static stacked content, nothing hidden; live toggling switches modes without reload.
- [ ] Resize across 900 px and short heights: `is-pinned` toggles, `ScrollTrigger.getAll()` shows no stale triggers.
- [ ] Keyboard: Tab never focuses something invisible; Space and PageDown move through the sequence.
- [ ] Performance panel at 4x CPU throttle: no long tasks while scrubbing; only `transform` and `opacity` change.
- [ ] After `revert()`: original inline styles, no `pin-spacer`, trigger count 0.

## Upstream references

`gsap:types/scroll-trigger.d.ts`, `gsap:src/ScrollTrigger.js`, `gsap:types/gsap-core.d.ts`, `gsap:src/gsap-core.js`,
`gsap:types/timeline.d.ts`, `lenis:README.md`. Notes: `knowledge/animations/gsap.md`,
`knowledge/animations/scroll-storytelling.md`.

## Licence notes

The recipe calls the public API of the `gsap` npm package and contains original code only; no GSAP source is copied or
quoted. The licence is custom and `catalog/licenses.yaml` records the review as `needs_human_review`; read
https://gsap.com/standard-license before shipping. This is not legal advice.
