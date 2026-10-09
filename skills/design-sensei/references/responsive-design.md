# Responsive design

How to make a layout, type scale, imagery and heavy effects work from a 375 px phone to a 1920 px desktop, and which widths to inspect.

Load this when choosing a layout approach, writing CSS for a new section, adapting a desktop-first effect for phones, or verifying responsive behaviour. The playbook [responsive layouts](../patterns/responsive-layouts.md) holds condensed layout recipes; this file holds the rules. The platform facts here (CSS units, media features, WCAG reflow) are standard web behaviour; numbers marked "heuristic" are starting points to adjust.

## Decisions to make

| Decision | Options | Guidance |
| --- | --- | --- |
| Authoring direction | mobile-first (`min-width` queries) vs desktop-first | Default to mobile-first: the base CSS is the 375 px layout, wider rules add to it. Desktop-first only when the project already is |
| Breakpoints | fixed device list vs content-driven | Content-driven: add a breakpoint where the layout breaks, not at a device width. Name them as tokens and reuse the project's existing set |
| Component adaptation | media query vs container query | Page shell (nav, columns) uses media queries; a card or widget that appears in several containers uses `@container` |
| Type and space | fixed steps vs fluid `clamp()` | Fluid for display type and section spacing; fixed `rem` steps for body text and UI |
| Heavy effects on small devices | keep, downgrade, replace | See "Heavy effects" below; read `performance_budget` and `webgl_enabled` |
| Density | collapse, scroll, or reflow | At 375 px lower effective `visual_density`: one column, fewer simultaneous items, details behind disclosure |

How the dials change things:

| Dial | Effect on responsive work |
| --- | --- |
| `design_variance` 8-10 | Experimental grids, overlaps and offset layouts need an explicit mobile composition (usually a simple single column that keeps the idea, not the geometry). Design it, do not let it collapse by accident |
| `design_variance` 1-3 | Standard stacked/grid reflow is enough |
| `motion_intensity` above 5 | Phones get a lower budget (about two points down, heuristic, from [scroll storytelling](../../../knowledge/animations/scroll-storytelling.md)); pinned sequences and cursor effects are desktop-only |
| `visual_density` 8-10 | Needs a real mobile information design (tabs, disclosure, tables that reflow); do not shrink the desktop table |

## Mobile-first CSS rules

- Include `<meta name="viewport" content="width=device-width, initial-scale=1">` (eval RESP-001, an error) and never block zoom (A11Y-005). For notched devices add `viewport-fit=cover` and pad with `env(safe-area-inset-*)`.
- Write the single-column layout first. Use `display: grid` with `repeat(auto-fit, minmax(min(100%, 16rem), 1fr))` or flex-wrap for card grids before reaching for breakpoints; `min(100%, ...)` keeps a track from overflowing a narrow container.
- Logical properties (`margin-inline`, `padding-block`, `inset-inline`) keep layouts correct in RTL.
- Content must reflow at 320 CSS px width and at 400% zoom without two-axis scrolling (WCAG 1.4.10). Long words and URLs need `overflow-wrap: anywhere` or `hyphens`.
- Use `gap` for spacing between siblings; avoid margins that break when items wrap.
- Fixed widths and heights on text containers cause overflow at 375 px and under text zoom: use `min-height`, `max-width`, `ch` and `rem`.
- eval RESP-002 warns when no responsive technique exists in the styles at all (no `@media`, `@container`, `clamp()`, `minmax()`, `auto-fit`, viewport units or Tailwind prefixes). It cannot tell whether the layout is good.

## Fluid type and space

- Pattern: `font-size: clamp(min, preferred, max)` where `preferred` mixes `rem` and a viewport term, for example `clamp(2rem, 1.2rem + 3vw, 4.5rem)` (illustrative values). Always keep a `rem` part in the preferred value, otherwise text may not respond to browser zoom (WCAG 1.4.4).
- Heuristic: keep the largest size within roughly 2.5 times the smallest so the scale stays predictable; check the result at 320 px, 768 px and 1920 px.
- Body text: fixed `1rem` to `1.125rem`, line length about 45-75 characters (`max-width: 65ch`), line-height 1.4-1.6 (heuristic). Display lines can be tighter. Scale and pairing live in [typography](typography.md).
- Fluid spacing: derive section padding and gaps from the same `clamp()` approach, tied to the spacing scale tokens rather than ad hoc values ([layout composition](layout-composition.md)).
- Avoid 10+ fixed `px` font sizes (eval TYPO-002 info); avoid viewport-only font sizes (`font-size: 5vw`).

## Media queries or container queries

| Situation | Use |
| --- | --- |
| Page-level structure: nav collapse, sidebar, hero composition | Media query on viewport width |
| A card, stat tile or form block reused in sidebar and main areas | Container query (`container-type: inline-size`, then `@container (min-width: ...)`) |
| Input capability | `(hover: hover) and (pointer: fine)` vs `(pointer: coarse)` |
| Short landscape phones | `(max-height: ...)` or `(orientation: landscape)`; do not assume tall viewports |
| User settings | `prefers-reduced-motion`, `prefers-color-scheme`, `prefers-contrast` |

Container queries change what a component needs to know: size the component to its slot, not to the device. Astryx's layout primitives follow a related idea (an intrinsic `Grid` with minimum column width, theme width points `sm` to `2xl`); they set no automatic region swapping, so narrow-width composition remains your job ([[astryx-responsive-layout-primitives]], [Astryx](../../../knowledge/components/astryx.md)).

## Touch versus hover

- Never hide information or actions behind hover. Guard hover styling with `@media (hover: hover)`; give touch an equivalent (visible control, tap, long press with an alternative).
- Touch targets: 24 x 24 CSS px is the WCAG 2.2 minimum, 44 x 44 the recommended size. Space adjacent targets.
- Cursor-driven effects (custom cursors, proximity text, trails, magnetic buttons) are pointer-only: mount them behind `(hover: hover) and (pointer: fine)` and a reduced-motion check; see [cursor interactions](../patterns/cursor-interactions.md) and [[fancy-cursor-proximity-text]].
- Do not intercept wheel or touch input to drive custom scrolling. Lenis leaves touch native unless `syncTouch` is enabled; enable it only for a measured reason ([Lenis](../../../knowledge/animations/lenis.md)).
- Text inputs at 16px or larger avoid iOS focus zoom.
- Sticky and fixed bars eat vertical space on phones; cap their height and test with the on-screen keyboard open.

## Viewport units

- `100vh` is taller than the visible area on mobile browsers with a collapsing address bar. Use `100svh` for "must always fit" (pinned stages, full-screen heroes), `100dvh` for "track the visible area" (layouts that may reflow as bars move), `100lvh` for large-viewport backgrounds. Provide a `vh` fallback line before them. Eval RESP-003 (info) flags `100vh` with no `dvh`/`svh`/`lvh`.
- A pinned scroll stage must fit the smallest supported viewport height, so size it in `svh` ([scroll storytelling](../../../knowledge/animations/scroll-storytelling.md)).
- Avoid `vw` for full-width elements when a vertical scrollbar exists; it includes the scrollbar width and can create horizontal overflow.

## Images and media

- Give every image intrinsic `width` and `height` or an `aspect-ratio` (eval PERF-001) so nothing shifts layout.
- Use `srcset` + `sizes` (or the framework image component) for resolution switching, `<picture>` for art direction (a different crop on phones), `object-fit` for fitting.
- Lazy-load below-the-fold images; never lazy-load or animate-in the LCP image. A static hero layer should be the LCP candidate, with the effect loaded afterwards ([React Bits background budget](../../../knowledge/implementation-recipes/react-bits-heavy-background-budget.md)).
- Video backgrounds: a poster, `muted playsinline`, no autoplay for reduced motion or data-saver. Replace remote placeholder images (Unsplash, picsum) that copy-in components ship with.
- Do not reuse media that ships inside upstream repositories ([source usage](source-usage.md)).

## Heavy effects on small devices

Gate by capability, not by user-agent guesses, and always keep a static layer underneath.

| Effect | Small-screen treatment |
| --- | --- |
| WebGL/WebGPU backgrounds | Static layer below 768 px or without a fine pointer (a policy choice used in the React Bits budget recipe); one live canvas at most; cap pixel ratio (about 1.5 for full-viewport shaders, 2 otherwise) and use `Math.min(devicePixelRatio, cap)` (eval PERF-006) |
| R3F scenes | Lazy-mount near the viewport, `dpr` cap, `frameloop="demand"` when static; poster fallback ([[r3f-lazy-canvas-webgl-fallback]], [[r3f-adaptive-resolution-performance]]) |
| Pinned ScrollTrigger sequences | Only for wide screens with a fine pointer (for example `(min-width: 900px) and (pointer: fine)`); below that, stacked sections with one-shot reveals via `gsap.matchMedia()` ([[gsap-scrolltrigger-pin-scrub]]) |
| Glass/refraction | Plain CSS glass on small or low-power devices; WebGL refraction only for one hero element on capable desktops ([[liquid-glass-css-fallback]]) |
| Cursor trails, physics piles | Do not mount |
| Heavy libraries | Lazy-load; count them against `allowed_dependencies` and `performance_budget.initial_js_kb` |

Signals to combine: `matchMedia` for width, pointer and reduced motion; `navigator.connection?.saveData` (Chromium only); `navigator.hardwareConcurrency` (coarse). Test on a real mid-range phone when possible; CPU throttling in DevTools only approximates it. More in [performance](performance.md) and [shaders and WebGL](shaders-and-webgl.md).

## Widths to inspect

Take a screenshot and check the items at each width (these are inspection points, not breakpoints). Procedure and evidence format: [design QA](design-qa.md).

| Width | Look for |
| --- | --- |
| 375 | One-column flow, no horizontal scroll, tap targets, nav collapse works, hero fits the first screen, text not clipped, heavy effects replaced by static layer |
| 768 | Awkward in-between layouts (cards too wide or a lone orphan), nav switch point, two-column break, images cropped sensibly |
| 1280 | The intended desktop composition, line lengths, alignment to the grid, hover states |
| 1920 | Content max-width and centring, empty margins, oversized type, images upscaled badly, backgrounds that run out |

Also check: 320 px width and 200% zoom (reflow), a short landscape phone height, and a reduced-motion pass at 375 and 1280. Detect overflow with `document.documentElement.scrollWidth > document.documentElement.clientWidth`.

## Checklist before saying done

- [ ] Viewport meta present and zoom allowed; layout written mobile-first
- [ ] No horizontal scroll at 320, 375, 768, 1280, 1920; content reflows at 200% zoom
- [ ] Display type and section spacing fluid with a `rem` component; body text readable at every width
- [ ] Hover-only interactions have touch and keyboard equivalents; targets large enough
- [ ] `dvh`/`svh` used instead of bare `100vh` where height matters
- [ ] Images sized, responsive and not lazy at the top; no layout shift
- [ ] Heavy effects gated by capability with a static fallback; budget respected
- [ ] A deliberate mobile composition exists for any experimental desktop layout

## Common mistakes

- Designing 1280 px first and squeezing it; breakpoints copied from device lists.
- `font-size` in `vw` only, or `clamp()` with no `rem` term.
- Fixed-height hero with `100vh` that is cut off by mobile browser bars.
- Pinned scroll sequences or cursor effects shipped to touch devices.
- Hover menus with no tap path; tooltips as the only label.
- Loading a full-viewport shader on a phone and hoping the GPU copes.
- Verifying only at one desktop width.

## Related

Patterns: [[astryx-responsive-layout-primitives]], [[astryx-card-and-grid-collections]], [[gsap-match-media-reduced-motion]], [[style-bento-layouts]], [[r3f-adaptive-resolution-performance]].
Notes: [scroll storytelling](../../../knowledge/animations/scroll-storytelling.md) (mobile strategy), [React Bits heavy backgrounds](../../../knowledge/implementation-recipes/react-bits-heavy-background-budget.md), [Bento layouts](../../../knowledge/design-styles/bento-layouts.md).
References: [layout composition](layout-composition.md), [typography](typography.md), [accessibility](accessibility.md), [performance](performance.md), [design QA](design-qa.md).
