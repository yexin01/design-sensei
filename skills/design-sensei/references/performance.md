# Performance

Keep a distinctive interface inside its budget: know the numbers, measure what you can, fix in a fixed order, and understand what `design-sensei eval` does and does not check. Load this when adding any dependency, animation, canvas, font or large image, and again before saying done.

## Budgets from configuration

`design-sensei config show --project .` prints the effective `performance_budget`. Defaults:

| Key | Default | Meaning | Checked by `eval`? |
| --- | --- | --- | --- |
| `initial_js_kb` | 200 | gzipped JavaScript needed for first render | No. Check the build output yourself. |
| `lcp_ms` | 2500 | largest contentful paint target | No. Needs a browser measurement. |
| `cls` | 0.1 | cumulative layout shift target | No. Only PERF-001 (missing image size) is a proxy. |
| `max_webgl_canvases` | 1 | simultaneous WebGL canvases | Yes, PERF-004. |

Related dials: `webgl_enabled` (false forbids WebGL; PERF-005), `allowed_dependencies` (PERF-007), `motion_intensity` (motion budget, see `motion-design.md`), `reduced_motion`. A budget outranks an effect: if the effect does not fit, cut the effect, not the budget.

Core Web Vitals "good" thresholds (standard): LCP <= 2.5 s, INP <= 200 ms, CLS <= 0.1. The defaults for `lcp_ms` and `cls` equal them; INP has no config key but still applies to any interactive effect.

Budget arithmetic: GSAP core plus ScrollTrigger is about 46 kB gzip (28.4 + 18.0 from the [GSAP note](../../../knowledge/animations/gsap.md), UMD builds; your bundler differs), so it takes roughly a quarter of the default `initial_js_kb`. three.js with R3F will not fit in 200 kB: load it lazily and keep it out of the initial bundle.

## What to measure, and with what

| Metric | How | Notes |
| --- | --- | --- |
| LCP, CLS, INP | Browser performance trace or Lighthouse via a browser tool if the session has one (Chrome DevTools MCP, Playwright, a headless browser skill) | Mobile profile with CPU throttling approximates a mid-range phone; it is only an approximation. |
| JS size | The framework build summary or a bundle analyzer if the project has one; the network list in the browser | Count gzipped, first-render JS only. |
| Failed or oversized assets | Browser network list; console | Fonts, models, textures, HDR files. |
| Long tasks, layout thrash | Performance panel during scroll and during the first 3 seconds | Scroll handlers should not read layout. |
| GPU/idle cost | Performance panel after the scene settles; watch for work while offscreen | Pause offscreen work. |
| WebGL stats | `gl.info.render` (triangles, calls) in development | Compare with the triangle budget. |
| Static rules | `design-sensei eval <project-dir>` | Heuristic lint, see below. |

If no browser tool exists, say so explicitly and list the metrics that were not measured. Never report a Web Vitals number you did not measure.

## Cost model

| Cost | Where it shows up | Controls |
| --- | --- | --- |
| JavaScript | initial_js_kb, INP, parse time | Native/CSS first; one animation system; lazy-load heavy code; avoid `gsap/all`; load Lenis and ScrollTrigger only on pages that use them (Lenis registers non-passive wheel/touch listeners; ScrollTrigger runs a 250 ms sync interval, per the [scroll storytelling note](../../../knowledge/animations/scroll-storytelling.md)). |
| GPU | frame rate, battery, heat | Pixels x work per pixel x fps. Cap DPR, render scale, 30 fps for ambient, pause offscreen, one canvas. See `shaders-and-webgl.md`, `three-dimensional-design.md`. |
| Images | LCP, CLS, bytes | Set `width` and `height` (or `aspect-ratio`); responsive `srcset`/`sizes`; modern formats; `loading="lazy"` below the fold only; never lazy-load the LCP image; give the LCP image high fetch priority. |
| Fonts | LCP, CLS | `font-display: swap` (or `optional`); subset; preload only the one or two faces used above the fold; fewer families (TYPO-001). |
| Animation | main thread, layout | Animate `transform` and `opacity`; no layout properties; `will-change` only on elements about to animate and removed after; one reusable `quickTo` setter for pointer-follow instead of a tween per event. |
| Layout shift | CLS | Reserve space for media, embeds, canvases and late content; entrances that start hidden must not move siblings. |
| Video | bytes, decode | Muted, `playsinline`, poster; stop offscreen; poster under reduced motion or data-saver. |

Lazy loading rules:

- Defer anything not needed for first paint: three.js/R3F, shader modules, heavy backgrounds, below-fold sections, large models. Mount near the viewport (IntersectionObserver with a margin) and unmount/pause when far away.
- The static layer (poster, CSS gradient, real `img`) is the LCP candidate; the effect loads after it. See the [heavy background budget recipe](../../../knowledge/implementation-recipes/react-bits-heavy-background-budget.md) and [[r3f-lazy-canvas-webgl-fallback]].
- Gate heavy effects on reduced motion, narrow viewport or coarse pointer (policy choices, for example under 768 px), and data-saver.
- Do not hide content until script runs: no-script and slow-script visitors must see it, and late reveals hurt LCP and CLS.

## Triage order

Fix in this order; re-measure after each step.

1. Establish the baseline: measure LCP element, CLS, JS size, canvas count. Note the device profile used.
2. LCP: identify the element. Ship it in the HTML, size it, prioritise it, remove anything blocking it (heavy scripts, hidden-until-JS states, fonts without `font-display`).
3. JS weight: remove or lazy-load libraries; replace a library with CSS where the result is the same; check `allowed_dependencies`; avoid overlapping libraries (GSAP + Motion + Lenis for one job).
4. Layout shift: image/embed dimensions, font swap metrics, reserved space for dynamic sections.
5. Main thread and INP: long tasks, scroll handlers, state updates per frame, large DOM from splitting text into characters.
6. GPU: canvas count, DPR cap, render scale, offscreen pause, shader loop cost, model triangles and texture sizes.
7. Animation: layout-property animation, `will-change` leaks, loops that never pause, orphan frames after unmount.
8. Re-measure and compare with the budget. State what was and was not measured.

## `design-sensei eval` rules that relate to performance

`design-sensei eval <path> [--strict] [--verbose] [--json]` is a regex linter over HTML, CSS, JS/TS, JSX/TSX, Vue, Svelte and Astro files (up to 600 files, 600 kB each, skipping `node_modules`, `dist`, `.next` and similar). It reads the effective config. Errors exit 1; with `--strict`, warnings do too. Info findings only show with `--verbose`. It cannot see rendered output, real bytes or timings.

| Code | Level | Fires when | Fix |
| --- | --- | --- | --- |
| PERF-001 | warning | an `<img>` tag lacks `width` or `height` | Set intrinsic size or `aspect-ratio`. |
| PERF-003 | warning | more than 3 `will-change:` declarations | Use sparingly, only on elements about to animate. |
| PERF-004 | warning | WebGL canvases found exceed `max_webgl_canvases`. It counts `new WebGLRenderer(`, `<Canvas` and `getContext('webgl'/'webgl2')` in the text | Share one renderer, or mount canvases only while visible. |
| PERF-005 | error | WebGL found while `webgl_enabled` is false | Remove the effect or enable it deliberately. |
| PERF-006 | warning | a file uses `devicePixelRatio` without `Math.min(...)` or a `dpr = [` range | Cap it. |
| PERF-007 | warning | `package.json` dependencies conflict with `allowed_dependencies`; the watched list is three, @react-three/fiber, gsap, framer-motion, motion, lenis, @studio-freight/lenis, ogl, pixi.js, @splinetool/react-spline | Remove, or extend the setting deliberately. `none`: any watched library warns; list: any watched library outside it warns; `minimal`: warns above 3. |
| PERF-008 | warning | a Google Fonts URL lacks `display=swap` or `display=optional` | Add it. |
| TYPO-003 | warning | `@font-face` without `font-display` | Add `swap` or `optional`. |
| RESP-003 | info | `100vh` without `dvh`/`svh`/`lvh` | Use `100dvh` or `svh`. |

Motion rules (category `motion`) that affect cost:

| Code | Level | Fires when | Fix |
| --- | --- | --- | --- |
| MOT-001 | warning, error if `reduced_motion` is `static_first` | motion code is present (gsap, ScrollTrigger, Lenis, framer-motion, requestAnimationFrame, useFrame, `<Canvas`, WebGLRenderer, `@keyframes`, `animation:`, `transition:`) and no reduced-motion handling appears anywhere | Add a media query, `matchMedia` or `useReducedMotion` branch. |
| MOT-004 | warning | a `transition` or `@keyframes` touches width, height, top, left, right, bottom, margin or padding | Animate `transform`/`opacity`. |
| MOT-005 | warning | `transition: all` | List the properties. |
| MOT-006 | warning | Lenis created in an effect without `.destroy(`; GSAP tween in an effect without `revert`/`context`/`useGSAP`/`kill`; `requestAnimationFrame(` without `cancelAnimationFrame(` | Clean up on teardown. |

Gaps to know about:

- There are no PERF-002, MOT-002 or MOT-003 rules. Do not cite them.
- `initial_js_kb`, `lcp_ms` and `cls` are never read by `eval`. A clean run proves nothing about them.
- No check for image format, image weight, `loading="lazy"`, font preloading, bundle size, offscreen pause, or context-loss handling. Verify those by hand.
- Regex matching: `<Canvas` also matches non-WebGL uses of that name, and one file reading a reduced-motion query anywhere silences MOT-001 for the whole project. Treat both as prompts to check, not proof.
- Next steps after a run: browser inspection at 375, 768, 1280 and 1920 px, as in the skill's verification step.

## Checklist before saying done

- [ ] Baseline and final numbers recorded for LCP, CLS, first-render JS and canvas count, or the gap stated.
- [ ] First-render JS within `initial_js_kb`; heavy libraries lazy-loaded; no overlapping animation libraries.
- [ ] LCP element identified, sized, not lazy-loaded, not hidden until script runs.
- [ ] Every `<img>`, video, embed and canvas has reserved space.
- [ ] Fonts: `font-display`, subset, few families.
- [ ] Only `transform`/`opacity` animate; `will-change` limited; loops pause offscreen and in hidden tabs.
- [ ] WebGL: canvases within `max_webgl_canvases`, DPR capped, context released on teardown, static fallback present.
- [ ] `design-sensei eval` run; every PERF and MOT finding fixed or consciously accepted and reported.

## Common mistakes

- Treating a clean `eval` as a passed performance review.
- Lazy-loading the hero image, or hiding hero content until a library initialises.
- Adding GSAP, Lenis and Motion together for one reveal.
- A full-viewport canvas at native DPR on phones; a loop that runs while offscreen.
- Importing `gsap/all` or a whole icon/animation package for one component.
- Optimising by guess instead of measuring the LCP element first.
- Reporting numbers from a desktop run as if they described mid-range phones.

## Related

- Patterns: [[r3f-adaptive-resolution-performance]], [[r3f-on-demand-rendering]], [[r3f-lazy-canvas-webgl-fallback]], [[webgl-effect-fallback-and-reduced-motion]], [[react-bits-self-pausing-shader-backgrounds]], [[motion-principles]].
- Notes: [motion principles](../../../knowledge/animations/motion-principles-for-ui.md), [R3F animation and performance](../../../knowledge/animations/r3f-animation-and-performance.md), [GLSL UI fundamentals](../../../knowledge/shaders/glsl-ui-fundamentals.md).
- Other references: `motion-design.md`, `shaders-and-webgl.md`, `three-dimensional-design.md`, `accessibility.md`, `design-qa.md`.
