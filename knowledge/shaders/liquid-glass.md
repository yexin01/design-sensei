---
title: "Liquid glass (liquid-glass-js)"
kind: shader
summary: "How liquid-glass-js builds its glass effect: one WebGL 1 canvas per element that samples an html2canvas snapshot of the page, with signed-distance refraction, blur and tint. Covers the Container and Button API, global controls, caveats and costs, and an original plain-CSS fallback approach."
source_ids: [liquid-glass-js, shadergradient]
pattern_ids: [liquid-glass-container, liquid-glass-button, liquid-glass-css-fallback]
updated: "2026-10-09"
---

# Liquid glass (liquid-glass-js)

## Concept

liquid-glass-js (by dashersw; MIT, copyright line in `liquid-glass-js:LICENSE` names Armagan Amcalar) draws glass-like UI surfaces inspired by Apple's Liquid Glass: a rounded rectangle, circle or pill that refracts and blurs what is behind it, with a tint gradient and a lit rim. It is a set of plain scripts (`Container` and `Button` classes become globals); at the pinned commit there is no npm package, and the README roadmap lists bundling for npm, React and Vue wrappers, accessibility improvements, performance work and mobile touch optimisation as open items.

## What technique it uses

| Question | Answer, verified in code |
|---|---|
| SVG filters? | No. There is no `<filter>`, no displacement map. |
| CSS `backdrop-filter`? | Not in the library (`liquid-glass-js:glass.css`, `liquid-glass-js:container.js`, `liquid-glass-js:button.js`). Only the demo uses it, on a link in `liquid-glass-js:index.html` and on the mobile toggle in `liquid-glass-js:controls.css`. |
| WebGL? | Yes: one canvas per Container or Button, context from `getContext('webgl', { preserveDrawingBuffer: true })` and GLSL ES 1.00 shaders. The README badge and requirements say WebGL 2.0; the code only asks for WebGL 1. |
| What does it sample? | A static bitmap of the page. The first instance calls `html2canvas(document.body, ...)` once (scale 1, `useCORS`, `allowTaint`, transparent background, glass elements ignored), turns the result into an `Image` through `toDataURL()` and uploads it as a texture. |
| When does it redraw? | Standalone elements: once at start, on every `scroll` event (a passive listener per instance) and when `render()` is called. Nested buttons: every animation frame. |

So the glass shows a snapshot taken at load time, not the live page. Anything that changes behind it afterwards (video, carousels, animations, late-loading images) is not reflected.

## Files

| File | Role |
|---|---|
| `liquid-glass-js:container.js` | `Container` class, snapshot capture, the standalone fragment shader, scroll-driven rendering |
| `liquid-glass-js:button.js` | `Button extends Container`: text overlay, click handler, sizing, nested-glass shader and per-frame loop |
| `liquid-glass-js:glass.css` | Layout, shadow and text classes only |
| `liquid-glass-js:controls.js` | Demo control panel and the `window.glassControls` defaults |
| `liquid-glass-js:demo.js` | Demo usage, and the debounced re-snapshot on window resize (not part of the library) |
| `liquid-glass-js:index.html` | Demo page; loads html2canvas 1.4.1 from jsDelivr, then `container.js`, `button.js`, `controls.js`, `demo.js` |

## How an element is built

- **DOM.** A Container creates `div.glass-container` holding an absolutely positioned canvas (`z-index: -1`, with a box shadow) plus child elements. A Button adds `glass-button`, a `.glass-button-text` div (absolute, centred, white, `pointer-events: none`) and a `click` listener on the container div.
- **Size.** `updateSizeFromDOM()` runs on the next animation frame and copies `getBoundingClientRect()` into the canvas width and height. That is CSS pixels: nothing reads `devicePixelRatio`.
- **Shapes.** Circles are forced square; pills use half the height as radius. The shader does not receive the type: it infers pill (radius close to half the height and width more than height plus 4) or circle (roughly square, radius close to half the side) from size and radius, otherwise rounded rectangle.
- **Standalone shader.** Maps the element's centre plus scroll offset into snapshot coordinates; computes a signed distance to the shape; builds refraction from three exponential falloffs (base, edge, rim) along the shape normal plus a corner term and a tangential ripple; blurs with a circular Gaussian kernel of radius 6 steps whose spacing scales with `blurRadius`; mixes a white-to-grey vertical tint by `tintOpacity`; mixes in colours sampled from the snapshot at three heights; masks with a `smoothstep` on the distance.
- **Nested glass.** `container.addChild(button)` marks the button nested. Its shader samples the parent canvas, copied into a texture with `texSubImage2D` every frame, with a radius-4 blur, its own gradient and a 1.08 to 0.92 brightness ramp.

## API (verified in code)

`Container` options: `borderRadius` (default 48; `0` falls back to 48), `type` (`'rounded'`, `'circle'`, `'pill'`), `tintOpacity` (default 0.2). Members: `element` (append this to the DOM), `canvas`, `children`, `addChild(child)`, `removeChild(child)`, `updateSizeFromDOM()`, `render()` (set after the shader is ready), and statics `Container.instances`, `pageSnapshot`, `isCapturing`, `waitingForSnapshot`.

`Button` options: `text` (default `'Button'`), `size` (font px, parsed with `parseInt`, default 48), `type`, `onClick(text)`, `warp` (default false, enables the centre distortion term), `tintOpacity`. Sizes derive from `size`: circle diameter 2.5 times size; pill width is measured text plus 2 times size, height 2.2 times size; rounded height 2.5 times size with radius equal to size. The README example that passes `borderRadius` to a Button has no effect, because Button never reads that option.

Global parameters live in `window.glassControls`, read once when each shader is set up with `value || default`, so a value of `0` is replaced by the default. Defaults: edgeIntensity 0.01, rimIntensity 0.05, baseIntensity 0.01, edgeDistance 0.15, rimDistance 0.8, baseDistance 0.1, cornerBoost 0.02, rippleEffect 0.1, blurRadius 5 (2 for nested buttons). Ranges used by the demo sliders: edge 0 to 0.1, rim 0 to 0.2, base 0 to 0.05, edge distance 0.05 to 0.5, rim distance 0.1 to 2, base distance 0.05 to 0.3, corner boost 0 to 0.1, ripple 0 to 0.5, blur 1 to 15, tint 0 to 1. Live updates come from the demo's `updateAllGlassInstances()` in `liquid-glass-js:controls.js`, which writes uniforms through `gl_refs`; it is a demo helper, not a public API. The library ignores `glassControls.tintOpacity` at setup (it uses the instance option).

CSS hooks: `.glass-container`, `.glass-container-circle`, `.glass-container-pill`, `.glass-button`, `.glass-button-circle`, `.glass-button-text`.

## Browser support

The README table lists Chrome 80+, Firefox 75+, Safari 14+ and Edge 80+ as full support and requires WebGL 2.0. I did not verify that table. What the code needs: WebGL 1, `html2canvas`, `Image` decoding, class static fields (`static instances = []`) and optional chaining. Check those against your baseline. If WebGL is missing, `setupCanvas` logs `WebGL not supported` and the element stays an empty box with its text. If the page snapshot fails, the glass never initialises and the error is only logged.

## Performance

- Counting the loops in `container.js`: the blur visits a 13 by 13 grid but skips samples beyond radius 6, leaving 113 texture reads per fragment; the colour-sampling block adds about 660 (roughly 20 steps across the width, 11 offsets, 3 rows). That is about 770 reads per fragment, my count from reading, not a profile. The sampled-colour block depends only on uniforms, so every fragment of an element repeats the same work. Nested buttons use about 52 reads.
- Redraw happens on each scroll event for every standalone instance, with no throttling. Nested buttons run a `requestAnimationFrame` loop that uploads a canvas to a texture every frame and has no stop handle.
- Each instance owns a WebGL context. Browsers cap live contexts and evict the oldest; the ShaderGradient Vue package documents the same hazard and works around it (`shadergradient:packages/shadergradient-vue/src/shared.ts`).
- The snapshot is the whole page at scale 1, so a long page becomes a very tall texture; texture size limits were not checked by the code.
- Fragment precision is `mediump`, which can be coarse for coordinates on tall pages.
- There is no destroy method: `Container.instances` only grows.

## Accessibility

The elements are `div`s with a `click` listener. They have no role, no `tabindex`, no keyboard activation and no focus style; only the demo's mobile toggle sets ARIA attributes. Text is real DOM text, but it is white and sits on an arbitrary refracted image, so contrast must be checked against the busiest backdrop. The effect barely animates (it follows scroll), so reduced motion is not the main issue; contrast, focus and semantics are.

## Pitfalls

- The snapshot is static. The library never re-captures. The demo re-snapshots on window resize after 300 ms (`liquid-glass-js:demo.js`); you must do the same, and also after content or layout changes.
- Element size changes are not observed. Call `updateSizeFromDOM()` yourself after layout changes; it only runs automatically at creation, `addChild` and `removeChild`.
- Cross-origin images without CORS headers can taint the snapshot canvas, which makes `toDataURL()` throw and leaves the glass uninitialised (general canvas behaviour; the failure path is the logged error above).
- The canvas has `z-index: -1` and `.glass-container` creates no stacking context, so an opaque ancestor background can cover the canvas. Add `isolation: isolate` to the container (inferred from CSS rules, not tested).
- Scroll mapping adds `scrollY` only; horizontal scroll is ignored.
- `Button.measureText` hard-codes `system-ui, -apple-system, sans-serif`; a different CSS font can overflow because the text is `nowrap`.
- Do not expect refraction of glass behind glass: glass elements are excluded from the snapshot.

## When not to use it

Skip it for content that changes behind the glass, pages with many glass elements, mobile-first or low-power targets, long pages, server-rendered apps without a client wrapper, and any control that must be keyboard and screen-reader accessible. Prefer plain CSS for those.

## Plain-CSS fallback approach (original)

CSS cannot refract, but it can blur and tint what is behind a surface, which carries most of the effect:

1. Start from a safe opaque-enough background so text is readable with no blur support.
2. Inside `@supports` for `backdrop-filter` (with the `-webkit-` prefix), switch to a translucent tint and apply `blur()` with a little `saturate()`.
3. Add a dark scrim layer; white text over bright backdrops fails contrast otherwise (the recipe measures this).
4. Draw the lit rim as a 1px gradient ring using a masked pseudo-element, and add a soft drop shadow.
5. Honour `prefers-contrast`, `prefers-reduced-transparency` where supported, and `forced-colors`.
6. Use real `button` and `nav` elements.

Full code and a verification checklist are in `knowledge/implementation-recipes/liquid-glass-ui-with-css-fallback.md`.

## Licence and reuse

MIT with the notice kept (`liquid-glass-js:LICENSE`). html2canvas is a separate dependency with its own licence that was not reviewed here. Attribution: Liquid Glass JS by dashersw (https://github.com/dashersw/liquid-glass-js).

## Related patterns

`liquid-glass-container`, `liquid-glass-button`, `liquid-glass-css-fallback`; general practice in `knowledge/shaders/glsl-ui-fundamentals.md`.
