# Background shaders and animated gradients playbook

Pick the cheapest background technique that delivers the art direction (static CSS, CSS/SVG motion, canvas, WebGL shader), and ship it with a fallback, a reduced-motion path and a pause.

## When to use / when not

- Use for hero or section backdrops, ambient gradients, aurora and mesh looks, an animated brand logo surface, generative texture.
- Do not use behind dense reading text, behind data visualisation, on pages that already run another live canvas, or when the audience is mostly low-power devices. In those cases use a CSS gradient, a pre-rendered image, or a short muted video with a poster.
- Aurora and mesh gradients are the most overused effect on generic sites. Start from the brand hue, not the default indigo-violet-pink sweep; see [aurora note](../../../knowledge/design-styles/aurora-gradient-mesh.md).
- Dials: `motion_intensity` <= 3 use static CSS only; 4-5 at most one subtle ambient loop (CSS/SVG or slow shader); 6+ one shader allowed. `webgl_enabled: false` means tiers 1-2 only. `allowed_dependencies: none` means route A (own shader) or CSS; no `ogl`, `three` or ShaderGradient. `reduced_motion: static_first`: the fallback is the design, the shader enhances it.

## Pick the approach (cheapest tier that works)

| Need | Pattern | Reuse class | Cost / notes |
| --- | --- | --- | --- |
| Soft gradient, no motion | CSS `radial-gradient` layers, OKLCH interpolation, optional 2-6% grain ([[style-grain-and-texture]], [[style-aurora-gradient-mesh]]) | license_review_required (style guidance only; write the CSS yourself) | Zero JS. Default choice. |
| Drifting blurred shapes, no WebGL | [[fancy-animated-gradient-svg]] | copy_with_attribution (MIT) | CSS keyframes on blurred SVG circles; seed positions for SSR; blur once, animate position/opacity. |
| Stripe aurora hero, pure CSS | [[vengeance-ui-aurora-hero-backgrounds]] | copy_with_attribution | Repeating gradients; has a recipe. |
| Dots, glitch letters or tile wall without a shader | [[react-bits-canvas-grid-backgrounds]] | license_review_required | Cheaper than WebGL; custom terms. |
| Ambient 2-4 colour gradient, no dependency | [[shader-gradient-background]] (route A of the recipe) | license_review_required in the catalog; the recipe's route A is original code | Full-screen fragment shader, CSS gradient fallback, still frame, pause, DPR cap. |
| Own shader from scratch | [[glsl-background-fundamentals]] | license_review_required (original guide) | Oversized triangle, uniforms, DPR cap, context loss. |
| 3D-noise displaced gradient with presets | [[shader-gradient-react]] | license_review_required (licence unresolved: no LICENSE file) | Use the npm package as a dependency, never copy shaders. Heavier (three + R3F). Vue: [[shader-gradient-vue]]. Settings via customizer URL: [[shader-gradient-url-config]]. |
| Ready-made WebGL background in React | [[react-bits-self-pausing-shader-backgrounds]] first, then [[react-bits-ogl-shader-backgrounds]], [[react-bits-webgpu-backgrounds]], [[react-bits-three-r3f-backgrounds]] | license_review_required (MIT plus Commons Clause) | Prefer components that pause offscreen and honour reduced motion; wrap the rest. |
| Fallback, reduced motion and teardown for any WebGL effect | [[webgl-effect-fallback-and-reduced-motion]] | license_review_required (original guide) | Apply to everything above that uses a canvas. |
| Animated logo surface | [[liquid-metal-logo]] | copy_with_attribution (MIT) | One logo only; transparent PNG/SVG; `img` stays as the fallback. Logo prep: [[image-background-removal-for-logos]]. |
| Chrome-border button | [[vengeance-ui-liquid-metal-button]] | copy_with_attribution | Live WebGL per button; do not repeat. |

Rule of thumb: tier 1 static CSS, tier 2 CSS/SVG motion, tier 3 WebGL. Move up a tier only when the lower one cannot deliver the look.

## Search commands

```bash
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "gradient background" --category gradient
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "shader background" --category background-shader --max-gpu medium --reduced-motion-safe
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "aurora" --scope all --limit 5
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "background" --no-webgl --category animation
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "uniform u_time" --content   # grep downloaded sources
```

## Implementation steps

1. Fix the palette from the project tokens before choosing a technique. Choose analogous colours of similar lightness; interpolate in OKLCH to avoid grey midpoints.
2. Layer order: CSS gradient on the container (first paint and fallback, same colours as the effect) -> optional canvas with `position:absolute; inset:0; z-index:-1; pointer-events:none; aria-hidden="true"` -> content in a simple high-contrast layer. The static layer is the LCP candidate; load the effect after it.
3. Own shader (route A in the [shader gradient recipe](../../../knowledge/implementation-recipes/animated-shader-gradient-background.md)): one oversized triangle, uniforms for resolution, time, palette; cap DPR at 2 times a render scale of 0.5-1 (soft gradients lose nothing at half resolution); clamp frame delta; 30 fps for ambient; check `COMPILE_STATUS`/`LINK_STATUS`; request the context with `failIfMajorPerformanceCaveat: true` and `powerPreference: 'low-power'`; show the canvas only after the first good frame.
4. Pause with `IntersectionObserver` and `visibilitychange`; handle `webglcontextlost` (call `preventDefault`) and `webglcontextrestored`; on teardown cancel the frame, delete GL objects, then `WEBGL_lose_context`. Create the context in an effect, never during server render (Next.js: client component or dynamic import with SSR off).
5. Reduced motion: listen to `matchMedia('(prefers-reduced-motion: reduce)')`; render one still frame at a time that looks good (not necessarily `t = 0`) and do not start the loop. If movement lasts over 5 s beside other content, add a visible pause control (WCAG 2.2.2).
6. Third-party component: wrap it in the effect-mode slot from the [heavy background budget recipe](../../../knowledge/implementation-recipes/react-bits-heavy-background-budget.md) (static on the server, static for reduced motion, data-saver, narrow screens or no WebGL; mount only near the viewport; unmount when far). Install per [variant chooser](../../../knowledge/implementation-recipes/react-bits-choose-variant-and-install.md); read the [licence guide](../../../knowledge/implementation-recipes/react-bits-license-safe-usage.md) first.
7. Add scrim or a text panel: dark 35-55% or a solid panel where the field varies. Add faint grain to prevent banding on large smooth fields.

## Accessibility and performance gates

- [ ] Text contrast (4.5:1 body, 3:1 large) measured on the lightest and most saturated frame, not an average.
- [ ] Canvas `aria-hidden`; no information carried only by the shader.
- [ ] WebGL disabled: CSS fallback visible, no console errors, no `alert`.
- [ ] Reduced motion: still frame or static gradient; pointer influence off; live toggle works.
- [ ] Flicker well under 3 flashes per second (WCAG 2.3.1); slow low-contrast drift is the safe default, large fast movement is a vestibular trigger.
- [ ] One live GPU canvas in view, two mounted at most. Pixel count capped (heuristic: one to two million pixels for full-screen ambient). Frame time measured on a mid-range phone.
- [ ] Pauses offscreen and in hidden tabs; context released on teardown; context loss recovered.
- [ ] LCP <= 2.5 s and CLS <= 0.1 with the effect enabled; JS within `performance_budget` (heavy libraries load lazily).
- [ ] Licence gate: react-bits, shadergradient, GSAP terms read; notices kept for MIT sources (fancy, vengeance-ui, liquid-logo).

## Common mistakes

- Several blurred multi-layer animated gradients on mobile; animating `filter: blur()` on a large layer.
- Text placed over the busiest region; thin type over colour transitions.
- Treating a third-party shader as safe: many React Bits backgrounds neither pause offscreen nor honour reduced motion (see the budget recipe for which do). Components avoided or needing stripping are listed there.
- Large time values in `sin`/hash at `mediump` (accumulate and wrap time); assigning `canvas.width` every frame (clears the buffer).
- Full-screen canvas intercepting wheel or touch: orbit controls on the canvas take over scroll; set pointer events to none.
- Copying ShaderGradient or React Bits code into the repo instead of using the dependency per its terms.
- Same indigo-to-pink aurora as every other site.

## Where to read more

- [GLSL UI fundamentals](../../../knowledge/shaders/glsl-ui-fundamentals.md), [ShaderGradient note](../../../knowledge/shaders/shadergradient.md), [liquid metal logo note](../../../knowledge/shaders/liquid-metal-logo.md), [liquid metal logo recipe](../../../knowledge/implementation-recipes/liquid-metal-logo-integration.md)
- [React Bits note](../../../knowledge/components/react-bits.md), [React Bits catalog](../../../knowledge/components/react-bits-catalog.md)
- [shaders-and-webgl reference](../references/shaders-and-webgl.md), [performance](../references/performance.md), [accessibility](../references/accessibility.md); related playbooks [liquid glass](liquid-glass.md), [3D scenes](three-dimensional-scenes.md), [hero sections](hero-sections.md)
