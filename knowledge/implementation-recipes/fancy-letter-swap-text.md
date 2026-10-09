---
title: "Letter swap text (hover roll) with Motion"
kind: recipe
summary: "Build a short label whose letters roll up into a duplicate on hover or keyboard focus, staggered, with one screen-reader label, cleanup of listeners and animations, and a no-movement reduced-motion variant. Original code inspired by the Fancy letter-swap components."
source_ids: [fancy]
pattern_ids: [fancy-letter-swap-text]
updated: "2026-10-09"
---

# Letter swap text (hover roll)

## Goal

A short label (navigation item, button, footer link) whose letters roll up and are replaced by an identical copy, one after another, when the pointer enters the link or button around it or keyboard focus lands on it. Leaving rolls them back.

## When to use

- Navigation links, buttons and short link-like headings of roughly 3 to 20 characters.
- Do not use it for body text or anything that wraps: every letter becomes its own box, so kerning and ligatures are lost.
- Do not rely on it where hover is the only way to reveal information.

## Where the idea comes from

Inspired by `fancy:src/fancy/components/text/letter-swap-pingpong-anim.tsx` (hover plays forward, leave plays back) and `fancy:src/fancy/components/text/letter-swap-forward-anim.tsx`, documented in `fancy:src/content/docs/components/text/letter-swap.mdx`. **The code below is original glue code written for Design Sensei. It is not copied from Fancy** and only calls the public `motion/react` API.

Differences from upstream: one track per letter holds two stacked copies, so no reset step is needed; listeners sit on the closest link or button, so keyboard focus works (upstream reacts to the mouse only); no lodash debounce; reduced motion is handled; listeners and playback are stopped on unmount.

## Prerequisites

- React and `motion`. Fancy pins `motion` ^12.23.24 and React ^19.2.1 (`fancy:package.json`); the code uses `stagger`, `useAnimate` and `useReducedMotion` from `motion/react`, all of which Fancy components also import.
- Tailwind CSS for the class names (`sr-only`, `select-none`, `motion-reduce:`, `data-[active=true]:`). Use plain CSS if you do not run Tailwind.
- Status: type-checked with TypeScript 5.9 against `motion` 12.38 and React 19 types, and exercised in a jsdom test for listener setup, teardown, state changes and the reduced-motion branch. It was not run in a real browser, so use the checklist below.

## Steps

1. Install `motion`.
2. Add the component, for example as `letter-swap.tsx`:

```tsx
"use client"

import { useEffect, useMemo, useRef } from "react"
import { stagger, useAnimate, useReducedMotion } from "motion/react"

type LetterSwapProps = {
  label: string
  /** Delay between neighbouring letters, in seconds. */
  step?: number
  className?: string
}

// Keep emoji and combined characters in one piece.
function toGraphemes(text: string): string[] {
  if (typeof Intl !== "undefined" && "Segmenter" in Intl) {
    const segmenter = new Intl.Segmenter(undefined, { granularity: "grapheme" })
    return Array.from(segmenter.segment(text), (part) => part.segment)
  }
  return Array.from(text)
}

export function LetterSwap({ label, step = 0.03, className }: LetterSwapProps) {
  const [scope, animate] = useAnimate<HTMLSpanElement>()
  const reduced = useReducedMotion() ?? false
  const letters = useMemo(() => toGraphemes(label), [label])
  const playback = useRef<ReturnType<typeof animate> | null>(null)

  useEffect(() => {
    const root = scope.current
    if (!root) return

    // Listen on the closest link or button so keyboard focus triggers the swap too.
    const host = root.closest<HTMLElement>("a, button, [role='button']") ?? root

    const setActive = (active: boolean) => {
      root.dataset.active = String(active) // styling hook, also used by the reduced-motion cue
      if (reduced) return // reduced motion: no movement at all
      playback.current?.stop()
      playback.current = animate(
        ".swap-track",
        { y: active ? "-50%" : "0%" },
        { type: "spring", duration: 0.5, bounce: 0, delay: stagger(step) }
      )
    }
    const on = () => setActive(true)
    const off = () => setActive(false)

    host.addEventListener("pointerenter", on)
    host.addEventListener("pointerleave", off)
    host.addEventListener("focusin", on)
    host.addEventListener("focusout", off)

    return () => {
      host.removeEventListener("pointerenter", on)
      host.removeEventListener("pointerleave", off)
      host.removeEventListener("focusin", on)
      host.removeEventListener("focusout", off)
      playback.current?.stop()
    }
  }, [animate, scope, reduced, step])

  const rootClass = [
    "inline-flex whitespace-nowrap",
    // Reduced-motion cue: dim slightly while the link or button is hovered or focused.
    "motion-reduce:data-[active=true]:opacity-70",
    className,
  ]
    .filter(Boolean)
    .join(" ")

  return (
    <span ref={scope} data-active="false" className={rootClass}>
      <span className="sr-only">{label}</span>
      {letters.map((letter, index) => {
        const glyph = letter === " " ? "\u00A0" : letter
        return (
          <span
            key={index}
            aria-hidden="true"
            className="inline-block h-[1.2em] select-none overflow-hidden leading-[1.2]"
          >
            <span className="swap-track flex flex-col">
              <span>{glyph}</span>
              <span>{glyph}</span>
            </span>
          </span>
        )
      })}
    </span>
  )
}
```

3. Place it inside the element that should trigger it:

```tsx
<a href="/work" className="text-lg font-medium">
  <LetterSwap label="Selected work" />
</a>
```

4. Tune `step` (seconds between letters), the spring `duration` and `bounce`, and the box height (`h-[1.2em]`, `leading-[1.2]`) so descenders and accents are not clipped in your font.

## How it works

- Each glyph sits in an `overflow-hidden` box one line high. Inside it a flex column holds two identical copies; moving the column up by 50 percent brings the second copy into view.
- `stagger(step)` delays each glyph to make the wave. Leaving or blurring animates the same value back to 0.
- The component finds the closest link or button and listens there with `pointerenter`, `pointerleave`, `focusin` and `focusout`. If there is none it listens on itself.
- `data-active` mirrors the state on the root. Under `prefers-reduced-motion: reduce` nothing moves; the CSS variant only dims the label slightly while it is hovered or focused.
- Screen readers get one `sr-only` label and the glyph layers are `aria-hidden`, the same approach Fancy uses. `select-none` stops users selecting the doubled glyphs.
- Cleanup: the effect removes all four listeners and stops the running animation.

## Verification checklist

- Hover and Tab focus both trigger the effect; leaving or blurring reverses it; fast in-and-out never strands letters half way.
- DevTools, Rendering panel, emulate `prefers-reduced-motion: reduce`: no movement, label dims on hover and focus.
- Accessibility tree: the label appears once and no doubled letters can be selected.
- 200 percent zoom and a narrow viewport: no wrapping and no clipped descenders or accents. Test with your real font.
- Console: no hydration warnings (server markup equals client markup) and no errors after navigating away.
- Performance: only `transform` is animated; with dozens of instances nothing runs until a link is hovered or focused.
- On a phone: tapping a link should not leave letters stuck in the swapped state.

## Upstream references

- `fancy:src/fancy/components/text/letter-swap-pingpong-anim.tsx`, `fancy:src/fancy/components/text/letter-swap-forward-anim.tsx`, `fancy:src/fancy/components/text/random-letter-swap-forward-anim.tsx` and `fancy:src/content/docs/components/text/letter-swap.mdx`.
- Facts read there: the effect is mouse-hover only; the ping-pong and random variants use lodash debounce; the visible letters are `aria-hidden` next to an `sr-only` label.
- Overview and caveats: `knowledge/components/fancy.md`.

## Licence notes

The code on this page is original. Fancy is MIT (`fancy:LICENSE`, Copyright (c) 2024 Daniel Petho); if you copy a Fancy file instead of using this recipe, keep its copyright and permission notice.
