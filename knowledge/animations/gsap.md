---
title: "GSAP toolkit overview"
kind: animation
summary: "What the GSAP 3.15.0 package ships (core, CSSPlugin and the plugin files present in the checkout), the public API vocabulary for tweens, timelines, staggers, contexts and matchMedia, bundle facts, and how to handle its custom licence."
source_ids: [gsap]
pattern_ids: [gsap-timeline-choreography, gsap-scrolltrigger-pin-scrub, gsap-stagger-reveal, gsap-split-text-reveal, gsap-match-media-reduced-motion, gsap-flip-layout-transition, page-transition-gsap]
updated: "2026-10-09"
---

# GSAP toolkit overview

GSAP (GreenSock Animation Platform) is a JavaScript animation engine: a tween and timeline core that animates CSS,
SVG, canvas and plain object properties, plus optional plugins. This checkout is version 3.15.0 (`gsap:package.json`).
The licence is custom, not MIT: read "Licence and handling" before using or recommending it. Nothing from GSAP's source
is quoted here; names, shapes and behaviour are described from `types/` and `src/`, and every code sample is original
glue that calls the public API of the npm package.

## What the package contains

| Directory | Contents |
|---|---|
| `gsap:src/` | Unbundled sources: `gsap-core.js`, `CSSPlugin.js`, `EasePack.js`, `index.js`, `all.js` and 23 plugin modules. `SplitText` is also present as TypeScript (`gsap:src/SplitText.ts`). |
| `gsap:esm/` | ES-module build with the same file names; this is what `import` resolves to. |
| `gsap:dist/` | UMD builds, 76 files: `gsap.js`, `all.js`, and for each plugin a `.js`, `.min.js` and `.min.js.map`. File listing only; there is no separate `CSSPlugin` file. |
| `gsap:types/` | Hand-maintained `.d.ts` files; `gsap:types/index.d.ts` declares the module names. |

Entry points (from the `exports` map in `gsap:package.json` and `gsap:esm/index.js`):

- `gsap` exports `gsap` (also the default). `CSSPlugin` is registered at import, so core plus CSS animation needs no
  registration. Legacy aliases (`TweenMax`, `TweenLite`, `TimelineLite`, `TimelineMax`) and ease classes are exported too.
- `gsap/all` (`gsap:esm/all.js`) re-exports the core, the utility functions and every plugin module.
- `gsap/<Name>` (for example `gsap/ScrollTrigger`, `gsap/SplitText`, `gsap/Flip`) is one module per plugin with a named
  and a default export. I confirmed both exports for ScrollTrigger, Flip, SplitText, Observer, ScrollToPlugin,
  ScrollSmoother, Draggable, MotionPathPlugin, CustomEase, TextPlugin and DrawSVGPlugin.
- Plugins must be registered with `gsap.registerPlugin(...)`; the README says so and shows the per-plugin imports.
- `require` resolves to the UMD files in `dist/`; the README also shows a jsDelivr script tag pinned to `gsap@3.15`.

## Plugin inventory (verified by file presence)

| Plugin | What it does, from `types/` | Type file |
|---|---|---|
| ScrollTrigger | Ties an animation to scroll position: start and end, scrub, pin, snap, class toggles, batching, refresh. | `gsap:types/scroll-trigger.d.ts` |
| ScrollSmoother | Smooth scrolling for a wrapper and content pair with per-element `speed` and `lag` effects. | `gsap:types/scroll-smoother.d.ts` |
| ScrollToPlugin | Tweens the scroll position of the window or an element through a `scrollTo` tween property. | `gsap:types/scroll-to-plugin.d.ts` |
| Observer | Normalises wheel, touch, pointer and scroll input into direction and velocity callbacks. | `gsap:types/observer.d.ts` |
| Draggable, InertiaPlugin | Drag, throw, snap and bounds; momentum tweens from measured velocity. | `gsap:types/draggable.d.ts`, `gsap:types/inertia-plugin.d.ts` |
| Flip | Animates layout changes by recording state, changing the DOM, then animating from the old state. | `gsap:types/flip.d.ts` |
| SplitText | Splits text into lines, words and characters with optional masks; reverts and can re-split. | `gsap:types/split-text.d.ts` |
| TextPlugin, ScrambleTextPlugin | Tween text content; scramble characters while revealing text. | `gsap:types/text-plugin.d.ts`, `gsap:types/scramble-text-plugin.d.ts` |
| MotionPathPlugin, MotionPathHelper | Move targets along SVG paths or point lists; path maths; an interactive path editor. | `gsap:types/motion-path-plugin.d.ts`, `gsap:types/motion-path-helper.d.ts` |
| DrawSVGPlugin, MorphSVGPlugin | Animate stroke drawing; morph one SVG shape into another. | `gsap:types/draw-svg-plugin.d.ts`, `gsap:types/morph-svg-plugin.d.ts` |
| CustomEase, CustomBounce, CustomWiggle, EasePack | Build custom eases; `EasePack` holds SlowMo, RoughEase and ExpoScaleEase. | `gsap:types/custom-ease.d.ts`, `gsap:types/ease.d.ts` |
| Physics2DPlugin, PhysicsPropsPlugin | Velocity, acceleration, gravity and friction based motion. | `gsap:types/physics-2d-plugin.d.ts`, `gsap:types/physics-props-plugin.d.ts` |
| PixiPlugin, EaselPlugin, CSSRulePlugin | Property helpers for PixiJS and EaselJS objects; tween properties of CSS rules found by selector. | `gsap:types/pixi-plugin.d.ts`, `gsap:types/easel-plugin.d.ts`, `gsap:types/css-rule-plugin.d.ts` |
| GSDevTools | On-page UI for scrubbing and inspecting an animation during development. | `gsap:types/gs-dev-tools.d.ts` |

The README states that the former members-only plugins (it names SplitText and MorphSVG) are now available at no charge.
The files are present in this checkout; confirm the terms yourself before depending on any of them.

## API vocabulary

Everything below is declared in `gsap:types/gsap-core.d.ts`, `gsap:types/tween.d.ts`, `gsap:types/timeline.d.ts`,
`gsap:types/animation.d.ts` and `gsap:types/gsap-utils.d.ts`.

- Creating tweens: `gsap.to`, `gsap.from`, `gsap.fromTo`, `gsap.set`. Targets may be selectors, elements, arrays or plain
  objects. Values may be functions of `(index, target, targets)`.
- Common vars: `duration`, `delay`, `ease`, `stagger`, `repeat`, `repeatDelay`, `yoyo`, `paused`, `overwrite`,
  `immediateRender`, `lazy`, `keyframes`, `startAt`, `id`, and the callbacks `onStart`, `onUpdate`, `onComplete`,
  `onRepeat`, `onReverseComplete`, `onInterrupt`. `easeReverse` is new in 3.15.0 and replaces the deprecated `yoyoEase`.
- CSS shorthands from `CSSPlugin`: `x`, `y`, `xPercent`, `yPercent`, `scale`, `rotation`, `skewX`, `opacity`, and
  `autoAlpha` (opacity plus `visibility`, so a hidden target also leaves the accessibility tree).
- Easing: strings such as `power1` to `power4`, `back`, `bounce`, `circ`, `elastic`, `expo`, `sine`, each with `.in`,
  `.out` and `.inOut`, plus `none`. `back` and `elastic` accept `config(...)` for overshoot or amplitude. Custom curves
  come from `gsap.registerEase` or `CustomEase`.
- Stagger: a number, or an object with `each` or `amount`, `from` (`start`, `center`, `end`, `edges`, `random`, an index),
  `grid`, `axis` and `ease`. `gsap.utils.distribute` builds the same distribution as a function.
- Timelines: `gsap.timeline({ defaults, paused, repeat, smoothChildTiming, ... })` with `to`, `from`, `fromTo`, `set`,
  `add`, `addLabel`, `addPause`, `call`, `tweenTo`, `getChildren`. Control methods shared by tweens and timelines:
  `play`, `pause`, `reverse`, `restart`, `progress`, `seek`, `timeScale`, `kill`, `revert`, `then`.
- Position parameter (third argument on timeline methods), per `_parsePosition` in `gsap:src/gsap-core.js`: a number is
  an absolute time; `"+=n"` and `"-=n"` offset from the timeline end; `"<"` is the start of the previously added
  animation and `">"` its end, each with an optional offset such as `"<0.2"` or `">-0.3"`; a label name, optionally with
  an offset such as `"intro+=0.5"`; percent offsets use `%`.
- Utilities: `gsap.utils` and the named exports `clamp`, `interpolate`, `mapRange`, `normalize`, `pipe`, `snap`, `wrap`,
  `wrapYoyo`, `random`, `shuffle`, `toArray`, `selector`, `splitColor`, `unitize`, `getUnit`, `distribute`
  (`gsap:esm/all.js` lists them).
- Performance helpers: `gsap.quickTo` and `gsap.quickSetter` for pointer-driven values, `gsap.ticker`
  (`add`, `remove`, `lagSmoothing`, `fps`, `deltaRatio`, `wake`, `sleep`), `gsap.config`, `gsap.defaults`.
- Reuse: `gsap.registerEffect` defines named effects; `gsap.registerEase` defines named eases.

Ticker facts read from `gsap:src/gsap-core.js`: callbacks receive `(time, deltaTime, frame, elapsed)`, with `time` in
seconds and `deltaTime` in milliseconds. Auto-sleep only applies when no listener beyond GSAP's own is registered, so a
`ticker.add` callback keeps the ticker awake. Lag smoothing defaults to a 500 ms threshold and 33 ms adjusted lag;
`lagSmoothing(0)` disables it.

## Cleanup and responsive logic: `gsap.context` and `gsap.matchMedia`

- `gsap.context(fn, scope)` records every tween, timeline, ScrollTrigger, SplitText and nested matchMedia created while
  `fn` runs. `ctx.revert()` restores the original state and kills ScrollTriggers; `ctx.kill()` stops without restoring;
  `ctx.add(fn)` (or the second argument passed to `fn`) lets later event handlers register animations into the context;
  a function returned from `fn` runs as cleanup on revert. A selector scope limits string selectors to that subtree, and
  a React ref object is accepted (the scope helper unwraps `.current`).
- `gsap.matchMedia(scope?)` returns an object whose `add(conditions, fn)` takes one media-query string or an object of named
  queries (the key `all` always matches). `fn` runs while any query matches and receives a context whose `conditions` hold
  a boolean per name. When any query flips, the context is reverted and `fn` re-runs if at least one query still matches.
  Returned functions are cleanup. `mm.revert()` and `mm.kill()` tear everything down; `gsap.matchMediaRefresh()` forces a
  re-run. ScrollTrigger listens to these events and refreshes itself.
- Reduced motion: a search of `gsap:src/gsap-core.js`, `gsap:src/ScrollTrigger.js`, `gsap:src/ScrollSmoother.js`,
  `gsap:src/Flip.js`, `gsap:src/SplitText.ts` and `gsap:src/Observer.js` found no code that reads
  `prefers-reduced-motion`. You must branch yourself, and `matchMedia` with `(prefers-reduced-motion: reduce)` is the
  natural tool because it also reverts the motion branch if the preference changes. See `gsap-pinned-section-sequence`.

## ScrollTrigger essentials

Types in `gsap:types/scroll-trigger.d.ts`, implementation in `gsap:src/ScrollTrigger.js`.

- Attach with a `scrollTrigger` var on a tween or timeline, or with `ScrollTrigger.create`. Main keys: `trigger`, `start`,
  `end` (strings like `"top 80%"`, `"+=300%"`, or functions), `scrub` (`true` or seconds), `pin`, `pinSpacing`,
  `anticipatePin`, `toggleActions`, `toggleClass`, `once`, `snap`, `markers`, `invalidateOnRefresh`, `scroller`,
  `containerAnimation`, `refreshPriority`, and the `onEnter`, `onLeave`, `onEnterBack`, `onLeaveBack`, `onUpdate` callbacks.
- A numeric `scrub` is the duration of a catch-up tween on the animation's progress, so it smooths scroll-linked motion.
  `anticipatePin` pins slightly early using scroll velocity to hide the one-frame lag on fast scrolls.
- Statics: `refresh`, `update`, `batch`, `getAll`, `getById`, `killAll`, `config`, `normalizeScroll`, `scrollerProxy`,
  `observe`, `isInViewport`, `saveStyles`. `ScrollTrigger.matchMedia` is marked deprecated in favour of `gsap.matchMedia`.
- It refreshes itself on `DOMContentLoaded`, `load`, `resize` and visibility changes, runs a 250 ms internal sync
  interval, and by default ignores address-bar resizes on touch-only devices (`ScrollTrigger.config({ ignoreMobileResize })`).
- It reads native scroll and registers scroll and wheel listeners, which is why a smooth scroller that keeps native scroll,
  such as Lenis, needs no `scrollerProxy`. Integration: `lenis-gsap-scrolltrigger-sync`.

## SplitText

`SplitText.create(target, vars)` (`gsap:types/split-text.d.ts`, `gsap:src/SplitText.ts`):

- `type` is a comma list of `lines`, `words`, `chars` (default all three; request only what you animate). Instances expose
  `lines`, `words`, `chars`, `masks`, `elements`, `isSplit`, and methods `split`, `revert`, `kill`.
- `mask: "lines" | "words" | "chars"` wraps that unit in a clone with `overflow: clip` for slide-up reveals.
- `autoSplit: true` (lines only) re-splits on container resize and when fonts finish loading. If `onSplit` returns a
  GSAP animation, SplitText reverts it before re-splitting and restores its time on the new one, so re-splits are seamless.
- `aria` defaults to `"auto"`: the trimmed text goes into an `aria-label` on the split element and every generated
  wrapper gets `aria-hidden="true"`. `"hidden"` hides the element itself; `"none"` adds no aria attributes. Screen-reader
  behaviour of `aria-label` on non-heading text is not verified here; test it.
- Import: `import { SplitText } from "gsap/SplitText"` then `gsap.registerPlugin(SplitText)`. Recipe: `gsap-text-reveal-and-stagger`.

## Flip

`Flip.getState(targets, { props, simple })` records position, size and optional properties; change the DOM (class,
order, parent); then `Flip.from(state, { duration, ease, stagger, absolute, scale, fade, nested, onEnter, onLeave, ... })`
animates from the recorded state to the new layout and returns a timeline. Related statics: `Flip.to`, `Flip.fit`,
`Flip.batch`, `Flip.isFlipping`, `Flip.killFlipsOf`, `Flip.makeAbsolute` (`gsap:types/flip.d.ts`). Elements can be matched
across states with a `data-flip-id` attribute.
Reduced-motion alternative defined here: under `(prefers-reduced-motion: reduce)` skip `Flip.from` and apply the DOM change
immediately, or cross-fade with a 150 to 200 ms opacity tween. Keep focus on the same logical element after the change.
No recipe exists yet for this pattern.

## React and frameworks

The README names a separate `@gsap/react` package with a `useGSAP()` hook that automates cleanup. It is not in this
checkout, so its API is not verified here. What is verified in this package: build animations inside
`gsap.context(fn, scopeRef)` within `useEffect` or `useLayoutEffect` and call `ctx.revert()` in the cleanup. This also
covers React Strict Mode's double invocation. Register plugins in client-only code; ScrollTrigger guards its window access
at registration (`gsap:src/ScrollTrigger.js`) but trigger creation belongs in effects.

## Bundle and tree-shaking facts

- `gsap:package.json` sets `sideEffects: false`, `module` to `esm/index.js` and `main` to `dist/gsap.js`.
- Import only the plugins you register. `gsap/all` pulls every plugin module into the dependency graph.
- UMD files in this checkout (minified, then gzip default level; your bundler output will differ):

| File | Minified | Gzip |
|---|---|---|
| `gsap:dist/gsap.min.js` | 72,927 B | 28,356 B |
| `gsap:dist/ScrollTrigger.min.js` | 44,575 B | 17,988 B |
| `gsap:dist/Flip.min.js` | 25,534 B | 9,706 B |
| `gsap:dist/ScrollSmoother.min.js` | 13,373 B | 5,531 B |
| `gsap:dist/SplitText.min.js` | 7,732 B | 3,660 B |

Check the project's `performance_budget.initial_js_kb` before adding core plus ScrollTrigger (about 46 kB gzip by the table).

## Performance and accessibility notes

- Animate `x`, `y`, `scale`, `rotation` and `opacity`. Avoid tweening layout properties on many elements.
- Create one `quickTo` per pointer-driven property instead of a new tween per event.
- Remove `markers: true` and `GSDevTools` from production builds.
- Every scroll-linked or large-travel animation needs a reduced-motion branch. Keep content visible by default and let
  the animation hide it, so no-script and reduced-motion visitors still see everything.
- `autoAlpha: 0` hides from assistive technology as well as sight; use plain `opacity` when stacked content must stay
  readable by screen readers.

## When to choose GSAP

Choose it for sequenced timelines, scroll choreography, SVG and text effects, and layout (Flip) animation. Choose CSS
transitions for simple hover and focus feedback. Choose something else when the licence does not fit the product or when
the project's `allowed_dependencies` setting forbids a new dependency.

## Licence and handling

- Custom licence, not an OSI licence. `gsap:package.json` points to https://gsap.com/standard-license, `gsap:README.md`
  links the same page, the header of every core and plugin source file refers to it (`index.js` and `all.js` excepted),
  and the repository has no LICENSE file.
- The review entry in `catalog/licenses.yaml` (reviewed 2026-10-09, status `needs_human_review`) records: the licence
  is owned by Webflow; use inside tools that let users build visual animations without code and compete with Webflow's
  animation builder is prohibited; the page summary says commercial use is free when end users are not charged a fee, with a
  business membership otherwise; terms can be amended by posting new terms.
- Project policy: depend on the published npm package. Never copy GSAP source or its `dist/` files into this repository or
  into generated sites' vendored code. Recipes here contain only original code calling the public API.
- A person must read the current terms before shipping. This note is a pointer, not legal advice.

## Related

Patterns: `gsap-timeline-choreography`, `gsap-scrolltrigger-pin-scrub`, `gsap-stagger-reveal`, `gsap-split-text-reveal`,
`gsap-match-media-reduced-motion`, `gsap-flip-layout-transition`, `page-transition-gsap`. Recipes:
`gsap-text-reveal-and-stagger`, `gsap-pinned-section-sequence`, `lenis-gsap-scrolltrigger-sync`,
`page-transition-with-gsap`. Guides: `motion-principles-for-ui`, `scroll-storytelling`.
