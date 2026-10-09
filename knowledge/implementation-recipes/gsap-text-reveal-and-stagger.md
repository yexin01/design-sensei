---
title: "Recipe: GSAP text reveal and stagger"
kind: recipe
summary: "Reveal card grids with batched ScrollTrigger staggers, split headlines into masked lines with SplitText, and compose a hero intro timeline with labels and positions, each with a reduced-motion branch and clean teardown."
source_ids: [gsap]
pattern_ids: [gsap-stagger-reveal, gsap-split-text-reveal, gsap-timeline-choreography]
updated: "2026-10-09"
---

# Recipe: GSAP text reveal and stagger

## Goal

Three reusable reveals that never hide content from visitors who cannot or should not see motion: (A) a staggered reveal
for repeated items, (B) a masked line reveal for a headline, (C) a hero intro timeline.

## When to use, and when not

Use for landing heroes, feature grids and short headlines. Do not split long body copy: splitting wraps text in many
elements, which can affect selection, translation and find-in-page (test them) and costs layout work on every re-split.
Skip the recipe when `allowed_dependencies` forbids GSAP; use the IntersectionObserver version in
`knowledge/animations/motion-principles-for-ui.md`.

## Prerequisites

- `gsap` 3.15.0 (`gsap:package.json`): `npm i gsap`. Plugins used: ScrollTrigger (`gsap/ScrollTrigger`) and SplitText
  (`gsap/SplitText`); both files exist in the package (`gsap:esm/ScrollTrigger.js`, `gsap:esm/SplitText.js`) and the README
  lists SplitText among the plugins available at no charge. GSAP has a custom licence: read `knowledge/animations/gsap.md`
  and https://gsap.com/standard-license before shipping.
- Web fonts should be declared with `font-display` and preloaded when possible; line splitting depends on final metrics.

## Steps

### 1. Register the plugins once

```ts
// lib/gsap.ts
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { SplitText } from 'gsap/SplitText'

if (typeof window !== 'undefined') gsap.registerPlugin(ScrollTrigger, SplitText)

export { gsap, ScrollTrigger, SplitText }
```

### 2. Keep content visible by default

An inline script in `<head>` adds `js` to `<html>`. Hidden starting states apply only when script runs and motion is allowed,
and a CSS timer reveals the hero if script fails later.

```css
@media (prefers-reduced-motion: no-preference) {
  .js [data-hero] { visibility: hidden; animation: hero-failsafe 0s 2.5s forwards; }
}
@keyframes hero-failsafe { to { visibility: visible; } }

/* Masks clip with overflow: clip; give glyph overhang room without moving the layout. */
.split-line-mask { padding-block: 0.1em; margin-block: -0.1em; }
```

Why `from`/`fromTo` and not a CSS `opacity: 0` on every target: a `from` tween animates toward the element's current
value, so a CSS-hidden element would tween from 0 to 0 and never appear. Only the hero container is hidden by CSS, and
GSAP reveals the container itself with `autoAlpha`.

### 3. Part A: staggered reveal for repeated items

```js
import { gsap, ScrollTrigger } from './lib/gsap'

export function revealCards(root = document) {
  const mm = gsap.matchMedia()

  mm.add('(prefers-reduced-motion: no-preference)', () => {
    const cards = gsap.utils.toArray('[data-card]', root)
    if (!cards.length) return

    gsap.set(cards, { autoAlpha: 0, y: 28 })

    ScrollTrigger.batch(cards, {
      start: 'top 88%',
      once: true,
      batchMax: 8,
      onEnter: (batch) =>
        gsap.to(batch, {
          autoAlpha: 1,
          y: 0,
          duration: 0.6,
          ease: 'power3.out',
          stagger: { each: 0.07 },
          overwrite: true,
        }),
    })
  })

  return mm
}
```

`ScrollTrigger.batch` creates one trigger per card and groups the callbacks that fire close together, so a row of cards
staggers as one unit (`gsap:types/scroll-trigger.d.ts`: `BatchVars` has `interval`, `batchMax`, `onEnter`, `once`).
Spread is capped at 8 items x 70 ms, inside the 400 to 600 ms stagger guideline. Under `reduce` the callback never runs and
the cards stay as authored.

### 4. Part B: masked line reveal for a headline

```js
import { gsap, SplitText } from './lib/gsap'

export function revealHeadline(el) {
  const mm = gsap.matchMedia()

  mm.add('(prefers-reduced-motion: no-preference)', () => {
    SplitText.create(el, {
      type: 'lines',
      mask: 'lines',
      linesClass: 'split-line',
      autoSplit: true,
      onSplit: (self) =>
        gsap.from(self.lines, {
          yPercent: 110,
          duration: 0.9,
          ease: 'power4.out',
          stagger: 0.08,
          scrollTrigger: { trigger: el, start: 'top 85%', once: true },
        }),
    })
  })

  return mm
}
```

How it behaves, from `gsap:src/SplitText.ts` and `gsap:types/split-text.d.ts`:

- `type: 'lines'` splits only what is animated (the default is chars, words and lines).
- `mask: 'lines'` wraps each line in a clone with `overflow: clip`; its class is the line class plus `-mask`, which is why
  `linesClass` is set and why the CSS above targets `.split-line-mask`.
- `autoSplit: true` (lines only) re-splits when the element resizes and when fonts finish loading. Because `onSplit`
  returns the animation, SplitText reverts it before re-splitting and restores its time on the new one, so a resize
  mid-reveal does not restart or break it.
- The instance registers with the active context, so `mm.revert()` restores the original markup. Outside a context or
  matchMedia, call `split.revert()` yourself.
- Accessibility: with `aria: 'auto'` (the default) the container receives an `aria-label` with the full text and each
  generated wrapper gets `aria-hidden="true"`. That is dependable on headings (`h1` to `h6`); on paragraphs a screen
  reader may ignore the label, so verify, and avoid splitting paragraph text.

### 5. Part C: hero intro timeline

```html
<section data-hero>
  <p data-hero-eyebrow>Eyebrow</p>
  <h1 data-hero-title>Headline</h1>
  <p data-hero-copy>Supporting copy</p>
  <a data-hero-action href="#start">Primary</a>
  <a data-hero-action href="#more">Secondary</a>
  <img data-hero-media src="hero.jpg" width="1200" height="800" alt="">
</section>
```

Animate a given headline with Part B or with the `title` entry below, not both.

```js
import { gsap } from './lib/gsap'

export function heroIntro(root = document) {
  const mm = gsap.matchMedia()

  mm.add(
    { motion: '(prefers-reduced-motion: no-preference)', reduce: '(prefers-reduced-motion: reduce)' },
    (ctx) => {
      const hero = root.querySelector('[data-hero]')
      if (!hero || ctx.conditions.reduce) return // content is already visible

      const part = (name) => hero.querySelectorAll(`[data-hero-${name}]`)
      gsap.set(hero, { autoAlpha: 1 })

      gsap
        .timeline({ defaults: { duration: 0.6, ease: 'power3.out' } })
        .from(part('eyebrow'), { autoAlpha: 0, y: 12 })
        .addLabel('title', '<0.1')
        .from(part('title'), { autoAlpha: 0, y: 28, duration: 0.8 }, 'title')
        .from(part('copy'), { autoAlpha: 0, y: 20 }, 'title+=0.2')
        .from(part('action'), { autoAlpha: 0, y: 16, stagger: 0.06 }, '>-0.3')
        .from(part('media'), { autoAlpha: 0, scale: 0.98, duration: 0.9 }, 'title+=0.1')
    },
  )

  return mm
}
```

Position strings, as parsed by `_parsePosition` in `gsap:src/gsap-core.js`: `'<0.1'` is 0.1 s after the previous child
starts; `'title'` is a label; `'title+=0.2'` is 0.2 s after that label; `'>-0.3'` is 0.3 s before the end of the previously
added child. Resulting starts: eyebrow 0, title 0.1, media 0.2, copy 0.3, actions about 0.6; the timeline lasts about
1.3 s, which is `motion_intensity` 5 to 6. Shorten durations for lower levels. Steps overlap on purpose.
`defaults` set shared duration and ease so each line only states what differs. `autoAlpha` also toggles `visibility`, which is
fine for decorative reveals; for content that must remain readable by assistive technology while transparent, tween
`opacity` instead.

### 6. Teardown

```js
const reveals = [revealCards(), revealHeadline(document.querySelector('[data-headline]')), heroIntro()]
// on route change or unmount:
reveals.forEach((mm) => mm.revert())
```

In React, create all three inside one `gsap.context(fn, scopeRef)` in `useEffect` and return `ctx.revert()`.

## Verification checklist

- [ ] JavaScript disabled: everything visible, in order.
- [ ] `prefers-reduced-motion: reduce` emulated: no movement, no hidden content; toggling it live switches without reload.
- [ ] Resize the window and swap fonts: lines re-split, no duplicate text in the DOM, mask padding keeps descenders intact.
- [ ] After `revert()` the headline markup equals the original and `ScrollTrigger.getAll().length` is 0.
- [ ] Screen reader reads the split headline once; text selection and copy work.
- [ ] Timeline length and stagger spread respect the `motion_intensity` budget in `motion-principles-for-ui`.
- [ ] No layout shift when the hero appears (check CLS); console is clean.

## Upstream references

`gsap:types/split-text.d.ts`, `gsap:src/SplitText.ts`, `gsap:types/scroll-trigger.d.ts`, `gsap:types/timeline.d.ts`,
`gsap:types/gsap-utils.d.ts`, `gsap:src/gsap-core.js`, `gsap:README.md`. Overview: `knowledge/animations/gsap.md`.

## Licence notes

The recipe calls the public API of the `gsap` npm package as an external dependency and contains only original code;
nothing from GSAP's source is copied or quoted. GSAP's terms are custom, and `catalog/licenses.yaml` marks the review
`needs_human_review`; a person must read https://gsap.com/standard-license before use. This is not legal advice.
