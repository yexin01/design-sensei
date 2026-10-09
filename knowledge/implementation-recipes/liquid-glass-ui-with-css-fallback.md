---
title: "Recipe: glass UI with a CSS baseline and an optional WebGL layer"
kind: recipe
summary: "Build frosted-glass cards, nav pills and buttons with plain CSS (backdrop blur, tint, scrim, lit rim, support and accessibility fallbacks), and optionally swap one hero surface for liquid-glass-js behind a capability check. Includes measured text-contrast numbers and a verification checklist."
source_ids: [liquid-glass-js]
pattern_ids: [liquid-glass-css-fallback, liquid-glass-container, liquid-glass-button]
updated: "2026-10-09"
---

# Recipe: glass UI with a CSS baseline and an optional WebGL layer

## Goal

Glass-looking surfaces that are readable and accessible everywhere, with the heavier WebGL refraction from liquid-glass-js available for one showcase element on capable devices. The CSS version is the product; the WebGL layer is an enhancement you can drop.

## When to use it, and when not

Use the CSS baseline for navigation, cards, toolbars and buttons over imagery or gradients. Add the WebGL layer only for a single hero panel on a mostly static page viewed on desktop. Do not use either where the backdrop is a flat colour (there is nothing to blur), where text must meet contrast on arbitrary imagery without a scrim, or on content that moves behind the glass if you plan to use the WebGL layer (its snapshot is static; see `knowledge/shaders/liquid-glass.md`).

## Prerequisites

- Baseline: none. Plain CSS.
- Optional layer: three vendored files from liquid-glass-js (`container.js`, `button.js`, `glass.css`) and html2canvas. There is no npm package at the pinned commit. The README loads html2canvas 1.4.1 from jsDelivr before the library scripts; self-host it to control CSP and privacy.

## Steps

### 1. Markup

Use real elements: `button` for actions, `a` inside `nav` for links.

```html
<section class="glass" style="max-width: 22rem">
  <h2>Glass card</h2>
  <p>Blur, tint and a lit rim from plain CSS.</p>
  <button class="glass glass--pill glass-button" type="button">Get started</button>
</section>
```

### 2. CSS baseline

Order matters: the safe default comes first, the enhancement sits in `@supports`, the user-preference overrides come last.

```css
:root {
  --glass-radius: 20px;
  --glass-tint: 255 255 255;            /* space-separated RGB so it can take an alpha */
  --glass-fill: 0.12;                   /* tint strength over the blurred backdrop */
  --glass-blur: 18px;
  --glass-scrim: 0.35;                  /* dark layer that keeps white text readable on bright backdrops */
  --glass-solid: rgb(28 32 48 / 0.92);  /* used when blur is unavailable or unwanted */
}

.glass {
  position: relative;
  isolation: isolate;
  border-radius: var(--glass-radius);
  padding: 1rem 1.25rem;
  color: #fff;
  background: var(--glass-solid);
  box-shadow: 0 18px 40px rgb(0 0 0 / 0.28);
}

@supports ((-webkit-backdrop-filter: blur(1px)) or (backdrop-filter: blur(1px))) {
  .glass {
    background:
      linear-gradient(180deg, rgb(255 255 255 / 0.22), rgb(255 255 255 / 0) 55%),
      linear-gradient(rgb(0 0 0 / var(--glass-scrim)), rgb(0 0 0 / var(--glass-scrim))),
      rgb(var(--glass-tint) / var(--glass-fill));
    -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(1.5);
    backdrop-filter: blur(var(--glass-blur)) saturate(1.5);
  }
}

/* lit rim: a 1px gradient ring, brighter at the top-left and bottom-right corners */
.glass::before {
  content: "";
  position: absolute;
  inset: 0;
  padding: 1px;
  border-radius: inherit;
  pointer-events: none;
  background: linear-gradient(135deg, rgb(255 255 255 / 0.7), rgb(255 255 255 / 0.05) 35%, rgb(255 255 255 / 0.05) 65%, rgb(255 255 255 / 0.4));
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  mask-composite: exclude;
}

.glass--pill { --glass-radius: 999px; padding: 0.5rem 0.75rem; }

.glass-button { font: inherit; border: 0; cursor: pointer; transition: transform 0.2s ease; }
.glass-button:hover { --glass-fill: 0.2; }
.glass-button:active { transform: scale(0.98); }
.glass-button:focus-visible { outline: 2px solid #fff; outline-offset: 3px; }

@media (prefers-reduced-motion: reduce) {
  .glass-button { transition: none; }
  .glass-button:active { transform: none; }
}
@media (prefers-reduced-transparency: reduce), (prefers-contrast: more) {
  .glass { background: var(--glass-solid); -webkit-backdrop-filter: none; backdrop-filter: none; }
}
@media (forced-colors: active) {
  .glass { background: Canvas; color: CanvasText; border: 1px solid CanvasText; box-shadow: none; -webkit-backdrop-filter: none; backdrop-filter: none; }
  .glass::before { display: none; }
}
```

What it gives you: blur and saturation of whatever sits behind, a dark scrim and a faint white tint, a top-down highlight, a gradient rim and a drop shadow. What it cannot do: refract or magnify the backdrop. Browsers that lack `backdrop-filter` get the solid style. `prefers-reduced-transparency` is not supported everywhere, so treat it as an extra, not the only safeguard.

### 3. Check contrast on your real backdrops

Translucent surfaces inherit the contrast of whatever is behind them. I rendered the baseline in headless Chrome over a deliberately bright orange shape and measured white text against the surface at points around the text:

| Variant | Worst measured | Median |
|---|---|---|
| Tint and blur only, no scrim | 2.1 : 1 | 4.3 : 1 |
| Scrim 0.25 | 3.1 : 1 | 5.7 : 1 |
| Scrim 0.35 (the CSS above) | 3.7 : 1 | 6.4 : 1 |
| Scrim 0.40 | 4.0 : 1 | 6.7 : 1 |
| Scrim 0.50 | 4.9 : 1 | 8.0 : 1 |
| Solid fallback | 14.4 : 1 | 15.6 : 1 |

Body text needs 4.5 : 1, which only the 0.5 scrim cleared in this test. So blur plus translucency alone is not enough over bright imagery. Raise `--glass-scrim`, lower the saturation, move text away from the brightest region, or use the solid style for text-heavy panels. Measure the worst frame of your own backdrop.

### 4. Optional: swap one hero surface for liquid-glass-js

Decide at creation time, not afterwards. The library snapshots the page when the first container is constructed, and the library has no destroy method, so a late swap would capture the CSS surface in the snapshot and could not be undone. This glue calls the public API only. I did not execute the library; the option names are read from `liquid-glass-js:container.js`.

```js
// Needs html2canvas, container.js and glass.css loaded first (classic scripts, in that order).
function createSurface(content) {
  const capable =
    typeof Container === 'function' && typeof html2canvas === 'function' && // a top-level class is not a window property: test by name
    matchMedia('(hover: hover) and (pointer: fine)').matches &&
    !matchMedia('(prefers-reduced-transparency: reduce)').matches &&
    !matchMedia('(prefers-contrast: more)').matches &&
    !navigator.connection?.saveData;

  if (!capable) {                              // the CSS baseline
    const el = document.createElement('div');
    el.className = 'glass';
    el.append(content);
    return el;
  }
  const glass = new Container({ type: 'rounded', borderRadius: 20, tintOpacity: 0.3 });
  const inner = document.createElement('div'); // one wrapper: .glass-container lays children out in a flex row
  inner.className = 'glass-upgraded';          // your own colour, padding and text styles
  inner.append(content);
  glass.element.appendChild(inner);
  return glass.element;                        // append it to the page; call glass.updateSizeFromDOM() if the layout changes
}
```

Add `.glass-container { isolation: isolate; }` so the canvas (`z-index: -1`) stays inside the container instead of dropping behind an opaque ancestor (inferred from the CSS rules, not tested). Wait for `document.fonts.ready` and the `load` event before creating it, so the snapshot matches the final page.

### 5. Keep the WebGL layer honest

- The snapshot is taken once. After resizes or content changes you must re-capture; copy the debounced approach in `liquid-glass-js:demo.js`, or accept staleness.
- Do not use more than a couple of containers; each owns a WebGL context and about 770 texture reads per fragment.
- Never rely on it for text or controls without the contrast checks above, and keep real `button` elements in your markup (the library's own buttons are `div`s with no keyboard support).

## Verification checklist

- Switch the `@supports` condition to something false: the solid style appears and text stays readable.
- Enable forced colours (Windows contrast themes or DevTools emulation) and increased contrast: no blur, visible borders.
- Check text contrast over the busiest part of every backdrop, in light and dark themes.
- Tab through the controls: visible focus ring, native button behaviour, correct names.
- Reduced motion: no hover scaling or transitions.
- Performance: record while scrolling on a mid-range phone; if frames drop, shrink the blurred area or lower `--glass-blur`, and avoid stacking large blurred layers.
- Optional layer: WebGL disabled and html2canvas blocked both leave the CSS surface working; console has no errors.

I rendered the CSS in headless Chrome with and without `backdrop-filter` support and measured the contrast above. The WebGL layer was not executed.

## Upstream references

`liquid-glass-js:container.js` (options, shader, snapshot), `liquid-glass-js:button.js`, `liquid-glass-js:glass.css`, `liquid-glass-js:demo.js` (re-snapshot on resize), `liquid-glass-js:README.md` (script order and API tables).

## Licence notes

The CSS and glue code here are original. liquid-glass-js is MIT; if you vendor its files keep `liquid-glass-js:LICENSE` and attribute Liquid Glass JS by dashersw (https://github.com/dashersw/liquid-glass-js). html2canvas has its own licence, which was not reviewed here.
