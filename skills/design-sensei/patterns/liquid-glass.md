# Liquid glass and glassmorphism playbook

Build glass-style surfaces (cards, nav pills, buttons, hero panels) that stay readable everywhere: plain CSS first, refraction only as an optional showpiece.

## When to use / when not

- Use for overlays, nav, media controls, hero cards and widgets over a rich backdrop (gradient, mesh, photo) where something worth blurring sits behind the panel.
- Do not use for text-heavy pages, data tables, long forms, flat or white backdrops (nothing to blur), content that moves behind the glass, or on every component at once. Two or three glass layers at most.
- "Liquid glass" claimed for plain blur is the common generic tell. Plain CSS blurs and tints but cannot refract; say which one you built.
- Dials: `motion_intensity` <= 3 or `visual_density` >= 8: CSS glass on one or two surfaces, or skip. `webgl_enabled: false` or `allowed_dependencies` none/existing: CSS only. `design_variance` >= 8 may justify one WebGL showpiece. `reduced_motion: static_first`: glass has no required motion; remove hover scale and parallax under `reduce`.

## Pick the approach

| Situation | Pattern | Reuse class | Notes |
| --- | --- | --- | --- |
| Default for every glass surface: card, nav pill, toolbar, button | [[liquid-glass-css-fallback]] | copy_with_attribution (MIT; recipe code is original) | Blur + saturate, tint, scrim, lit rim, `@supports` solid fallback, forced-colors, increased-contrast. Ship this. |
| Style direction and what to avoid | [[style-glassmorphism]] | license_review_required (guidance; mixed sources) | Alpha, blur and scrim token ranges; mistakes list. |
| One showpiece panel with real refraction, desktop, static page | [[liquid-glass-container]] | copy_with_attribution (MIT) | WebGL canvas over a one-time html2canvas snapshot; one context per element; no destroy method. Keep the CSS surface as the fallback. |
| Glass button with WebGL | [[liquid-glass-button]] | copy_with_attribution (MIT) | `div` with no keyboard support or focus style: wrap or replace with a real `button`. |
| SVG displacement or shader-rim glass in React | [[react-bits-glass-surfaces]] | license_review_required (MIT plus Commons Clause) | GlassSurface has feature detection and fallbacks; FluidGlass needs 3D assets. Dependency only, never republish. |
| Floating dock or expanding glass navigation | [[vengeance-ui-floating-dock-navigation]] | copy_with_attribution (MIT) | See [navigation](navigation.md). |
| Aurora or gradient backdrop for the glass | [[style-aurora-gradient-mesh]], [[shader-gradient-background]] | license_review_required | See [background shaders](background-shaders.md). |

Defaults: always CSS (`liquid-glass-css-fallback`). Add `liquid-glass-container` only when the brief needs refraction, the page is static, and one or two instances suffice.

## Search commands

```bash
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "glass" --category liquid-glass
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "frosted glass backdrop blur" --scope all --limit 5
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "glass" --no-webgl --reduced-motion-safe
${CLAUDE_SKILL_DIR}/scripts/design-sensei sources show liquid-glass-js
```

## Original example to start from

[`examples/glass-hero/index.html`](../../../examples/glass-hero/index.html) with [`styles.css`](../../../examples/glass-hero/styles.css) is a project-authored hero: CSS-only frosted glass over a slow transform-only gradient, no JavaScript or dependencies. It demonstrates: a scrim variable independent of the backdrop, `@supports not` swap to an opaque surface, `forced-colors` handling, `prefers-reduced-motion` that stops the drift and hover motion, a skip link, visible focus ring, 44 px (2.75rem) button height and semantic landmarks. Not covered by the example, add in real projects: `prefers-contrast: more` and `prefers-reduced-transparency` overrides (see the recipe's baseline CSS). Original code, free to adapt.

## Implementation steps

1. Confirm the backdrop is worth blurring; if flat, add a gradient or image first. Keep the busiest region away from text lines.
2. Define tokens: radius, tint alpha (heuristic 8-25% white on dark), blur (heuristic 12-32 px, avoid above about 40 px), scrim (black 35-55%), solid fallback colour, 1 px edge (white 15-30%). Follow [glass recipe](../../../knowledge/implementation-recipes/liquid-glass-ui-with-css-fallback.md) step 2 for ordering: safe default first, `@supports ((-webkit-backdrop-filter: blur(1px)) or (backdrop-filter: blur(1px)))` enhancement, user-preference overrides last.
3. Use real elements: `button`, `a` inside `nav`. Focus ring opaque, outside the blur.
4. Measure contrast on the worst backdrop region, light and dark themes. The recipe measured white text over a bright orange shape: tint and blur only 2.1:1 worst case, scrim 0.35 gives 3.7:1, scrim 0.5 gives 4.9:1, solid 14.4:1. Raise the scrim or use the solid style for text-heavy panels; do not trust blur alone.
5. Overrides: `prefers-reduced-transparency: reduce` and `prefers-contrast: more` switch to the solid style; `forced-colors: active` uses `Canvas`/`CanvasText` with a visible border. Treat reduced-transparency as an extra (limited support), not the only safeguard.
6. Optional WebGL layer ([recipe step 4-5](../../../knowledge/implementation-recipes/liquid-glass-ui-with-css-fallback.md)): decide at creation time (no destroy method, the snapshot would capture the CSS surface otherwise); capability check (fine pointer, no reduced-transparency, no increased contrast, no data-saver, html2canvas present); wait for `document.fonts.ready` and `load`; re-snapshot after resize or content change; add `isolation: isolate` to the container; self-host html2canvas (separate licence, not reviewed). Details and pitfalls: [liquid glass note](../../../knowledge/shaders/liquid-glass.md).
7. If copying liquid-glass-js files: keep `LICENSE` and credit "Liquid Glass JS by dashersw", and add to third-party notices.

## Accessibility and performance gates

- [ ] Body text >= 4.5:1, large text and UI boundaries >= 3:1, measured over the worst backdrop region.
- [ ] `@supports` forced false: solid style appears and stays readable.
- [ ] Forced colors and increased contrast emulated: no blur, visible borders.
- [ ] Tab through: visible focus, native button behaviour, correct accessible names; targets >= 24x24 CSS px, 44 recommended.
- [ ] Reduced motion: no hover scaling, parallax or drifting backdrop.
- [ ] Never animate `backdrop-filter` values; no blur on large scrolling areas; check scrolling frame rate on a mid-range phone and reduce area or `--glass-blur` if frames drop.
- [ ] WebGL layer: at most one or two contexts (each costs roughly 770 texture reads per fragment per the note, a reading not a profile); WebGL off and html2canvas blocked both leave the CSS surface working; no console errors.
- [ ] Refractive areas carry no text.

## Common mistakes

- `bg-white/10 backdrop-blur-xl border-white/20` on every card over a near-black page with two purple blobs.
- Glass nav, glass cards and glass buttons together; glass on glass on glass.
- Light-grey text on bright regions; missing border; no solid fallback; forgetting the `-webkit-` prefix.
- Using liquid-glass-js buttons as controls (div, no keyboard, no focus) or expecting live refraction (the snapshot is static, taken once).
- Mapping horizontal scroll or tall pages onto the snapshot; opaque ancestor hiding the `z-index: -1` canvas.
- Skipping the licence step for react-bits (custom terms) or html2canvas.

## Where to read more

- [Liquid glass note](../../../knowledge/shaders/liquid-glass.md), [glassmorphism style](../../../knowledge/design-styles/glassmorphism.md), [liquid materials style](../../../knowledge/design-styles/liquid-materials.md), [GLSL fundamentals](../../../knowledge/shaders/glsl-ui-fundamentals.md), [React Bits licence guide](../../../knowledge/implementation-recipes/react-bits-license-safe-usage.md)
- [accessibility](../references/accessibility.md), [performance](../references/performance.md), [source usage](../references/source-usage.md); related playbooks [background shaders](background-shaders.md), [navigation](navigation.md), [cards and grids](cards-and-grids.md)
