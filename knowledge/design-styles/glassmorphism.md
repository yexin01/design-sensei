---
title: "Glassmorphism"
kind: design-style
summary: "Translucent, blurred panels over rich backdrops to create depth and hierarchy, from plain CSS frosted glass to SVG-displacement and WebGL refraction. Covers contrast against the worst backdrop region, fallbacks, cost limits and three verified local implementations."
source_ids: [design-md, liquid-glass-js, react-bits, vengeance-ui]
pattern_ids: [style-glassmorphism]
updated: "2026-10-09"
---

# Glassmorphism

Glassmorphism stacks translucent, blurred panels over a colourful backdrop so that panels read as sheets of frosted glass. The effect needs something worth blurring behind the panel and a deliberate answer to the question of text contrast. Three implementation families exist: CSS frosted glass (`backdrop-filter`), glass that also bends what is behind it (SVG displacement or WebGL refraction, the "liquid glass" look), and transmission materials inside a 3D scene.

## Visual characteristics
- Panels filled with white at 8-25% alpha on dark (or a tint on light), with 12-32 px background blur and often a saturation boost.
- A 1 px light border (white at 15-30%) and sometimes an inner top-left highlight to define the edge.
- Large, soft, low-opacity shadows to separate layers.
- A vivid blurred backdrop (gradient, mesh, photo) so the glass has colour to work with.
- Rounded corners (16-28 px), floating cards, pill navigation, dock bars, media widgets.

## When it fits, when it does not
- Fits: overlays above rich imagery or gradients (navigation, media controls, widgets, modals), hero cards, weather, music and fintech dashboards.
- Poor fit: text-heavy pages, data tables, long forms, flat or white backdrops (nothing to blur, the result is a grey smudge), low-end devices, video backdrops behind text.
- Supporting influences that work: aurora-gradient-mesh, bento-layouts, futurism, liquid-materials, product-led-saas used lightly. Avoid brutalism, neumorphism, swiss-international-typographic and retro-vintage.

## Typography
- Neutral sans (Inter, Geist or a system UI face). Go one weight heavier than on solid surfaces (500 for body) and keep body at 15-16 px or larger.
- Near-white (90-95% alpha) on dark glass, near-black on light glass; avoid mid-grey text.
- A faint `text-shadow` can help over bright patches but does not replace contrast. Avoid weights below 400.

## Colour
- Backdrops of two to four analogous hues at mid to deep lightness. Pale yellow or lime patches under white text are the usual failure.
- Compute contrast against the worst backdrop region. White text on a 20% white glass tint measures 5.96:1 over deep blue #1E3A8A, 4.75:1 over purple #7E22CE, 3.59:1 over pink #DB2777 and 1.19:1 over pale yellow #FDE68A. A 50% black scrim under the text lifts the yellow case to 4.75:1.
- Define a scrim token (black at 35-55%) for text-heavy glass, and a solid fallback colour for every glass surface.

## Composition and layout
- At most two or three glass layers: a base panel and one raised element. Glass on glass on glass loses hierarchy.
- Keep the busiest part of the backdrop away from text lines; leave calmer regions beneath copy.
- Keep a consistent light direction (top-left highlight). Outer margins of 24 px or more so the backdrop stays visible.
- A two-level scheme from the local DESIGN.md example is a good starting point: standard cards at 10% white with a 20 px blur, elevated cards at 20% white with a 40 px blur.

## Interaction and motion
- Subtle: lift 2-4 px and add 5% alpha on hover over 150-250 ms. Do not animate blur radius; it is expensive.
- Small parallax between layers (10 px or less); springs for docks and morphing.
- Reduced motion: remove parallax and morphing, keep static blur. Provide an opaque variant for users who ask for reduced transparency (`prefers-reduced-transparency` has limited support, so also offer a setting).

## Accessibility cautions
- Text over moving or video backdrops changes contrast continuously; use a scrim or a static backdrop.
- In Windows forced-colors mode shadows and translucency cues disappear; give every panel a visible 1 px border and a solid system-colour background.
- Refractive effects distort what lies beneath the glass; do not put text there.
- Keep focus rings opaque and outside the blur.

## Common mistakes
- Glass over a flat backdrop, or glass on every component, so nothing stands out.
- Blur above about 40 px, many layers, or blur on large scrolling areas.
- Light grey text (`text-white/60`) on bright regions; missing border; no fallback; forgetting `-webkit-backdrop-filter` for older Safari.
- Animating `backdrop-filter` values.

## Typical mistakes of AI-generated versions
- `bg-white/10 backdrop-blur-xl border-white/20` applied to every card over a near-black page with two purple blobs.
- Glass navigation, glass cards and glass buttons together, and "liquid glass" claimed for plain blur.
- No fallback and no contrast check.

## How to build it
- Pattern: `style-glassmorphism`. A minimal CSS version with fallbacks (original code):

```css
.glass { background: rgb(255 255 255 / .12); border: 1px solid rgb(255 255 255 / .22);
  backdrop-filter: blur(20px) saturate(1.4); -webkit-backdrop-filter: blur(20px) saturate(1.4); }
@supports not (backdrop-filter: blur(1px)) { .glass { background: rgb(20 24 40 / .88); } }
@media (forced-colors: active) { .glass { background: Canvas; border-color: CanvasText; } }
```

- Token example: `design-md:examples/atmospheric-glass/DESIGN.md` is a complete DESIGN.md for a glass UI (alpha levels, blur levels, border, shadow, white text, weight bump on glass).
- Accessible controls on glass: `vengeance-ui:src/components/ui/music-player.tsx` (white 15% fill with `backdrop-blur-md`, labelled buttons, `aria-expanded`, a seek slider exposing value and text).
- SVG displacement glass, described only because react-bits is licence-restricted: `react-bits:src/content/Components/GlassSurface/GlassSurface.jsx` and `.css` build a displacement map per instance and apply it through `backdrop-filter`. It treats Safari and Firefox user agents as unsupported and then uses a blur-and-saturate fallback, with a further `@supports` fallback in the CSS.
- WebGL refraction: `liquid-glass-js:container.js`, `liquid-glass-js:button.js` and `liquid-glass-js:glass.css`. Each glass element creates its own canvas and WebGL context over a one-time html2canvas snapshot of the page, redraws on scroll, and on context failure only logs an error. Its README lists accessibility and performance work as roadmap items. Use it for one to three showpiece elements with your own fallback.

## Sources
Original guidance written for this project. design-md (Apache-2.0), liquid-glass-js and vengeance-ui (MIT) are cited as reference; react-bits is MIT with the Commons Clause and is described, not quoted.
