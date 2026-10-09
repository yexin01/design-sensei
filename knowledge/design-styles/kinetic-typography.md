---
title: "Kinetic typography"
kind: design-style
summary: "Type as moving material: staggered reveals, variable-font morphing, scramble and decode, cursor proximity, scroll-linked and path-bound text. Rules for keeping text real, short and accessible, with a required static reduced-motion state and verified Motion and GSAP building blocks."
source_ids: [fancy, gsap, react-bits, vengeance-ui]
pattern_ids: [style-kinetic-typography]
updated: "2026-10-09"
---

# Kinetic typography

Kinetic typography makes letterforms the moving subject: reveals by character, word or line, weight and width changing along variable-font axes, scramble and decode effects, letters reacting to the cursor, text scrolling as bands or running along a path. One animated statement can make a page feel physical. Animated everywhere, it makes text unreadable, slow and inaccessible. Four rules hold throughout: keep the text real, keep the animated unit short, animate for a reason, and always ship a static state.

## Visual characteristics
- Display type at 8-20vw as the main visual, often with one or two typefaces and a monochrome or two-colour scheme so motion is what you notice.
- A motion vocabulary: stagger reveals, mask and cut reveals, scramble, letter swaps, axis morphing (weight, width, slant), cursor proximity, scroll-linked scale or skew, tickers, text on a path.
- Tight leading, extreme scale contrast, outline-to-fill transitions, text masks over imagery.

## When it fits, when it does not
- Fits: hero statements, brand moments, section openers, loaders, campaign and event microsites, portfolios, music, fashion and cultural sites.
- Poor fit: body copy, forms, error messages, documentation, legal text, anything read under time pressure. Limit any animated unit to about twelve words.
- Supporting influences that work: editorial, brutalism, swiss-international-typographic, maximalism, motion-led-storytelling, cyberpunk. Combine with minimalism only if the motion stays restrained.

## Typography
- Choose faces with the axes you will animate: variable fonts with `wght`, `wdth`, `slnt` or `opsz` (Roboto Flex, Bricolage Grotesque, Fraunces, Anybody, Recursive). Positional-only motion works with any display face.
- Hero size `clamp(3rem, 12vw, 14rem)`, line-height 0.85-1.0, resting tracking -0.03 to -0.06em. Do not animate tracking over large ranges; it reflows lines.
- Animate axes only on short strings, inside fixed-width `inline-block` or `ch`-sized containers so neighbours do not shift.
- Split and measure after fonts load (`document.fonts.ready`). Per-character `inline-block` spans break kerning, so split long strings by word.

## Colour
- Motion lowers legibility, so exceed the minimum: aim for 7:1 on animated text, never below 3:1 for large text.
- Use colour to mark state sparingly (outline to fill, one accent on the letters near the cursor). Do not animate the colour of long strings.
- Text with `mix-blend-mode: difference` over video has unpredictable contrast; provide a solid fallback.

## Composition and layout
- One kinetic element per viewport and a static surround.
- Reserve space (`min-height`, fixed `ch` widths) so scramble and swap effects cause no layout shift.
- Reveal masks need extra line padding so descenders are not clipped, and must survive user text-spacing overrides (WCAG 1.4.12).
- Tickers: duplicate copies are `aria-hidden`, and the band pauses on hover and focus.
- Touch screens have no hover. Cursor-proximity effects need a scroll-driven alternative or must simply not exist on touch.

## Interaction and motion
- Per-unit entrances 400-900 ms; stagger 20-60 ms per character with the total capped near 800 ms (stagger by word for long strings); ease-out-expo such as `cubic-bezier(0.16, 1, 0.3, 1)` or a spring.
- Triggers: when scrolled into view, on hover, or on scroll progress. Loops only if slow (cycles of four seconds or more) and pausable.
- Reduced motion (required): render the final text immediately with no stagger, scramble or axis morph; replace scramble with a 150 ms opacity fade; turn tickers into static text or a manually scrollable row; leave scroll-linked effects off. Implement with `matchMedia('(prefers-reduced-motion: reduce)')`, Motion's `useReducedMotion`, or `gsap.matchMedia()`.

## Accessibility cautions
- When text is split into spans, expose the full string once (`sr-only` text or `aria-label`) and hide the fragments with `aria-hidden`. The local fancy components do this.
- For scramble effects the accessible copy must be the final string, not the live one.
- Loops over five seconds need pause, stop or hide (WCAG 2.2.2); keep flashing below three per second (2.3.1).
- Fixed-size containers clip at 200% zoom; size in relative units. Never animate text that carries status or errors.

## Common mistakes
- Every heading wrapped in the same fade-up component; no hierarchy of motion.
- Letter-by-letter reveals on paragraphs.
- Splitting before fonts load, then misaligned glyphs; layout shift from weight changes.
- Cursor effects with no touch alternative; no reduced-motion branch.

## Typical mistakes of AI-generated versions
- A character-splitting wrapper on every heading with identical timing, spans without `aria-hidden`, and no reduced-motion handling.
- Infinite marquees on everything, and hover scramble on navigation links so the menu is unreadable.
- Two animation libraries driving the same elements.

## How to build it
- Pattern: `style-kinetic-typography`. Write the static final state first, then the reduced-motion path, then add motion.
- Verified Motion-based components in `fancy` (all use `motion/react`): `fancy:src/fancy/components/text/variable-font-cursor-proximity.tsx` (props `fromFontVariationSettings`, `toFontVariationSettings`, `containerRef`, `radius` (50), `falloff`; it measures every glyph each frame, so keep strings short; it renders an `sr-only` copy), `fancy:src/fancy/components/text/breathing-text.tsx` (an endless mirrored axis morph with stagger; it reserves width for the heaviest weight with an invisible pseudo-element to prevent layout shift, a technique worth reusing, but the endless loop needs a pause or reduced-motion guard), `fancy:src/fancy/components/text/vertical-cut-reveal.tsx` (`splitBy`, `staggerDuration`, `staggerFrom`, spring defaults of stiffness 190 and damping 22), `fancy:src/fancy/components/text/scramble-hover.tsx` and `fancy:src/fancy/components/text/text-along-path.tsx` (`animationType` of `auto` or `scroll`). None has a reduced-motion branch.
- `fancy:src/fancy/components/text/scramble-hover.tsx` places the live scrambled string in its `sr-only` span; override it so the hidden text is the final string.
- GSAP: `gsap:src/SplitText.js` offers `type` (`chars,words,lines`), `mask`, `autoSplit`, `onSplit`, an `aria` option defaulting to `auto`, and `revert()`; `gsap:src/ScrollTrigger.js` handles scroll-linked cases. Use the npm package under the GSAP no-charge licence and do not copy its source.
- Described only because react-bits is licence-restricted: `react-bits:src/content/TextAnimations/SplitText/SplitText.jsx`, `react-bits:src/content/TextAnimations/VariableProximity/VariableProximity.jsx` and `react-bits:src/content/TextAnimations/ScrollFloat/ScrollFloat.jsx`. `vengeance-ui:src/components/ui/cyber-glitch-text.tsx` is a scramble example with no hidden final text.

## Sources
Original guidance written for this project. fancy and vengeance-ui are MIT-licensed; gsap uses GreenSock's no-charge licence and react-bits is MIT with the Commons Clause, so both are described and referenced by path only.
