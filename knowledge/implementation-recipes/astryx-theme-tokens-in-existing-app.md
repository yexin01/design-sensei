---
title: "Adopt Astryx theme tokens in an existing React app"
kind: recipe
summary: "Step by step: install Astryx 0.6.6 core and a theme, load its layered CSS, mount Theme, read its tokens from your own CSS and TypeScript, and extend a shipped theme into a brand theme, without replacing your component system."
source_ids: [astryx]
pattern_ids: [astryx-design-system-react, astryx-theme-token-system, astryx-theme-presets, astryx-typography-scale]
updated: "2026-10-09"
---

# Adopt Astryx theme tokens in an existing React app

## Goal

Give an existing React 19 app Astryx's semantic design tokens (colour with light and dark, spacing, radius, shadow, type, motion,
focus ring) and optionally a few Astryx components, while your current buttons, forms and layouts keep working. The same steps work
for Next.js App Router and Vite.

## When to use, and when not

Use it when you want one token vocabulary, dark mode through `light-dark()` and a swappable theme. Do not use it if the app is not on
React 19 (`react` and `react-dom` are peers at `>=19.0.0` in `astryx:packages/core/package.json`), if another library already writes
`data-theme` on `<html>` (Astryx's root provider does too), or if you need a stable 1.x API: the packages are 0.6.x and README-labelled beta.

## Prerequisites (read from manifests)

| Package | Version in the checkout | Why |
|---|---|---|
| `@astryxdesign/core` | 0.6.6 | `Theme`, `defineTheme`, token helpers, components (`astryx:packages/core/package.json`) |
| `@astryxdesign/theme-neutral` | 0.6.6; peer `@astryxdesign/core` pinned to `0.6.6` | a ready theme and `theme.css` (`astryx:packages/themes/neutral/package.json`) |
| `@stylexjs/stylex` | peer `^0.19.0` | required peer of core (the README install line includes it) |
| `react`, `react-dom` | `>=19.0.0` | peers |

These are the versions at the pinned commit; whether they are published was not checked (no network). Pin exact versions of core and
theme packages together. `@astryxdesign/cli` is optional and is not in the local checkout.

## Steps

1. Install, as `astryx:README.md` shows for npm: `npm install @astryxdesign/core @astryxdesign/theme-neutral @stylexjs/stylex`.
2. Load the CSS once, in the order `astryx:packages/core/README.md` gives (`reset.css` in `@layer reset`, `astryx.css` in
   `@layer astryx-base`, `theme.css` in `@layer astryx-theme`):

   ```css
   /* src/astryx.css, imported from your root layout or entry file */
   @import '@astryxdesign/core/reset.css';
   @import '@astryxdesign/core/astryx.css';
   @import '@astryxdesign/theme-neutral/theme.css';
   ```

   Your own unlayered CSS beats all three layers (header of `astryx:packages/core/src/reset.css`). `reset.css` is global and zero
   specificity: it removes heading and list defaults, makes images and svg `display: block` and resets buttons. Review it against
   your existing reset. Dropping it is not a documented configuration, so test `MediaTheme`, `AspectRatio` and native control colours
   if you do. With Tailwind v4, copy the explicit `@layer` order block and the `tailwind-theme.css` bridge from the same README.
3. Mount the provider once at the root as a client component. Original glue:

   ```tsx
   'use client';
   import type {ReactNode} from 'react';
   import Link from 'next/link'; // remove with LinkProvider on Vite
   import {Theme} from '@astryxdesign/core/theme';
   import {LinkProvider} from '@astryxdesign/core/Link';
   import {neutralTheme} from '@astryxdesign/theme-neutral/built';

   export function AstryxProviders({children, isDark}: {children: ReactNode; isDark?: boolean}) {
     const mode = isDark === undefined ? 'system' : isDark ? 'dark' : 'light';
     return (
       <Theme theme={neutralTheme} mode={mode}>
         <LinkProvider component={Link}>{children}</LinkProvider>
       </Theme>
     );
   }
   ```

   `mode` is `system` (default), `light` or `dark` (`astryx:packages/core/src/theme/Theme.tsx`); `Theme` renders a
   `display: contents` wrapper, so it adds no layout box. The root provider writes
   `data-theme` and `data-astryx-theme` on `<html>`; if your app owns a dark-mode switch, derive `mode` from it and remove any
   competing `data-theme` use. For a forced mode, also put `data-theme="dark"` on `<html>` in the server layout to avoid a flash.
   To try another preset, swap the package: all seven theme manifests export `/built`, `/theme.css` and `/fonts.css`, name the object
   `<name>Theme` (for example `gothicTheme`) and peer-pin core to 0.6.6. Gothic is dark-only, so pass `mode="dark"`
   (`astryx:packages/themes/gothic/README.md`).
4. Use tokens from your own CSS. Reference them directly so nested `Theme` or `MediaTheme` regions keep working; a root-level alias
   such as `--app-bg: var(--color-background-body)` is resolved once at `:root` and inherited as that value, so a nested region that
   overrides the token does not change it.

   ```css
   .panel {
     background: var(--color-background-card);
     color: var(--color-text-primary);
     border: var(--border-width) solid var(--color-border);
     border-radius: var(--radius-container);
     padding: var(--spacing-4);
     box-shadow: var(--shadow-low);
     font-family: var(--font-family-body);
     transition: transform var(--duration-medium) var(--ease-standard);
   }
   .panel:focus-visible {
     outline: var(--focus-outline-width) var(--focus-outline-style) var(--focus-outline-color);
     outline-offset: var(--focus-outline-offset);
   }
   .panel-note { color: var(--color-text-secondary); font-size: var(--font-size-sm); }
   @media (prefers-reduced-motion: reduce) { .panel { transition-duration: 0s; } }
   ```

   Token names are listed in `astryx:packages/core/src/theme/tokens.stylex.ts`. The reduced-motion block is your responsibility for
   your own components; Astryx components guard their own.
5. Use tokens from TypeScript. `tokenVar('--color-accent')` returns `var(--color-accent)`, `tokenVars` is the whole map, and
   `resolveThemeToken(theme, name, {mode})` returns a concrete value for canvas, SVG or tests. They suit configs for Emotion,
   styled-components, MUI, Panda and similar (`astryx:packages/core/src/theme/tokens.ts`).
6. Add Astryx components gradually. Import per path (`import {Button} from '@astryxdesign/core/Button'`), pass `label` (required),
   use numeric spacing steps (`gap={4}`) and put layout overrides in `xstyle` or `className`
   (`astryx:packages/core/src/Button/Button.doc.mjs`).
7. Make a brand theme by extending, not forking. Original example (field meanings in
   `knowledge/components/astryx-themes-and-tokens.md`):

   ```ts
   import {defineTheme} from '@astryxdesign/core/theme';
   import {neutralTheme} from '@astryxdesign/theme-neutral/built';

   export const brandTheme = defineTheme({
     name: 'brand',
     extends: neutralTheme,
     color: {accent: ['#9a3412', '#fdba74'], neutralStyle: 'warm'},
     typography: {scale: {base: 16, ratio: 1.25}, heading: {family: 'Fraunces', fallbacks: 'Georgia, serif'}},
     radius: {base: 4, multiplier: 1.5},
   });
   ```

   Pass `brandTheme` to `Theme`. Without a prebuilt stylesheet this injects `<style>` elements at runtime and, in development only,
   logs a one-time hint; for production compile it with `npx @astryxdesign/cli theme build <file>` (hint text in `Theme.tsx`; the
   neutral package builds with `astryx theme build src/neutralTheme.ts -o dist/theme.css`; other flags were not verified). Load
   your fonts yourself: themes name them but never bundle them.

## Verification checklist

- Console: no hydration warning and no missing-peer warning. The runtime-injection hint is development-only, so in a production
  build check `<head>` instead: with a built theme there should be no `<style data-astryx-theme>` element.
- DevTools: `<html>` carries `data-astryx-theme`; computed `--color-background-surface` changes when `mode` changes; the Layers view
  shows `reset`, `astryx-base`, `astryx-theme` in that order.
- Dark and light both checked; focus ring visible on keyboard focus only; contrast spot-checked for your own text on surfaces.
- Reduced motion on (OS or DevTools emulation): your transitions stop, Astryx components settle immediately.
- Responsive: 320px and 1440px; confirm `reset.css` did not change headings, lists, buttons or images you rely on.
- Network: fonts load from the source you intend (theme `fonts.css` files import Google Fonts), and the single `astryx.css` size is
  acceptable; a source build via `@astryxdesign/build` exists but was not verified here.

## Upstream references

`astryx:packages/core/README.md`, `astryx:packages/core/src/theme/Theme.tsx`, `astryx:packages/core/src/theme/defineTheme.ts`,
`astryx:packages/core/src/theme/tokens.ts`, `astryx:docs/architecture/theme-application.md`,
`astryx:docs/architecture/theme-compilation.md`, `astryx:packages/themes/neutral/README.md` (its `XDSTheme` snippet is stale; the
export is `Theme`).

## Licence notes

Astryx is MIT (`astryx:LICENSE`): keep the copyright and permission notice if you copy source. Your code above is original glue that
calls public APIs. Fonts and Lucide icons carry their own terms.
