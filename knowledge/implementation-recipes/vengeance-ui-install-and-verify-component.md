---
title: "Install and verify a Vengeance UI component"
kind: recipe
summary: "Add one Vengeance UI component to a Next.js and Tailwind v4 project through the shadcn registry, then check npm imports, local modules, global CSS, dark mode, media and reduced motion before shipping. Includes a dependency check script and a table of gaps found in the upstream registry."
source_ids: [vengeance-ui]
pattern_ids: [vengeance-ui-registry-copy-paste-install, vengeance-ui-theme-token-layer]
updated: "2026-10-09"
---

# Install and verify a Vengeance UI component

## Goal

Get one component into your own project as source you control, with every npm package, stylesheet rule and local import present, and with the upstream's sample media and brand text replaced. Library overview and counts: `knowledge/components/vengeance-ui.md`.

## When to use it, and when not

- Use it for marketing-page effects (text reveals, hero backgrounds, navbars, showcase galleries) where you want editable source rather than a package.
- Do not use it for application primitives that need full accessibility. The 52 primitives in `vengeance-ui:src/components/ui/` follow shadcn conventions on Radix, but you can get the same from shadcn directly.
- Do not use the 133 `registry:block` items as a base: their provenance is unverified (see the library note).

## Prerequisites

- Next.js App Router, TypeScript, Tailwind CSS v4 and the `@/*` alias. The upstream docs describe exactly this shape (`vengeance-ui:src/app/docs/install-nextjs/page.tsx`, `vengeance-ui:src/app/docs/install-tailwind/page.tsx`).
- `shadcn` initialised (`components.json` exists) and a `cn` helper built from `clsx` and `tailwind-merge` (`vengeance-ui:src/lib/utils.ts` is the six-line original).
- Class-based dark mode: `@custom-variant dark (&:is(.dark *));` in your global CSS and a provider that toggles `.dark` on `html`. The upstream uses `next-themes` with `attribute="class"` (`vengeance-ui:src/components/theme-provider.tsx`).
- Versions the upstream site builds with, from `vengeance-ui:package.json`: Next.js 16.3.6, React ^19.3.0, Tailwind ^4.3.3, framer-motion ^13.4.4, gsap ^3.15.0, three ^0.186.1. Older versions were not checked.

## Steps

1. **Resolve the name.** The docs slug and the registry name can differ (`my-animated-button` is `animated-button`). With the MCP server use `search_components`, then `get_component`; without it read `vengeance-ui:src/lib/components-catalog.ts`. Confirm the item exists in `vengeance-ui:public/r/`. Six catalog items have no JSON there (image-collage, cylinder-carousel, ripple-displacement-slider, solar-system, why-us-bento, magnetic-spotlight-marquee); for those the CLI route fails and you must copy the file from `src/components/ui` by hand or pick another component.
2. **Initialise shadcn** if needed: `npx shadcn@latest init`. The upstream docs answer New York, Zinc and CSS variables (`vengeance-ui:src/app/docs/cli/page.tsx`).
3. **Optional alias** in `components.json`, taken from the same docs page:

   ```json
   {
     "registries": {
       "@vengeanceui": "https://raw.githubusercontent.com/Ashutoshx7/VengeanceUI/main/public/r/{name}.json"
     }
   }
   ```

4. **Install** by URL or alias:

   ```bash
   npx shadcn@latest add https://raw.githubusercontent.com/Ashutoshx7/VengeanceUI/main/public/r/gooey-text-reveal.json
   npx shadcn@latest add @vengeanceui/gooey-text-reveal
   ```

   The in-repo skill shows `https://www.vengenceui.com/r/<name>.json` as an alternative host; the code default is the GitHub one (`vengeance-ui:src/lib/registry.ts`).
5. **Check npm imports against `package.json`.** The item's `dependencies` array and the docs install string are both hand-maintained and incomplete in places, so read the imports. Save this as `scripts/check-imports.mjs` (original code; it reads only your own files):

   ```js
   // Usage: node scripts/check-imports.mjs components/ui/staggered-grid.tsx [more files]
   import { readFileSync } from "node:fs";
   import { builtinModules } from "node:module";

   const pkg = JSON.parse(readFileSync("package.json", "utf8"));
   const installed = new Set([
     ...Object.keys(pkg.dependencies ?? {}),
     ...Object.keys(pkg.devDependencies ?? {}),
   ]);
   const nodeBuiltins = new Set(builtinModules);

   function packageOf(specifier) {
     if (specifier.startsWith(".") || specifier.startsWith("@/") || specifier.startsWith("node:")) return null;
     const [first, second] = specifier.split("/");
     const name = specifier.startsWith("@") ? `${first}/${second}` : first;
     return nodeBuiltins.has(name) ? null : name;
   }

   let problems = 0;
   for (const file of process.argv.slice(2)) {
     const source = readFileSync(file, "utf8");
     const wanted = new Set();
     for (const match of source.matchAll(/\b(?:from|import)\s*\(?\s*["']([^"']+)["']/g)) {
       const name = packageOf(match[1]);
       if (name) wanted.add(name);
     }
     const missing = [...wanted].filter((name) => !installed.has(name));
     if (missing.length > 0) {
       problems += 1;
       console.log(`${file}\n  missing: ${missing.join(" ")}\n  fix:     npm install ${missing.join(" ")}`);
     } else {
       console.log(`${file}: all ${wanted.size} imported packages are in package.json`);
     }
   }
   process.exit(problems > 0 ? 1 : 0);
   ```

   Run it on every file the CLI wrote. Known omissions are in the first table below.
6. **Check local imports and types:** `npx tsc --noEmit`. Some published items import site modules they do not ship. `expandable-bento-grid` needs `@/hooks/use-outside-click` (`vengeance-ui:src/hooks/use-outside-click.ts` is the original; a click-outside hook of your own works). `notch-navbar` needs `@/components/theme-toggle` and `@/assets/logo/logo-icon`, which are site-specific; replace both. `sidebar` and several shadcn primitives import other primitives; add those first.
7. **Check global CSS.** Some items rely on rules that live only in the site's `vengeance-ui:src/app/globals.css`; see the second table. Copy only the blocks you need, put the upstream's MIT notice in a comment above them, and prefer namespacing the class names so they cannot collide with yours.
8. **Respect the client boundary.** Most animated items start with `"use client"` and can be imported from a server component. `next/dynamic` with `ssr: false` must be called from a client component, which is how the upstream demo renderer does it (`vengeance-ui:src/components/docs/demo-renderer.tsx`). Do this for GSAP-heavy and WebGL items.
9. **Replace defaults.** Swap sample images, avatars, copy and brand text: "VENGEANCE" in the reveal loader, "VengeanceUI" in the animated footer, the anime-character slides in the ripple slider, Unsplash and pravatar URLs. Load any font the component names, or pass your own `fontFamily`.
10. **Check theming.** Components read `--background`, `--foreground`, `--border` and friends. To also get the shared `--vng-*` tokens, add the optional theme item (`vengeance-ui:public/r/vengeance-theme.json`) and edit the values as the theming page shows (`vengeance-ui:src/app/docs/theming/page.tsx`).
11. **Add motion fallbacks** for looping, scroll-driven or WebGL items using `knowledge/implementation-recipes/vengeance-ui-motion-safe-wrapper.md`.
12. **Keep the notice.** MIT requires the copyright line to travel with copied source. Add to a `NOTICE` or `THIRD_PARTY.md`: "Portions from Vengeance UI, MIT License, Copyright (c) 2025-2026 Ashutoshx7".

## Known gaps found in the clone

Packages that the published payload imports but does not list (besides `class-variance-authority`, missing from 12 shadcn primitives such as button, badge and toggle, which `shadcn init` normally provides; not verified):

| Item | Also install |
|---|---|
| agent-bento-grid | `@phosphor-icons/react` |
| staggered-grid | `imagesloaded`, `react-icons` |
| liquid-ocean | `three`, `@react-three/fiber` |
| liquid-text | `three` |
| smooth-scroll | `lenis` |
| social-flip-button, github-button, testinomial-card2 | `react-icons` |
| morphing-disclosure | `zod` |
| code-block | `shiki` (it also uses Node `fs` and `path`, so server-only) |
| chart | `recharts` |
| resizable | `react-resizable-panels` |

CSS the component needs but the registry item does not ship (all in `vengeance-ui:src/app/globals.css`):

| Item | Missing rules |
|---|---|
| flip-text | `.flip-char` block and the `flip` and `fade` keyframes |
| glass-dock | `.glass-dock` button rules and `.glass-border` |
| glow-border-card | `.glow-conic` and `@property --glow-angle` |
| perspective-grid | `.tile` and its hover colours |
| spotlight-navbar | `.spotlight-nav`, `.spotlight-nav-bg`, `.spotlight-nav-shadow`, `.glass-border`; it also uses `<style jsx>`, which is built into Next.js |
| stacked-logos | `.stacked-logos*` rules and the `stacked-logos-appear` keyframes |
| animated-rays | `.animate-aurora-bg` and the `--stripe-color` variable (`aurora-hero` carries its own CSS and avoids this) |
| social-flip-button | `.glass-border` |
| border-beam | uses `<style jsx>` (Next.js only) |
| logo-slider | no rules for its `logo-slider__*` classes were found anywhere in the clone; write your own marquee CSS |

## Verification checklist

- [ ] `node scripts/check-imports.mjs` exits 0 for every installed file.
- [ ] `npx tsc --noEmit` is clean and `next build` passes.
- [ ] Console is free of errors and hydration warnings at 320, 768 and 1280 px (`animated-rays` returns nothing until mounted, which can shift layout).
- [ ] Light and dark both render; the theme toggle changes `.dark` on `html`.
- [ ] Reduced motion: emulate `prefers-reduced-motion: reduce` in DevTools and confirm looping motion stops or a static alternative appears. Only 7 of 76 catalog components handle it themselves.
- [ ] Keyboard: every interactive part is reachable, focus is visible, Escape closes overlays. Check `pop-button`, `liquid-metal` and `faq-accordion`, which have no focus style.
- [ ] Network tab: no unexpected third-party requests (Google Fonts `@import` in `morph-text` and `kinetic-text-loader`, hotlinked sample images).
- [ ] Heavy items: scroll with 4x CPU throttling and confirm nothing keeps rendering offscreen (`wave-grid-background`, `liquid-text` and `twisting-ribbon` keep looping).
- [ ] Safari and iOS: SVG-filter and backdrop-filter effects can differ; the upstream's own `gooey-search` switches blur off for Safari (`vengeance-ui:src/components/ui/gooey-search.tsx`).
- [ ] No upstream media, brand text or logos remain.

## Agent route

`npx vengeanceui init claude` writes a skill, an MCP entry and a CLAUDE.md block into the project; the tools then give search, props and the install command (`knowledge/components/vengeance-ui-agent-interfaces.md`). Run steps 5 to 7 anyway: the tool output copies the same incomplete dependency strings.

## Upstream references

`vengeance-ui:src/lib/registry.ts`, `vengeance-ui:public/r/registry.json`, `vengeance-ui:public/r/animated-button.json` (item shape), `vengeance-ui:docs/dependency-validation.md` (the installers read the JSON, not the source files), `vengeance-ui:src/app/globals.css`.

## Licence notes

The code is MIT (`vengeance-ui:LICENSE`). Media under `public/`, the ported third-party demos and the block kits may carry other terms; `gsap` imports bring GSAP's own licence. Details in `knowledge/components/vengeance-ui.md`.
