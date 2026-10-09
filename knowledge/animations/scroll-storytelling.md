---
title: "Scroll storytelling with Lenis and ScrollTrigger"
kind: guide
summary: "Original design guidance for scroll-led storytelling: beats and pacing, trigger versus scrub, pinning rules, mobile and reduced-motion strategy, performance and a test protocol, plus the verified Lenis to ScrollTrigger sync approach."
source_ids: [lenis, gsap]
pattern_ids: [lenis-gsap-scrolltrigger-sync, gsap-scrolltrigger-pin-scrub]
updated: "2026-10-09"
---

# Scroll storytelling with Lenis and ScrollTrigger

Scroll storytelling uses scroll position as the timeline of a narrative: the visitor moves, the story advances. Done well
it paces information. Done badly it hijacks the page. The numbers below are Design Sensei heuristics, not measurements:
tune them by testing. Library facts are cited to the cloned sources.

## When it fits and when it does not

- Fits: a linear story with few ideas, where order matters: product walkthrough, case study, launch page, editorial feature.
- Does not fit: documentation, pricing and comparison tables, forms and checkout, search-landing pages where the visitor
  wants one answer, and long reads where reading speed is slower than scroll speed.
- Hard rule: the story must survive with all motion removed, with the same content in the same order and readable.
- Dependencies cost budget. If the project's `allowed_dependencies` is `none` or `existing`, build reveals with CSS and
  IntersectionObserver instead and skip pinned sequences.

## How the two libraries fit together

```
real scroll position  <- Lenis writes it for smoothed wheel input; the browser writes it for touch, keys, scrollbar
        |
        +-> ScrollTrigger reads it -> scrubbed timelines, one-shot triggers, pins
```

Lenis keeps native scroll, so ScrollTrigger needs no `scrollerProxy`. The upstream approach, shown in
`lenis:README.md` (GSAP ScrollTrigger section), `lenis:packages/react/README.md`, `lenis:packages/vue/README.md` and
`lenis:playground/nuxt/app.vue`, has four parts:

1. Lenis runs with `autoRaf` off (`lenis:packages/core/src/lenis.ts`: `autoRaf` starts its own loop, `raf` is the manual path).
2. A `scroll` listener on Lenis calls `ScrollTrigger.update`. That static ignores `this` and arguments other than
   `true` (`gsap:src/ScrollTrigger.js`, `gsap:types/scroll-trigger.d.ts`).
3. GSAP's ticker drives Lenis: `lenis.raf(seconds * 1000)`. The ticker passes seconds and Lenis wants milliseconds.
4. `gsap.ticker.lagSmoothing(0)` stops GSAP from shortening long frames, which would put timelines out of step with scroll.

Reasoning, not measured here: Lenis writes the scroll position inside a frame callback, and the browser delivers the
matching native `scroll` event on a later frame. Calling `ScrollTrigger.update` from Lenis' own event keeps ScrollTrigger
on the same frame. ScrollTrigger also listens for document scroll and window wheel events itself
(`gsap:src/ScrollTrigger.js`), and a `ticker.add` listener keeps GSAP's ticker awake (`gsap:src/gsap-core.js`).
`lenis:V2-ROADMAP.md` lists, as planned housekeeping, a check whether the ScrollTrigger integration is still needed, so
re-read the README when you upgrade. Implementation: recipe `lenis-gsap-scrolltrigger-sync`.

## Pacing: design the story as beats

A beat is one idea, one visual change and one or two sentences. Budget scroll distance per beat in viewport heights (vh).

| Beat type | Scroll length | Motion | Notes |
|---|---|---|---|
| Statement (headline plus line) | 0.8 to 1.2 vh | one-shot trigger | No scrub; let the text sit still. |
| Evidence (stat, quote, logos) | 0.6 to 1.0 vh | one-shot trigger with stagger | Counters only when the number matters. |
| Demonstration (UI or product steps) | 0.5 to 1.0 vh per step plus a hold | pinned scrub | Desktop only; needs a stacked fallback. |
| Breather | 0.3 to 0.6 vh | none or very slow parallax | Rest every three beats or so. |
| Call to action | about 1 vh | one-shot trigger | Never pinned; repeat it near the end. |

- Total pinned travel on one page: keep it under about 6 vh at `motion_intensity` 5 to 7. Visitors leave long sequences.
- The first beat must deliver value above the fold without scrolling.
- Alternate dense and light beats. Escape hatches matter: working anchors, a reachable footer, no scroll locking.

## Trigger or scrub

| Mechanism | Use for | Why | Risk |
|---|---|---|---|
| One-shot trigger (`once: true`) | entrances, reveals, counters | Finishes even if the visitor stops; independent of scroll speed. | After a jump or reload the state must still be coherent. |
| Toggle (`toggleActions`, `toggleClass`) | header themes, active nav, reversible states | Cheap and reversible. | Flicker near the boundary if start and end are too close. |
| Scrub | a continuous quantity the visitor controls: progress, zoom, a line drawing itself, before and after | Direct-manipulation feel. | Every scroll position must be legible. |
| Pinned scrub | demonstrations | Holds a stage while steps change. | Highest vestibular and layout risk; needs a fallback. |

- Use linear easing inside scrubbed timelines so scroll distance maps to progress; shape pacing with durations and holds.
- A numeric `scrub` value (seconds) adds smoothing; 0.3 to 1 is a sensible range. `true` locks to the scrollbar.
- Never scrub text that must be read mid-motion. Scrub transforms and opacity, not layout properties.

## Pinning rules

- Pin one thing at a time; do not nest pins.
- The pinned stage must fit the smallest supported viewport height (use `svh` units), or content clips while pinned.
- Give about one viewport of travel per beat plus a hold: `end: "+=100%"` per beat is a start.
- Set `invalidateOnRefresh: true` when values depend on layout, and `anticipatePin: 1` to hide the lag on fast flicks
  (the code pins slightly early based on scroll velocity).
- Keep interactive elements out of cross-fading beats and keep DOM order equal to reading order.
- Use `opacity`, not `autoAlpha`, for stacked beats: `autoAlpha` also sets `visibility`, which hides inactive beats from
  screen readers. Content that is merely transparent stays in the accessibility tree.
- Do not enable both ScrollTrigger `snap` and Lenis `lenis/snap` over the same range. Both move the scroll position and
  their interaction is not verified here.
- Create triggers before wiring anchors, then refresh, so `lenis.scrollTo` measures with pin spacers in place.

## Mobile strategy

- Native touch scrolling is the baseline: Lenis leaves touch alone unless `syncTouch` is on. The README lists
  instability on iOS before 16 and Safari frame-rate caps, so enable `syncTouch` only for a measured reason.
- Branch with `gsap.matchMedia()`: pinned sequences only for wide screens with a fine pointer (for example
  `(min-width: 900px) and (pointer: fine)`); below that, stacked sections with one-shot reveals.
- ScrollTrigger measures a helper element sized 100vh rather than `innerHeight` and ignores address-bar resizes on
  touch-only devices by default (`gsap:src/ScrollTrigger.js`). Still test with the address bar collapsing.
- Apply a lower budget on phones (intensity minus 2), lighter media, fewer simultaneous tweens. Test on a mid-range
  device; DevTools throttling only approximates it.

## Reduced motion

- Lenis honours `prefers-reduced-motion` by default (`lenis:README.md`, Reduced motion). Or do not create it at all under
  `reduce` (see `lenis-smooth-scroll-setup`).
- Wrap every scroll-linked or large-travel animation in `gsap.matchMedia()` with `(prefers-reduced-motion: no-preference)`.
  GSAP does not read the preference itself (`gsap-core`, `ScrollTrigger`, `ScrollSmoother`, `Flip` sources contain no check).
- Default CSS shows the final content. Hidden initial states belong to the motion branch, so reduced-motion and
  no-script visitors see everything.
- Replace pinned sequences with stacked sections; at most a one-time opacity fade of 200 ms or less. Keep hover and focus feedback.

## Performance

- Animate `transform` and `opacity`. Avoid scrubbing `filter`, `box-shadow`, `width`, `height`, `top`, `left` on large areas.
- One ScrollTrigger per section; use `ScrollTrigger.batch` for lists; do not create hundreds of individual triggers.
- Reserve image and video space (width, height or aspect ratio) so refreshes are rare. After dynamic content changes call
  `lenis.resize()` and then `ScrollTrigger.refresh()`. ScrollTrigger already refreshes on `load` and `resize`.
- Keep `scroll` and `onUpdate` callbacks free of layout reads and framework state updates; write CSS variables instead.
- Both libraries cost something while idle: Lenis registers non-passive wheel and touch listeners
  (`lenis:packages/core/src/virtual-scroll.ts`) and ScrollTrigger runs a 250 ms sync interval. Load them only on pages that use them.
- Remove `markers` and dev overlays from production. Check `performance_budget` keys (`initial_js_kb`, `lcp_ms`, `cls`).

## Test protocol

| Check | How | Pass |
|---|---|---|
| Speed sweep | Slow wheel, fast flick, scrollbar drag | No popping or jitter; correct end states. |
| Jumps | Anchor links, Home and End, reload mid-story, back and forward | State is coherent wherever you land. |
| Resize and rotate | Drag the window, toggle device mode | Triggers refresh; matchMedia rebuilds without leftovers. |
| Keyboard | Tab, Space, PageDown | Focus never lands on something invisible. |
| Reduced motion | DevTools Rendering panel emulation, toggled live | Complete static story; live toggle reverts. |
| No script | Disable JavaScript | All content visible, in order. |
| Performance | 4x CPU throttle, Performance panel | No long tasks or layout thrash during scroll. |
| Teardown | Route change in a single-page app | `ScrollTrigger.getAll().length` returns 0; ticker callback removed; `lenis.destroy()` called. |
| Sync drift | Log `lenis.animatedScroll` against `window.scrollY` in development | Difference stays within about a pixel. |

## Symptoms and likely causes

| Symptom | Likely cause | Fix |
|---|---|---|
| Pinned stage jitters | Two `raf` drivers, or `ScrollTrigger.update` not wired | One clock; wire the scroll listener. |
| Triggers fire at wrong positions after load | Fonts or images changed layout | `ScrollTrigger.refresh()` after they settle. |
| Scroll feels late | GSAP lag smoothing on, or heavy `onUpdate` | `lagSmoothing(0)`; slim the callbacks. |
| Anchor lands off target | Pin spacers created after the anchor was computed | Refresh first, then scroll. |
| Double smoothing | CSS `scroll-behavior: smooth` plus Lenis | Remove the CSS. |
| Content invisible without script | Stylesheet hides it | Move the hidden state into the motion branch. |
| Leaks after navigation | Triggers not reverted | Build inside `gsap.context` and revert on teardown. |

## Config mapping

`motion_intensity` budgets (maximum pinned sequences, beats and scrubbed effects) are in `motion-principles-for-ui`.
In short: levels 1 to 3 use no scroll-linked motion, level 4 one passive indicator, level 5 light scrubbed accents and at
most one three-beat pinned sequence, levels 6 to 8 one to three pinned sequences on desktop, levels 9 to 10 more with full
fallbacks. `reduced_motion: static_first` means build the stacked, static page first and add the motion branch on top.

## Related

Patterns `lenis-gsap-scrolltrigger-sync` and `gsap-scrolltrigger-pin-scrub`. Recipes `lenis-gsap-scrolltrigger-sync` and
`gsap-pinned-section-sequence`. Notes `lenis` and `gsap` in `knowledge/animations/`.
