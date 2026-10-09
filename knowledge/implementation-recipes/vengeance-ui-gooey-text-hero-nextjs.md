---
title: "Gooey text hero reveal in Next.js with Vengeance UI"
kind: recipe
summary: "Adopt the Vengeance UI gooey text reveal as a hero or section headline in a Next.js and Tailwind project: install, use the immediate, scroll and scrub modes, keep props stable, handle reduced motion and Safari, and verify. The component skips animation itself when reduced motion is requested."
source_ids: [vengeance-ui]
pattern_ids: [vengeance-ui-gooey-text-reveal, vengeance-ui-kinetic-text-effects]
updated: "2026-10-09"
---

# Gooey text hero reveal in Next.js

## Goal

A headline (and optionally a short paragraph) that resolves line by line from blur to sharp text, on load or when it scrolls into view, with plain text for visitors who ask for reduced motion.

## How the upstream does it

`vengeance-ui:src/components/ui/gooey-text-reveal.tsx` splits each target element into lines with GSAP SplitText, wraps each line's content in an inner span, gives each line a CSS filter that combines an SVG colour-matrix filter (the "goo" step) with a small blur, and tweens the inner spans from a blur measured in `em` to zero. A hidden SVG holds the filter definition, with an id made unique per instance. It rebuilds the split when the container width changes (ResizeObserver) and once web fonts have loaded, and it reverts everything on unmount. If `prefers-reduced-motion: reduce` matches, it returns before splitting, so the text stays as authored.

Props, from the docs entry in `vengeance-ui:src/lib/component-docs.ts`: `mode` (`immediate`, `scroll`, `scrub`), `delay`, `duration` (1.5), `stagger` (0.1), `blurAmount` (0.35, in em), `ease` (`power3.out`), `start` (`top 80%`), `end` (`bottom 75%`), `scroller`, `once` (true), `disabled`, `onComplete`, plus `className` and a forwarded `ref`.

## When to use it, and when not

- Use it for one or two display headings per page, set large, on a calm background.
- Skip it for long body copy: every split line gets its own filter layer (`will-change: filter`).
- Skip it where the first paint must show final text with no flash (see Flash below), or where the heading is the page's only content and must be readable the instant it loads.

## Prerequisites

- The setup in `knowledge/implementation-recipes/vengeance-ui-install-and-verify-component.md`.
- `gsap` and `@gsap/react` (the docs say `npm install gsap @gsap/react`). The component imports `gsap/ScrollTrigger` and `gsap/SplitText`; the upstream lockfile resolves gsap 3.15.0 and @gsap/react 2.1.2 (`vengeance-ui:package-lock.json`). Use gsap ^3.15.0; whether older releases ship SplitText in the public package was not verified.
- GSAP is under its own licence, not MIT (the lockfile calls it a "standard no charge" licence). Read GSAP's terms before shipping a commercial product.

## Steps

1. **Install.**

   ```bash
   npx shadcn@latest add https://raw.githubusercontent.com/Ashutoshx7/VengeanceUI/main/public/r/gooey-text-reveal.json
   npm install gsap @gsap/react
   node scripts/check-imports.mjs components/ui/gooey-text-reveal.tsx
   ```

2. **Use it in a server component.** The component file is a client component, so the page can stay on the server (original code):

   ```tsx
   // app/page.tsx
   import { GooeyTextReveal } from "@/components/ui/gooey-text-reveal";

   export default function Home() {
     return (
       <main>
         <section className="mx-auto flex min-h-[70vh] max-w-4xl flex-col justify-center px-6 py-24">
           <GooeyTextReveal mode="immediate" delay={0.2} duration={1.4} stagger={0.12} blurAmount={0.4}>
             <h1 className="text-5xl font-semibold leading-[1.05] tracking-tight md:text-7xl">
               Interfaces that arrive the way light does.
             </h1>
             <p className="mt-6 max-w-xl text-lg text-neutral-600 dark:text-neutral-400">
               One supporting sentence, revealed line by line after the headline.
             </p>
           </GooeyTextReveal>
         </section>
       </main>
     );
   }
   ```

   Each direct child is a target. To target nested elements instead, mark them with `data-gooey-reveal-item`. The component sets no text colour, so your theme colours apply.
3. **Pick the mode.**
   - `immediate`: runs on mount, after `delay`. Use for the first screen.
   - `scroll`: runs when the block reaches `start`; `once` keeps it from replaying. Use below the fold.
   - `scrub`: ties the blur to scroll between `start` and `end`. Use sparingly; it needs scroll distance.

   ```tsx
   <GooeyTextReveal mode="scroll" start="top 80%" once>
     <h2 className="text-4xl font-semibold">A section that reveals when reached</h2>
   </GooeyTextReveal>
   ```

   Inside a modal or panel with its own scrollbar, pass that element or a ref as `scroller`.
4. **Keep props stable.** The effect depends on `children`, `onComplete`, `scroller` and every tuning prop (see the dependency list in the component file). A parent that re-renders with new JSX children or an inline `onComplete` will rebuild the split and replay the reveal, as read from the code. Keep the parent a server component, or memoize the children and wrap callbacks in `useCallback`.
5. **Reduced motion.** Nothing to add: the component leaves the text untouched when the media query matches. Use `disabled` if your site also has its own motion setting. The query is read once per effect run, so a user who changes the OS setting mid-visit sees the change on the next rebuild.
6. **Flash.** The server renders plain text; the blur is applied after hydration, so a brief unblurred frame is possible (not measured here). Options: accept it for below-the-fold use with `mode="scroll"`, or hide the block until mounted and accept that visitors without JavaScript then see nothing. Decide deliberately.
7. **Fonts and layout.** Load fonts with `next/font` so the line split is right on first measure; the component re-splits when `document.fonts` finishes loading and on width changes, which keeps wrapping correct after resize.
8. **Safari and iOS.** The effect applies an SVG filter to HTML elements. The upstream's `gooey-search` sniffs the user agent and turns its blur off in Safari (`vengeance-ui:src/components/ui/gooey-search.tsx`), which suggests this class of effect needs testing there. `gooey-text-reveal` has no such guard.
9. **Accessibility.** The component passes `aria: "auto"` to SplitText. Check the installed GSAP version's docs for what that does, then test with a screen reader that the heading reads as one phrase.

## Verification checklist

- [ ] `node scripts/check-imports.mjs components/ui/gooey-text-reveal.tsx` exits 0 and `next build` passes.
- [ ] Console clean in development and in a production build. React Strict Mode runs effects twice in development; confirm the reveal still plays once.
- [ ] Resize from 1280 to 320 px: lines re-wrap and the effect does not leave stale spans.
- [ ] DevTools emulation of `prefers-reduced-motion: reduce`: text appears immediately, unblurred.
- [ ] Reload with a slow connection: the heading is readable before the script runs.
- [ ] Safari desktop and iOS Safari checked.
- [ ] Light and dark themes both show sufficient contrast during and after the reveal.
- [ ] Performance panel with 4x CPU throttling: no long frames while the lines resolve.
- [ ] Parent re-render test: toggle unrelated state in a client parent and confirm the reveal does not replay.

## Upstream references

`vengeance-ui:src/components/ui/gooey-text-reveal.tsx`, `vengeance-ui:public/r/gooey-text-reveal.json` (identical payload), `vengeance-ui:src/lib/component-docs.ts` (props and usage), `vengeance-ui:src/components/docs/gooey-text-reveal-demo.tsx` (scrollable demo with painting images and a custom font; do not reuse those assets).

## Licence notes

Code is MIT (`vengeance-ui:LICENSE`); keep the notice when copying. GSAP has its own terms. The demo's images and the font `vengeance-ui:public/gooey-text-reveal/de-fonte-plus.ttf` have unknown terms: do not reuse them.
