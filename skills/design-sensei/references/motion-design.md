# Motion design

Define the motion language of an interface, size it to `motion_intensity`, and implement it with one animation system and a reduced-motion path. Load this before adding any animation, scroll effect or page transition.

All numbers below are Design Sensei heuristics, taken from [motion principles](../../../knowledge/animations/motion-principles-for-ui.md) and [scroll storytelling](../../../knowledge/animations/scroll-storytelling.md). Tune them by testing; none is a standard. Only `prefers-reduced-motion` and the WCAG rules named below are standards.

## Decisions to make

| Decision | Options | Default rule |
| --- | --- | --- |
| Tempo | feedback only / purposeful transitions / cinematic | Derive from `motion_intensity` (budget table below). |
| Animation system | CSS only / one library (GSAP, Motion) | Use what the project already ships. One system per project. |
| Scroll behaviour | native / Lenis smoothing / pinned sequences | Native unless the story needs pacing. Lenis only at intensity 5+ and only if allowed. |
| Reduced-motion posture | `respect` / `static_first` | Read `reduced_motion` from `config show`. |
| Dependency | none / existing / add | Follow `allowed_dependencies`. `none` or `existing`: CSS transitions plus IntersectionObserver. |

| `allowed_dependencies` | Build reveals with | Scroll storytelling |
| --- | --- | --- |
| `none`, `existing` | CSS transitions, `@keyframes`, IntersectionObserver | stacked sections, no pinning |
| `minimal` | the installed library; add at most one | pinned only if it earns its bytes |
| `any` or a list | GSAP plus ScrollTrigger, Lenis if listed | full toolset |

## Motion language: tokens first

Define three durations, three easings and one travel distance as tokens, then use only those. Consistency beats variety.

| Interaction | Duration | Easing |
| --- | --- | --- |
| Hover, focus colour or opacity | 80-150 ms | linear or ease-out |
| Press (scale 0.97-0.99) | 80-120 ms in, 120-200 ms out | ease-out |
| Tooltip, popover | enter 120-200 ms, exit 80-140 ms | ease-out in, ease-in out |
| Dropdown, accordion | 180-280 ms | in-out |
| Modal, drawer | enter 220-350 ms, exit 160-250 ms | ease-out in, ease-in out |
| Toast | 200-300 ms in, 150-200 ms out | ease-out, ease-in |
| Content reveal on scroll | 400-800 ms, 16-40 px travel | strong ease-out |
| Hero or intro timeline | 0.9-2.0 s total | ease-out per element |
| Page transition | 300-600 ms per phase | in-out |
| Scrubbed scroll | set by distance; smoothing 0.3-1 s | linear |
| Ambient loop | period 6 s or longer, small amplitude | sine in-out |

Rules that hold at every level:

- Exits are about 70 percent as long as enters. Doubling travel adds roughly 30-50 percent time, not 100.
- Feedback to a user input never waits on an animation and stays under 200 ms.
- Linear easing only for progress, colour and scrubbed timelines. Never for movement.
- Animation must be interruptible: reverse from the current state instead of restarting.
- Never block input during an entrance. Only a full page transition may gate input, briefly.
- Overshoot (3-8 percent) only for toggles and badges. No bounce or elastic in forms, tables, pricing, data UI, or on text being read.

Token starting point (CSS custom properties, collapse travel under reduced motion):

```css
:root {
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-in: cubic-bezier(0.32, 0, 0.67, 0);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --duration-fast: 120ms;
  --duration-base: 240ms;
  --duration-slow: 480ms;
  --travel: 24px;
}
@media (prefers-reduced-motion: reduce) {
  :root { --travel: 0px; --duration-slow: 160ms; }
}
```

## Choreography and stagger

- Order by importance: primary message, supporting copy, call to action, decoration. The element to read first is largest and gets the most time.
- Overlap steps by 30-60 percent instead of chaining end to end. In GSAP use relative positions such as `"<0.1"` or `">-0.3"` ([[gsap-timeline-choreography]]).
- Give motion a spatial origin: menus grow from the trigger, toasts leave toward the edge they came from, cards enter from the scroll direction. Keep paired motions symmetric.
- Stagger step 30-80 ms; above about 100 ms a group reads as a queue. Cap the whole spread near 400-600 ms and use a total (`amount`) for long lists.
- Follow reading order. `from: "center"` or `"edges"` only for symmetric layouts. Stagger only what is in view. No stagger inside a staggered group.
- Text: lines for paragraphs, words for short headings, characters only for headlines under about 40 characters ([[gsap-split-text-reveal]], [[gsap-stagger-reveal]]).
- One focal motion at a time; everything else supports it or stays still.

## Mapping `motion_intensity` to budgets

Treat each row as a ceiling. Full tables are in the [motion principles note](../../../knowledge/animations/motion-principles-for-ui.md); this condensed form covers the decisions Claude makes most often.

| Level | Character | One-shot entrance | Hero timeline | Stagger | Page transition | Scrubbed effects in view | Pinned sequences (desktop) | Smooth scroll | Ambient loops |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | static | none | none | none | none | 0 | 0 | off | 0 |
| 2 | minimal | fade <= 200 ms, no travel | none | none | none | 0 | 0 | off | 0 |
| 3 | restrained | <= 300 ms, <= 12 px | none | none | 200 ms fade | 0 | 0 | off | 0 |
| 4 | calm | <= 400 ms, <= 20 px | 0.8 s | 40-60 ms x 6 | 300 ms | 1 passive indicator | 0 | off | 0 |
| 5 | balanced | <= 600 ms, <= 32 px | 1.2 s | 50-80 ms x 8 | 400 ms | 2 | 0-1 x 3 beats | optional | 1 subtle |
| 6 | expressive | <= 700 ms, <= 40 px | 1.6 s | 50-90 ms x 10 | 500 ms | 4 | 1 x 4 | optional | 2 |
| 7 | rich | <= 800 ms, <= 48 px | 2.0 s | 40-100 ms x 12 | 600 ms | 6 | 2 x 4 | allowed | 3 |
| 8 | bold | <= 900 ms, <= 64 px | 2.4 s | 30-100 ms x 16 | 700 ms | 8 | 3 x 5 | allowed | 4 |
| 9 | cinematic | <= 1.2 s | 3.0 s | 30-100 ms x 20 | 900 ms | 12 | 4 x 6 | allowed | 6 |
| 10 | motion-led | <= 1.5 s | 3.5 s | 30-100 ms x 24 | 1.2 s | 16 | 6 x 8 | allowed | 8 |

Rules that do not scale with the level:

- Phones, coarse pointers and low-power devices use `max(1, level - 2)`.
- Every effect above level 3 needs a defined reduced-motion alternative before it is built.
- Hover and focus feedback stays at 80-240 ms at every level.
- Performance budgets (see `performance.md`) and `reduced_motion` override the table.
- Total pinned travel on one page stays under about 6 vh at levels 5-7.

## One animation system per project

- Detect first: `package.json` and imports for `gsap`, `motion`/`framer-motion`, `lenis`, plus existing CSS `transition` and `@keyframes`. Extend what exists.
- Pick by job: CSS for hover, focus, press, simple reveals; the project's library for timelines, scroll choreography, layout (Flip) and text splitting. Do not use GSAP, Motion and CSS keyframes for the same job.
- GSAP has a custom licence: depend on the published package, never copy or vendor its source, read the terms before shipping (`license_review_required`; see `source-usage.md` and [GSAP overview](../../../knowledge/animations/gsap.md)). Check `gsap` plus ScrollTrigger against `initial_js_kb` (about 46 kB gzip in the note's table).
- Lenis (MIT, `copy_with_attribution`) keeps native scroll. See the pairing rules below.
- React Bits and similar copy-in animation components are `license_review_required`: use per their terms, do not republish ([[react-bits-scroll-driven-components]]).

## Scroll-led motion

Fits: linear stories with few ideas (product walkthrough, case study, launch page). Does not fit: docs, pricing, comparison tables, forms, checkout. The story must survive with all motion removed, same content, same order.

| Mechanism | Use for | Notes |
| --- | --- | --- |
| One-shot trigger (`once: true`) | entrances, reveals, counters | Finishes even if the visitor stops. |
| Toggle | header theme, active nav | Avoid start and end too close together. |
| Scrub | a continuous quantity: progress, a drawn line, before/after | Linear easing; numeric `scrub` 0.3-1 s smooths. Never scrub text that must be read. |
| Pinned scrub | demonstrations | Highest risk. Desktop and fine pointer only; stacked fallback required. |

Pacing, per beat (vh = viewport heights of scroll): statement 0.8-1.2, evidence 0.6-1.0, demonstration 0.5-1.0 per step plus a hold, breather 0.3-0.6, call to action about 1 and never pinned. The first beat delivers value above the fold.

Pinning rules: one pin at a time, never nested; size the stage in `svh`; about one viewport of travel per beat; `invalidateOnRefresh: true` when values depend on layout; use `opacity`, not `autoAlpha`, for stacked beats so inactive beats stay in the accessibility tree.

Lenis with ScrollTrigger: Lenis `autoRaf` off, GSAP ticker drives `lenis.raf(seconds * 1000)`, Lenis `scroll` event calls `ScrollTrigger.update`, `gsap.ticker.lagSmoothing(0)`. Two `raf` drivers desync the page. Do not enable both ScrollTrigger `snap` and `lenis/snap` over one range. No CSS `scroll-behavior: smooth` with Lenis. No scroll hijacking: smoothing is allowed, taking over is not. Details: [Lenis note](../../../knowledge/animations/lenis.md), [scroll storytelling note](../../../knowledge/animations/scroll-storytelling.md).

## Reduced motion: `respect` versus `static_first`

`prefers-reduced-motion: reduce` removes what can trigger discomfort (large movement, parallax, spinning, zoom, scroll-linked motion, autoplay), not all feedback.

| | `respect` | `static_first` |
| --- | --- | --- |
| Build order | Motion version, then an alternative per effect | Static page first, motion added only inside `(prefers-reduced-motion: no-preference)` |
| Hidden initial states | In the motion branch only | In the motion branch only |
| Lenis | Keep default `respectReducedMotion: true` | Do not construct it while `reduce` matches; destroy it if the preference changes |
| GSAP | `gsap.matchMedia()` with a `reduce` branch | `gsap.matchMedia()` with only a `no-preference` branch |
| `design-sensei eval` MOT-001 | warning | error |

Alternatives under `reduce`: parallax and scrubbed transforms become static positions; pinned sequences become stacked sections; slide, scale and rotate entrances become no movement or a fade of 200 ms or less; marquees and loops pause (keep a play control if they carry content); page transitions swap instantly or cross-fade 150 ms; Flip changes apply immediately; cursor-follow and magnetic effects turn off; counters show the final value; video backgrounds show a poster. Hover and focus colour changes stay. GSAP does not read the preference itself, so branch explicitly. Toggling the preference live must update the page without reload. WCAG 2.2.2: auto-playing motion longer than 5 seconds beside other content needs a pause control.

## Cleanup

- GSAP in React: build inside `gsap.context()` (or the project's `useGSAP` if installed) scoped to a ref; `ctx.revert()` on unmount. `gsap.matchMedia()` reverts its branch when a query flips.
- Lenis: `destroy()` in cleanup; create in an effect, never during SSR.
- ScrollTrigger: after route change `ScrollTrigger.getAll().length` is 0.
- Raw `requestAnimationFrame`: keep the id, `cancelAnimationFrame` on teardown; pause when the tab is hidden or the element is offscreen.
- Remove `markers: true` and dev tools from production. Remove `will-change` after the animation.

## Checklist before saying done

- [ ] Duration, easing and travel come from tokens; feedback under 200 ms.
- [ ] Counts and times fit the `motion_intensity` row; phones use level minus 2.
- [ ] Only `transform` and `opacity` animate; no `transition: all`.
- [ ] One animation system; every new dependency justified and within `allowed_dependencies`.
- [ ] Reduced-motion alternative exists per effect and was tested by toggling it live.
- [ ] Content is visible without script; hidden states live in the motion branch.
- [ ] Teardown verified (contexts reverted, Lenis destroyed, no orphan frames).
- [ ] Scroll test: slow wheel, flick, scrollbar drag, anchors, reload mid-page, resize, keyboard.

## Common mistakes

- Everything animates at once with no hierarchy; stagger step above 100 ms or across dozens of items.
- Content invisible until script runs; entrances replayed on every re-render or route change.
- Animating `width`, `height`, `top`, `left`, `margin`, large `box-shadow` or `filter: blur()`.
- Two drivers calling Lenis `raf`; `autoAlpha` on stacked beats; scrubbed readable text; nested pins.
- A reduced-motion branch that only shortens durations.
- Motion added because the library made it easy, not because a change needed explaining.

## Related

- Patterns: [[motion-principles]], [[gsap-timeline-choreography]], [[gsap-scrolltrigger-pin-scrub]], [[gsap-match-media-reduced-motion]], [[gsap-flip-layout-transition]], [[smooth-scroll-lenis]], [[lenis-gsap-scrolltrigger-sync]], [[page-transition-gsap]], [[taste-skill-three-dials]].
- Recipes: [Lenis setup](../../../knowledge/implementation-recipes/lenis-smooth-scroll-setup.md), [Lenis with ScrollTrigger](../../../knowledge/implementation-recipes/lenis-gsap-scrolltrigger-sync.md), [pinned sequence](../../../knowledge/implementation-recipes/gsap-pinned-section-sequence.md), [text reveal and stagger](../../../knowledge/implementation-recipes/gsap-text-reveal-and-stagger.md), [page transition](../../../knowledge/implementation-recipes/page-transition-with-gsap.md).
- Other references: `performance.md` (budgets, MOT rules in eval), `accessibility.md`, `source-usage.md` (licence gate), `shaders-and-webgl.md`, `three-dimensional-design.md`.
