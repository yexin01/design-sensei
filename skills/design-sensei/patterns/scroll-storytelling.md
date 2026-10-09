# Scroll storytelling playbook

Choose and build scroll-driven motion (smooth scroll, reveals, scrubbed and pinned sequences, stacking cards) so the story still works with every effect removed.

## When to use / when not

- Use for a short linear story where order matters: product walkthrough, case study, launch page, editorial feature.
- Do not use for documentation, pricing or comparison tables, forms, checkout, search-landing pages, or long reads. Do not hijack scroll (never cancel wheel or touch input to drive a custom scroll; smoothing is allowed, taking over is not).
- Gate by dials. `motion_intensity` 1-3: no scroll-linked motion, CSS or IntersectionObserver reveals at most. 4: one passive progress indicator. 5: light scrubbed accents, at most one 3-beat pinned sequence. 6-8: one to three pinned sequences on desktop. 9-10: more, each with a full fallback. Phones and coarse pointers use `max(1, level - 2)`. Source of these ceilings: [motion budgets](../../../knowledge/animations/motion-principles-for-ui.md).
- `allowed_dependencies` is `none` or `existing`: use CSS plus IntersectionObserver for reveals and skip pinning, unless `gsap` or `lenis` is already installed.
- `reduced_motion: static_first` means build the stacked static page first, then add motion inside `(prefers-reduced-motion: no-preference)`.

## Pick the approach

| Situation | Pattern | Reuse class | Notes |
| --- | --- | --- | --- |
| Smoother wheel scroll on a brand page, no scroll-linked animation | [[smooth-scroll-lenis]] | copy_with_attribution (MIT) | Skip for app UIs with many nested scrollers, iframe or map pages. For anchor jumps only, CSS `scroll-behavior` is enough. |
| Lenis in a React or Next.js root layout | [[lenis-react-provider]] | copy_with_attribution | `lenis/react`; client component only. |
| Lenis in Vue or Nuxt | [[lenis-vue-nuxt-module]] | copy_with_attribution | Reference only, no recipe. |
| Modal, drawer or inner scrolling panel on a Lenis page | [[lenis-nested-scroll-and-modals]] | copy_with_attribution | Stop Lenis for modals; mark inner scrollers with the `data-lenis-prevent` attributes. |
| Snap sections on a Lenis page | [[lenis-scroll-snap]] | copy_with_attribution | Lenis does not support CSS scroll-snap. Never combine with ScrollTrigger `snap` over the same range. |
| Scrub or pin together with Lenis | [[lenis-gsap-scrolltrigger-sync]] | license_review_required (GSAP terms) | One clock: GSAP ticker drives Lenis, `ScrollTrigger.update` on Lenis scroll. |
| Pinned stage whose beats cross-fade (3-6 steps, desktop) | [[gsap-scrolltrigger-pin-scrub]] | license_review_required | Needs a stacked fallback for narrow, touch and reduced motion. |
| Rows of cards or list items entering with stagger | [[gsap-stagger-reveal]] | license_review_required | `ScrollTrigger.batch`, `once`, capped stagger. |
| Branch GSAP by viewport and reduced motion | [[gsap-match-media-reduced-motion]] | license_review_required | Use for every scroll-linked GSAP effect. |
| Intro choreography, not scroll-linked | [[gsap-timeline-choreography]] | license_review_required | Labels and relative positions. |
| Case-study or feature cards piling up while scrolling | [[fancy-stacking-cards]] | copy_with_attribution (MIT) | Sticky positioning plus scroll-progress scale; the recipe is original code on `motion`. |
| Ready-made scroll reveals, media-expand, card stack in React | [[react-bits-scroll-driven-components]] | license_review_required | Custom terms: use as a dependency per its terms, never bundle or republish. |
| Route change between pages | [[page-transition-gsap]] | license_review_required | See [page transitions](page-transitions.md). |
| Choosing the overall narrative style | [[style-motion-led-storytelling]] | copy_with_attribution | Style guidance, no code. |

Defaults: `motion_intensity` <= 4 or no GSAP installed: reveals with CSS/IntersectionObserver. 5-6: one-shot reveals plus at most one pinned sequence. Add Lenis only when smoothing is part of the brand; it is optional at 5-6 and allowed from 7.

## Search commands

```bash
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "scroll" --category scroll
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "pinned sequence" --category scroll --reduced-motion-safe
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "stagger reveal" --framework react --max-gpu low
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "scroll" --dependency lenis
${CLAUDE_SKILL_DIR}/scripts/design-sensei sources show gsap     # read the licence review before using GSAP
```

## Implementation steps

1. Write the beats first: one idea, one visual change, one or two sentences each. Budgets (heuristics): statement 0.8-1.2 vh, evidence 0.6-1.0 vh, demonstration 0.5-1.0 vh per step plus a hold, breather 0.3-0.6 vh, call to action about 1 vh and never pinned. Keep total pinned travel under about 6 vh. The first beat must deliver value without scrolling.
2. Build the static page: semantic sections in reading order, all content visible, no hidden initial states in the base CSS.
3. Add one-shot reveals (`once: true`) for entrances and counters. Use scrub only for a quantity the visitor controls (progress, zoom, line drawing). Use linear easing inside scrubbed timelines; scrub `transform` and `opacity` only. A numeric `scrub` of about 0.3-1 adds smoothing.
4. Add pinning last, one pin at a time, never nested. Follow the recipe [GSAP pinned section sequence](../../../knowledge/implementation-recipes/gsap-pinned-section-sequence.md): pin only under `(min-width: 900px) and (min-height: 640px) and (pointer: fine) and (prefers-reduced-motion: no-preference)`, stage height in `svh`, `anticipatePin: 1`, `invalidateOnRefresh: true`, `opacity` not `autoAlpha` on stacked beats (keeps inactive beats in the accessibility tree).
5. If using Lenis with GSAP, follow [Lenis and ScrollTrigger sync](../../../knowledge/implementation-recipes/lenis-gsap-scrolltrigger-sync.md): `autoRaf: false`, ticker-driven `raf(seconds * 1000)`, `lagSmoothing(0)`, no `scrollerProxy`. Import `lenis/dist/lenis.css`. Remove `scroll-behavior: smooth` from CSS. Mount once in the root layout. Setup details: [Lenis recipe](../../../knowledge/implementation-recipes/lenis-smooth-scroll-setup.md).
6. Build inside `gsap.context` or `gsap.matchMedia` and revert on unmount. Create triggers before wiring anchors, then refresh. After fonts or lazy media change layout call `lenis.resize()` then `ScrollTrigger.refresh()`.
7. Remove `markers`. Pin versions of `lenis` and `gsap` (Lenis upstream plans option changes for v2).

## Accessibility and performance gates

- [ ] Reduced motion emulated: complete static story, same order, nothing hidden; pinned sequences become stacked sections; live toggling works without reload.
- [ ] JavaScript disabled: all content visible and ordered.
- [ ] Keyboard (Tab, Space, PageDown, Home, End) and anchor links work; focus never lands on invisible content; after an anchor jump, move focus yourself when it matters.
- [ ] No scroll locking except modals; footer and anchors reachable.
- [ ] Mobile: native touch scrolling is the baseline. Enable Lenis `syncTouch` only for a measured reason.
- [ ] Only `transform` and `opacity` animate; no scrubbed `filter`, `box-shadow`, width or height on large areas; one ScrollTrigger per section, `ScrollTrigger.batch` for lists.
- [ ] No layout reads or framework state updates inside `scroll` or `onUpdate`; write CSS variables or refs.
- [ ] 4x CPU throttle: no long tasks while scrolling. CLS <= 0.1 (reserve media size), INP <= 200 ms, and the project's `performance_budget`.
- [ ] Teardown after route change: `ScrollTrigger.getAll().length` is 0, ticker callback removed, `lenis.destroy()` called.
- [ ] Licence gate passed for GSAP (custom terms, read `sources show gsap`) and for react-bits (custom terms).

## Common mistakes

- Two clocks: `autoRaf: true` plus the GSAP ticker causes jitter. One driver only.
- Hidden initial state in the base stylesheet, so reduced-motion and no-JS visitors see nothing.
- Pinning on touch and narrow screens; stage taller than the smallest viewport height.
- `autoAlpha` on stacked beats, which hides them from screen readers.
- ScrollTrigger `snap` together with `lenis/snap`; CSS `scroll-snap` on a Lenis page.
- Scrubbing text that must be read mid-motion; easing other than linear inside a scrub.
- Triggers created after anchor positions were computed, so anchors land off target.
- Not reverting on unmount in single-page apps; mixing GSAP, Motion and CSS keyframes for the same job.
- Copying GSAP code into the repository instead of depending on the npm package.

## Where to read more

- [Scroll storytelling guide](../../../knowledge/animations/scroll-storytelling.md) (pacing, symptoms table, test protocol)
- [Lenis note](../../../knowledge/animations/lenis.md), [GSAP note](../../../knowledge/animations/gsap.md), [motion principles](../../../knowledge/animations/motion-principles-for-ui.md)
- [Stacking cards recipe](../../../knowledge/implementation-recipes/fancy-stacking-cards-scroll.md), [React Bits variant chooser](../../../knowledge/implementation-recipes/react-bits-choose-variant-and-install.md)
- [motion-design reference](../references/motion-design.md), [accessibility](../references/accessibility.md), [performance](../references/performance.md); related playbooks [page transitions](page-transitions.md), [hero sections](hero-sections.md)
