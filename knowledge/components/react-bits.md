---
title: "React Bits component library"
kind: component-library
summary: "Source-verified map of React Bits (MIT + Commons Clause): 215 copy-in animated React components in four variants (JS or TS, plain CSS or Tailwind), how they are installed, what they import, and where they are heavy, fragile or weak on accessibility."
source_ids: [react-bits]
pattern_ids:
  - react-bits-ogl-shader-backgrounds
  - react-bits-self-pausing-shader-backgrounds
  - react-bits-three-r3f-backgrounds
  - react-bits-webgpu-backgrounds
  - react-bits-canvas-grid-backgrounds
  - react-bits-gsap-text-reveals
  - react-bits-lightweight-text-effects
  - react-bits-target-cursor
  - react-bits-webgl-cursor-trails
  - react-bits-scroll-driven-components
  - react-bits-bento-and-card-grids
  - react-bits-pointer-lit-cards
  - react-bits-animated-navigation-menus
  - react-bits-3d-image-galleries
  - react-bits-glass-surfaces
  - react-bits-micro-spring-controls
updated: "2026-10-09"
---

# React Bits

Read from the checkout pinned in `catalog/sources.yaml` (commit `d86fccb`, "rebuild LaserFlow"; sparse checkout of `src/` and `scripts/` plus root files). Nothing was executed. Counts come from directory listings and from regular-expression scans of the TS + Tailwind files, so treat them as approximate. The component code is licence-restricted: this note describes behaviour and cites paths, it never reproduces code.

## What it is

- A collection of animated, interactive React components by David Haz (`react-bits:README.md`, `react-bits:LICENSE.md`). It is not an npm library. The repository is the documentation site (a private Vite + React 19 app, `react-bits:package.json`, version 0.0.0) plus the component sources and a registry definition (`react-bits:jsrepo.config.ts`). The upstream introduction describes the model: you install source you then own, props are the main customisation surface, and nothing depends on React Bits at runtime (`react-bits:src/docs/Introduction.jsx`).
- 215 components in five categories (`react-bits:src/constants/Information.js`); the README says "200+". The library moves fast: 25 of the 27 changelog entries in that file are "rebuilt" notes dated 2026-10-08 or 2026-10-09 (Threads, Iridescence, Dock, Lanyard, InfiniteMenu and others). Prop lists remembered from older tutorials may be wrong, so read the file you install.
- Out of scope here: React Bits Pro (separate paid product; only marketing metadata sits in `react-bits:src/constants/Pro.js`), three free browser tools in `react-bits:src/tools/` (Background Studio, Shape Magic, Texture Lab) and the official Vue and Svelte ports named in the README.
- Contribution policy (`react-bits:CONTRIBUTING.md`): no new community components, only fixes and enhancements, and every change must land in all four variants.

## Repository map

| Path | Contents |
|---|---|
| `react-bits:src/content/`, `react-bits:src/tailwind/`, `react-bits:src/ts-default/`, `react-bits:src/ts-tailwind/` | the four variant trees, one folder per component under `<Category>/<Name>/` |
| `react-bits:src/demo/` | one `<Name>Demo.jsx` per component: live preview, prop controls and the `propData` props table (the best prop reference) |
| `react-bits:src/constants/Information.js` | per component: description, category, docs URL, added date, update notes, optional tags |
| `react-bits:src/constants/code/` | per component: imports the five source strings plus a usage snippet and a dependency string |
| `react-bits:src/docs/` | Introduction, Installation, MCP Server and Changelog pages |
| `react-bits:src/components/`, `react-bits:src/hooks/`, `react-bits:src/utils/`, `react-bits:src/pages/` | the docs website (Chakra UI, router, search), not part of the library |
| `react-bits:scripts/` | scaffolding, registry watcher, prop-docs checker, llms.txt, sitemap, OG images, Pro sync |

## The four variants

| Registry suffix | Folder | Language | Styling | Files per component | Previewed by the docs site |
|---|---|---|---|---|---|
| JS-CSS | `react-bits:src/content/` | JavaScript | plain CSS file imported by the component (196 of 215 have one) | `.jsx` + `.css` | 209 of 215 demos |
| JS-TW | `react-bits:src/tailwind/` | JavaScript | Tailwind utility classes, no stylesheet | `.jsx` | 1 demo (InfiniteSpiral) |
| TS-CSS | `react-bits:src/ts-default/` | TypeScript | plain CSS | `.tsx` + `.css` | 5 demos (Plasma, Ferrofluid, GradientBlinds, Lightfall, Antigravity) |
| TS-TW | `react-bits:src/ts-tailwind/` | TypeScript | Tailwind | `.tsx` | none |

Evidence: the mapping is declared in `react-bits:jsrepo.config.ts` and mirrored by the Vite aliases in `react-bits:vite.config.js`; each module in `react-bits:src/constants/code/` imports the five source strings of one component. All four trees hold the same 215 folders (names compared per category). The folder names do not match the suffixes, so use the table. The variants are hand-maintained copies: nothing generates one from another (`react-bits:scripts/generateComponent.js` only scaffolds empty files) and `react-bits:scripts/checkPropDocs.js` exists to catch default-value drift between them. All 860 component files start with the client-component directive.

## Installing (as the source documents it)

| Route | Shape of the command | Where documented |
|---|---|---|
| shadcn CLI | `npx shadcn@latest add @react-bits/<Name>-<Variant>` | `react-bits:README.md`, `react-bits:src/docs/Installation.jsx` |
| jsrepo CLI | `npx jsrepo@latest add https://reactbits.dev/r/<Name>-<Variant>` | `react-bits:src/docs/Installation.jsx`, `react-bits:src/utils/cli.js` |
| Manual copy | copy the files from a component's Code tab and install the npm packages it lists | `react-bits:src/docs/Installation.jsx` |
| AI client via shadcn MCP | add an `@react-bits` entry to `registries` in `components.json`, run `npx shadcn@latest mcp init --client claude` (or cursor, vscode), restart the client | `react-bits:src/docs/McpServer.jsx` |

`<Variant>` is JS-CSS, JS-TW, TS-CSS or TS-TW. For other package managers the docs swap `npx` for `pnpm dlx`, `yarn` or `bun x --bun`. The README example installs BlurText in the TS-TW variant. The registry config (`react-bits:jsrepo.config.ts`) builds one item per component and variant, named `<Name>-<Variant>`, from the component's whole folder. Stylesheets are listed as separate files targeted at the `components` alias so the component's relative CSS import still resolves. The config sets `excludeDeps` to React only and lists no npm packages by hand.

Not verified from this checkout: the generated registry JSON (`public/` is not checked out), whether the CLIs install npm dependencies for you, whether `shadcn add` needs an initialised `components.json` (the README does not say), and minimum React or Tailwind versions (the upstream site runs React 19 and Tailwind 4). `react-bits:src/tools/background-studio/backgrounds/index.js` still shows an older URL style (`/default/backgrounds/<slug>`); prefer the forms above.

## Categories

| Folder (site label) | Components | GPU-driven | What is in it |
|---|---|---|---|
| `Backgrounds` | 59 | 53 | full-bleed backdrops: 34 OGL shaders, 10 three.js, 3 R3F, 4 raw WebGL, 2 WebGPU; the other 6 are canvas 2D (5) or DOM (1) |
| `Animations` | 41 | 20 | a grab bag: cursor effects and trails, animated borders, grain overlay, scroll wrappers, shader widgets |
| `Components` | 48 | 12 | navigation menus, cards, bento grids, carousels, galleries, glass surfaces |
| `TextAnimations` ("Text Animations") | 33 | 2 | reveals, scramble, marquees, gradient and shader text |
| `Micro` | 34 | 1 | form-level micro-interactions (switch, hold-to-confirm, OTP input, toast); all added 2026-09-18 to 2026-09-22 |

"GPU-driven" means the file imports `ogl`, `three`, `@react-three/fiber` or `vgpu`, or requests a WebGL context directly. 88 of 215 components qualify.

## What components import (TS + Tailwind files)

| Package | Components | Typical use | Version in upstream `package.json` |
|---|---|---|---|
| `ogl` | 50 | shader backgrounds, cursors, galleries, text | ^1.0.11 |
| `motion` (imported as `motion/react`) | 36 | springs and layout animation in micro, text, cards | ^12.23.12 |
| `gsap` | 30 | ScrollTrigger reveals, timelines, menus | ^3.13.0 |
| `three` | 22 | 3D backgrounds, cursors, Lanyard | ^0.180.0 |
| `@hugeicons/react`, `@hugeicons/core-free-icons` | 16, 18 | icons in Micro and Carousel | ^1.1.10, ^4.3.3 |
| `@react-three/fiber`, `@react-three/drei` | 7, 4 | R3F canvases | ^9.3.0, ^10.7.4 |
| `postprocessing`, `@react-three/postprocessing` | 3, 1 | Dither, GridScan, PixelBlast | ^6.36.0, ^3.0.4 |
| `vgpu` | 2 | the WebGPU backgrounds | ^0.3.1 |
| `matter-js`, `@gsap/react` | 2, 2 | physics text and folder; `useGSAP` | ^0.20.0, ^2.1.2 |
| single use | 1 each | `lenis` (ScrollStack), `face-api.js` (GridScan), `@use-gesture/react` (DomeGallery), `maath` (FluidGlass), `lucide-react` (ReflectiveCard), `react-icons` (CardNav), `react-router-dom` (PillNav) | see file |

63 components import nothing beyond React. GSAP plugins in use: ScrollTrigger (8 files), SplitText (3), and Draggable, Observer, InertiaPlugin, ScrambleTextPlugin (1 each). GSAP has its own licence terms (see `catalog/licenses.yaml`).

Do not trust `react-bits:package.json` as a per-component list: 18 of its packages (for example `@react-three/rapier`, `meshline`, `gl-matrix`, `mathjs`, `react-confetti`) are imported by no component. The "dependencies" strings in `react-bits:src/constants/code/` are also hand-written: 9 of 215 differ from the imports (FadeContent, StickerPeel and MagicRings import packages they do not list; GradualBlur lists `mathjs` but imports nothing). Read the imports of the variant you install.

## Performance observations

- Cost is dominated by the GPU backgrounds. In the 53 GPU-driven backgrounds the scan found an IntersectionObserver in 27, a visibilitychange listener in 20, neither in 26, a reduced-motion check in 10, a devicePixelRatio cap in about 37, and renderer cleanup in about 37. Only Plasma handles WebGL context loss.
- Older single-file shaders (`react-bits:src/ts-tailwind/Backgrounds/Aurora/Aurora.tsx`, `react-bits:src/ts-tailwind/Backgrounds/DarkVeil/DarkVeil.tsx`) run a frame loop forever. The R3F backgrounds Beams and Silk force an always-on frame loop at DPR 1 to 2.
- Best-equipped examples: `react-bits:src/ts-tailwind/Backgrounds/Plasma/Plasma.tsx` (render-scale, max-DPR, target-fps and iteration props; one static frame under reduced motion; context-loss handlers), `react-bits:src/ts-tailwind/Backgrounds/AeroShards/AeroShards.tsx` and `react-bits:src/ts-tailwind/Backgrounds/ShapeWaves/ShapeWaves.tsx` (WebGPU; `paused` and `onError` props; AeroShards picks a quality tier from device memory, core count and canvas size and lowers it at runtime), `react-bits:src/ts-tailwind/Backgrounds/LightPillar/LightPillar.tsx` (quality tiers, user-agent downgrade on mobile, a visible unsupported-WebGL state).
- Upstream's own advice (`react-bits:src/docs/Introduction.jsx`): use no more than two or three of these on a page, swap heavy effects for static placeholders on mobile, test on several devices. The docs site gates its own previews on desktop width, a fine pointer, no reduced-motion preference and no data-saver (`react-bits:src/hooks/usePreviewMediaAllowed.js`) and uses an in-view plus tab-visible render gate (`react-bits:src/utils/renderGate.js`).
- 15 files default to remote placeholder images (Unsplash, picsum, pravatar), for example CircularGallery, DomeGallery, DepthCarousel, MorphSlider. Replace them and size real images.
- Budgeting and fallbacks: `knowledge/implementation-recipes/react-bits-heavy-background-budget.md`.

## Accessibility observations

- Reduced motion: 95 of 215 components check it (JS, a CSS media query or Tailwind `motion-reduce:`; the two TypeScript variants agree): Micro 34 of 34, Components 19 of 48, Animations 17 of 41, TextAnimations 14 of 33, Backgrounds 11 of 59. Treat the rest as "no support" and gate them yourself.
- Micro is the best-built group: every component sets ARIA attributes and 26 of 34 handle keyboard events. Elsewhere it is uneven: PillNav, StaggeredMenu and BubbleMenu carry ARIA, FlowingMenu (Tailwind variants), MagicBento, ChromaGrid, Masonry, CardSwap, Stepper and Counter carry none.
- Text splitters (SplitText, BlurText, ScrollFloat) wrap letters or words in spans and contain no label or screen-reader text handling in their TS + Tailwind files; DecryptedText, FoldText, ParticleText and RotatingText do add some. Whether GSAP's SplitText adds ARIA labelling itself was not verified, so test with a screen reader.
- Only 9 of 59 backgrounds mark themselves `aria-hidden`; wrap decorative canvases yourself. TargetCursor hides the native cursor on the whole page by default, ReflectiveCard asks for camera access on mount, GridScan can use the webcam when enabled.
- Several effects flicker or glitch by design (GlitchText, LetterGlitch, FaultyTerminal, Noise); check them against flashing-content guidance before using them near reading text.

## Pitfalls

1. **Variants are not perfect twins.** Ballpit's TS variants also import GSAP (`react-bits:src/ts-tailwind/Backgrounds/Ballpit/Ballpit.tsx`); ElasticSlider's CSS variants pull in Chakra UI and react-icons while the Tailwind ones do not (`react-bits:src/ts-default/Components/ElasticSlider/ElasticSlider.tsx`). The JS + Tailwind StaggeredMenu has stray import-like text inside an embedded CSS rule near line 522 that corrupts the panel's `position` declaration (`react-bits:src/tailwind/Components/StaggeredMenu/StaggeredMenu.jsx`). Check the exact variant.
2. **"Tailwind variant" can still need extra CSS.** 22 of the 215 TS + Tailwind files embed a `<style>` block (for example `react-bits:src/ts-tailwind/Components/MagicBento/MagicBento.tsx`), and GlitchText only animates after you add keyframes and animation entries to the Tailwind config, as a trailing comment explains (`react-bits:src/ts-tailwind/TextAnimations/GlitchText/GlitchText.tsx`).
3. **CSS variants leak globals.** Six declare generic custom properties on `:root` (MagicBento, Cubes, Folder, ProfileCard, StickerPeel, GooeyNav), for example hue, white and border-color style names; check for clashes with your tokens (`react-bits:src/content/Components/MagicBento/MagicBento.css`).
4. **Content and assets are baked in.** MagicBento's tiles are a constant inside the file (`react-bits:src/ts-tailwind/Components/MagicBento/MagicBento.tsx`); FluidGlass expects GLB models at root-absolute `/assets/3d/` paths, which a folder-only registry install would not include (`react-bits:src/ts-tailwind/Components/FluidGlass/FluidGlass.tsx`); StaggeredMenu defaults to the upstream repo's logo path (`react-bits:src/ts-tailwind/Components/StaggeredMenu/StaggeredMenu.tsx`); TextPressure fetches a Google-hosted font by default.
5. **Framework coupling.** PillNav imports `Link` from `react-router-dom` and renders it for internal hrefs, so it needs a Router or an edit for Next.js (`react-bits:src/ts-tailwind/Components/PillNav/PillNav.tsx`). ScrollStack creates its own Lenis instance (`react-bits:src/ts-tailwind/Components/ScrollStack/ScrollStack.tsx`), which clashes with a site-wide one.
6. **Lifecycle bugs.** SplashCursor registers window listeners and a frame loop with no cleanup and re-runs on prop changes, so mount it once at the root (`react-bits:src/ts-tailwind/Animations/SplashCursor/SplashCursor.tsx`). PixelBlast exposes an offscreen-pause flag that nothing ever updates, so it never pauses (`react-bits:src/ts-tailwind/Backgrounds/PixelBlast/PixelBlast.tsx`). AnimatedContent hides its children until its effect runs and restarts when callback props change identity (`react-bits:src/ts-tailwind/Animations/AnimatedContent/AnimatedContent.tsx`); do not wrap the LCP element in it.
7. **Network and permissions.** GridScan loads face-detection weights from a public CDN on mount even when the webcam is off (`react-bits:src/ts-tailwind/Backgrounds/GridScan/GridScan.tsx`). ReflectiveCard requests the camera immediately (`react-bits:src/ts-tailwind/Components/ReflectiveCard/ReflectiveCard.tsx`).
8. **Docs pages mostly exercise one variant.** The live previews run the JS-CSS copy (209 of 215), so TS and Tailwind copies get less real-world testing.

## Licence and reuse

`react-bits:LICENSE.md` is a custom text, MIT plus a Commons Clause style restriction, copyright David Haz. In paraphrase: you may use, copy and modify the components as part of an application, website or product, commercial ones included, as long as the copyright and permission notice stay with copies; you may not sell, sublicense or redistribute the components themselves, whether alone, in a bundle or as a port. The README summarises it as free for personal and commercial use and notes that some components draw on public code examples (credit requests go through issues). Design Sensei therefore describes and cites React Bits and never copies or republishes its components. This is not legal advice; see `knowledge/implementation-recipes/react-bits-license-safe-usage.md`.

## Related

- Catalog of 100 components: `knowledge/components/react-bits-catalog.md`.
- Recipes: `knowledge/implementation-recipes/react-bits-choose-variant-and-install.md`, `knowledge/implementation-recipes/react-bits-heavy-background-budget.md`, `knowledge/implementation-recipes/react-bits-license-safe-usage.md`.
