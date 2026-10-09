---
title: "Stacking cards on scroll (sticky and scale)"
kind: recipe
summary: "Build a pile of sticky cards that scale down as later cards stack over them, driven by scroll progress with Motion's useScroll and useTransform, with a no-scaling reduced-motion variant. Original code inspired by Fancy's Stacking Cards component."
source_ids: [fancy]
pattern_ids: [fancy-stacking-cards]
updated: "2026-10-09"
---

# Stacking cards on scroll

## Goal

Cards stick near the top of the viewport while the page scrolls. Each earlier card shrinks a little as the next one slides over it, so the pile looks like layered paper.

## When to use

- Case studies, feature lists, process steps: three to six cards of equal height.
- Avoid many cards or very tall cards on small screens, and avoid it when the content under the overlap must stay fully readable (earlier cards remain visible only as a strip).

## Where the idea comes from

Inspired by `fancy:src/fancy/components/blocks/stacking-cards.tsx` (its header comment credits Khoa Phan; the repository is MIT), the demo `fancy:src/fancy/examples/blocks/stacking-cards-demo.tsx` and the docs `fancy:src/content/docs/components/blocks/stacking-cards.mdx`. Upstream shares the scroll progress of a wrapper through React context and derives one scale per card with `useTransform`. **The code below is original glue code written for Design Sensei and is not copied from Fancy**; it only calls `useScroll`, `useTransform` and `useReducedMotion` from `motion/react`.

Differences: the wrapper tracks the window only (upstream also accepts scroll options for an inner container), and reduced motion removes the scaling while keeping the sticky layering.

## Prerequisites

- React and `motion` (Fancy pins `motion` ^12.23.24, `fancy:package.json`). Tailwind classes are optional.
- Status: type-checked with TypeScript 5.9 against `motion` 12.38 and React 19 types, server-rendered once, and rendered in jsdom. Scroll-linked behaviour was not run in a real browser.

## Steps

1. Add the components, for example as `card-stack.tsx`:

```tsx
"use client"

import { createContext, useContext, useRef, type ReactNode } from "react"
import {
  motion,
  useReducedMotion,
  useScroll,
  useTransform,
  type MotionValue,
} from "motion/react"

type StackState = {
  progress: MotionValue<number>
  total: number
  shrink: number
  reduced: boolean
}

const StackContext = createContext<StackState | null>(null)

function useStack(): StackState {
  const state = useContext(StackContext)
  if (!state) throw new Error("CardStackItem must be rendered inside CardStack")
  return state
}

type CardStackProps = {
  /** Number of CardStackItem children. */
  total: number
  /** How much each earlier card shrinks per card stacked after it (0.04 = 4%). */
  shrink?: number
  className?: string
  children: ReactNode
}

export function CardStack({ total, shrink = 0.04, className, children }: CardStackProps) {
  const ref = useRef<HTMLDivElement>(null)
  const reduced = useReducedMotion() ?? false
  // 0 when the stack's top reaches the viewport top, 1 when its bottom reaches the viewport bottom.
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end end"] })

  return (
    <StackContext.Provider value={{ progress: scrollYProgress, total, shrink, reduced }}>
      <div ref={ref} className={className}>
        {children}
      </div>
    </StackContext.Provider>
  )
}

type CardStackItemProps = {
  index: number
  /** Distance in px between the sticky offsets of neighbouring cards. */
  gap?: number
  className?: string
  children: ReactNode
}

export function CardStackItem({ index, gap = 16, className, children }: CardStackItemProps) {
  const { progress, total, shrink, reduced } = useStack()

  // The card starts shrinking when the cards after it begin to arrive, and ends at this scale.
  const endScale = reduced ? 1 : 1 - (total - 1 - index) * shrink
  const scale = useTransform(progress, [index / total, 1], [1, endScale])

  return (
    <div className="sticky" style={{ top: 24 + index * gap }}>
      <motion.div style={{ scale, transformOrigin: "top center" }} className={className}>
        {children}
      </motion.div>
    </div>
  )
}
```

2. Use them. Give every card the same explicit height; the stack takes its height from its cards:

```tsx
<CardStack total={cards.length} className="relative">
  {cards.map((card, index) => (
    <CardStackItem key={card.title} index={index} className="h-[70vh] rounded-3xl p-8">
      {card.content}
    </CardStackItem>
  ))}
</CardStack>
```

3. Tune `shrink` (scale lost per later card) and `gap` (pixels between sticky offsets). The first sticky offset is 24 px from the top; change it for a fixed header.
4. Make sure no ancestor between the stack and the page sets `overflow` to anything but `visible`: `position: sticky` pins to the nearest scrolling ancestor and will not work otherwise.

## How it works

- `useScroll` with `target` and the offset `["start start", "end end"]` gives a 0 to 1 value: 0 when the stack's top meets the viewport top, 1 when its bottom meets the viewport bottom. Fancy's component uses the same default offset.
- Each item is a `position: sticky` wrapper with a growing `top`, so later cards stop slightly lower and the earlier ones peek out above them.
- Inside, a `motion.div` scales from 1 to a per-card end value as the progress passes the card's own start fraction (`index / total`). The last card keeps scale 1.
- With reduced motion the end scale is 1, so cards still stack but nothing scales.

## Verification checklist

- Scroll down: cards stick at increasing offsets, earlier cards shrink progressively, the last card stays at full size. Scroll back up: it reverses without jumps.
- Emulate `prefers-reduced-motion: reduce`: layering stays, scaling stops.
- Test a 600 px high laptop viewport, a phone, and iOS Safari with its collapsing toolbar: card height plus offsets must fit.
- Temporarily set `overflow: hidden` on a parent to confirm that this is what breaks stickiness, then remove it.
- Console clean; no layout shift when the page loads.
- DevTools paint flashing should not flash the whole page while you scroll.

## Pitfalls

- Sticky breaks under any `overflow` ancestor, a frequent cause of "it just scrolls away".
- Scaled text can look soft while it moves; check legibility on your target screens.
- To track an inner scroll area instead of the window, pass `container` to `useScroll`. Fancy's docs say such a container needs a non-static position (see the scroll notes in `fancy:src/content/docs/components/text/scroll-and-swap.mdx`).
- Keep the card count in `total` equal to the number of items; a wrong value shifts every scale range.

## Upstream references

- `fancy:src/fancy/components/blocks/stacking-cards.tsx`, `fancy:src/fancy/examples/blocks/stacking-cards-demo.tsx`, `fancy:src/content/docs/components/blocks/stacking-cards.mdx`.
- Upstream notes: the card wrapper needs a defined height so `topPosition` works, and the scroll container can be changed through `scrollOptions`.
- Overview and caveats: `knowledge/components/fancy.md`.

## Licence notes

The code on this page is original. The upstream component is by Khoa Phan inside an MIT repository (`fancy:LICENSE`, Copyright (c) 2024 Daniel Petho); keep both the notice and the author comment if you copy that file.
