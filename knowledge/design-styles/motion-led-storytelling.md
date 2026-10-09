---
title: "Motion-led storytelling"
kind: design-style
summary: "Scroll-driven narrative in which pacing, pinned scenes, reveals and camera-like transitions carry the story. Covers chaptering, scroll mapping with Lenis and GSAP ScrollTrigger, the mandatory reduced-motion and static alternatives, and the scroll-hijack failure modes."
source_ids: [astryx, fancy, gsap, lenis, vengeance-ui]
pattern_ids: [style-motion-led-storytelling]
updated: "2026-10-09"
---

# Motion-led storytelling

Motion-led storytelling (scrollytelling) uses scroll position as a timeline. The page is divided into chapters; each chapter reveals, pins, transforms or moves content so that pacing, not layout alone, carries the narrative. Done well it explains a product, an investigation or a launch step by step. Done badly it hides content behind animation, traps scroll and excludes anyone who cannot or will not use motion.

## Visual characteristics
- Full-viewport chapters, each with one statement, one visual and a clear transition to the next.
- Pinned stages whose content changes with scroll progress; stacked cards, zoom-through and parallax layers.
- Large type per beat, colour shifts between chapters, a progress cue.
- Scrubbed media: image sequences, video or a 3D camera tied to scroll.

## When it fits, when it does not
- Fits: product launches, campaigns, annual reports, data stories, long-form features, case studies.
- Poor fit: tools, documentation, checkout, anything people return to for quick access, and audiences who need predictable scrolling.
- Supporting influences that work: editorial, kinetic-typography, experimental-3d, minimalism, high-fashion-luxury, product-led-saas for a single hero narrative. Avoid dense dashboards.

## Typography
- One idea per viewport: 40-120 px statements, 20-28 px supporting lines, nothing smaller than 16 px in pinned scenes.
- Keep line lengths short (under 45 characters on display lines) so beats read at a glance.
- Load fonts before measuring triggers; font swaps move trigger positions, so refresh scroll triggers after fonts load.

## Colour
- Assign each chapter a ground and an accent and change them with the story, not with every element.
- Check text contrast against every state of a transitioning background, including mid-fade.
- Progress or step indicators must not rely on colour alone.

## Composition and layout
- Use `100dvh` (not `100vh`) for chapter heights so mobile browser bars do not break pinning.
- Keep a normal document flow underneath: real headings, text in the DOM, content readable with scripts failing.
- Limit pinned distance (about two to three viewport heights per scene on desktop; much less on phones) and always provide a visible way forward.
- On phones prefer stacked, unpinned sections with simple reveals.

## Interaction and motion
- Native scroll stays native. Lenis wraps the browser scroll so sticky positioning, anchors and accessibility keep working, and it syncs with GSAP ScrollTrigger from one ticker.
- Motion carries meaning (entry, continuity, spatial change); small feedback is faster than large entrances. The Astryx motion record states the rule that matters most here: every animated transition needs an immediate or minimal-movement form that communicates the same state change (`astryx:docs/design/motion.md`, a draft record).
- Typical timings: reveals 400-700 ms ease-out; scrubbed motion tied to progress with at most light smoothing.
- Reduced motion (required): Lenis already disables smoothing and makes programmatic scrolls instant by default, but content animation is yours to handle. Branch on `prefers-reduced-motion` (or `gsap.matchMedia()`): drop pinning and scrubbing, show each chapter as static stacked content with final states, replace parallax with none, replace video scrubbing with a poster, keep the progress cue.

## Accessibility cautions
- Scroll-jacking, pinned scenes with no exit and scroll-triggered content that stays invisible until animated all harm keyboard, screen-reader and zoom users. Content must exist and be focusable regardless of animation state.
- Keep anchor links, Page Down and Home/End working; do not intercept wheel events beyond smoothing.
- Parallax and large zooms can cause vestibular symptoms; cap amplitude and honour the preference.
- Do not hide essential text until a trigger fires; if JavaScript fails the page must still read.

## Common mistakes
- "Fade up" on every element, so nothing has emphasis.
- Long pinned sequences on phones, and `100vh` sections that jump with browser bars.
- Triggers not refreshed after fonts or images load, producing misaligned scenes.
- Mixing GSAP, Motion and CSS keyframes on the same elements.
- No reduced-motion branch for content animations because the scroll library handles its own.

## Typical mistakes of AI-generated versions
- ScrollTrigger on every section with identical translate-and-fade, a pinned hero that cannot be skipped, and no preference handling.
- Text that starts at opacity 0 and relies on JavaScript to appear.

## How to build it
- Pattern: `style-motion-led-storytelling`. Storyboard the chapters, write the static version, then add scroll mapping, then smoothing.
- `lenis:README.md` documents the setup, the GSAP ScrollTrigger synchronisation recipe, the `respectReducedMotion` option (default on) and the `prefersReducedMotion` getter; the implementation is in `lenis:packages/core/src/lenis.ts`. Limits listed there include no CSS scroll-snap support (use the snap package), a 60 fps cap in Safari and no smoothing over iframes.
- GSAP: ScrollTrigger options such as `scrub`, `pin`, `pinSpacing`, `anticipatePin`, `invalidateOnRefresh` and `normalizeScroll` exist in `gsap:src/ScrollTrigger.js`; `gsap.matchMedia()` is the documented way to branch on media queries. Use the npm package under GSAP's no-charge licence; do not copy its source.
- Motion-based sticky stack: `fancy:src/fancy/components/blocks/stacking-cards.tsx` (`totalCards`, `scaleMultiplier`, `scrollOptions`; sticky cards scale as scroll progresses). It has no reduced-motion branch.
- `vengeance-ui:src/components/ui/smooth-scroll.tsx` wires Lenis into a React app, and `vengeance-ui:src/components/ui/scroll-dissolve-reveal.tsx` ties a React Three Fiber shader dissolve to scroll progress.

## Sources
Original guidance written for this project. astryx, fancy, lenis and vengeance-ui are MIT-licensed; gsap uses GreenSock's no-charge licence and is referenced by path only.
