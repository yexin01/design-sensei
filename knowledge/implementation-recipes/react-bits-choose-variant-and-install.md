---
title: "Choose a React Bits variant and install it"
kind: recipe
summary: "Pick between the JS or TS and CSS or Tailwind variants, install components with the shadcn or jsrepo CLI as the upstream docs show, verify the npm packages from the imports, wire them into Next.js or Vite, and add a reduced-motion and fine-pointer gate."
source_ids: [react-bits]
pattern_ids:
  - react-bits-gsap-text-reveals
  - react-bits-lightweight-text-effects
  - react-bits-target-cursor
  - react-bits-scroll-driven-components
  - react-bits-bento-and-card-grids
  - react-bits-pointer-lit-cards
  - react-bits-animated-navigation-menus
  - react-bits-micro-spring-controls
updated: "2026-10-09"
---

# Choose a React Bits variant and install it

## Goal

Add one or more React Bits components to an existing React app as source code you own, in the variant that matches the app, with the right npm packages and a reduced-motion fallback. This recipe only covers installing and wrapping the library as upstream intends. It reproduces no React Bits code (see the licence notes).

## When to use

- You picked components from `knowledge/components/react-bits-catalog.md` and now need them in a project.
- Do not use it to copy React Bits files into a library, template, registry or port of your own: the licence forbids that (`knowledge/implementation-recipes/react-bits-license-safe-usage.md`).
- GPU-driven rows of the catalog (WebGL or WebGPU) need the extra budget steps in `knowledge/implementation-recipes/react-bits-heavy-background-budget.md`.

## Prerequisites

- A React app. Upstream's own site uses React ^19, Vite ^5, TypeScript ^5.7 and Tailwind ^4 (`react-bits:package.json`). The components state no minimum versions; test on your versions.
- For Tailwind variants: Tailwind configured to scan the folder where the component lands. For CSS variants: a bundler that accepts a component importing its sibling `.css` file.
- npm packages are per component. Upstream's versions for the common ones: gsap ^3.13.0, @gsap/react ^2.1.2, motion ^12.23.12, ogl ^1.0.11, three ^0.180.0 (`react-bits:package.json`). GSAP has its own licence terms.

## Steps

1. **Choose the variant.** Match your styling system first, language second.

   | Your project | Variant | Source folder | Notes |
   |---|---|---|---|
   | TypeScript and Tailwind | TS-TW | `react-bits:src/ts-tailwind/` | one `.tsx` per component; 22 embed a `<style>` block; GlitchText needs Tailwind config additions |
   | TypeScript, no Tailwind | TS-CSS | `react-bits:src/ts-default/` | `.tsx` plus a sibling `.css`; six stylesheets declare generic `:root` variables |
   | JavaScript and Tailwind | JS-TW | `react-bits:src/tailwind/` | one `.jsx` |
   | JavaScript, no Tailwind | JS-CSS | `react-bits:src/content/` | `.jsx` plus `.css`; the copy the docs site previews for 209 of 215 components |

   The variants are hand-maintained copies and can drift (Ballpit, ElasticSlider, StaggeredMenu: `knowledge/components/react-bits.md`). If a TS or Tailwind copy misbehaves, compare with the JS-CSS copy before blaming your setup.

2. **Install.** Both commands come from the upstream docs (`react-bits:README.md`, `react-bits:src/docs/Installation.jsx`, `react-bits:src/utils/cli.js`). Replace the name and the variant suffix (JS-CSS, JS-TW, TS-CSS, TS-TW).

   ```bash
   npx shadcn@latest add @react-bits/SplitText-TS-TW
   npx jsrepo@latest add https://reactbits.dev/r/SplitText-TS-TW
   ```

   The docs swap `npx` for `pnpm dlx`, `yarn` or `bun x --bun` on other package managers. Manual route: copy the component from its Code tab into a new file and install its packages yourself. The README does not say whether `shadcn add` needs an initialised `components.json`; if the CLI cannot resolve the `@react-bits` namespace, the MCP page shows the registry entry to add (below).

   Optional, for AI clients (`react-bits:src/docs/McpServer.jsx`): add `@react-bits` to `registries` in `components.json`, run `npx shadcn@latest mcp init --client claude`, restart Claude Code, then ask for components in plain language.

   ```json
   { "registries": { "@react-bits": "https://reactbits.dev/r/{name}.json" } }
   ```

3. **Read the imports, then install what they name.** The docs' dependency strings are hand-written and 9 of 215 are wrong. Open the file the CLI created and read its import statements. Install every non-React package it imports, for example `gsap` and `@gsap/react` for SplitText, and nothing else. Do not copy the site's `package.json`: 18 of its packages are used by no component.

4. **Wire it in.** The upstream docs name no framework-specific steps; what follows is general React practice plus facts from the source.
   - Every component file starts with the client-component directive. In Next.js App Router you can render them from server components, but only serialisable props can cross that boundary, so callbacks (`onLetterAnimationComplete`, `onError`) belong in a small client wrapper like the example below.
   - A scan found no browser API touched at module scope in the TS + Tailwind files, so SSR should not crash on import. If an effect-time API still breaks a page, load that component from a client component with `next/dynamic` and `ssr: false`.
   - Next.js Pages Router restricts component-level global CSS imports in many versions; prefer a Tailwind variant there. Vite needs nothing special (the upstream site is a Vite app: `react-bits:vite.config.js`).
   - Components are self-contained: apart from their own `.css`, they import nothing from the site, so no path aliases are required. Adjust the import path in your code to wherever the CLI placed the file.

5. **Gate motion and pointer effects.** Most components ignore the user's motion preference (95 of 215 check it; see `knowledge/components/react-bits.md`). This original wrapper renders a static fallback for reduced motion and, for cursor effects, for touch devices.

   ```tsx
   'use client';

   import { useCallback, useSyncExternalStore, type ReactNode } from 'react';

   function useMediaQuery(query: string, serverValue: boolean): boolean {
     const subscribe = useCallback(
       (onChange: () => void) => {
         const mql = window.matchMedia(query);
         mql.addEventListener('change', onChange);
         return () => mql.removeEventListener('change', onChange);
       },
       [query],
     );
     return useSyncExternalStore(
       subscribe,
       () => window.matchMedia(query).matches,
       () => serverValue,
     );
   }

   interface MotionGateProps {
     children: ReactNode;
     /** Rendered instead of the animated children. Give it the same typography and layout classes. */
     fallback?: ReactNode;
     /** Cursor-style effects: also require a mouse-like pointer. */
     requireFinePointer?: boolean;
   }

   export function MotionGate({ children, fallback = null, requireFinePointer = false }: MotionGateProps) {
     // Server snapshot: render the animated branch; the client corrects it right after hydration.
     const reduced = useMediaQuery('(prefers-reduced-motion: reduce)', false);
     const finePointer = useMediaQuery('(hover: hover) and (pointer: fine)', true);
     const allowed = !reduced && (!requireFinePointer || finePointer);
     return <>{allowed ? children : fallback}</>;
   }
   ```

   Usage with two components whose props were read from the upstream TS files (SplitText: `text`, `tag`, `splitType`, `delay`; TargetCursor: `targetSelector`, `hideDefaultCursor`):

   ```tsx
   'use client';

   import SplitText from '@/components/SplitText';
   import TargetCursor from '@/components/TargetCursor';
   import { MotionGate } from '@/lib/motion-gate';

   export function HeroTitle({ text }: { text: string }) {
     return (
       <MotionGate fallback={<h1 className="text-center text-6xl font-semibold">{text}</h1>}>
         <SplitText text={text} tag="h1" splitType="words" delay={60} className="text-6xl font-semibold" />
       </MotionGate>
     );
   }

   export function SiteCursor() {
     return (
       <MotionGate requireFinePointer>
         <TargetCursor targetSelector="[data-cursor-target]" hideDefaultCursor={false} />
       </MotionGate>
     );
   }
   ```

   Both snippets type-check under TypeScript 5.9 strict mode against React 19 types with stub components; they were not run in a browser.

6. **Replace baked-in defaults.** Swap remote placeholder images (15 files use Unsplash, picsum or pravatar), supply your own logo to StaggeredMenu, host fonts and model files yourself (TextPressure, FluidGlass), and keep the native cursor unless you offer a fallback. Record the upstream commit or date you copied from next to each file.

## Verification checklist

- [ ] Build passes and the import list of each file matches `package.json`; no unused packages were added.
- [ ] No console errors in development with React Strict Mode on (effects run twice; cleanup must work).
- [ ] 360 px, 768 px and 1280 px widths: parents of fill-style components have a real height.
- [ ] DevTools Rendering panel, emulate `prefers-reduced-motion: reduce`: the static fallback appears and nothing keeps animating.
- [ ] Device-mode touch emulation: cursor effects are off and the native cursor is untouched.
- [ ] The LCP element is not wrapped in a component that hides it until JS runs (AnimatedContent does).
- [ ] The licence notice for React Bits is stored in your project (`knowledge/implementation-recipes/react-bits-license-safe-usage.md`).

## Upstream references

- Install paths: `react-bits:README.md`, `react-bits:src/docs/Installation.jsx`, `react-bits:src/docs/McpServer.jsx`, `react-bits:src/utils/cli.js`.
- Variant mapping and registry: `react-bits:jsrepo.config.ts`, `react-bits:vite.config.js`, `react-bits:src/constants/code/Backgrounds/auroraCode.js` (one example of the five-source module).
- Props tables: `react-bits:src/demo/TextAnimations/BlurTextDemo.jsx` (typical layout of a demo file).
- Components used in the examples: `react-bits:src/ts-tailwind/TextAnimations/SplitText/SplitText.tsx`, `react-bits:src/ts-tailwind/Animations/TargetCursor/TargetCursor.tsx`.

## Licence notes

React Bits is MIT plus a Commons Clause style restriction (`react-bits:LICENSE.md`): use inside your own application is allowed, redistributing the components is not. The code above is original and calls only props the upstream components declare. Keep installed copies inside your app and keep the upstream copyright and permission notice with them.
