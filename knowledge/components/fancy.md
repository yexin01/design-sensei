---
title: "Fancy Components (animated React components)"
kind: component-library
summary: "Source-verified map of Fancy Components, a copy-and-paste React, Tailwind and Motion collection of text effects, cursor trails, physics, marquees and 3D blocks: how it is installed, what each family does, performance and accessibility findings, pitfalls and MIT reuse terms."
source_ids: [fancy]
pattern_ids: [fancy-letter-swap-text, fancy-vertical-cut-reveal, fancy-text-rotate, fancy-scramble-text, fancy-variable-font-text, fancy-text-highlighter, fancy-cursor-proximity-text, fancy-image-trail, fancy-pixel-trail, fancy-matter-gravity, fancy-stacking-cards, fancy-simple-marquee, fancy-box-carousel, fancy-animated-gradient-svg, fancy-svg-filters]
updated: "2026-10-09"
---

# Fancy Components

Read from the checkout pinned in `catalog/sources.yaml` (commit `f9f62c6`). Nothing was executed; every statement below comes from reading files.

## What it is

- A collection of animated React components and microinteractions (`fancy:README.md`), published as copy-and-paste source rather than as a package (`fancy:src/content/docs/introduction.mdx`). Copyright holder: Daniel Petho (`fancy:LICENSE`). Docs site: fancycomponents.dev (`fancy:src/config/site.ts`).
- Stack named by its own docs: React, TypeScript, Tailwind CSS and Motion (`fancy:src/content/docs/introduction.mdx`). All animation helpers are imported from `motion/react`; there is no GSAP, Three.js or shader code under `fancy:src/fancy/components/`. Physics uses Matter.js.
- Intent (`fancy:ACCEPTANCE_CRITERIA.md`): playful, unconventional effects rather than utility UI; contributors must credit inspirations and not copy other work one-to-one.
- A few files name another author in a header comment (Khoa Phan: `fancy:src/fancy/components/blocks/stacking-cards.tsx`, `fancy:src/fancy/components/image/image-trail.tsx`).

## How components are consumed

`fancy:package.json` is `private` and defines no library build or exports, so there is no npm package to install. Two routes are documented in `fancy:src/content/docs/installation.mdx`:

1. **shadcn CLI.** The project needs a `components.json` whose `registries` field contains the `@fancy` entry (the repository's own `fancy:components.json` shows the URL template). Then `shadcn add @fancy/<component-name>` copies the component plus the hooks and utilities it imports. The docs warn that extra npm dependencies are only added to `package.json`; install them yourself.
2. **Manual copy.** Copy the source from the "Installation" tab of the component page and fix the import paths.

Both routes assume Tailwind CSS and `motion` are installed. Components import `cn` from `@/lib/utils` (clsx plus tailwind-merge, `fancy:src/lib/utils.ts`); the `utils` alias in `components.json` points there.

How the registry is generated (`fancy:src/scripts/build-registry-index.ts`, `fancy:src/scripts/build-registry-sources.ts`):

- The registry name is the file base name (`letter-swap-forward-anim.tsx` becomes `@fancy/letter-swap-forward-anim`).
- External dependencies are inferred from import statements, skipping names that start with `react` or `next`; scoped packages and `@/` aliases are not detected. Hooks come from `@/hooks/...` imports and helpers from `@/utils/...`. Extra items (CSS variables, `poly-decomp`, `@types/matter-js`) come from a `.json` file beside the component, for example `fancy:src/fancy/components/physics/gravity.json`.
- Install targets are `components/fancy/<category>/<file>.tsx`, `hooks/<file>.ts` and `utils/<file>.ts`; imports of `@/fancy/components/...` are rewritten to `@/components/fancy/...`.
- Generated output (`public/r/`, `src/fancy/index.ts`, `public/docs/`) is git-ignored (`fancy:.gitignore`), so a clone contains no registry JSON.
- `fancy:src/content/docs/components/blocks/css-box.mdx` installs `@fancy/3d-css-box` while the file is `css-box.tsx`. The live registry name was not verified.
- Every docs page is also published as markdown for LLMs (`fancy:public/llms.txt`).

## Directory map

| Path | Contents |
|---|---|
| `fancy:src/fancy/components/` | the components, one folder per category: `text`, `background`, `blocks`, `carousel`, `filter`, `image`, `physics` |
| `fancy:src/fancy/examples/` | demo files used by the docs previews, several per component |
| `fancy:src/fancy/schema.ts` | zod schema of a registry item |
| `fancy:src/hooks/` | shared hooks: pointer position, dimensions, line measuring |
| `fancy:src/utils/` | `calculate-position`, `svg-path-to-vertices`, demo image data |
| `fancy:src/content/docs/` | one MDX page per component: install, usage, notes, props |
| `fancy:src/config/docs.ts` | sidebar list of released components |
| `fancy:src/scripts/` | generators for registry, markdown docs and `llms.txt` |
| `fancy:src/app/`, `fancy:src/components/` | the Next.js docs website, not part of the library |
| `fancy:public/` | fonts, icons and `llms.txt` |

## Component families

Registry names equal file base names unless noted. "-" means no dedicated catalog pattern.

| Component | What it does | File | Pattern |
|---|---|---|---|
| Letter Swap (forward, ping-pong) | Each letter rolls out and a duplicate rolls in on hover; ping-pong reverses on leave (lodash debounce) | `fancy:src/fancy/components/text/letter-swap-forward-anim.tsx`<br>`fancy:src/fancy/components/text/letter-swap-pingpong-anim.tsx` | `fancy-letter-swap-text` |
| Random Letter Swap | Same roll, letters in shuffled order | `fancy:src/fancy/components/text/random-letter-swap-forward-anim.tsx`<br>`fancy:src/fancy/components/text/random-letter-swap-pingpong-anim.tsx` | `fancy-letter-swap-text` |
| Letter 3D Swap | Each letter is a small CSS 3D box that rotates to a second face; four directions | `fancy:src/fancy/components/text/letter-3d-swap.tsx` | `fancy-letter-swap-text` |
| Vertical Cut Reveal | Words, characters or lines slide up out of an overflow-hidden mask; ref methods start and reset | `fancy:src/fancy/components/text/vertical-cut-reveal.tsx` | `fancy-vertical-cut-reveal` |
| Text Rotate | Cycles through a list of strings with `AnimatePresence`; `auto`, `next()`, `previous()`, `jumpTo()` | `fancy:src/fancy/components/text/text-rotate.tsx` | `fancy-text-rotate` |
| Scramble Hover, Scramble In | Random-character scramble that resolves to the text, on hover or on mount | `fancy:src/fancy/components/text/scramble-hover.tsx`<br>`fancy:src/fancy/components/text/scramble-in.tsx` | `fancy-scramble-text` |
| Typewriter | Types and deletes one or several strings with a blinking cursor | `fancy:src/fancy/components/text/typewriter.tsx` | - |
| Text Highlighter | Marker highlight drawn by animating `background-size`; triggers hover, ref, in-view or auto | `fancy:src/fancy/components/text/text-highlighter.tsx` | `fancy-text-highlighter` |
| Underline animations | A separate div acts as underline (from centre, in-then-out, out-then-in) and a variant that fills the text background | `fancy:src/fancy/components/text/underline-center.tsx`<br>`fancy:src/fancy/components/text/underline-comes-in-goes-out.tsx`<br>`fancy:src/fancy/components/text/underline-goes-out-comes-in.tsx`<br>`fancy:src/fancy/components/text/underline-to-background.tsx` | - |
| Variable-font hover, Breathing Text | Animate `font-variation-settings` per letter on hover, in random order, or continuously; needs a variable font | `fancy:src/fancy/components/text/variable-font-hover-by-letter.tsx`<br>`fancy:src/fancy/components/text/variable-font-hover-by-random-letter.tsx`<br>`fancy:src/fancy/components/text/breathing-text.tsx` | `fancy-variable-font-text` |
| Cursor-driven text | Per-letter effect scaled by pointer distance (any CSS property, or font axes); one variant maps pointer x and y to two font axes | `fancy:src/fancy/components/text/text-cursor-proximity.tsx`<br>`fancy:src/fancy/components/text/variable-font-cursor-proximity.tsx`<br>`fancy:src/fancy/components/text/variable-font-and-cursor.tsx` | `fancy-cursor-proximity-text` |
| Scroll and Swap | Text slides vertically as a spring-smoothed function of scroll progress | `fancy:src/fancy/components/text/scroll-and-swap-text.tsx` | - |
| Text Along Path | SVG `textPath` moved by SMIL animation or by scroll progress | `fancy:src/fancy/components/text/text-along-path.tsx` | - |
| Basic Number Ticker | Counts a number from one value to another with a motion value | `fancy:src/fancy/components/text/basic-number-ticker.tsx` | - |
| Animated Gradient with SVG | Blurred, randomly placed SVG circles drifting by CSS keyframes | `fancy:src/fancy/components/background/animated-gradient-with-svg.tsx` | `fancy-animated-gradient-svg` |
| Pixel Trail | Grid of div cells that flash where the pointer passes | `fancy:src/fancy/components/background/pixel-trail.tsx` | `fancy-pixel-trail` |
| Gravity | Wraps DOM children in a Matter.js world (rectangle, circle or SVG-path bodies), draggable, synced to DOM transforms | `fancy:src/fancy/components/physics/gravity.tsx` | `fancy-matter-gravity` |
| Cursor Attractor and Gravity | Same wrapper without gravity; an attractor point and the cursor push or pull bodies | `fancy:src/fancy/components/physics/cursor-attractor-and-gravity.tsx` | `fancy-matter-gravity` |
| Elastic Line | SVG line whose control point follows the pointer and springs back | `fancy:src/fancy/components/physics/elastic-line.tsx` | - |
| Image Trail | Pool of children that appear along the pointer path once it travels a threshold distance | `fancy:src/fancy/components/image/image-trail.tsx` | `fancy-image-trail` |
| Parallax Floating | Elements registered with a depth drift toward the pointer, eased each frame | `fancy:src/fancy/components/image/parallax-floating.tsx` | - |
| Gooey, Pixelate SVG filters | Hidden SVG filters (blur plus colour matrix; convolution plus tile plus morphology) applied via CSS `filter` | `fancy:src/fancy/components/filter/gooey-svg-filter.tsx`<br>`fancy:src/fancy/components/filter/pixelate-svg-filter.tsx` | `fancy-svg-filters` |
| Drag Elements | Motion `drag` with elastic constraints, inertia and bring-to-front | `fancy:src/fancy/components/blocks/drag-elements.tsx` | - |
| Circling Elements | Children orbit a centre by CSS keyframes driven by custom properties | `fancy:src/fancy/components/blocks/circling-elements.tsx` | - |
| Media Between Text | Image or video expands between two text runs on hover, ref or in-view | `fancy:src/fancy/components/blocks/media-between-text.tsx` | - |
| CSS Box | Six-face CSS 3D box with spring rotation, drag and ref methods (`showFront`, `rotateTo`); its docs install it as `3d-css-box` | `fancy:src/fancy/components/blocks/css-box.tsx` | - |
| Screensaver | Child bounces off container edges (DVD-logo motion) | `fancy:src/fancy/components/blocks/screensaver.tsx` | - |
| Float | Sine-wave drift and tilt on six motion values | `fancy:src/fancy/components/blocks/float.tsx` | - |
| Stacking Cards | Sticky cards that scale down as later cards stack over them, driven by `useScroll` | `fancy:src/fancy/components/blocks/stacking-cards.tsx` | `fancy-stacking-cards` |
| Simple Marquee | Frame-driven marquee with hover slow-down, scroll-velocity response, drag and easing | `fancy:src/fancy/components/blocks/simple-marquee.tsx` | `fancy-simple-marquee` |
| Marquee Along SVG Path | Marquee whose items follow CSS `offset-path`; rolling z-index | `fancy:src/fancy/components/blocks/marquee-along-svg-path.tsx` | `fancy-simple-marquee` |
| Element Along SVG Path | Items move along a path by time or scroll; its sidebar entry is commented out in `fancy:src/config/docs.ts` and it has no docs page | `fancy:src/fancy/components/blocks/element-along-svg-path.tsx` | - |
| Box Carousel | Four-face rotating cube of images or videos; drag, arrow keys, ref, optional autoplay | `fancy:src/fancy/components/carousel/box-carousel.tsx` | `fancy-box-carousel` |
| Sticky Footer | No component: a documented recipe of a sticky footer under a higher-z-index main block | `fancy:src/content/docs/components/blocks/sticky-footer.mdx` | - |

`fancy:src/fancy/components/blocks/simple-carousel.tsx` is an unreferenced near-copy of `simple-marquee.tsx` (only the scroll container handling differs).

Hooks in `fancy:src/hooks/`: `use-mouse-position-ref` (pointer in a ref, no re-render), `use-mouse-position` (state), `use-dimensions` and `use-debounced-dimensions` (250 ms), `use-elastic-line-events`, `use-screen-size`, `use-detect-browser` (user-agent sniffing), `use-mounted`. `use-line-breakdown`, `use-line-count` and `use-mouse-vector` are not imported by any component or demo in this checkout.

## Dependencies (from imports and `fancy:package.json`)

| Package | Used by |
|---|---|
| `motion` (`^12.23.24`), imported from `motion/react` | nearly every effect component |
| `lodash` (debounce) | letter-swap ping-pong, random letter swap, variable-font hover by letter, gravity components |
| `matter-js`, `poly-decomp`, `svg-path-commander`, `@types/matter-js` | gravity and cursor-attractor components, `fancy:src/utils/svg-path-to-vertices.ts` |
| `uuid` | `fancy:src/fancy/components/background/pixel-trail.tsx` |
| `clsx` and `tailwind-merge` | the `cn` helper imported by most components |
| `lenis` | demos only (`fancy:src/fancy/examples/text/scroll-and-swap-text-demo.tsx`), not the components |

The docs site itself runs on React `^19.2.1`, Next.js `^16.0.7` and Tailwind `^4.1.0`. `fancy:CONTRIBUTING.md` still says React 19 is unsupported; test your React version.

## Performance observations

- Components built on `useAnimationFrame` keep a per-frame loop alive for as long as they are mounted, including when the effect is idle: Float, Screensaver, Parallax Floating, Simple Marquee, Marquee Along SVG Path, Elastic Line and the three cursor-driven text components.
- The proximity text components call `getBoundingClientRect()` on the container and on every letter on each frame (`fancy:src/fancy/components/text/text-cursor-proximity.tsx`). The docs advise limiting the text length (`fancy:src/content/docs/components/text/text-cursor-proximity.mdx`).
- `fancy:src/fancy/components/physics/gravity.tsx` runs a Matter `Runner`, a Matter canvas renderer (transparent unless `debug`) and its own `requestAnimationFrame` loop that writes a `transform` per body each frame. It cancels the frame and stops the runner on teardown. SVG bodies need an expensive path-to-vertex step (docs note this).
- Pixel Trail renders one `motion.div` per grid cell (container width and height divided by `pixelSize`); the docs warn about large grids (`fancy:src/content/docs/components/background/pixel-trail.mdx`).
- Image Trail queries its pooled items once and mutates inline styles on each pointer event; docs advise against very large images or videos.
- Circling Elements and Animated Gradient use CSS keyframes rather than JavaScript loops. The gradient blurs full-bleed SVG shapes (`blur-2xl` to `blur-[100px]`), which can be paint-heavy; cost was not measured here.
- Cleanup is mostly in place: window listeners are removed in effect cleanups (CSS Box, Box Carousel, Marquee Along SVG Path, the underline components and the pointer, dimension and screen-size hooks), and intervals and timeouts are cleared (Text Rotate, Scramble Hover and In, Typewriter, Box Carousel autoplay). The `useAnimationFrame` loops are managed by the Motion hook. The gap is the Gravity pair, described under Pitfalls.
- `fancy:ACCEPTANCE_CRITERIA.md` asks contributors to prefer MotionValues and `useAnimationFrame` and to test with react-scan.

## Accessibility observations

- Reduced motion: only `fancy:src/fancy/components/carousel/box-carousel.tsx` calls `useReducedMotion`. It sets the transition duration to 0; its autoplay effect has no such check, and its docs say drag keeps working. No other component checks `prefers-reduced-motion`; the only other matches are in the docs-search CSS of the website.
- Text effects mostly render the full string in an `sr-only` span and hide the per-letter copies with `aria-hidden` (letter swap, random letter swap, vertical cut reveal, text rotate, scramble in, breathing text, variable-font hover, proximity text). Exceptions seen in code:
  - `fancy:src/fancy/components/text/letter-3d-swap.tsx` adds an `sr-only` copy but does not hide the visual characters, so text may be announced twice.
  - `fancy:src/fancy/components/text/scramble-hover.tsx` puts the changing display text (not the final text) in its `sr-only` span.
  - `fancy:src/fancy/components/text/typewriter.tsx` has no screen-reader handling; the DOM text grows character by character.
- Hover-only triggers (letter swap, scramble hover, random letter swap) have no focus handlers, so keyboard users never see the effect; the text itself stays readable.
- Marquees mark repeated copies `aria-hidden` but offer no pause control and no reduced-motion branch. Text Rotate with `auto` (default) replaces the visible text every 2 seconds.
- Box Carousel has keyboard arrows, `aria-label`, `aria-live` and a visually hidden "Showing item x of y" line. Against that, its focusable root removes the focus outline (`focus:outline-0`) and `aria-describedby` points to an id (`carousel-instructions`) that exists nowhere in the repository.

## Reduced-motion alternatives (catalog guidance)

Use `useReducedMotion()` from `motion/react` (or the CSS media query) in your own wrapper and switch as follows. Props named here exist in the source.

| Pattern | Alternative |
|---|---|
| `fancy-letter-swap-text`, `fancy-cursor-proximity-text`, `fancy-stacking-cards`, `fancy-matter-gravity` | Follow the linked recipe; each defines a static or reduced variant |
| `fancy-vertical-cut-reveal` | Pass `transition={{ duration: 0 }}` and `staggerDuration={0}` so text appears in place, or render plain text |
| `fancy-text-rotate` | Set `auto={false}` and show the first string, or list all strings statically; keep a pause control if you keep auto mode |
| `fancy-scramble-text` | Render the final text as plain text; do not mount the component (Scramble In starts with empty text) |
| `fancy-variable-font-text` | Render static text at `fromFontVariationSettings`; never mount Breathing Text (it loops forever) |
| `fancy-text-highlighter` | Pass `transition={{ duration: 0 }}` so the highlight appears without animating |
| `fancy-image-trail`, `fancy-pixel-trail` | Do not mount them; show static images or no decoration |
| `fancy-simple-marquee` | Render the items as a static wrapped list instead of the marquee |
| `fancy-box-carousel` | Built-in zero-duration transitions; also set `autoPlay={false}` |
| `fancy-animated-gradient-svg` | Remove the inline `animation` style in your copy when reduced motion is set, or override it with `animation: none !important` inside a `prefers-reduced-motion` media query |
| `fancy-svg-filters` | Not needed for the filters themselves, which are static; apply the rule to whatever content animates under them |

## Pitfalls

Items marked "observed" come from reading the code; nothing was run.

- Install CSS: Circling Elements and Animated Gradient need keyframes in your global CSS (their `.json` files and docs list them). The changelog says the CLI does not merge CSS variables when layers are used, so add them by hand (`fancy:src/content/docs/changelog.mdx`).
- `use client`: seven component files have no `"use client"` directive. The five that use hooks (`text-along-path.tsx`, `simple-marquee.tsx`, `marquee-along-svg-path.tsx`, `element-along-svg-path.tsx` and the unreferenced `simple-carousel.tsx`) need a client boundary in the Next.js App Router. The two filter components are plain markup.
- Variable-font components need a font that has the axes you name. Heavier weights are wider: Breathing Text reserves the full-weight width with a hidden pseudo-element, while the docs of the two cursor-driven variants tell you to leave room yourself.
- Gooey and Pixelate filters: the docs say Safari support is limited or missing; plan a fallback (`fancy:src/content/docs/components/filter/gooey-svg-filter.mdx`).
- Hooks inside loops (observed): `text-cursor-proximity.tsx` creates motion values and transforms while mapping letters; `marquee-along-svg-path.tsx` calls hooks inside `items.map`. Changing text length, `repeat` or the number of children at runtime can break the Rules of Hooks. `useInView` is called conditionally on `triggerType` in `text-highlighter.tsx` and `media-between-text.tsx`; keep that prop constant.
- `motion.create(as)` is called during render without memoising in `media-between-text.tsx` and `variable-font-and-cursor.tsx`, which can remount the element on each render.
- `fancy:src/fancy/components/physics/gravity.tsx`, when `grabCursor` is true (the default), adds anonymous `mousedown` and `mouseup` listeners and a Matter `beforeUpdate` handler in its init function and does not remove them in teardown; with `resetOnResize` (default true) init runs again after each resize, so they can accumulate. It also calls `require("poly-decomp")` inside the component.
- `fancy:src/fancy/components/background/animated-gradient-with-svg.tsx` uses `Math.random()` during render for positions and sizes, so server and client markup can differ.
- Image Trail repeats its children (`repeatChildren`, default 3) and relies on the class `.image-trail-item`; ids or refs inside children are duplicated.
- Pixel Trail cells have no default colour: pass `pixelClassName` with a background, or nothing is visible. Its usage paragraph mentions a `pixelColor` prop that the component does not have (`fancy:src/content/docs/components/background/pixel-trail.mdx`).
- The debounced handlers in the letter-swap ping-pong, random letter swap and variable-font hover-by-letter components are re-created on every render.
- Demo files use project-only Tailwind tokens (`bg-primary-red`, `font-calendas`, defined in `fancy:src/app/globals.css`). The registry script swaps colour names for hex values; copying demos by hand does not.

## Licence and reuse

- Code: MIT, "Copyright (c) 2024 Daniel Petho" (`fancy:LICENSE`); the catalog marks it `redistributable_with_notice`. Keep the copyright and permission notice with any copied or adapted code, and keep per-file author comments.
- Not covered by that finding: demo photographs (credited to individual photographers in `fancy:src/utils/demo-images.ts`), remote artwork referenced by the docs, and the fonts in `fancy:public/fonts/`. Their terms were not verified; do not copy them.
- Several components credit an inspiration (for example Simple Marquee cites a Motion example; Circling Elements cites Bakken & Bæck). `fancy:ACCEPTANCE_CRITERIA.md` says components may be removed if an original creator makes a valid claim, so keep attribution when you adapt them.
- The project docs say the library is free for personal and commercial use (`fancy:src/content/docs/introduction.mdx`).

## When not to use it

- Body copy, forms and anything that must be read quickly: per-letter spans break kerning, ligatures and selection.
- Safari-critical sites, for the SVG filter pair.
- Pages that must meet strict motion or auto-update rules without extra work: most components ship without a reduced-motion branch or pause control.

## Related

- Recipes written from these components: `knowledge/implementation-recipes/fancy-letter-swap-text.md`, `knowledge/implementation-recipes/fancy-cursor-proximity-text.md`, `knowledge/implementation-recipes/fancy-stacking-cards-scroll.md`, `knowledge/implementation-recipes/fancy-matter-gravity-pile.md`.
- Pattern records: `catalog/patterns.d/ui-fancy-skiper.yaml`.
- Another unofficial UI collection with no licence, for ideas only: `knowledge/components/skiper-ui.md`.
