---
title: "Vengeance UI component library"
kind: component-library
summary: "Map of the Vengeance UI repository (MIT): animated React and Tailwind components installed by copy-paste through a shadcn-style registry, plus a docs site, CLI and MCP server. Covers the install flow, honest counts, notable components, design language, dependencies, accessibility, pitfalls and reuse limits."
source_ids: [vengeance-ui]
pattern_ids: [vengeance-ui-registry-copy-paste-install, vengeance-ui-agent-skill-mcp-cli, vengeance-ui-theme-token-layer, vengeance-ui-animated-cta-buttons, vengeance-ui-liquid-metal-button, vengeance-ui-gooey-text-reveal, vengeance-ui-kinetic-text-effects, vengeance-ui-landing-navbars, vengeance-ui-floating-dock-navigation, vengeance-ui-bento-grids, vengeance-ui-3d-image-carousels, vengeance-ui-three-js-scenes, vengeance-ui-cursor-image-trails, vengeance-ui-aurora-hero-backgrounds]
updated: "2026-10-09"
---

# Vengeance UI

Read at the pinned commit `87f5a77` (see `catalog/sources.yaml`). Everything below was read from the clone; nothing was run and no network was used.

## What it is

- A set of animated React components for landing pages, written in TypeScript with Tailwind CSS and delivered as source the consumer copies into their own project (`vengeance-ui:README.md`).
- The repository is one Next.js application (docs site and live demos), a registry of JSON files in `vengeance-ui:public/r/`, and two small workspaces for agent tooling, `vengeance-ui:packages/cli/package.json` and `vengeance-ui:packages/mcp/package.json`. The agent side is covered in `knowledge/components/vengeance-ui-agent-interfaces.md`.
- One maintainer, Ashutosh (`Ashutoshx7`), per `vengeance-ui:LICENSE` and `vengeance-ui:funding.json`. Some components carry contributor credits (see Licence).
- The README lists Vite in its tech stack, but the repository is a Next.js app with no Vite dependency (`vengeance-ui:package.json`).

## How a consumer obtains components

1. Have a Tailwind CSS v4 project with shadcn set up. The docs run `npx shadcn@latest init` (answers shown: New York, Zinc, CSS variables), recommend the App Router, TypeScript and the `@/*` alias, and add a `cn` helper from `clsx` and `tailwind-merge` (`vengeance-ui:src/app/docs/cli/page.tsx`, `vengeance-ui:src/app/docs/install-nextjs/page.tsx`, `vengeance-ui:src/app/docs/add-utilities/page.tsx`).
2. Add by URL: `npx shadcn@latest add <base>/<componentName>.json`. The base in code is `https://raw.githubusercontent.com/Ashutoshx7/VengeanceUI/main/public/r`; a code comment says GitHub is used so installs do not depend on the docs site's DNS (`vengeance-ui:src/lib/registry.ts`). The packaged CLI templates and the MCP index use the same base. The in-repo Cursor skill still shows `https://www.vengenceui.com/r/` (`vengeance-ui:.cursor/skills/vengeance-ui/install.md`), and `vengeance-ui:next.config.ts` serves `/r/*` with CORS and cache headers, so both hosts look intended; neither was tested.
3. Or register an alias: a `registries` entry named `@vengeanceui` in `components.json`, then `shadcn add @vengeanceui/<componentName>` (same docs page).
4. Optional theme item `vengeance-theme` (type `registry:theme`) adds `--vng-*` tokens (`vengeance-ui:public/r/vengeance-theme.json`).
5. Manual route: install the npm packages and paste `files[].content` of the item JSON into `components/ui/`. An item has `name`, `type`, `dependencies` and `files` with `path`, `content`, `target` (`vengeance-ui:public/r/animated-button.json`).
6. Names differ between docs slug and registry name for some items: slug `my-animated-button` is `animated-button`, and `stagger-text` lives in `staggerText.tsx`.
7. `vengeanceui` (CLI) and `vengeanceui-mcp` are both version 0.1.0. The CLI README says it installs agent files only, not components. Whether either package is published to npm was not verified.

## Directory map

| Path | What is there |
|---|---|
| `vengeance-ui:src/components/ui/` | 143 files: 76 catalog components, 52 shadcn-style primitives (accordion to tooltip), 15 others (border-beam, smooth-scroll, reveal-loader, liquid-gradient, cyber-glitch-text, code-block, and similar) |
| `vengeance-ui:src/components/docs/` | 94 files: one demo wrapper per component plus docs plumbing (not in the registry) |
| `vengeance-ui:src/components/landing/` | 37 files: the site's own landing sections and an isometric SVG illustration set; not in the registry |
| `vengeance-ui:src/components/layout/` | docs shell: navbar, sidebar, table of contents |
| `vengeance-ui:src/registry/` | four older demo copies (bento-grid, books-showcase, my-animated-button, reveal-loader) |
| `vengeance-ui:src/lib/` | catalog (9 categories, 76 items), per-slug docs data (props, usage, install string, credits), registry helpers, marketing copy, Stripe sponsorship helpers |
| `vengeance-ui:src/app/` | App Router: docs pages, component pages, marketing pages, API routes (GitHub stars, component source, sponsor checkout and webhook), `globals.css` |
| `vengeance-ui:public/r/` | 273 files: `registry.json` (134 entries), `index.json` (120, older), `mist-registry.json`, and 270 item JSONs (136 `registry:ui`, 133 `registry:block`, 1 `registry:theme`) |
| `vengeance-ui:public/` | media: avatars, anime-character PNGs, gallery and trail photos, sponsor SVGs, template screenshots, a GLB model, a WAV, a TTF |
| `vengeance-ui:packages/cli/`, `vengeance-ui:packages/mcp/` | agent tooling |
| `vengeance-ui:tests/` | three `node:test` files and one Playwright spec |
| `vengeance-ui:docs/` | `dependency-validation.md` (pre-merge checks, lint baseline) and Stripe sponsorship setup |

The 133 block items (hero sections, features, pricing and so on, in two kits named dusk and mist) point at `packages/dusk-kit`, `packages/mist-kit` and `packages/core`, which are not in this clone, and some depend on motion-primitives and Magic UI registries (`vengeance-ui:public/r/hero-section-1.json`, `vengeance-ui:public/r/mist-registry.json`). Their provenance is not verified; treat them as reference only.

## Categories and counts

From `vengeance-ui:src/lib/components-catalog.ts`: Buttons 9, Text and Motion 9, Interactive 19, Layout and Cards 10, Tooltip and Marquee 9, Loaders 1, Navbar and Docs 8, Collections 3, Backgrounds 8, total 76. Marketing copy in the repo says 46, 50+ and 80+ (`vengeance-ui:src/components/landing/landing-page-grid.tsx`, `vengeance-ui:src/lib/marketing-pages.ts`); those numbers do not match the files.

## Notable components

Files are under `vengeance-ui:src/components/ui/` as cited. "None" means no pattern record yet.

| Name | What it does (as read in code) | File | Pattern |
|---|---|---|---|
| Animated Button | framer-motion CTA, looping shine mask and border sweep, spring hover and tap | `vengeance-ui:src/components/ui/animated-button.tsx` | vengeance-ui-animated-cta-buttons |
| Candy, Radial Glow, Generate Button | radial-gradient glossy button; CSS-only glow driven by `@property` variables; hue-configurable AI-style button | `vengeance-ui:src/components/ui/candy-button.tsx`, `vengeance-ui:src/components/ui/radial-glow-button.tsx`, `vengeance-ui:src/components/ui/generate-button.tsx` | vengeance-ui-animated-cta-buttons |
| Pop, Creepy, Corner, Social Flip Button | layered-shadow pushable button; eyes follow the pointer; animated corner marks with `accentColor`; letter tiles that flip to social icons | `vengeance-ui:src/components/ui/pop-button.tsx`, `vengeance-ui:src/components/ui/creepy-button.tsx`, `vengeance-ui:src/components/ui/corner-button.tsx`, `vengeance-ui:src/components/ui/social-flip-button.tsx` | None |
| Liquid Metal | Paper Design shader as a button border; exports `LiquidMetal` and `LiquidMetalButton` | `vengeance-ui:src/components/ui/liquid-metal.tsx` | vengeance-ui-liquid-metal-button |
| Gooey Text Reveal | GSAP SplitText lines plus SVG goo filter; modes immediate, scroll, scrub; skips when reduced motion is set | `vengeance-ui:src/components/ui/gooey-text-reveal.tsx` | vengeance-ui-gooey-text-reveal |
| Stagger Text, Flip Fade Text, Morph Text, Stats Counter | masked slide-up reveal; letter flip word cycler; SVG-threshold word morph; spring count-up on view | `vengeance-ui:src/components/ui/staggerText.tsx`, `vengeance-ui:src/components/ui/flip-fade-text.tsx`, `vengeance-ui:src/components/ui/morph-text.tsx`, `vengeance-ui:src/components/ui/stats-counter.tsx` | vengeance-ui-kinetic-text-effects |
| Flip Text, Animated Number, Liquid Text, ASCII Glitch Ripple | CSS 3D per-character flip (needs global CSS); digit roll; three.js text distortion with text fallback; character-scramble ripple on hover | `vengeance-ui:src/components/ui/flip-text.tsx`, `vengeance-ui:src/components/ui/animated-number.tsx`, `vengeance-ui:src/components/ui/liquid-text.tsx`, `vengeance-ui:src/components/ui/ascii-glitch-ripple.tsx` | None |
| Spotlight, Notch, Mega Menu Navbar | pill with cursor spotlight; cutout header with SVG outlines; SaaS mega menu with mobile dialog | `vengeance-ui:src/components/ui/spotlight-navbar.tsx`, `vengeance-ui:src/components/ui/notch-navbar.tsx`, `vengeance-ui:src/components/ui/mega-menu-navbar.tsx` | vengeance-ui-landing-navbars |
| Glass Dock, Awwwards Nav, Verse Cards | macOS-style dock with morphing icons; bottom pill expanding to a mega menu; nav tile fanning a card deck | `vengeance-ui:src/components/ui/glass-dock.tsx`, `vengeance-ui:src/components/ui/awwwards-nav.tsx`, `vengeance-ui:src/components/ui/verse-cards.tsx` | vengeance-ui-floating-dock-navigation |
| Gooey Search, Search Modal | blob search button with debounced results; command-palette modal with a Cmd/Ctrl+K hotkey | `vengeance-ui:src/components/ui/gooey-search.tsx`, `vengeance-ui:src/components/ui/search-modal.tsx` | None |
| Agent, Expandable, Developer Service, Why Us Bento | animated bento grids; expandable one opens cards into a shared-layout overlay | `vengeance-ui:src/components/ui/agent-bento-grid.tsx`, `vengeance-ui:src/components/ui/expandable-bento-grid.tsx`, `vengeance-ui:src/components/ui/research-bento-grid.tsx`, `vengeance-ui:src/components/ui/why-us-bento.tsx` | vengeance-ui-bento-grids |
| Highlight Grid, Glow Border Card, Testimonials Card, Team Reveal Grid | sliding hover highlight; conic-gradient border via `@property`; animated testimonial stack; team portraits with auto-cycling reveal | `vengeance-ui:src/components/ui/highlight-grid.tsx`, `vengeance-ui:src/components/ui/glow-border-card.tsx`, `vengeance-ui:src/components/ui/testimonials-card.tsx`, `vengeance-ui:src/components/ui/team-reveal-grid.tsx` | None |
| Staggered Grid, Image Scatter | GSAP ScrollTrigger galleries (imagesloaded for the grid) | `vengeance-ui:src/components/ui/staggered-grid.tsx`, `vengeance-ui:src/components/ui/image-scatter.tsx` | None |
| Perspective, Diagonal, Cylinder Carousel, Circular Gallery | spring-driven carousels with ARIA and arrow keys; pure-CSS rotating cylinder; GSAP ring of up to 150 cards | `vengeance-ui:src/components/ui/perspective-carousel.tsx`, `vengeance-ui:src/components/ui/diagonal-carousel.tsx`, `vengeance-ui:src/components/ui/cylinder-carousel.tsx`, `vengeance-ui:src/components/ui/circular-gallery.tsx` | vengeance-ui-3d-image-carousels |
| Scroll Dissolve Reveal, Interactive Particles, 3D Books Showcase, Wave Grid | scroll-driven shader dissolve; image-sampled GPU particles; procedural 3D books; cursor-driven cube-grid waves | `vengeance-ui:src/components/ui/scroll-dissolve-reveal.tsx`, `vengeance-ui:src/components/ui/interactive-particles.tsx`, `vengeance-ui:src/components/ui/books-showcase.tsx`, `vengeance-ui:src/components/ui/wave-grid-background.tsx` | vengeance-ui-three-js-scenes |
| Model Viewer, Ripple Displacement Slider, Liquid Ocean | R3F GLB viewer with arrow-key rotation; full-screen WebGL slider; R3F ocean scene | `vengeance-ui:src/components/ui/model-viewer.tsx`, `vengeance-ui:src/components/ui/ripple-displacement-slider.tsx`, `vengeance-ui:src/components/ui/liquid-ocean.tsx` | vengeance-ui-three-js-scenes |
| Image Trail, Pixelated Image Trail, Cursor Card | pointer-spawned image trails; hover preview card in a portal | `vengeance-ui:src/components/ui/image-trail.tsx`, `vengeance-ui:src/components/ui/pixelated-image-trail.tsx`, `vengeance-ui:src/components/ui/cursor-card.tsx` | vengeance-ui-cursor-image-trails |
| Aurora Hero, Animated Rays, Fluid Morph, Light Lines | stripe-and-rainbow aurora with fluted-glass title; same stripes needing global CSS; morphing SVG blobs; SVG light streaks | `vengeance-ui:src/components/ui/aurora-hero.tsx`, `vengeance-ui:src/components/ui/animated-rays.tsx`, `vengeance-ui:src/components/ui/fluid-morph-bg.tsx`, `vengeance-ui:src/components/ui/light-lines.tsx` | vengeance-ui-aurora-hero-backgrounds |
| Twisting Ribbon, Perspective Grid | canvas 2D ribbon; CSS tile grid with hover colours (needs global CSS) | `vengeance-ui:src/components/ui/twisting-ribbon.tsx`, `vengeance-ui:src/components/ui/perspective-grid.tsx` | None |
| Logo Slider, Stacked Logos, Magnetic Spotlight Marquee | logo marquee; cross-fading logo stacks; GSAP full-screen marquee | `vengeance-ui:src/components/ui/logo-slider.tsx`, `vengeance-ui:src/components/ui/stacked-logos.tsx`, `vengeance-ui:src/components/ui/magnetic-spotlight-marquee.tsx` | None |
| Elastic Stack, Masked Avatars, Shared Tooltip Avatars, Image Reveal List, FAQ Accordion | avatar and list hover effects; hand-rolled accordion | `vengeance-ui:src/components/ui/elastic-stack.tsx`, `vengeance-ui:src/components/ui/masked-avatars.tsx`, `vengeance-ui:src/components/ui/shared-tooltip-avatars.tsx`, `vengeance-ui:src/components/ui/image-reveal-list.tsx`, `vengeance-ui:src/components/ui/faq-accordion.tsx` | None |
| Line Hover Link, Folder Preview, Animated Tooltip | 11 underline variants (honours reduced motion); folder stack preview; spring SVG tooltip shapes | `vengeance-ui:src/components/ui/line-hover-link.tsx`, `vengeance-ui:src/components/ui/folder-preview.tsx`, `vengeance-ui:src/components/ui/animated-tooltip.tsx` | None |
| Kinetic Text Loader, Reveal Loader | CSS letter loader; GSAP ten-bar curtain preloader (Next-only font import) | `vengeance-ui:src/components/ui/kinetic-text-loader.tsx`, `vengeance-ui:src/components/ui/reveal-loader.tsx` | None |
| Share Sheet, Music Player, Animated Footer | portal share dialog with local QR; glass audio player; GSAP and canvas ASCII-art footer | `vengeance-ui:src/components/ui/share-sheet.tsx`, `vengeance-ui:src/components/ui/music-player.tsx`, `vengeance-ui:src/components/ui/animated-footer.tsx` | None |
| Interactive Book, Image Collage, Interactive and Typing Keyboard, Solar System | 3D page-flip book; scattered collage; keyboard UIs; orbiting icon ring | `vengeance-ui:src/components/ui/interactive-book.tsx`, `vengeance-ui:src/components/ui/image-collage.tsx`, `vengeance-ui:src/components/ui/interactive-keyboard.tsx`, `vengeance-ui:src/components/ui/typing-keyboard.tsx`, `vengeance-ui:src/components/ui/solar-system.tsx` | None |
| Smooth Scroll | Lenis with default options, in the registry (a tuned variant exists but is unused: `vengeance-ui:src/components/landing/smooth-scroll.tsx`) | `vengeance-ui:src/components/ui/smooth-scroll.tsx` | None |

## Design language as used in the code

- **Typography.** Inter (body) and Orbitron (`font-orbitron`, headings) loaded with `next/font/google`; headings are `font-medium tracking-tight` at `text-3xl md:text-4xl lg:text-6xl`; sub-headings use the mono stack (`vengeance-ui:src/app/layout.tsx`, `vengeance-ui:src/components/landing/heading.tsx`, `vengeance-ui:src/components/landing/subheading.tsx`). `--font-mono` names Geist Mono and Fira Code (`vengeance-ui:src/app/globals.css`) but Geist Mono is never loaded. Components pick their own families: Space Grotesk and Roboto are fetched at runtime from Google Fonts through a CSS `@import` (morph-text, kinetic-text-loader), Anton comes from `next/font/google` (reveal-loader), and Poppins (generate-button) and Instrument Sans and Serif (magnetic-spotlight-marquee) are named but never loaded.
- **Colour.** A monochrome zinc system: `--vng-*` tokens give white or zinc-950 backgrounds and a primary that equals the foreground in both modes, with red, green and yellow only for danger, success and warning (`vengeance-ui:public/r/vengeance-theme.json`, `vengeance-ui:src/app/globals.css`). Accent colour is local to each component (blue candy button, pastel pop button, lime corner button, rainbow aurora, orange footer ASCII art).
- **Composition.** The site frames sections in ruled borders (`md:border-x`, `divide-x`), uses isometric line illustrations and mono micro-labels, and shows components on neutral canvases (`vengeance-ui:src/components/landing/hero.tsx`, `vengeance-ui:src/components/landing/features.tsx`). Glass pills use `backdrop-blur`, soft shadows and hairline borders.
- **Motion.** Five stacks: framer-motion springs, `whileInView` and imperative `animate` (29 of the 76 catalog components); GSAP timelines, ticker, ScrollTrigger and SplitText (11); CSS keyframes, `@property` and inline `<style>` blocks (many); canvas 2D (5) and WebGL via three, react-three-fiber or Paper shaders (9); Lenis in one registry item. Easings are mostly expo-out-like cubic-béziers such as 0.22, 1, 0.36, 1, GSAP `power3.out` and `power4.inOut`, and springs with stiffness 200 to 500. Many effects loop forever.
- **Dark mode.** Class based: `next-themes` with `attribute="class"` and a Tailwind v4 `@custom-variant dark` rule. `animated-rays`, `spotlight-navbar` and `animated-footer` also read the theme directly (MutationObserver on `html` or `useTheme`).

## Dependencies

Ranges from `vengeance-ui:package.json`, licences from `vengeance-ui:package-lock.json`.

| Package | Range | Used by | Licence in lockfile |
|---|---|---|---|
| framer-motion | ^13.4.4 | 29 catalog components | MIT |
| gsap, @gsap/react | ^3.15.0, ^2.1.2 | 11 catalog components, reveal-loader | GSAP standard no-charge licence (its own terms) |
| three, @react-three/fiber, @react-three/drei | ^0.186.1, ^9.8.1, ^10.7.9 | 8 components (3 with R3F) | MIT |
| @paper-design/shaders-react | ^0.0.81 | liquid-metal | Apache-2.0 |
| lenis | ^1.3.26 | smooth-scroll | MIT |
| tailwindcss, @tailwindcss/postcss | ^4.3.3 | all styling | MIT |
| next, react | 16.3.6, ^19.3.0 | site; some components import next/link or next/font | MIT |
| lucide-react, react-icons, @phosphor-icons/react | ^1.48.0, ^5.7.0, ^2.1.10 | icons (33, 5 and 4 ui files) | ISC, MIT, MIT |
| Radix packages, class-variance-authority, clsx, tailwind-merge | various | primitives and `cn` | MIT (cva Apache-2.0) |
| next-themes | ^0.4.6 | theme provider, notch-navbar, animated-footer | MIT |
| qrcode-generator, imagesloaded, zod, shiki | various | share-sheet, staggered-grid, morphing-disclosure, code-block | MIT |

Node `^22.13.0 || >=24.0.0` for the repo. Site-only packages (`stripe`, `@vercel/analytics`, `@vercel/speed-insights`) are not needed by consumers.

## Performance observations

- Site level: landing sections use `content-visibility: auto`, a global `.paused-section` rule pauses CSS animations, and the landing component grid keeps only two CSS animations running (`vengeance-ui:src/app/globals.css`, `vengeance-ui:src/app/landing-grid.css`). The `LazySection` wrapper that toggles that class is defined but not used anywhere (`vengeance-ui:src/components/landing/lazy-section.tsx`).
- Good component habits: `books-showcase` lowers pixel ratio and antialiasing on low-power devices and shows a message without WebGL; `interactive-particles` caps at 30 fps and stops offscreen; `liquid-ocean` sets the R3F frameloop to never when hidden; `scroll-dissolve-reveal` renders on demand; `circular-gallery` pauses offscreen. Most WebGL components dispose geometry and textures on unmount.
- No offscreen pause was found in `wave-grid-background`, `liquid-text` and `twisting-ribbon`, whose render loops run continuously.
- Each `LiquidMetalButton` mounts its own shader canvas. `circular-gallery` defaults to 150 `img` elements without lazy loading. Several CTAs loop animations forever.
- Whole libraries are imported (gsap with ScrollTrigger and SplitText, three), so load heavy items with a dynamic import inside a client component, as the docs demos do (`vengeance-ui:src/components/docs/demo-renderer.tsx`).

## Accessibility observations

- Reduced motion: only 7 of the 76 catalog components react to it (books-showcase, circular-gallery, cylinder-carousel, gooey-text-reveal, line-hover-link, research-bento-grid, share-sheet; circular-gallery only stops auto-rotation and cylinder-carousel only slows to one turn per 128 seconds). The site-wide `prefers-reduced-motion` rule in `globals.css` is not shipped with registry items and cannot affect JS-driven animation. The maintainers' funding file lists accessibility and reduced-motion support as planned work (`vengeance-ui:funding.json`).
- Keyboard and ARIA are strong in `mega-menu-navbar` (expanded and controls attributes, Escape, dialog, focus rings), `perspective-carousel` and `diagonal-carousel` (region, arrow keys, `aria-current`), `model-viewer` (arrow-key rotation, label) and `share-sheet` (focus return, labelled dialog). By text search, 41 of 76 catalog components contain none of `aria-`, `role`, key handlers or `tabIndex`.
- Focus styles are missing or removed on `pop-button` (none), `liquid-metal` (`outline-none`) and `faq-accordion` (`outline-none`); prefer the Radix `accordion` primitive for FAQs.
- Split-text effects (`staggerText`, `flip-text`, `morph-text`) add no label or live-region handling; `morph-text` keeps every word in the DOM at opacity 0. `gooey-text-reveal` passes `aria: "auto"` to SplitText.
- Pointer-only effects: spotlight glow, `circular-gallery`, `cursor-card`, `creepy-button`. `aurora-hero` draws its title with blend modes, so contrast depends on the background.
- Reduced-motion alternatives to apply are defined in `knowledge/implementation-recipes/vengeance-ui-motion-safe-wrapper.md`.

## Pitfalls

- What `shadcn add` installs is the JSON, and 15 of the 136 `registry:ui` items have a payload that differs from the file in `src/components/ui` (for example the published candy button lacks `tone`, `asChild` and the focus ring). `vengeance-ui:docs/dependency-validation.md` says the installers read `public/r`, not the source files.
- Six catalog items have no JSON in `public/r`: image-collage, cylinder-carousel, ripple-displacement-slider, solar-system, why-us-bento, magnetic-spotlight-marquee. Three more have JSON but are missing from `registry.json`.
- Dependency lists are hand-maintained and incomplete: 24 `registry:ui` items import an npm package missing from their `dependencies` (12 of them only `class-variance-authority`; others include liquid-ocean and liquid-text without three, staggered-grid without imagesloaded and react-icons, smooth-scroll without lenis, agent-bento-grid without Phosphor icons). Ten docs install strings omit a package the in-tree file imports (staggered-grid omits gsap; liquid-ocean lists Paper shaders instead of three and R3F). Derive dependencies from the imports.
- Some items rely on CSS that lives only in the site's `globals.css`: flip-text, glass-dock, glow-border-card, perspective-grid, spotlight-navbar, stacked-logos, animated-rays, social-flip-button. The `logo-slider` rules were not found in any file. Detail and a check are in `knowledge/implementation-recipes/vengeance-ui-install-and-verify-component.md`.
- Some payloads import site modules they do not ship, such as `@/hooks/use-outside-click` (expandable-bento-grid) or `@/components/theme-toggle` and `@/assets/logo/logo-icon` (notch-navbar). Run `tsc` after every install.
- Brand and media defaults leak into components: "VENGEANCE" loader text, a "VengeanceUI" footer heading, anime-character PNGs in the ripple slider, Unsplash and pravatar hotlinks.
- `AuroraHero` declares `showSwitch` but never reads it, so the catalog's "interactive switch" does not exist in that file. `animated-rays` renders nothing until mounted. `morph-text` and `kinetic-text-loader` fetch Google Fonts at runtime through CSS `@import`.
- `spotlight-navbar` anchors call `preventDefault`; navigation must be wired through `onItemClick`. `expandable-bento-grid` resets `document.body.style.overflow` on every change.
- Tests cover registry payload parity for two items, a lint baseline (126 recorded errors), credits rendering and docs sidebar scrolling; no automated accessibility or visual tests of the animated components exist (`vengeance-ui:tests/`, `vengeance-ui:eslint-suppressions.json`).
- The docs "Install Next.js" page leads with a community crypto-token address (`vengeance-ui:src/app/docs/install-nextjs/page.tsx`). It is unrelated to the code but worth knowing before linking users to the site.

## Licence and reuse

- Code: MIT, Copyright (c) 2025-2026 Ashutoshx7 (`vengeance-ui:LICENSE`). Keep the notice when copying; the catalog marks attribution as required.
- Third-party origins inside the code: docblocks say these are ports or rebuilds of other authors' demos. Awwwards-nav, circular-gallery, highlight-grid, music-player, search-modal and verse-cards name CodeGrid demos; animated-footer names a different author's footer demo; interactive-particles names a Codrops demo by Bruno Imbrizi; wave-grid-background names a Three.js demo; animated-tooltip is Codrops-inspired; and staggered-grid shows a Codrops credit on the page. The original terms are not in this repo and were not checked.
- Contributor credits in `vengeance-ui:src/lib/component-docs.ts`: team-reveal-grid, stagger-text, interactive-keyboard, solar-system, mega-menu-navbar, books-showcase, share-sheet.
- Media under `public/` is not covered by the code licence in any way that was verified. Do not reuse: the anime-character PNGs, avatars, gallery, trail and painting photos, template screenshots, sponsor logos (brand assets per `vengeance-ui:public/sponsors/README.md`), the font `vengeance-ui:public/gooey-text-reveal/de-fonte-plus.ttf` and the model `vengeance-ui:public/models/sample.glb`. Remote Unsplash and pravatar defaults belong to their owners.
- npm dependencies keep their own licences; GSAP's applies to every `gsap` import. The block kits are unverified (see Directory map).
- For Design Sensei: describe and link patterns, and when a user wants the code, send them through the install recipe so they get the MIT notice with the source.

## Related

Patterns are listed in this note's front matter. Install and verification: `knowledge/implementation-recipes/vengeance-ui-install-and-verify-component.md`. One animated section end to end: `knowledge/implementation-recipes/vengeance-ui-gooey-text-hero-nextjs.md`. Fallbacks for heavy or looping components: `knowledge/implementation-recipes/vengeance-ui-motion-safe-wrapper.md`.
