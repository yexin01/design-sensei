---
title: "Motion principles for interfaces"
kind: guide
summary: "Original, concise guide to interface motion: duration and easing bands by interaction, hierarchy and choreography, stagger rules, restraint with overshoot, performance, reduced-motion policy, and a motion_intensity 1 to 10 budget table."
source_ids: []
pattern_ids: [motion-principles]
updated: "2026-10-09"
---

# Motion principles for interfaces

Fully original guidance. Numbers are starting heuristics for Design Sensei to apply and for you to tune by testing; none is
a standard. Library details live in `knowledge/animations/gsap.md` and `knowledge/animations/lenis.md`.

## Principles

1. Motion explains change. Use it to show where something came from, where it went, or what just happened. Decoration
   is the last thing to add, and the first to cut.
2. Fast for feedback, slower for narrative. The visitor's input should never wait for an animation.
3. One focal motion at a time. Everything else supports it or stays still.
4. Consistency beats variety. Three duration tokens and three easings cover most interfaces.
5. Every effect has a static alternative defined before it ships.

## Duration and easing by interaction

Easing meaning: ease-out decelerates (things arriving), ease-in accelerates (things leaving), in-out suits movement
between two on-screen positions, linear suits continuous values such as progress, colour and scrubbed timelines.

| Interaction | Duration | Easing | GSAP ease |
|---|---|---|---|
| Hover, focus colour or opacity | 80 to 150 ms | linear or ease-out | `power1.out` |
| Press (scale 0.97 to 0.99) | 80 to 120 ms in, 120 to 200 ms out | ease-out | `power2.out` |
| Tooltip, popover enter | 120 to 200 ms | ease-out | `power2.out` |
| Tooltip, popover exit | 80 to 140 ms | ease-in | `power2.in` |
| Dropdown, accordion | 180 to 280 ms | in-out | `power2.inOut` |
| Modal, drawer enter | 220 to 350 ms | ease-out | `power3.out` |
| Modal, drawer exit | 160 to 250 ms | ease-in | `power2.in` |
| Toast | 200 to 300 ms in, 150 to 200 ms out | ease-out, ease-in | `power2.out`, `power2.in` |
| Content reveal on scroll | 400 to 800 ms, 16 to 40 px travel | strong ease-out | `power3.out` or `expo.out` |
| Hero or intro timeline | 0.9 to 2.0 s total | ease-out per element | `power3.out` |
| Page transition | 300 to 600 ms per phase | in-out | `power3.inOut` |
| Scroll-linked (scrub) | set by scroll distance; smoothing 0.3 to 1 s | linear | `none` |
| Ambient loop | period 6 s or longer, small amplitude | sine in-out | `sine.inOut` |

Rules: exits are shorter than enters (about 70 percent). Distance changes duration: double the travel adds about 30 to
50 percent time, not double. Use the same tokens everywhere:

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

## Hierarchy and choreography

- Order by importance: primary message, supporting copy, call to action, then decoration. Lead with the element the
  visitor should read first, make it the largest and give it the most time.
- Overlap steps by 30 to 60 percent instead of chaining them end to end; chained sequences feel slow and mechanical.
  In GSAP use `"<0.1"` or `">-0.3"` style positions (`gsap-text-reveal-and-stagger`).
- Give motion a spatial origin: a menu grows from its trigger, a toast arrives from the edge it will leave to, a card
  enters from the direction of the scroll.
- Keep paired motions symmetric: whatever enters from below exits upward or reverses.
- UI animation must be interruptible. Reverse from the current state rather than restarting; CSS transitions do this by
  default, and in GSAP prefer `overwrite: "auto"` or reversing a stored timeline.
- Never block input while an entrance plays. Only full page transitions may gate interaction, briefly.
- Cap total choreography time per view using the budgets below.

## Stagger rules

- Step: 30 to 80 ms between items. Above about 100 ms the group reads as a queue.
- Cap the whole spread near 400 to 600 ms. For long lists use a total (`stagger: { amount: 0.5 }`) instead of a fixed step.
- Follow reading order. Use `from: "center"` or `"edges"` only for symmetric layouts such as a row of equal cards.
- Stagger only what is in view; items beyond the fold animate when they arrive.
- Text: lines for paragraphs, words for short headings, characters only for headlines under about 40 characters.
- One stagger per group. Do not stagger inside a staggered group.

## Anticipation and overshoot

- Anticipation (a small pull-back before the move) belongs to playful brands, at most 100 ms and a few pixels.
- Overshoot of 3 to 8 percent suits toggles and badges. Avoid bounce and elastic in forms, tables, pricing and data UI.
  `back.out` with a low overshoot value is the tame option; `elastic` and `bounce` are rarely appropriate.
- Never use overshoot on text that is being read.

## Performance

- Animate `transform` and `opacity`. They can be composited without layout. Avoid animating `width`, `height`, `top`,
  `left`, `margin`, and large `box-shadow` or `filter: blur()` values.
- Use `will-change` only on elements about to animate, and remove it afterwards.
- Do not write animation values from React state on every frame; set CSS variables or use refs.
- Pointer-follow effects: one reusable setter per property (`gsap.quickTo`), not a new tween per event.
- Pause or stop looping animation when off screen or when the tab is hidden.
- Respect the project's `performance_budget` (`initial_js_kb`, `lcp_ms`, `cls`) and `max_webgl_canvases`; they outrank
  motion. Entrances that start hidden can cause layout shift or invisible content, so reserve space and gate the hidden
  state on script running.
- If `allowed_dependencies` is `none` or `existing`, reveals work without a library:

```js
const io = new IntersectionObserver((entries) => {
  for (const entry of entries) {
    if (!entry.isIntersecting) continue
    entry.target.classList.add('is-visible')
    io.unobserve(entry.target)
  }
}, { rootMargin: '0px 0px -10% 0px' })
document.querySelectorAll('.reveal').forEach((el) => io.observe(el))
```
```css
.js .reveal { opacity: 0; transform: translateY(var(--travel)); }
.js .reveal.is-visible {
  opacity: 1; transform: none;
  transition: opacity var(--duration-slow) var(--ease-out), transform var(--duration-slow) var(--ease-out);
}
```

## `motion_intensity` budgets

`motion_intensity` is an integer from 1 (essentially static) to 10 (cinematic, motion-led) in the project configuration.
Treat these rows as ceilings. Table A covers time-based motion, table B scroll-linked motion.

Table A, time-based:

| Level | Character | Feedback | One-shot entrance | Hero timeline | Stagger step x items | Page transition | Moving at once |
|---|---|---|---|---|---|---|---|
| 1 | static | 0 to 100 ms | none | none | none | none | 0 to 2 |
| 2 | minimal | 80 to 150 ms | fade 200 ms or less, no travel | none | none | none | 2 |
| 3 | restrained | 100 to 150 ms | 300 ms or less, 12 px or less | none | none | 200 ms fade | 4 |
| 4 | calm | 100 to 200 ms | 400 ms or less, 20 px or less | 0.8 s | 40 to 60 ms x 6 | 300 ms | 6 |
| 5 | balanced | 120 to 200 ms | 600 ms or less, 32 px or less | 1.2 s | 50 to 80 ms x 8 | 400 ms | 10 |
| 6 | expressive | 120 to 220 ms | 700 ms or less, 40 px or less | 1.6 s | 50 to 90 ms x 10 | 500 ms | 14 |
| 7 | rich | 120 to 220 ms | 800 ms or less, 48 px or less | 2.0 s | 40 to 100 ms x 12 | 600 ms | 18 |
| 8 | bold | 120 to 240 ms | 900 ms or less, 64 px or less | 2.4 s | 30 to 100 ms x 16 | 700 ms | 24 |
| 9 | cinematic | 120 to 240 ms | 1.2 s or less | 3.0 s | 30 to 100 ms x 20 | 900 ms | 32 |
| 10 | motion-led | 120 to 240 ms | 1.5 s or less | 3.5 s | 30 to 100 ms x 24 | 1.2 s | 40 |

Table B, scroll-linked and ambient:

| Level | Scrubbed effects in view | Pinned sequences x beats (desktop) | Smooth scroll (Lenis) | Ambient loops |
|---|---|---|---|---|
| 1 to 3 | 0 | 0 | off | 0 |
| 4 | 1 passive indicator, such as progress | 0 | off by default | 0 |
| 5 | 2 | 0 to 1 x 3 | optional | 1 subtle |
| 6 | 4 | 1 x 4 | optional | 2 |
| 7 | 6 | 2 x 4 | allowed | 3 |
| 8 | 8 | 3 x 5 | allowed | 4 |
| 9 | 12 | 4 x 6 | allowed | 6 |
| 10 | 16 | 6 x 8 | allowed | 8 |

Rules that do not scale with the level:

- Phones, coarse pointers and low-power devices use `max(1, level - 2)`.
- Every effect above level 3 needs a defined `prefers-reduced-motion` alternative before it is built.
- No scroll hijacking: do not cancel wheel or touch input to drive a custom scroll. Smoothing is allowed, taking over is not.
- Performance budgets and the `reduced_motion` setting override the table.

## Reduced-motion policy

`prefers-reduced-motion: reduce` means remove what can trigger discomfort (large movement, parallax, spinning, zoom,
scroll-linked motion, autoplay), not remove all feedback. The `reduced_motion` configuration key selects the posture:

- `respect`: build the motion version, and define the alternative for each effect with a media query or `gsap.matchMedia()`.
- `static_first`: build the static page first and add motion only inside `(prefers-reduced-motion: no-preference)`.

| Effect | Alternative under `reduce` |
|---|---|
| Parallax, scrubbed transforms | Static positions |
| Pinned sequences | Stacked sections, normal flow |
| Slide, scale or rotate entrances | No movement; fade of 200 ms or less, or nothing |
| Looping ambient motion, marquees | Paused or removed; keep a play control when it carries content |
| Page transitions | Instant swap or a 150 ms cross-fade |
| Smooth scroll | Native scroll (Lenis does this itself by default) |
| Layout (Flip) transitions | Apply the change immediately |
| Cursor-follow, magnetic effects | Off |
| Counters | Show the final value |
| Video backgrounds | Poster image |
| Hover and focus colour changes | Keep |

Test by toggling the preference live (browser rendering tools or OS setting); the page must update without reload.

## Common mistakes

- Feedback slower than 200 ms, or entrances slower than 800 ms without a reason.
- Everything animates at once, with no hierarchy.
- Stagger across dozens of items, or a stagger step above 100 ms.
- Linear easing on movement, or bounce and elastic in business UI.
- Content that is invisible until script runs, or that never reappears after a failed load.
- Scroll-jacking, or scrubbed text the visitor must stop on and read.
- Animating layout properties, or running looped effects that never pause.
- Replaying entrances on every re-render or route change.
- Moving focus targets or losing focus during transitions.
- No `prefers-reduced-motion` branch, or one that only shortens durations.
- Motion that exists because a library made it easy rather than because a change needed explaining.

## Related

Pattern `motion-principles`. Notes `knowledge/animations/scroll-storytelling.md` (pacing for long pages),
`knowledge/animations/gsap.md` and `knowledge/animations/lenis.md` (APIs), and the recipes in
`knowledge/implementation-recipes/` for implementation.
