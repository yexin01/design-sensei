---
title: "Matter.js gravity pile for DOM chips"
kind: recipe
summary: "Make DOM labels fall and pile up under Matter.js while the DOM stays the visual layer: static layout without JavaScript or under reduced motion, physics only while visible, cached sizes, and full teardown of engine, runner, frames and observers. Original code inspired by Fancy's Gravity component."
source_ids: [fancy]
pattern_ids: [fancy-matter-gravity]
updated: "2026-10-09"
---

# Matter.js gravity pile for DOM chips

## Goal

A box of short labels (tags, skills, tech names) renders as a normal wrapped list. When the box scrolls into view the labels fall, collide and settle at the bottom. Resizing the window rebuilds the world.

## When to use

- Playful footers and "stack" sections with up to a few dozen short labels.
- Do not use it for essential navigation, long text or large element counts: every body costs physics time and the labels move until they settle.
- Reduced-motion visitors, visitors without JavaScript and crawlers get the static list, so that list must make sense on its own.

## Where the idea comes from

Inspired by `fancy:src/fancy/components/physics/gravity.tsx` and its docs `fancy:src/content/docs/components/physics/gravity.mdx`. **The code below is original glue code written for Design Sensei and is not copied from Fancy.**

What upstream does, as read in the source: it wraps children in a Matter.js world, creates rectangle, circle or SVG-path bodies, runs a Matter `Runner` plus Matter's own canvas renderer (transparent unless `debug`) and a separate `requestAnimationFrame` loop that writes a `transform` per body, and supports dragging through a mouse constraint. It rebuilds the world on resize (`resetOnResize`, debounced 500 ms).

Differences in this recipe: rectangle bodies only, no canvas renderer and no dragging, sizes cached once instead of read per frame, physics runs only while the box is on screen, the static flow layout is the fallback, and every observer, frame and body is removed on teardown.

## Prerequisites

- `matter-js` and `@types/matter-js`. Fancy pins `matter-js` ^0.20.0 and `@types/matter-js` ^0.19.7 (`fancy:package.json`). `motion` is used only for `useReducedMotion`; `matchMedia` works as well.
- Every Matter call used here (`Engine.create`, `Bodies.rectangle`, `World.add`, `Runner.create`, `Runner.run`, `Runner.stop`, `World.clear`, `Engine.clear`) also appears in `gravity.tsx`, so it is known to exist in the pinned version. Check Matter's own docs for newer replacements before upgrading.
- Status: type-checked against a local stand-in declaration for those calls (the real `@types/matter-js` was not installed) and run in jsdom against a stub of Matter, which verified build, run-once, pause, teardown and style restoration. It was not run against real Matter or in a browser.

## Steps

1. Install `matter-js` and `@types/matter-js`.
2. Add the component, for example as `gravity-pile.tsx`:

```tsx
"use client"

import { useEffect, useRef, useState, type RefObject } from "react"
import { useReducedMotion } from "motion/react"
import { Bodies, Engine, Runner, World } from "matter-js"

// Re-read the container size only after resizing has settled (matches the "reset on resize" idea).
function useSettledSize(ref: RefObject<HTMLElement | null>, delay = 250) {
  const [size, setSize] = useState({ width: 0, height: 0 })

  useEffect(() => {
    const el = ref.current
    if (!el) return
    let timer: ReturnType<typeof setTimeout> | undefined

    const read = () => {
      const width = el.clientWidth
      const height = el.clientHeight
      setSize((prev) => (prev.width === width && prev.height === height ? prev : { width, height }))
    }

    read()
    const observer = new ResizeObserver(() => {
      clearTimeout(timer)
      timer = setTimeout(read, delay)
    })
    observer.observe(el)

    return () => {
      clearTimeout(timer)
      observer.disconnect()
    }
  }, [ref, delay])

  return size
}

type GravityPileProps = {
  items: string[]
  /** Give the container an explicit height, for example "h-[420px]". */
  className?: string
  itemClassName?: string
  gravityY?: number
}

export function GravityPile({ items, className, itemClassName, gravityY = 1 }: GravityPileProps) {
  const hostRef = useRef<HTMLDivElement>(null)
  const itemRefs = useRef<(HTMLSpanElement | null)[]>([])
  const reduced = useReducedMotion() ?? false
  const size = useSettledSize(hostRef)

  useEffect(() => {
    const host = hostRef.current
    if (!host || reduced || size.width === 0 || size.height === 0) return

    const els = itemRefs.current
      .slice(0, items.length)
      .filter((el): el is HTMLSpanElement => el !== null)
    if (els.length === 0) return

    // 1. Read the static flow layout once. Sizes are cached, so no layout reads happen per frame.
    const rects = els.map((el) => ({
      x: el.offsetLeft,
      y: el.offsetTop,
      w: el.offsetWidth,
      h: el.offsetHeight,
    }))

    // 2. Build the physics world from those rectangles plus a floor and two side walls.
    const engine = Engine.create()
    engine.gravity.y = gravityY

    const bodies = rects.map((r) =>
      Bodies.rectangle(r.x + r.w / 2, r.y + r.h / 2, r.w, r.h, {
        restitution: 0.25,
        friction: 0.6,
        angle: (Math.random() - 0.5) * 0.3,
      })
    )
    const { width, height } = size
    const wall = 60
    World.add(engine.world, [
      ...bodies,
      Bodies.rectangle(width / 2, height + wall / 2, width * 2, wall, { isStatic: true }),
      Bodies.rectangle(-wall / 2, height / 2, wall, height * 2, { isStatic: true }),
      Bodies.rectangle(width + wall / 2, height / 2, wall, height * 2, { isStatic: true }),
    ])

    // 3. Take the elements out of flow and keep them in sync with the bodies.
    els.forEach((el) => {
      el.style.position = "absolute"
      el.style.left = "0"
      el.style.top = "0"
      el.style.willChange = "transform"
    })

    const draw = () => {
      bodies.forEach((body, i) => {
        const { w, h } = rects[i]
        els[i].style.transform = `translate(${body.position.x - w / 2}px, ${
          body.position.y - h / 2
        }px) rotate(${body.angle}rad)`
      })
    }
    draw() // same task as the style changes above, so there is no visible jump

    const runner = Runner.create()
    let frame = 0
    let running = false
    const loop = () => {
      draw()
      frame = requestAnimationFrame(loop)
    }
    const play = () => {
      if (running) return // Runner.run starts a new loop each call, so never call it twice
      running = true
      Runner.run(runner, engine)
      frame = requestAnimationFrame(loop)
    }
    const pause = () => {
      if (!running) return
      running = false
      Runner.stop(runner)
      cancelAnimationFrame(frame)
      frame = 0
    }

    // Run only while the container is on screen; the pile starts to fall when it scrolls into view.
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) play()
      else pause()
    })
    observer.observe(host)

    return () => {
      observer.disconnect()
      pause()
      World.clear(engine.world, false)
      Engine.clear(engine)
      els.forEach((el) => {
        el.style.position = ""
        el.style.left = ""
        el.style.top = ""
        el.style.transform = ""
        el.style.willChange = ""
      })
    }
  }, [items.length, reduced, size, gravityY])

  return (
    <div
      ref={hostRef}
      className={["relative flex flex-wrap content-start gap-2 overflow-hidden", className]
        .filter(Boolean)
        .join(" ")}
    >
      {items.map((label, i) => (
        <span
          key={`${label}-${i}`}
          ref={(el) => {
            itemRefs.current[i] = el
          }}
          className={["whitespace-nowrap", itemClassName].filter(Boolean).join(" ")}
        >
          {label}
        </span>
      ))}
    </div>
  )
}
```

3. Use it. The container needs an explicit height:

```tsx
<GravityPile
  items={["React", "Motion", "Matter", "Tailwind"]}
  className="h-[420px] rounded-3xl bg-neutral-100"
  itemClassName="rounded-full bg-black px-5 py-2 text-white"
/>
```

4. Tune `gravityY`, `restitution` (bounciness) and `friction` in the body options, and the wall thickness.

## How it works

1. The static flow layout is the baseline: the server renders it, visitors without JavaScript see it and reduced-motion users keep it.
2. In an effect, each item's rectangle is read once and turned into a body at the same position, plus a floor and two side walls sized from the container.
3. The items are taken out of flow and a frame loop writes `translate` and `rotate` from each body. Cached sizes mean no layout reads per frame.
4. An `IntersectionObserver` starts and stops the Matter runner and the frame loop together; a `running` flag prevents a second runner from starting.
5. A debounced `ResizeObserver` updates the size, which re-runs the effect and rebuilds the world, like upstream's reset on resize. Teardown stops everything, clears the world and engine and restores the inline styles.

## Verification checklist

- Before it is visible the list is static; scrolled into view, the labels drop, collide and settle at the bottom without leaving the box.
- Scroll away: the Performance panel shows scripting stops. Scroll back: it resumes at normal speed (a doubled speed means two runners are active).
- Resize the window: after about 250 ms the world rebuilds, with no duplicated items or stale transforms.
- Emulate `prefers-reduced-motion: reduce`: the labels stay as a static list.
- React Strict Mode in development: physics speed looks normal.
- Navigate away: no console errors and no frame loop left running.
- Load with a slow web font: labels must be sized for the final font (see pitfalls).
- Try 40 or more labels and watch frame time on a mid-range phone.

## Pitfalls

- Measure after web fonts load, otherwise the bodies are sized for the fallback font. Delay mounting until `document.fonts.ready` resolves if the font changes the label width.
- Labels must not wrap (the component adds `whitespace-nowrap`); wrapped text changes size when taken out of flow.
- Rectangle bodies approximate pill shapes, so small gaps appear at the corners.
- The frame loop keeps writing transforms while the box is visible, even after everything has settled. Consider pausing once bodies rest; Matter has a sleeping feature for that, which was not verified here.
- Dragging needs Matter's mouse constraint on a canvas, as upstream does. It is not included, and how Matter's mouse handling interacts with page scrolling was not verified.
- Resizing rebuilds the world, so the pile restarts from the top.

## Upstream references

- `fancy:src/fancy/components/physics/gravity.tsx`, `fancy:src/fancy/components/physics/cursor-attractor-and-gravity.tsx`, `fancy:src/content/docs/components/physics/gravity.mdx`.
- Observed there and worth avoiding: anonymous listeners and a Matter `beforeUpdate` handler that are not removed on teardown, an always-running frame loop, and `require("poly-decomp")` inside the component. See `knowledge/components/fancy.md`.

## Licence notes

The code on this page is original. Fancy is MIT (`fancy:LICENSE`, Copyright (c) 2024 Daniel Petho); keep its notice if you copy any Fancy file. Matter.js and its types have their own licences; check them before shipping.
