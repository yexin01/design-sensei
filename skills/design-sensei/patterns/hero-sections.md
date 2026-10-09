# Hero sections playbook

Pick, build and verify the first screen of a landing page: promise, proof, one background tier and optional headline motion, with fallbacks.

In this file `design-sensei` means `${CLAUDE_SKILL_DIR}/scripts/design-sensei`.

## When to use / when not

- Use for a landing, product, portfolio or campaign first screen. Read [art direction](../references/art-direction.md) first so the hero follows a written direction.
- Not for app dashboards (use [navigation](navigation.md) and [cards and grids](cards-and-grids.md)) or long-form article openers (see [[style-editorial]]).
- The catalog has one `hero` pattern. Most heroes are a composition of a style, a background tier and a headline treatment from the rows below.

## Pick the approach

| Situation | Pick | Reuse class | Cost and notes |
| --- | --- | --- | --- |
| Software with a real interface | [[style-product-led-saas]] | copy_with_attribution | Promise, proof, real screenshot. No background effect needed. |
| Calm glass over a slow gradient, no dependencies | The original example [glass-hero](../../../examples/glass-hero/index.html) plus [[liquid-glass-css-fallback]] | original / copy_with_attribution | CSS only. Scrim token, `@supports` fallback, `forced-colors`, reduced motion are already in the example. |
| Soft drifting colour blobs | [[fancy-animated-gradient-svg]] | copy_with_attribution | Blurred full-bleed SVG can be paint-heavy (not measured). Needs keyframes in global CSS. |
| Aurora stripes behind a title (React, Tailwind, framer-motion) | [[vengeance-ui-aurora-hero-backgrounds]] | copy_with_attribution | None of the four components handles reduced motion; wrap with the motion-safe recipe. Title contrast depends on the backdrop. |
| Animated gradient, dependency-free | [[shader-gradient-background]], fundamentals in [[glsl-background-fundamentals]] | license_review_required | WebGL. Recipe has CSS fallback, still frame, offscreen pause, pixel caps. Package licence unresolved: use the original recipe code. |
| Shader backdrop from a component library | [[react-bits-self-pausing-shader-backgrounds]] over [[react-bits-ogl-shader-backgrounds]] | license_review_required | Prefer the self-pausing family. Install into your app only, never redistribute. |
| Interactive 3D object | [[r3f-lazy-canvas-webgl-fallback]] | copy_with_attribution | See [3D scenes](three-dimensional-scenes.md). Poster image is the LCP element. |
| Animated logo mark | [[liquid-metal-logo]] | copy_with_attribution | GPU high. Logo needs a transparent background. |
| Headline reveal | See [typography effects](typography-effects.md) | mixed | One reveal on one headline. |
| Intro sequence of 3 to 5 elements | [[gsap-timeline-choreography]] | license_review_required | GSAP terms apply. Without GSAP use CSS transitions with the stagger rules in [[motion-principles]]. |
| Fashion, culture, luxury | [[style-high-fashion-luxury]], [[style-editorial]] | copy_with_attribution | Image quality and type carry the page; motion stays slow. |

Dials: `design_variance` 1-3 use a centred or split layout with a real visual; 8-10 allow asymmetric or type-led compositions. `motion_intensity` caps the intro timeline (heuristics from [[motion-principles]]: level 4 about 0.8 s, 5 about 1.2 s, 6 about 1.6 s, 7 about 2.0 s; levels 1-3 none). `webgl_enabled: false` or `allowed_dependencies: none` limits you to the CSS rows. `reduced_motion: static_first` means build the still hero first.

## Search commands

```bash
design-sensei search "hero background" --category hero,gradient,background-shader --max-gpu low --reduced-motion-safe
design-sensei search "<mood words>" --category design-style --limit 5
design-sensei search "headline reveal" --category typography --max-gpu none
design-sensei search "hero" --scope docs
```

The `reduced-motion alt` flag in search output means the notes define an alternative, not that the upstream code implements it. Open the pattern's note (`vengeance-ui-aurora-hero-backgrounds` shows `yes` while its source has no handling).

## Implementation steps

1. Write the one-sentence promise, the primary action, and the proof (a number, a logo set, a screenshot). Decide the LCP element: the headline text or the product image, never the animated background.
2. Build the static hero first: semantic `h1`, lede, actions, visual, then tokens (type scale, colour, one radius). Copy the structure of the [glass-hero example](../../../examples/glass-hero/index.html) when glass fits: skip link, landmarks, 44 px (2.75 rem) buttons, visible focus.
3. Choose one background tier: solid or CSS gradient, then SVG or canvas 2D, then WebGL. Go up a tier only if the design needs it and `performance_budget` allows.
4. Give every layer a fallback: a CSS gradient that matches the effect's resting state, a poster for WebGL, a solid colour where `backdrop-filter` is missing.
5. Add headline motion last, only inside `@media (prefers-reduced-motion: no-preference)` or `gsap.matchMedia()`. Hide content only when script runs, with a CSS timer failsafe ([recipe](../../../knowledge/implementation-recipes/gsap-text-reveal-and-stagger.md)).
6. For any GPU backdrop follow the [budget recipe](../../../knowledge/implementation-recipes/react-bits-heavy-background-budget.md) rules: one live canvas in view, pixel ratio cap, pause offscreen, static layer for reduced motion and no WebGL.
7. Run the anti-generic pre-flight [[taste-skill-anti-generic-ui-checklist]] and change one default decision if the hero still looks like a template.

## Accessibility and performance gates

- Text contrast 4.5:1 body, 3:1 large text, measured against the worst region of the backdrop, not the average. The [glassmorphism note](../../../knowledge/design-styles/glassmorphism.md) shows white text on a 20 percent white tint measuring 1.19:1 over pale yellow; add a scrim.
- Looping or auto-updating motion longer than 5 s needs a pause control (WCAG 2.2.2). Ambient loops: period 6 s or longer, small amplitude.
- Reduced motion: still frame of the same composition, no parallax, no auto-rotating content.
- `forced-colors: active`: give glass panels a border and `Canvas` background; do not rely on shadows.
- LCP at most 2.5 s and CLS at most 0.1: reserve the hero height, preload the LCP image or font, do not hide the `h1` until a library loads.
- Buttons and links at least 24 px, 44 px recommended; focus ring visible on every background.

## Common mistakes

- Centred headline over a violet gradient with three identical cards below (the generic tell).
- Backdrop effect mounted before the poster and text have painted; animated layer used as the LCP element.
- Glass on a flat backdrop, or blur above about 40 px, or animating `backdrop-filter`.
- Aurora title drawn with blend modes with no contrast check; `showSwitch` on `AuroraHero` is declared but unused.
- Copying a React Bits or GSAP file into a template or published package. Check the licence gate: `license_review_required` means depend on the package under its terms, never bundle or republish.
- Two animation systems on the hero (CSS keyframes plus GSAP plus Motion).

## Where to read more

- Notes: [Vengeance UI](../../../knowledge/components/vengeance-ui.md), [React Bits catalog](../../../knowledge/components/react-bits-catalog.md), [aurora and gradient mesh](../../../knowledge/design-styles/aurora-gradient-mesh.md), [product-led SaaS](../../../knowledge/design-styles/product-led-saas.md), [ShaderGradient](../../../knowledge/shaders/shadergradient.md).
- Recipes: [motion-safe wrapper](../../../knowledge/implementation-recipes/vengeance-ui-motion-safe-wrapper.md), [animated shader gradient](../../../knowledge/implementation-recipes/animated-shader-gradient-background.md), [glass with CSS baseline](../../../knowledge/implementation-recipes/liquid-glass-ui-with-css-fallback.md), [gooey text hero](../../../knowledge/implementation-recipes/vengeance-ui-gooey-text-hero-nextjs.md).
- Related playbooks: [typography effects](typography-effects.md), [microinteractions](microinteractions.md), [navigation](navigation.md), [liquid glass](liquid-glass.md), [background shaders](background-shaders.md), [3D scenes](three-dimensional-scenes.md).
- References: [art direction](../references/art-direction.md), [accessibility](../references/accessibility.md), [performance](../references/performance.md), [source usage and licences](../references/source-usage.md).
