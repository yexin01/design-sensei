---
title: "Motion-safe wrapper for Vengeance UI components"
kind: recipe
summary: "Put looping, scroll-driven or WebGL Vengeance UI components behind a small hook and wrapper that honours prefers-reduced-motion, skips heavy scenes on low-power devices or without WebGL, and renders a static fallback. Original code, per-family examples and a verification list."
source_ids: [vengeance-ui]
pattern_ids: [vengeance-ui-animated-cta-buttons, vengeance-ui-liquid-metal-button, vengeance-ui-kinetic-text-effects, vengeance-ui-bento-grids, vengeance-ui-3d-image-carousels, vengeance-ui-three-js-scenes, vengeance-ui-cursor-image-trails, vengeance-ui-aurora-hero-backgrounds]
updated: "2026-10-09"
---

# Motion-safe wrapper for Vengeance UI components

## Goal

Most Vengeance UI components animate without regard to the visitor's settings: only 7 of the 76 catalog components react to `prefers-reduced-motion`, and the site-wide CSS rule that covers the upstream's own pages is not installed with registry items (`knowledge/components/vengeance-ui.md`). This recipe adds one decision point in your project: a hook that says whether motion and heavy scenes are allowed, and a wrapper that swaps in a static fallback when they are not.

## When to use it

- Looping CTAs, rotating word effects, carousels, hero backgrounds, canvas and WebGL scenes, pointer-driven trails.
- Not needed for components that already handle it: `gooey-text-reveal`, `research-bento-grid`, `share-sheet`, `line-hover-link` (see the gooey recipe for the first).
- Not a substitute for testing: the code below was reviewed but not run in a browser.

## The policy

| Signal | Used for | Note |
|---|---|---|
| `prefers-reduced-motion: reduce` | any motion | read live, so a settings change applies without reload |
| viewport at most 900 px, 4 or fewer logical cores, `saveData` | heavy scenes only | the same cut-offs the upstream `books-showcase` uses for its low-power mode (`vengeance-ui:src/components/ui/books-showcase.tsx`), plus `saveData`, which only Chromium exposes. Phones and small tablets are treated as low power; tune this |
| WebGL context available | heavy scenes only | probed once, then released |
| near the viewport | optional | keeps continuous render loops from running offscreen |

## Code

Hook (original code):

```ts
// hooks/use-motion-policy.ts
"use client";

import { useEffect, useState } from "react";

export type MotionPolicy = {
  /** False until the first client effect has run; render the static fallback until then. */
  ready: boolean;
  /** The visitor has not asked for reduced motion. */
  motionOk: boolean;
  /** motionOk, on a device that can plausibly run WebGL scenes. */
  heavyOk: boolean;
};

function hasWebGL(): boolean {
  try {
    const canvas = document.createElement("canvas");
    const gl2 = canvas.getContext("webgl2");
    if (gl2) {
      gl2.getExtension("WEBGL_lose_context")?.loseContext();
      return true;
    }
    const gl1 = canvas.getContext("webgl");
    gl1?.getExtension("WEBGL_lose_context")?.loseContext();
    return gl1 !== null;
  } catch {
    return false;
  }
}

export function useMotionPolicy(): MotionPolicy {
  const [policy, setPolicy] = useState<MotionPolicy>({ ready: false, motionOk: false, heavyOk: false });

  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    const narrow = window.matchMedia("(max-width: 900px)");
    const connection = (navigator as Navigator & { connection?: { saveData?: boolean } }).connection;

    const update = () => {
      const lowPower =
        narrow.matches || (navigator.hardwareConcurrency ?? 8) <= 4 || connection?.saveData === true;
      const motionOk = !reduced.matches;
      setPolicy({ ready: true, motionOk, heavyOk: motionOk && !lowPower && hasWebGL() });
    };

    update();
    reduced.addEventListener("change", update);
    narrow.addEventListener("change", update);
    return () => {
      reduced.removeEventListener("change", update);
      narrow.removeEventListener("change", update);
    };
  }, []);

  return policy;
}
```

Wrapper (original code). It renders a `span`, so it is valid inside headings and buttons; give it a `className` to control its box:

```tsx
// components/motion-safe.tsx
"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { useMotionPolicy } from "@/hooks/use-motion-policy";

type MotionSafeProps = {
  children: ReactNode;
  /** Static content for the server render, the first client render, and whenever motion is not allowed. */
  fallback: ReactNode;
  /** Use the stricter policy (reduced motion, low power, WebGL) for canvas and WebGL scenes. */
  heavy?: boolean;
  /** Mount children only while the wrapper is near the viewport. Remounting restarts the scene. */
  whileVisible?: boolean;
  className?: string;
};

export function MotionSafe({ children, fallback, heavy = false, whileVisible = false, className }: MotionSafeProps) {
  const { ready, motionOk, heavyOk } = useMotionPolicy();
  const allowed = ready && (heavy ? heavyOk : motionOk);
  const ref = useRef<HTMLSpanElement>(null);
  const [visible, setVisible] = useState(!whileVisible);

  useEffect(() => {
    if (!whileVisible || !allowed || !ref.current) return;
    const observer = new IntersectionObserver(([entry]) => setVisible(entry.isIntersecting), {
      rootMargin: "200px 0px",
    });
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [whileVisible, allowed]);

  return (
    <span ref={ref} className={className}>
      {allowed && visible ? children : fallback}
    </span>
  );
}
```

The first client render always shows the fallback, so server and client markup match and there is no hydration warning. Make the fallback look like the animated version's resting state so the swap does not jump.

## Examples by family

1. **Looping CTA** (`animated-button`, whose shine loops forever). Match the fallback to the component's base classes (`px-6 py-2 rounded-md border bg-background text-foreground font-medium`):

   ```tsx
   import AnimatedButton from "@/components/ui/animated-button";
   import { MotionSafe } from "@/components/motion-safe";

   <MotionSafe
     className="inline-block"
     fallback={<button className="rounded-md border bg-background px-6 py-2 font-medium text-foreground">Browse components</button>}
   >
     <AnimatedButton>Browse components</AnimatedButton>
   </MotionSafe>;
   ```

2. **WebGL or canvas background** (`wave-grid-background`, `liquid-text`, `twisting-ribbon`). Their render loops run continuously, so also use `whileVisible`. `liquid-ocean` already stops rendering offscreen but still benefits from `heavy`:

   ```tsx
   "use client";
   import dynamic from "next/dynamic";
   import type { ReactNode } from "react";
   import { MotionSafe } from "@/components/motion-safe";

   const WaveGridBackground = dynamic(
     () => import("@/components/ui/wave-grid-background").then((m) => m.WaveGridBackground),
     { ssr: false },
   );

   export function HeroBackdrop({ children }: { children: ReactNode }) {
     return (
       <section className="relative isolate overflow-hidden">
         <MotionSafe
           heavy
           whileVisible
           className="absolute inset-0 -z-10 block"
           fallback={<span className="block h-full w-full bg-gradient-to-b from-neutral-100 to-white dark:from-neutral-900 dark:to-neutral-950" />}
         >
           <WaveGridBackground className="h-full w-full" />
         </MotionSafe>
         <div className="relative z-10">{children}</div>
       </section>
     );
   }
   ```

   Give the scene an explicit size, as above, since its wrapper is absolutely positioned.
3. **Shader button** (`LiquidMetalButton`, one WebGL canvas per button): use `heavy` and a plain bordered button as fallback.
4. **Carousel** (`perspective-carousel`, `diagonal-carousel`, `circular-gallery`): fall back to a scroll-snap row so every item stays reachable:

   ```tsx
   <MotionSafe
     className="block"
     fallback={
       <ul className="flex snap-x snap-mandatory gap-4 overflow-x-auto p-4">
         {items.map((item) => (
           <li key={item.src} className="shrink-0 snap-center">
             <img src={item.src} alt={item.title} className="h-72 w-52 rounded-lg object-cover" />
           </li>
         ))}
       </ul>
     }
   >
     <div className="h-[420px]">
       <PerspectiveCarousel items={items} />
     </div>
   </MotionSafe>
   ```

5. **Pointer trail** (`image-trail`): it already has a `disabled` prop, so use the hook directly: `disabled={!ready || !motionOk}`.
6. **Rotating words** (`flip-fade-text`, `morph-text`): fall back to the first word as plain text. Do not rely on a blanket CSS kill switch for these. By reading `morph-text`, every word starts at opacity 0 and its last keyframe is also transparent, so forcing one short iteration would leave it blank.
7. **Aurora and gradient backgrounds** (`aurora-hero`, `animated-rays`, `fluid-morph-bg`): fall back to a static gradient. These loop for tens of seconds and are decoration only.

## Entrance reveals without a flash

For one-shot reveals driven by framer-motion's initial hidden style (`stagger-text`), swapping after hydration would show the text, hide it, then reveal it. A CSS override avoids the swap. Mark the wrapper and neutralise inline hidden states under reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  [data-reveal] * {
    opacity: 1 !important;
    transform: none !important;
    filter: none !important;
  }
}
```

```tsx
<h1 data-reveal><TextAnimation divideBy="word">{title}</TextAnimation></h1>
```

Use it only on text wrappers, since `transform: none` would also remove layout transforms. Optionally wrap a whole framer-motion tree in framer-motion's `MotionConfig` with `reducedMotion="user"`; the upstream does not use it, so check the installed framer-motion version's docs, and remember it affects framer-motion only, not GSAP, CSS or WebGL.

## Pausing CSS loops offscreen

The upstream has the idea but does not apply it: a wrapper that toggles a `paused-section` class from an IntersectionObserver, and a global rule setting `animation-play-state: paused` inside it (`vengeance-ui:src/components/landing/lazy-section.tsx`, `vengeance-ui:src/app/globals.css`). `LazySection` is unused in the clone. If you want it, write your own wrapper and rule; it does not stop requestAnimationFrame or WebGL loops, which is why the wrapper above unmounts them.

## Verification checklist

- [ ] With `prefers-reduced-motion: reduce` emulated, every wrapped component shows its static fallback and nothing keeps animating.
- [ ] Toggle the setting while the page is open: the swap happens without a reload.
- [ ] No hydration warning in development; the fallback and the animated version have the same box size (no layout shift).
- [ ] Throttle to 4x CPU and 3G, scroll past a `whileVisible` scene: the canvas unmounts and the render loop stops (Performance panel shows no frames from it).
- [ ] A browser or profile with WebGL disabled shows the fallback and no console error.
- [ ] Keyboard: fallback controls (the plain button, the scroll row) are reachable and show focus.
- [ ] The static fallback meets contrast requirements in light and dark.

## Upstream references

`vengeance-ui:src/components/ui/books-showcase.tsx` (low-power heuristic, WebGL failure message), `vengeance-ui:src/components/ui/circular-gallery.tsx` (live reduced-motion listener), `vengeance-ui:src/components/ui/image-trail.tsx` (`disabled` prop), `vengeance-ui:src/components/ui/morph-text.tsx`, `vengeance-ui:src/components/ui/animated-button.tsx`, `vengeance-ui:src/components/ui/wave-grid-background.tsx`.

## Licence notes

The hook and wrapper above are original and free to use. The referenced components are MIT (`vengeance-ui:LICENSE`); keep that notice when you copy them, and see `knowledge/components/vengeance-ui.md` for media and third-party-origin caveats.
