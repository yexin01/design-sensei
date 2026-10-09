# Product showcases playbook

Choose how to present a product or a set of images: real interface, image carousel with depth, scroll walkthrough, or a 3D viewer, and build it with a static fallback.

## When to use / when not

- Use when a product, work sample or set of images is the proof on the page: product pages, launches, portfolios, feature tours.
- Prefer the simplest form that shows the product honestly: a real screenshot or photo beats a clever carousel. Use 3D only when shape, finish or scale is part of the decision (hardware, furniture, footwear, vehicles). Do not build a fake dashboard from `div` rectangles or invent logos and testimonials.
- Software with a visible interface: [[style-product-led-saas]] (real interface as the hero, proof, restrained polish).
- Dials: `motion_intensity` <= 3: static images, tabs or a scroll-snap row, no autoplay. 4-6: one featured motion element, muted loops that pause offscreen. 7+: 3D or pinned walkthrough allowed with fallbacks. `webgl_enabled: false`: DOM/CSS options only. `visual_density` high: grids and tabs over full-screen carousels.

## Pick the approach

| Situation | Pattern | Reuse class | Notes |
| --- | --- | --- | --- |
| Software product page, real UI as hero | [[style-product-led-saas]] | copy_with_attribution | Style guidance; real screenshots with alt text; hairline structure. |
| Feature set as modular tiles | [[astryx-card-and-grid-collections]] (React 19 + design system), [[vengeance-ui-bento-grids]], [[react-bits-bento-and-card-grids]] | copy_with_attribution; copy_with_attribution; license_review_required | See [cards and grids](cards-and-grids.md). |
| Step-by-step product walkthrough on scroll (3-6 steps, desktop) | [[gsap-scrolltrigger-pin-scrub]] | license_review_required (GSAP terms) | Stacked fallback on narrow/touch/reduced motion. See [scroll storytelling](scroll-storytelling.md). |
| Case studies or features piling up as the page scrolls | [[fancy-stacking-cards]] | copy_with_attribution | Sticky layering; reduced motion removes the scaling. |
| Auto-cycling feature screenshots | [[skiper-ui-stepped-feature-card]] | reimplement_only | Idea only, no licence: design and write your own; add pause and reduced-motion handling. |
| Cube-style image/video carousel | [[fancy-box-carousel]] | copy_with_attribution | CSS 3D; arrow keys and live region; set `autoPlay` off for reduced motion yourself; restore the focus outline; videos are the cost. Reference only. |
| Perspective / diagonal carousel with ARIA | [[vengeance-ui-3d-image-carousels]] | copy_with_attribution | Region + arrow keys + `aria-current` on perspective and diagonal variants; ring gallery is pointer-only and defaults to many `img` elements. Wrap with the motion-safe recipe. |
| Coverflow carousel | [[skiper-ui-coverflow-card-carousel]] | reimplement_only | Idea only, rights unresolved; write your own, or use Swiper's own docs for the effect. No autoplay under reduced motion; pause control otherwise. |
| Image gallery with drag, sphere or dome | [[react-bits-3d-image-galleries]] | license_review_required | Defaults use remote placeholder images; supply your own sized assets; most do not check reduced motion: use the budget recipe and a plain grid as fallback. |
| 3D product viewer (GLB) | [[r3f-product-showcase-scene]] | copy_with_attribution | Draggable turntable, studio lighting, on-demand render, pause button, reduced-motion state. Pair with [[r3f-lazy-canvas-webgl-fallback]] and [[r3f-gltf-loading-suspense]]. |
| Packaged 3D (books, particles from an image) | [[vengeance-ui-three-js-scenes]] | copy_with_attribution | GPU cost high; see [3D scenes](three-dimensional-scenes.md). |
| Product only exists as a photo, 3D wanted | [[image-to-3d-img2threejs-pipeline]] | copy_with_attribution | Approximate stylized rebuild; see [image to 3D](image-to-3d.md). |

Defaults: real imagery + a grid/bento or scroll-snap row first; a stacked-card or pinned walkthrough as the motion layer; 3D only when the brief justifies it.

## Search commands

```bash
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "product showcase" --category product-showcase
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "carousel" --category product-showcase --reduced-motion-safe --max-gpu low
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "product viewer" --framework r3f
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "gallery" --no-webgl --scope all --limit 5
```

## Implementation steps

1. Gather real assets first: screenshots at native fidelity, photographs, or a licensed GLB; write alt text that says what the interface or object shows. Reserve width/height or aspect ratio to avoid CLS.
2. Build the static version: semantic list of items, each with image, heading and text; a scroll-snap row or grid is the fallback for every carousel.
3. Add the chosen enhancement. For a carousel: labelled region (`aria-roledescription="carousel"` pattern or plain region with a label), previous/next buttons that are real `button` elements, arrow keys, `aria-current` on the active item, visible focus ring, no autoplay by default; if autoplay exists, a visible pause control and none under `prefers-reduced-motion`.
4. 3D viewer: follow [R3F product showcase recipe](../../../knowledge/implementation-recipes/r3f-product-showcase-scene.md) inside the lazy shell from the [canvas recipe](../../../knowledge/implementation-recipes/r3f-canvas-in-a-page-with-fallback.md): fit the model on a wrapper group (never mutate the cached asset), neutral room environment plus one weak directional light, `dpr={[1, 1.5]}`, `frameloop` `always` only while spinning, wheel zoom off so page scroll stays free, pause button, label that states the interaction, product described in text as well.
5. Third-party carousels: wrap in the [motion-safe wrapper](../../../knowledge/implementation-recipes/vengeance-ui-motion-safe-wrapper.md) (reduced motion, low-power, no WebGL, offscreen unmount) or the [heavy background budget slot](../../../knowledge/implementation-recipes/react-bits-heavy-background-budget.md) for react-bits; install per the [variant chooser](../../../knowledge/implementation-recipes/react-bits-choose-variant-and-install.md) and respect the [licence guide](../../../knowledge/implementation-recipes/react-bits-license-safe-usage.md).
6. For `reimplement_only` items write original markup, styles and images; do not copy class strings, markup or images.
7. Muted demo loops longer than 5 s need a pause control (WCAG 2.2.2); start paused with a play control under reduced motion.

## Accessibility and performance gates

- [ ] Every image has meaningful alt text; 3D canvas has a label and the facts are also in DOM text.
- [ ] Keyboard: carousel controls and 3D viewer operable; no traps; focus never lost to hidden slides (inactive slides not focusable if off-screen).
- [ ] Reduced motion emulated: no autoplay, no auto-rotation, no continuous spin; manual controls still work.
- [ ] Contrast 4.5:1 text, 3:1 UI components; targets >= 24x24 CSS px (44 recommended).
- [ ] WebGL off: poster/grid shown, no console errors.
- [ ] LCP <= 2.5 s (the first product image or poster is the LCP candidate, not lazy-loaded), CLS <= 0.1, INP <= 200 ms; many-image rings lazy-load images.
- [ ] Mid-range phone test; one live canvas at most; pause offscreen.
- [ ] Licence gate: react-bits and GSAP custom terms; skiper-ui patterns are idea-only; model and image rights confirmed (example-app models in R3F are not cleared).

## Common mistakes

- Autoplaying carousels with no pause, or a pause that reduced-motion users cannot reach.
- A 150-image ring gallery without lazy loading; remote placeholder images left in.
- Hiding product facts inside the canvas only.
- Three identical feature cards with icons; invented testimonials and logos; fake dashboards built from `div`s.
- Mutating the cached GLTF scene to fit it; showing one model in two places without cloning.
- Pinned walkthrough on touch devices; zoom capturing page scroll.
- Copying `reimplement_only` source because the demo looks good.

## Where to read more

- [Product-led SaaS style](../../../knowledge/design-styles/product-led-saas.md), [R3F note](../../../knowledge/components/react-three-fiber.md), [Vengeance UI note](../../../knowledge/components/vengeance-ui.md), [Fancy note](../../../knowledge/components/fancy.md), [React Bits catalog](../../../knowledge/components/react-bits-catalog.md), [Skiper UI note](../../../knowledge/components/skiper-ui.md)
- [Stacking cards recipe](../../../knowledge/implementation-recipes/fancy-stacking-cards-scroll.md), [pinned section recipe](../../../knowledge/implementation-recipes/gsap-pinned-section-sequence.md)
- [component-selection reference](../references/component-selection.md), [accessibility](../references/accessibility.md), [source usage](../references/source-usage.md); related playbooks [cards and grids](cards-and-grids.md), [3D scenes](three-dimensional-scenes.md), [scroll storytelling](scroll-storytelling.md)
