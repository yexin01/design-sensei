---
title: "Lenis smooth scroll"
kind: animation
summary: "What Lenis 1.3.26 is and how its scroll loop works, with constructor options, methods, events, anchors, modals, nested scroll, the React, Vue/Nuxt and snap packages, pitfalls and accessibility notes, all read from the cloned source."
source_ids: [lenis, gsap]
pattern_ids: [smooth-scroll-lenis, lenis-react-provider, lenis-vue-nuxt-module, lenis-scroll-snap, lenis-nested-scroll-and-modals, lenis-gsap-scrolltrigger-sync]
updated: "2026-10-09"
---

# Lenis smooth scroll

Lenis is a small smooth-scroll library from darkroom.engineering, MIT licensed, version 1.3.26 in `lenis:package.json`.
It does not replace the browser scroller. It intercepts wheel input (and touch input only if you opt in), animates a
target value, and writes the result back to the real scroll position. The page therefore keeps a genuine scroll offset,
so sticky positioning, scrollbars and libraries that read the scroll position (ScrollTrigger, WebGL rigs) keep working.
`lenis:MANIFESTO.md` says the library was built to synchronise WebGL and the DOM while scrolling and that smooth
scrolling was a side effect.

## How it works (read from `lenis:packages/core/src/lenis.ts`)

1. `VirtualScroll` (`lenis:packages/core/src/virtual-scroll.ts`) attaches non-passive `wheel`, `touchstart`, `touchmove`
   and `touchend` listeners and converts line and page wheel deltas to pixels.
2. `onVirtualScroll` filters each event: ignores ctrl-key (zoom) wheels, taps and unknown gestures, skips elements
   marked as nested scroll areas, blocks input while stopped or locked, and leaves touch native unless `syncTouch` is on.
   Otherwise it cancels the native event and calls `scrollTo(targetScroll + delta)`.
3. `Animate` (`lenis:packages/core/src/animate.ts`) advances every `raf(time)` call. With both `duration` and `easing`
   set it is time-based; otherwise it uses frame-rate-independent damping controlled by `lerp`.
4. Each step calls the wrapper's `scrollTo` with instant behaviour, so a CSS `scroll-behavior` value does not slow Lenis.
5. When no animation is running, native `scroll` events are read back. Keyboard, scrollbar drags and focus-driven
   scrolling therefore stay in sync. Velocity resets 400 ms after the last native event.
6. State is mirrored as classes on the root element: `lenis`, `lenis-smooth`, `lenis-scrolling`, `lenis-stopped`,
   `lenis-locked`, `lenis-autoToggle`.

## Packages and entry points

| Import | Provides | Source |
|---|---|---|
| `lenis` | default export `Lenis` class, option and event types | `lenis:packages/core/index.ts` |
| `lenis/dist/lenis.css` | recommended stylesheet, copied into `dist/` by the build | `lenis:packages/core/lenis.css` |
| `lenis/react` | `ReactLenis`, `useLenis`, `LenisContext`, types | `lenis:packages/react/index.ts` |
| `lenis/vue` | `VueLenis`, `useLenis`, plugin (default export) | `lenis:packages/vue/index.ts` |
| `lenis/nuxt` | Nuxt module | `lenis:packages/vue/nuxt/module.ts` |
| `lenis/snap` | `Snap` class | `lenis:packages/snap/index.ts` |
| `dist/lenis.min.js` | browser build, global `Lenis` | `lenis:packages/core/browser.ts` |

`dist/` is build output and is not in the checkout; the `exports` map in `lenis:package.json` and the build in
`lenis:tsdown.config.ts` define it. `react`, `vue` and `@nuxt/kit` are optional peer dependencies. The React bundle gets a
`"use client"` banner in the build config. A Framer adapter is linked from the README but is not part of this repository.

## Install

README commands: `npm i lenis` (or yarn or pnpm), then `import Lenis from 'lenis'` and `import 'lenis/dist/lenis.css'`.
Script-tag usage pins `unpkg.com/lenis@1.3.26/dist/lenis.min.js` plus `lenis.css`. Minimal use:

```js
const lenis = new Lenis({ autoRaf: true })
lenis.on('scroll', (instance) => { /* read instance.scroll, .velocity, .progress */ })
```

## Frame loop: `autoRaf` or manual `raf`

- `autoRaf: true` starts an internal `requestAnimationFrame` loop in the constructor; `destroy()` cancels it.
- The default is `false`: you must call `lenis.raf(timeInMilliseconds)` every frame. `raf` computes the delta from the
  previous call, so feed it one steady clock.
- Never run both. With GSAP, `autoRaf` stays off and `gsap.ticker` calls `raf(seconds * 1000)`; see
  `lenis-gsap-scrolltrigger-sync`. The README troubleshooting list and the React and Vue READMEs show the same split.
- Wrapper defaults differ: `ReactLenis` and `VueLenis` default their `autoRaf` prop to `true`, and `options.autoRaf` wins
  when set (`lenis:packages/react/src/provider.tsx`, `lenis:packages/vue/src/provider.ts`).

## Constructor options (defaults from the constructor in `lenis:packages/core/src/lenis.ts`)

| Option | Default | Notes |
|---|---|---|
| `wrapper`, `content` | `window`, `document.documentElement` | A custom wrapper needs its own overflow CSS; `content` is its direct child. |
| `eventsTarget` | `wrapper` | Where wheel and touch listeners attach. |
| `smoothWheel` | `true` | Wheel input is smoothed. |
| `syncTouch`, `syncTouchLerp`, `touchInertiaExponent` | `false`, `0.075`, `1.7` | Smooth touch. README: can be unstable on iOS before 16. |
| `lerp` | `0.1` | Damping per frame, used when no duration and easing apply. |
| `duration`, `easing` | unset | Providing either makes the animation time-based. A lone `duration` implies the default easing (an exponential ease-out); a lone `easing` implies `duration` 1. |
| `orientation`, `gestureOrientation` | `'vertical'`, and `'both'` when orientation is horizontal | Scroll axis and which gesture axis drives it. |
| `touchMultiplier`, `wheelMultiplier` | `1`, `1` | Scale input deltas. |
| `infinite` | `false` | Looping scroll. README: touch devices also need `syncTouch`. |
| `autoResize` | `true` | ResizeObserver plus window resize, debounced 250 ms. If off, call `resize()`. |
| `prevent` | unset | `(node) => boolean`; `true` leaves that element's input native. |
| `virtualScroll` | unset | `(data) => boolean`; mutate `deltaX`/`deltaY` or return `false` to skip smoothing. |
| `overscroll` | `true` | `false` stops events from chaining to a parent instance, like `overscroll-behavior`. |
| `autoRaf` | `false` | See above. |
| `anchors` | `false` | `true` or `scrollTo` options; smooths same-page hash links. |
| `autoToggle` | `false` | Starts and stops from the root's `overflow`. Needs `lenis.css` and `transition-behavior` support (README: Safari above 17.3, Chrome above 116, Firefox above 128). |
| `allowNestedScroll` | `false` | Detects scrollable descendants automatically. Reads the DOM on every event (cached 2 s per node). |
| `naiveDimensions` | `false` | Measures with `scrollHeight` and `clientHeight`; README warns of a performance cost. `__experimental__naiveDimensions` is its deprecated alias. |
| `stopInertiaOnNavigate` | `false` | Resets inertia when an internal link to another path is clicked. |
| `respectReducedMotion` | `true` | See Accessibility. |

README versus code: the README table lists `duration` default `1.2` and says it is ignored when `lerp` is set; in the code
`duration` has no default and `Animate` checks `duration && easing` before `lerp`, so passing `duration` wins. The README
property table says `direction` is `1` for up; the code uses `Math.sign` of the scroll change, so `1` means down or right.
Trust the code.

The one-line configuration in the README "No-code usage" section turns on `autoRaf`, `autoToggle`, `anchors`,
`allowNestedScroll`, `naiveDimensions` and `stopInertiaOnNavigate`. It is convenient, but two of those carry the costs above.

## Methods, properties and events

| Member | What it does |
|---|---|
| `raf(time)` | Advance one frame (milliseconds). Needed unless `autoRaf`. |
| `scrollTo(target, options)` | Target is a number, a CSS selector, a `#id`, an element or a keyword (`top`, `left`, `start`, `bottom`, `right`, `end`). |
| `stop()`, `start()` | Pause and resume smoothing; see below. |
| `resize()` | Recompute limits after layout changes (also emits `scroll`). |
| `on(event, fn)`, `off(event, fn)` | `on` returns an unsubscribe function. `off` exists in code though the README omits it. |
| `destroy()` | Removes listeners, observers, root classes and the internal rAF loop. |

`scrollTo` options (`lenis:packages/core/src/types.ts`): `offset`, `immediate`, `lock` (block input until arrival),
`duration`, `easing`, `lerp`, `onStart`, `onComplete`, `force` (move even if stopped) and `userData` (forwarded to `scroll` listeners via `lenis.userData`).

Read-only state: `scroll`, `animatedScroll`, `targetScroll`, `actualScroll`, `limit`, `progress`, `velocity`,
`lastVelocity`, `direction`, `isScrolling` (`false`, `'native'` or `'smooth'`), `isSmooth`, `isStopped`, `isLocked`,
`isHorizontal`, `isTouching`, `isIos`, `prefersReducedMotion`, `rootElement`, `className`, `dimensions`, `options`.

Events: `scroll` (callback receives the instance; fires on smooth frames, native scrolls, `resize()`, `start()`, `stop()`)
and `virtual-scroll` (`{ deltaX, deltaY, event }`, fires before Lenis decides what to do with the input).

## Anchors and programmatic scrolling

- With `anchors` on, a click handler matches links whose host and pathname equal the current page and that carry a hash,
  decodes the hash, and calls `scrollTo`. The handler does not call `preventDefault`, so the browser's own hash
  navigation still runs alongside it.
- Selector targets starting with `#` use `getElementById`, so ids with characters such as `†` or spaces work
  (`lenis:playground/www/pages/anchor-special-chars.astro`).
- `scroll-margin-top` on the target and `scroll-padding-top` on the root are subtracted
  (`lenis:playground/www/pages/scroll-margin.astro`). Use them, or `offset`, for fixed headers.
- Calls are ignored while stopped or locked unless `force: true`. Under reduced motion they become instant.

## Stopping scroll for modals and route changes

- `stop()` resets inertia, sets `isStopped` and adds `lenis-stopped`; the stylesheet turns that class into `overflow: clip`
  on the root. Without `lenis.css` only the JavaScript half applies.
- While stopped, Lenis cancels wheel and touch defaults. That also blocks scrolling inside the modal itself unless the
  modal is excluded: nested-scroll checks run before the stopped check. Put `data-lenis-prevent` on the scrollable dialog.
- `autoToggle` replaces manual calls: it watches the root's `overflow`, so a modal library that sets `overflow: hidden`
  on `html` stops Lenis (a rule on `body` is not seen). In that mode `stop()` writes an inline `overflow: clip`.
- For client-side navigation a clean sequence is `stop()`, swap the content, `scrollTo(0, { immediate: true, force: true })`,
  then `start()` (`page-transition-with-gsap`). `stopInertiaOnNavigate` covers ordinary internal link clicks.

## Nested scroll containers

| Attribute | Effect |
|---|---|
| `data-lenis-prevent` | Leave all input on this element and its children native. |
| `data-lenis-prevent-wheel`, `data-lenis-prevent-touch` | Only that input type. |
| `data-lenis-prevent-vertical`, `data-lenis-prevent-horizontal` | Only that gesture axis. |

Alternatives are `prevent: (node) => ...` and `allowNestedScroll: true`, or a second `Lenis` with its own `wrapper` and
`content` (set `overscroll` as needed). The stylesheet adds `overscroll-behavior: contain` to attributed elements.
`lenis:playground/core/style.css` and `lenis:playground/core/test.ts` show vertical and horizontal nested boxes.

## Horizontal, infinite and custom wrappers

`orientation: 'horizontal'` plus `gestureOrientation` (`lenis:playground/horizontal/test.ts`), `infinite: true`
(`lenis:playground/infinite/test.ts`) and a custom `wrapper` (`lenis:playground/react/style.css` builds an absolutely
positioned scroll container for `root="asChild"`) are exercised in the playground. `lenis:V2-ROADMAP.md` plans a warning for
`infinite` on `html` or `body` because of iOS flicker.

## React (`lenis/react`)

| Piece | Behaviour (`lenis:packages/react/src/provider.tsx`) |
|---|---|
| `<ReactLenis root>` | No wrapper elements. Lenis uses `<html>`. The instance is published to a module-level store so `useLenis` works anywhere. |
| `<ReactLenis root="asChild">` | Wrapper and content `div`s, Lenis on the wrapper, also published globally. |
| `<ReactLenis>` (default) | Wrapper and content `div`s; instance available through context to descendants only. |
| `options`, `className`, div props, `ref` | `ref` exposes `{ wrapper, content, lenis }` (`LenisRef`). |
| `useLenis(callback?, deps?, priority?)` | Returns the instance (undefined until created). The callback runs once on registration and on every scroll, ordered by ascending priority. |

Notes: the instance is created in an effect, so it is `undefined` on the first render. The instance is rebuilt when
`JSON.stringify` of `options` changes, and JSON drops functions, so changing `easing`, `prevent` or `virtualScroll` does
not rebuild it. `useLenis` re-registers whenever the callback identity changes, so memoise it
(`lenis:packages/react/src/use-lenis.ts`). `import { Lenis } from 'lenis/react'` is the component, not the class.

## Vue and Nuxt (`lenis/vue`, `lenis/nuxt`)

`VueLenis` takes `root` (boolean), `options`, `autoRaf` and `props` (attributes for the wrapper). `useLenis(callback?, priority = 0)`
returns a computed ref. The default export is a plugin registering `vue-lenis` globally. In Nuxt, add `lenis/nuxt` to
`modules`: the module installs the plugin, auto-imports `useLenis` and registers `VueLenis`
(`lenis:packages/vue/nuxt/module.ts`). Options are deep-watched and a change recreates the instance. The README shows a GSAP
ticker integration for Vue and `lenis:playground/nuxt/app.vue` implements it. The wrapper imports `onWatcherCleanup`
and the repository develops against Vue ^3.5.13 (`lenis:packages/vue/package.json`), while the root peer range says
`>=3.0.0`; assume Vue 3.5 or newer.

## Snap (`lenis/snap`)

`new Snap(lenis, options)` aligns scrolling to points or elements (`lenis:packages/snap/src/snap.ts`).

| Item | Detail |
|---|---|
| `type` | `'proximity'` (default, snaps within `distanceThreshold`, default `'50%'` of the viewport), `'mandatory'` (always nearest), `'lock'` (one snap point per debounced input burst, input locked while animating). |
| Other options | `debounce` (default 500 ms), `lerp`, `easing`, `duration`, `onSnapStart`, `onSnapComplete`. |
| Adding points | `add(px)`, `addElement(el, { align, ignoreSticky, ignoreTransform })`, `addElements(list, options)`. `align` is `'start'`, `'center'`, `'end'` or an array. |
| Control | `next()`, `previous()`, `goTo(index)`, `start()`, `stop()`, `resize()`, `destroy()`. |

It listens to Lenis `virtual-scroll`, so only wheel and touch input triggers it. A TODO comment in the file mentions arrow
keys and space. Element positions are measured with sticky ancestors temporarily made static (`ignoreSticky`, default
`true`; `lenis:packages/snap/src/element.ts`). The function returned by `addElement` only deletes the element from the list; it does not
disconnect that element's ResizeObservers, and `snap.destroy()` only reaches elements still in the list. Prefer one
`snap.destroy()` for teardown. The README calls this partial CSS scroll-snap support.

## Pitfalls

- Missing `lenis.css`: stopped and autoToggle states do not lock scroll, iframes swallow wheel events, `html` height rules
  conflict. The README troubleshooting list starts with the latest version, the CSS, and a working `raf`.
- SSR: the constructor reads `window`, `document` and `navigator`. Create it in an effect or `onMounted`.
- Two drivers calling `raf` desync the animation; none at all leaves wheel scrolling dead because the animation never advances.
- Stopping for a modal without `data-lenis-prevent` on its scrollable area.
- Iframes: wheel events do not cross them; the stylesheet disables iframe pointer events while `lenis-smooth`.
- Sticky and fixed elements: scroll is native, so `position: sticky` keeps working (README features). Snap is the exception
  and flattens sticky ancestors while measuring. `position: fixed` can lag on pre-M1 Safari (README).
- CSS `scroll-snap` is unsupported (README limitation); use `lenis/snap`.
- Browser limits from the README: Safari capped at 60 fps and 30 fps in low-power mode; touch behaves unexpectedly with
  `syncTouch` on iOS before 16. The core also ignores touches that grab an
  iOS text-selection handle.
- `scroll-behavior: smooth` in your CSS: Lenis's own writes ignore it, but native jumps would still be smoothed twice.
  Not tested here; avoid combining.
- Performance: wheel and touch listeners are non-passive and every smooth frame calls `scrollTo` and emits `scroll`, so
  keep listeners light and write CSS variables or refs instead of React state per frame. `allowNestedScroll` and
  `naiveDimensions` add per-event DOM work; prefer attributes on known containers. The README advertises a few
  kilobytes with no runtime dependencies; this checkout has no built `dist/` to measure.
- Version drift: `lenis:V2-ROADMAP.md` plans renamed options and flipped defaults for v2. Pin the version.

## Accessibility

- `respectReducedMotion` defaults to `true`. When the OS preference is `reduce`, `lerp` is forced to `1`, `duration` and
  `easing` are ignored and programmatic scrolls (`scrollTo`, anchors) become instant. The preference is evaluated on every
  scroll event, so changes take effect without a reload. Read `lenis.prefersReducedMotion` to adapt your own motion. Opting out
  (`respectReducedMotion: false`) is not recommended by upstream.
- Stricter alternative (policy B in the recipe, suited to `reduced_motion: static_first`): do not construct Lenis at all
  while `prefers-reduced-motion: reduce` matches, and destroy it if the preference changes.
- Keyboard scrolling, scrollbar dragging and focus-driven scrolling are native events that Lenis reads back, so they are
  not smoothed but keep working. Find-in-page also uses native scrolling; not tested here.
- Smoothing does not move focus. After an anchor jump, move focus to the target yourself when it matters.
- Lenis smooths wheel input only. Touch scrolling stays native by default, which is the safest mobile default.
- Some visitors dislike the extra lag even without a system setting; keep `lerp` near the default (0.1) and do not use
  Lenis to hijack scroll.

## When not to use Lenis

Pages that only need smooth in-page jumps (CSS `scroll-behavior` is enough), dense app UIs with many nested scrollers,
pages dominated by iframes or maps, and projects where scroll feel must match the OS exactly. GSAP also ships a
`ScrollSmoother` plugin with its own wrapper and content structure (`gsap:types/scroll-smoother.d.ts`); this catalog
documents Lenis because it keeps native scroll.

## Related

Patterns: `smooth-scroll-lenis`, `lenis-react-provider`, `lenis-vue-nuxt-module`, `lenis-scroll-snap`,
`lenis-nested-scroll-and-modals`, `lenis-gsap-scrolltrigger-sync`. Recipes: `lenis-smooth-scroll-setup`,
`lenis-gsap-scrolltrigger-sync`, `page-transition-with-gsap`. Guides: `scroll-storytelling`, `motion-principles-for-ui`.

## Licence and reuse

MIT, copyright darkroom.engineering (`lenis:LICENSE`). Keep the notice if you copy code. The recipes here are original code
that calls the public API of the npm package; nothing is copied from the repository. The sponsor images in the README are
not ours to reuse.
