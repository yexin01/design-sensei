# Page transitions playbook

Choose and build route-change and state-change transitions (curtain, theme reveal, layout morph) that keep focus, scroll, titles and back-button behaviour correct.

In this file `design-sensei` means `${CLAUDE_SKILL_DIR}/scripts/design-sensei`.

## When to use / when not

- Use for small multi-page marketing or portfolio sites with one shared layout shell, or for a single high-value moment such as a theme switch.
- Not for apps whose pages depend on inline scripts, per-page `<head>` assets, form redirects or authentication flows ([recipe](../../../knowledge/implementation-recipes/page-transition-with-gsap.md) says so explicitly).
- A transition that delays navigation is a cost on every click. If `motion_intensity` is 3 or lower, use no transition or a 200 ms fade.

## Pick the approach

| Situation | Pick | Reuse class | Notes |
| --- | --- | --- | --- |
| Fetch-and-swap curtain on a small site | [[page-transition-gsap]] | license_review_required | Original recipe code calling the `gsap` package (own terms). Optional Lenis for scroll reset. Total motion 0.6 s. |
| Theme toggle with a circle, polygon or mask reveal | [[skiper-ui-theme-toggle-view-transition]] | reimplement_only | Idea only; no licence. Write your own code from the public View Transitions API documentation; switch instantly when the API is missing or reduced motion is set. |
| Animate reorder, filter or expand inside one page | [[gsap-flip-layout-transition]] | license_review_required | No recipe yet. Apply the change immediately under reduce; keep focus on the same logical element. |
| Branch transitions on reduced motion and viewport | [[gsap-match-media-reduced-motion]] | license_review_required | Reverts the motion branch when the preference changes. |
| Smooth scroll that must pause and reset across routes | [[smooth-scroll-lenis]], [[lenis-nested-scroll-and-modals]] | copy_with_attribution | `stop` during the transition, `scrollTo(0, { immediate: true, force: true })` after the swap. |
| Scroll triggers that must rebuild after a swap | [[lenis-gsap-scrolltrigger-sync]] | license_review_required | `ScrollTrigger.refresh()` after mounting; tear down old triggers with `gsap.context`. |
| Timing budget | [[motion-principles]] | original | Page transition 300 to 600 ms per phase, `power3.inOut`. |
| Framework router (Next.js, Nuxt, Astro) | Keep the module and lifecycle from [[page-transition-gsap]]; let the framework swap content | license_review_required | How to intercept exits in each router is not covered by the cloned sources and is not verified. |

The browser's native cross-document view transitions are an alternative to evaluate; the catalog does not cover them, so check browser support and the platform documentation before relying on them.

Dials: total transition budget by `motion_intensity` (heuristic table in [[motion-principles]], the recipe treats it as the sum of cover and reveal): level 3 about 200 ms fade, 4 about 300 ms, 5 about 400 ms, 6 about 500 ms, 7 about 600 ms, 8 about 700 ms. `reduced_motion` either value: instant swap or a 150 ms fade.

## Search commands

```bash
design-sensei search "page transition" --category page-transition
design-sensei search "view transition theme" --category page-transition --scope all --limit 5
design-sensei search "layout animation flip" --category animation
design-sensei search "route change scroll reset" --scope docs
```

## Implementation steps

1. Confirm every page server-renders the same outlet element (for example `<main id="main">`) and shares one stylesheet. If not, drop the transition.
2. Add the overlay (`aria-hidden="true"`, `pointer-events: none`, hidden until script runs) and a visually hidden `aria-live="polite"` announcer. Set the initial transform with the animation library only, not CSS.
3. Intercept only same-origin, same-tab, unmodified left clicks. Leave modifier clicks, `target`, `download`, external and hash-only links to the browser.
4. Run the fetch in parallel with the cover animation; swap the outlet only when both finish. Any error falls back to `window.location.assign(url)`.
5. After the swap: update `document.title`, `history.pushState`, scroll to top, mount the new page's animations inside a `gsap.context` scoped to the outlet and `revert()` the old one, refresh ScrollTrigger on the next frame.
6. Move focus to the new outlet (`tabindex="-1"`, `focus({ preventScroll: true })`) and write the new title into the announcer.
7. Set `history.scrollRestoration = 'manual'` and handle `popstate` with the same flow (`push: false`). Guard against double clicks with a busy flag.
8. Send analytics page views yourself; scripts in fetched HTML do not run.
9. For theme reveals: write the transition rules from the public API, run the theme change inside the transition, and fall back to an immediate switch.

## Accessibility and performance gates

- Reduced motion: no overlay at all, instant swap, still scrolled to top, focus on `main`.
- Keyboard and screen reader: focus lands on the new content and the new title is announced; Tab continues from there; no focus lost during the transition.
- Back and Forward restore the correct page and scroll behaviour; failed fetch still navigates.
- The overlay is a transformed full-viewport layer: avoid blur and large shadows on it.
- Overlay colour comes from tokens and keeps contrast with the edges of both pages.
- Core Web Vitals: swap must not add layout shift (CLS at most 0.1); do not hide content so the new page's LCP element is delayed.
- `ScrollTrigger.getAll().length` must match the new page's own triggers after each navigation (it must not grow).

## Common mistakes

- Replaying entrance animations on every route change or re-render.
- Forgetting to stop and restart smooth scroll; leaving momentum after the swap.
- Not tearing down per-page animation, so triggers stack on every navigation.
- Treating the transition as mandatory: a slow fetch with a long animation feels broken.
- Copying Skiper UI code or its hotlinked GIF masks (no licence; ideas only).
- Treating GSAP as free to bundle everywhere: read its current terms before shipping; never copy its source.

## Where to read more

- Notes: [GSAP](../../../knowledge/animations/gsap.md), [Lenis](../../../knowledge/animations/lenis.md), [motion principles](../../../knowledge/animations/motion-principles-for-ui.md), [Skiper UI (reference only)](../../../knowledge/components/skiper-ui.md), [scroll storytelling](../../../knowledge/animations/scroll-storytelling.md).
- Recipes: [page transition with GSAP](../../../knowledge/implementation-recipes/page-transition-with-gsap.md), [Lenis smooth scroll setup](../../../knowledge/implementation-recipes/lenis-smooth-scroll-setup.md), [Lenis and ScrollTrigger sync](../../../knowledge/implementation-recipes/lenis-gsap-scrolltrigger-sync.md).
- Related playbooks: [navigation](navigation.md), [microinteractions](microinteractions.md), [scroll storytelling](scroll-storytelling.md), [cards and grids](cards-and-grids.md).
- References: [motion design](../references/motion-design.md), [accessibility](../references/accessibility.md).
