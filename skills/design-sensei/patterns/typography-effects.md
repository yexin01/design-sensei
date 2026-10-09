# Typography effects playbook

Choose and build animated or expressive text (reveals, swaps, scramble, variable-font motion, counters) without hurting readability, layout stability or screen-reader output.

In this file `design-sensei` means `${CLAUDE_SKILL_DIR}/scripts/design-sensei`.

## When to use / when not

- Use for hero statements, section openers, short labels, stats and brand moments. Do the static type system first ([typography reference](../references/typography.md)).
- Not for body copy, forms, errors, legal text or anything read under time pressure. Per-letter spans break kerning, ligatures and selection.
- Limit any animated unit to about twelve words ([kinetic typography note](../../../knowledge/design-styles/kinetic-typography.md)). One kinetic element per viewport.

## Pick the approach

| Need | Pick | Reuse class | Notes |
| --- | --- | --- | --- |
| Type scale and semantic roles | [[astryx-typography-scale]] | copy_with_attribution | Base size plus ratio generate sizes and leading. Use even if you do not adopt the components: the method transfers. |
| Style direction for moving type | [[style-kinetic-typography]] | copy_with_attribution | Rules: real text, short units, a reason, a static state. |
| Masked slide-up reveal, no GSAP | [[fancy-vertical-cut-reveal]] | copy_with_attribution | Motion library. Reduced motion: `transition={{ duration: 0 }}` and `staggerDuration={0}`. |
| Masked line reveal with re-split on resize | [[gsap-split-text-reveal]] | license_review_required | GSAP terms; SplitText `autoSplit` handles resize and fonts. Recipe included. |
| Line-by-line blur-to-sharp headline | [[vengeance-ui-gooey-text-reveal]] | copy_with_attribution | Skips itself under reduced motion. Depends on GSAP. Safari untested, one filter layer per line: one or two headings only. |
| Scroll-triggered GSAP text family | [[react-bits-gsap-text-reveals]] | license_review_required | Add your own reduced-motion branch for SplitText, ScrollReveal. Install into your app only. |
| Lighter text effects (blur-in, shiny, gradient, count-up) | [[react-bits-lightweight-text-effects]] | license_review_required | ShinyText and GradientText need no package. DecryptedText ships screen-reader text. |
| Masked word or letter slide-up, flip-fade cycler, count-up | [[vengeance-ui-kinetic-text-effects]] | copy_with_attribution | None handles reduced motion or labels split text; use the motion-safe wrapper. `morph-text` hides words at opacity 0. |
| Hover label roll in nav or buttons | [[fancy-letter-swap-text]] | copy_with_attribution | Recipe adds focus support and reduced motion. |
| Rotating phrases | [[fancy-text-rotate]] | copy_with_attribution | Default `auto` replaces text every 2 s: set `auto={false}` or add a pause. |
| Scramble or decode | [[fancy-scramble-text]] | copy_with_attribution | Upstream puts the live string in the screen-reader span; override so it is the final string. Under reduce, render plain text. |
| Weight or width animation | [[fancy-variable-font-text]] | copy_with_attribution | Needs a font with the named axes. Never mount Breathing Text under reduced motion (endless loop). |
| Marker highlight on key phrase | [[fancy-text-highlighter]] | copy_with_attribution | Under reduce, `transition={{ duration: 0 }}`. |
| Letters follow the pointer | [[fancy-cursor-proximity-text]] | copy_with_attribution | See [cursor interactions](cursor-interactions.md). Large display text on desktop only. |
| Counters and stats | stats-counter in [[vengeance-ui-kinetic-text-effects]] or CountUp in [[react-bits-lightweight-text-effects]] | mixed | Show the final value under reduced motion; use tabular numerals. |

Dials: `motion_intensity` 1-3 allows underline or colour changes only; 4-6 one reveal per section; 7+ allows a hero kinetic moment plus one hover effect. `design_variance` high favours display type at 8-20vw and axis motion; low favours plain fade-up of whole lines.

## Search commands

```bash
design-sensei search "text reveal" --category typography --reduced-motion-safe
design-sensei search "variable font" --category typography
design-sensei search "headline" --category typography --max-gpu none --framework react
design-sensei search "kinetic typography" --scope docs
```

## Implementation steps

1. Fix the static state: font families (with the axes you will animate), `clamp()` sizes, tracking, measure. Hero example from the note: `clamp(3rem, 12vw, 14rem)`, line-height 0.85 to 1.0.
2. Load fonts with `font-display` and preload; split only after fonts are ready (`document.fonts.ready`), or let SplitText `autoSplit` re-split.
3. Choose the unit: words for headings of more than a few words, characters only for strings under about 40 characters (heuristic from [[motion-principles]]). Stagger 20-60 ms per character with the total near 800 ms at most.
4. Accessible output: render the full string once (`sr-only` text or `aria-label`) and mark fragments `aria-hidden`. For scramble, the accessible text is the final string.
5. Reserve space (`min-height`, `ch` widths, inline-block with the heaviest weight) so swaps and axis changes cause no layout shift. Add vertical padding to reveal masks so descenders are not clipped.
6. Reduced motion before motion: final text immediately, no stagger or scramble; replace with a 150 ms fade at most. Use `useReducedMotion`, `matchMedia` or `gsap.matchMedia()`, not only a CSS kill switch (see the `morph-text` warning in the [motion-safe recipe](../../../knowledge/implementation-recipes/vengeance-ui-motion-safe-wrapper.md)).
7. Keep content visible by default; hide only when script runs, with a timer failsafe ([GSAP recipe](../../../knowledge/implementation-recipes/gsap-text-reveal-and-stagger.md)).
8. One animation library per effect: Motion, GSAP or CSS, not a mix on the same element.

## Accessibility and performance gates

- Contrast 4.5:1 body, 3:1 large text, in every frame of the animation; aim higher on animated text (the note suggests 7:1 as a heuristic). No `mix-blend-mode` text over video without a solid fallback.
- WCAG 2.2.2: loops over 5 s need pause or stop; flashing at most three times per second.
- Text must survive 200 percent zoom and user text-spacing overrides.
- Hover-only triggers need a focus path; touch has no hover.
- Test with a screen reader that a split headline reads as one phrase (`aria: "auto"` behaviour should be verified, not assumed).
- Split text re-flows on resize: test 320 to 1280 px. Heavy splitting and per-frame measuring (proximity text) cost main-thread time; check INP stays at most 200 ms.

## Common mistakes

- The same fade-up wrapper on every heading, with no hierarchy of motion.
- Letter-by-letter reveals on paragraphs; scramble on navigation links.
- Splitting before fonts load; weight changes that reflow lines.
- `autoAlpha: 0` on text that must stay readable by assistive technology (it also hides from the accessibility tree); use `opacity`.
- Copying React Bits components into a shared package or template (licence gate); GSAP source or `dist` files copied into the repo.

## Where to read more

- Notes: [Fancy components](../../../knowledge/components/fancy.md), [GSAP](../../../knowledge/animations/gsap.md), [motion principles](../../../knowledge/animations/motion-principles-for-ui.md), [kinetic typography](../../../knowledge/design-styles/kinetic-typography.md), [Astryx themes and tokens](../../../knowledge/components/astryx-themes-and-tokens.md).
- Recipes: [GSAP text reveal and stagger](../../../knowledge/implementation-recipes/gsap-text-reveal-and-stagger.md), [letter swap](../../../knowledge/implementation-recipes/fancy-letter-swap-text.md), [cursor proximity text](../../../knowledge/implementation-recipes/fancy-cursor-proximity-text.md), [gooey text hero](../../../knowledge/implementation-recipes/vengeance-ui-gooey-text-hero-nextjs.md), [React Bits install](../../../knowledge/implementation-recipes/react-bits-choose-variant-and-install.md).
- Related playbooks: [hero sections](hero-sections.md), [navigation](navigation.md), [cursor interactions](cursor-interactions.md), [scroll storytelling](scroll-storytelling.md).
- References: [typography](../references/typography.md), [motion design](../references/motion-design.md), [accessibility](../references/accessibility.md).
