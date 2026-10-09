---
title: "Cursor proximity text (per-letter response)"
kind: recipe
summary: "Make each letter of a heading react to pointer distance with one measuring pass, event-driven animation frames instead of an always-on loop, CSS variables for the look, a touch and reduced-motion fallback, and full cleanup. Original code inspired by Fancy's proximity text components."
source_ids: [fancy]
pattern_ids: [fancy-cursor-proximity-text]
updated: "2026-10-09"
---

# Cursor proximity text

## Goal

Letters of a heading scale, lift or fade according to how close the pointer is, within a radius. The strength (0 to 1) is written to a CSS custom property on every letter, so the look is plain CSS.

## When to use

- Large display text on desktop: hero headings, posters, one to three lines.
- Do not use it for paragraphs: every letter is a box, so long text means many style writes and lost kerning.
- Touch screens have no hover, so the text stays static there by design.

## Where the idea comes from

Inspired by `fancy:src/fancy/components/text/text-cursor-proximity.tsx` (interpolates any CSS property by proximity), `fancy:src/fancy/components/text/variable-font-cursor-proximity.tsx` (font axes) and the ref-based pointer hook `fancy:src/hooks/use-mouse-position-ref.ts`. **The code below is original glue code written for Design Sensei and is not copied from Fancy.**

What upstream does, as read in the source: a `useAnimationFrame` loop runs for as long as the component is mounted and calls `getBoundingClientRect()` for the container and every letter on each frame; the pointer is tracked on `window`. Its docs advise limiting the text length (`fancy:src/content/docs/components/text/text-cursor-proximity.mdx`).

Differences in this recipe: letter centres are measured once with layout metrics (unaffected by the scale transform) and again on resize and font load; a pointer event schedules at most one update per frame, and nothing runs while the pointer is idle or outside; touch pointers are ignored; reduced motion leaves the letters untouched.

## Prerequisites

- React and `motion` (only for `useReducedMotion`; `matchMedia` works too). Fancy pins `motion` ^12.23.24 (`fancy:package.json`).
- Tailwind classes are optional; the CSS below is required.
- Status: type-checked with TypeScript 5.9 against `motion` 12.38 and React 19 types, and exercised in a jsdom test with stubbed layout metrics (strength 1 under the pointer, falling to 0 at the radius, reset on leave, no listeners under reduced motion). Not run in a real browser.

## Steps

1. Add the component, for example as `proximity-text.tsx`:

```tsx
"use client"

import { useEffect, useMemo, useRef, type RefObject } from "react"
import { useReducedMotion } from "motion/react"

type Falloff = "linear" | "smooth" | "sharp"

const falloffs: Record<Falloff, (distance: number, radius: number) => number> = {
  linear: (d, r) => Math.max(0, 1 - d / r),
  smooth: (d, r) => {
    const t = Math.max(0, 1 - d / r)
    return t * t * (3 - 2 * t) // smoothstep
  },
  sharp: (d, r) => Math.max(0, 1 - d / r) ** 2,
}

function toGraphemes(text: string): string[] {
  if (typeof Intl !== "undefined" && "Segmenter" in Intl) {
    const segmenter = new Intl.Segmenter(undefined, { granularity: "grapheme" })
    return Array.from(segmenter.segment(text), (part) => part.segment)
  }
  return Array.from(text)
}

type ProximityTextProps = {
  text: string
  /** Distance in px at which the effect has faded to zero. */
  radius?: number
  falloff?: Falloff
  /** Optional larger area to listen on (a card, a section). Defaults to the text itself. */
  container?: RefObject<HTMLElement | null>
  className?: string
}

export function ProximityText({
  text,
  radius = 120,
  falloff = "smooth",
  container,
  className,
}: ProximityTextProps) {
  const rootRef = useRef<HTMLSpanElement>(null)
  const letterRefs = useRef<(HTMLSpanElement | null)[]>([])
  const reduced = useReducedMotion() ?? false
  const words = useMemo(() => text.split(" ").map(toGraphemes), [text])
  const total = useMemo(() => words.reduce((sum, word) => sum + word.length, 0), [words])

  useEffect(() => {
    const root = rootRef.current
    if (!root || reduced) return // reduced motion: letters stay at --prox: 0

    const target = container?.current ?? root
    const letters = letterRefs.current.slice(0, total)
    const ease = falloffs[falloff]
    let centres: { x: number; y: number }[] = []
    let pointer: { x: number; y: number } | null = null
    let frame = 0
    let disposed = false

    // Layout metrics ignore transforms, so the scaled letters do not move their own targets.
    // The root is `relative`, which makes it the offsetParent of every letter.
    const measure = () => {
      if (disposed) return
      centres = letters.map((el) =>
        el
          ? { x: el.offsetLeft + el.offsetWidth / 2, y: el.offsetTop + el.offsetHeight / 2 }
          : { x: 0, y: 0 }
      )
    }

    const reset = () => letters.forEach((el) => el?.style.setProperty("--prox", "0"))

    const update = () => {
      frame = 0
      if (!pointer) return
      const box = root.getBoundingClientRect()
      const px = pointer.x - box.left - root.clientLeft
      const py = pointer.y - box.top - root.clientTop
      letters.forEach((el, i) => {
        if (!el || !centres[i]) return
        const strength = ease(Math.hypot(px - centres[i].x, py - centres[i].y), radius)
        el.style.setProperty("--prox", strength.toFixed(3))
      })
    }

    const onMove = (event: PointerEvent) => {
      if (event.pointerType === "touch") return // no hover on touch: text stays static
      pointer = { x: event.clientX, y: event.clientY }
      if (!frame) frame = requestAnimationFrame(update) // at most one update per frame
    }

    const onLeave = () => {
      pointer = null
      if (frame) cancelAnimationFrame(frame)
      frame = 0
      reset()
    }

    measure()
    const resizeObserver = new ResizeObserver(measure)
    resizeObserver.observe(root)
    document.fonts?.ready.then(measure) // web fonts change glyph widths after first paint
    target.addEventListener("pointermove", onMove)
    target.addEventListener("pointerleave", onLeave)

    return () => {
      disposed = true
      target.removeEventListener("pointermove", onMove)
      target.removeEventListener("pointerleave", onLeave)
      resizeObserver.disconnect()
      onLeave()
    }
  }, [container, falloff, radius, reduced, total])

  let index = 0
  return (
    <span ref={rootRef} className={["relative inline-block", className].filter(Boolean).join(" ")}>
      <span className="sr-only">{text}</span>
      <span aria-hidden="true">
        {words.map((word, wordIndex) => (
          <span key={wordIndex}>
            {wordIndex > 0 ? " " : null}
            <span className="inline-block whitespace-nowrap">
              {word.map((letter) => {
                const i = index++
                return (
                  <span
                    key={i}
                    ref={(el) => {
                      letterRefs.current[i] = el
                    }}
                    className="prox-letter inline-block"
                  >
                    {letter}
                  </span>
                )
              })}
            </span>
          </span>
        ))}
      </span>
    </span>
  )
}
```

2. Add the look in CSS. Change the numbers to taste, or drive opacity or colour from `--prox` instead:

```css
.prox-letter {
  transform: translateY(calc(var(--prox, 0) * -0.12em)) scale(calc(1 + var(--prox, 0) * 0.35));
  transition: transform 120ms ease-out;
}

@media (prefers-reduced-motion: reduce) {
  .prox-letter {
    transform: none;
    transition: none;
  }
}
```

3. Use it, optionally listening on a larger area such as the card around the heading:

```tsx
const card = useRef<HTMLDivElement>(null)

<div ref={card} className="p-12">
  <ProximityText text="Move closer" container={card} radius={160} className="text-5xl font-semibold" />
</div>
```

4. Tune `radius` and `falloff` (`linear`, `smooth`, `sharp`). Fancy's variable-font variant writes `font-variation-settings` from JavaScript; this recipe sticks to a CSS variable because custom-property maths inside that property was not verified here.

## How it works

- The root is `relative`, so it is the offset parent of every letter; `offsetLeft` and `offsetWidth` give the centres without being affected by the transform the effect applies.
- `pointermove` stores the pointer and schedules one animation frame. The frame reads one rectangle (the root), computes distance and falloff per letter and writes `--prox`. `pointerleave` cancels the frame and resets every letter to 0.
- A `ResizeObserver` and `document.fonts.ready` re-measure when the layout or the web font changes. Cleanup removes the listeners, the observer and any pending frame.
- Words sit in `nowrap` boxes so lines break between words. An `sr-only` copy carries the text for screen readers and the letter layer is `aria-hidden`.

## Verification checklist

- Mouse: letters near the pointer respond, the response fades to zero at the radius, leaving the area resets all letters.
- Idle pointer: the Performance panel shows no scripting frames while the mouse is still.
- Reload with a web font: centres still match the glyphs after the font swaps in.
- Emulate `prefers-reduced-motion: reduce` and a touch device: letters never change.
- 200 percent zoom and a narrow viewport: words wrap as whole words.
- Console: no errors on route change; in Chrome use `getEventListeners` on the container to confirm nothing is left behind.
- Overlap: at full strength neighbouring letters should not collide; lower the scale or add letter spacing.

## Pitfalls

- Do not add other positioned wrappers between the root and the letters: the measurement assumes the root is their offset parent.
- Per-letter boxes break kerning and ligatures; keep it to display text.
- Smoothness comes from the CSS `transition`, not from per-frame easing in script.
- Scaled ancestors are not handled: the layout metrics ignore an ancestor's scale, while the pointer position is computed from a rectangle that includes it.

## Upstream references

- `fancy:src/fancy/components/text/text-cursor-proximity.tsx`, `fancy:src/fancy/components/text/variable-font-cursor-proximity.tsx`, `fancy:src/fancy/components/text/variable-font-and-cursor.tsx`, `fancy:src/hooks/use-mouse-position-ref.ts`.
- Observed there: three falloff curves (linear, exponential, gaussian), per-frame layout reads, and hook calls inside loops in `text-cursor-proximity.tsx`; see `knowledge/components/fancy.md`.

## Licence notes

The code on this page is original. Fancy is MIT (`fancy:LICENSE`, Copyright (c) 2024 Daniel Petho); keep its notice if you copy any Fancy file.
