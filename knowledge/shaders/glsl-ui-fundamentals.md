---
title: "GLSL UI fundamentals: fragment-shader backgrounds"
kind: guide
summary: "Original guide for UI engineers building fragment-shader backgrounds and effects: full-screen drawing, uniforms for time, resolution and pointer, DPR and resize, pausing, context loss, reduced motion, WebGL detection and mobile budgets, with examples verified in three upstream projects."
source_ids: [liquid-logo, liquid-glass-js, shadergradient]
pattern_ids: [glsl-background-fundamentals, webgl-effect-fallback-and-reduced-motion]
updated: "2026-10-09"
---

# GLSL UI fundamentals: fragment-shader backgrounds

This is project-authored guidance. Upstream files are cited only as examples that were read and verified. Figures marked "rule of thumb" were not measured here.

## The model in one paragraph

A shader background is a canvas the GPU fills pixel by pixel. You draw one shape that covers the canvas; a fragment shader runs once per drawing-buffer pixel and returns a colour from a few inputs (position, time, parameters). The browser then composites the canvas like an image. Nothing in it is part of the DOM, so it has no text, no layout and no accessibility tree. Treat it as decoration that you must size, throttle and provide a fallback for.

## Minimal anatomy

Cover the viewport with one oversized triangle (corners at (-1,-1), (3,-1), (-1,3)) rather than a quad: one draw call, no diagonal seam, nothing to clip. The vertex shader only forwards positions. A fragment shader that drifts a gradient (GLSL ES 1.00, works in WebGL 1 and 2):

```glsl
precision mediump float;
uniform vec2 uRes;    // drawing-buffer size in pixels
uniform float uTime;  // seconds
void main() {
  vec2 uv = gl_FragCoord.xy / uRes;                 // 0..1, origin bottom-left
  float wave = 0.5 + 0.5 * sin(uv.x * 6.0 + uTime);
  gl_FragColor = vec4(mix(vec3(0.10, 0.10, 0.30), vec3(0.90, 0.50, 0.40), uv.y * wave), 1.0);
}
```

Always check `COMPILE_STATUS` and `LINK_STATUS` and print the info log; shader errors are otherwise silent.

## Uniforms you almost always need

| Uniform | Type | Meaning and care |
|---|---|---|
| `uRes` | `vec2` | Drawing-buffer size in pixels (`canvas.width`, `canvas.height`), not CSS pixels. |
| `uTime` | `float` | Seconds. Accumulate it yourself so pausing does not jump, and keep it small: large values lose precision in `sin` and hashes at `mediump`. |
| `uPointer` | `vec2` | Pointer position inside the canvas, 0 to 1, smoothed on the CPU. Optional. |
| palette | `vec3` | Colours as uniforms so design tokens drive the effect. |
| `uScroll` | `float` | Optional progress through a section for scroll-linked looks. |

## Coordinates

`gl_FragCoord` is in drawing-buffer pixels with the origin at the bottom-left. Divide by `uRes` for 0 to 1. For a centred, aspect-correct space use `(gl_FragCoord.xy * 2.0 - uRes) / uRes.y`; liquid-logo builds its plasma field this way (`liquid-logo:fragment-shader.glsl`). DOM images are top-origin while GL textures are bottom-origin, so flip Y once: liquid-logo flips its logo coordinates in the shader, and the recipe code flips in the sampling line.

## Size, DPR and resize

```js
const dpr = Math.min(window.devicePixelRatio || 1, 2) * renderScale;       // cap DPR; renderScale 0.5 to 1
const w = Math.max(1, Math.round(canvas.clientWidth * dpr));
const h = Math.max(1, Math.round(canvas.clientHeight * dpr));
if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
gl.viewport(0, 0, w, h);                                                    // then update uRes and redraw
```

- Let CSS size the canvas (`width: 100%; height: 100%`); the width and height attributes only set the buffer.
- Assigning `canvas.width` or `height` clears the buffer, so assign only on change and redraw immediately.
- Observe the canvas with `ResizeObserver`; window `resize` misses container changes.
- Cap the pixel count (rule of thumb: about one to two million pixels for a full-screen ambient effect). Soft gradients look the same at half resolution scaled up by CSS and cost a quarter of the work.

## Time and the render loop

Use the timestamp that `requestAnimationFrame` passes, add the delta to your own clock only while running, and clamp the delta (about 100 ms) so a returning tab does not jump. For ambient backgrounds skip frames to run at 30 fps. Do not drive rendering with `setInterval` (it is acceptable only for video capture, as liquid-logo does in `liquid-logo:canvasVideoExport.js`).

## Pointer input

Listen on the section or window, not on a canvas that has `pointer-events: none`. Convert with `getBoundingClientRect`, smooth with exponential damping, and never call `preventDefault` on wheel or touch events. Libraries that attach orbit controls to the canvas take over wheel and one-finger touch; ShaderGradient's React canvas does this unless `pointerEvents` is set to none.

## Pause, throttle and release

- Pause with `IntersectionObserver` and `document.visibilitychange`. ShaderGradient's React canvas goes further and unmounts itself offscreen (`shadergradient:packages/shadergradient/src/hooks/useInView.ts`).
- On teardown: cancel the frame, disconnect observers, delete buffers, textures and programs, then call `getExtension('WEBGL_lose_context')?.loseContext()`. Browsers cap live contexts and drop the oldest; the Vue package releases contexts explicitly for that reason (`shadergradient:packages/shadergradient-vue/src/ShaderGradientCanvas.ts`).
- Many views, one context: render once and copy the canvas into 2D canvases with `drawImage`, as `shadergradient:packages/shadergradient-vue/src/shared.ts` does.

## Context loss

```js
canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault(); stopLoop(); showFallback(); });
canvas.addEventListener('webglcontextrestored', () => { setupGlObjects(); startLoop(); hideFallback(); });
```

Without `preventDefault` the context is never restored. After restore every GL object is invalid, so keep the data you need (image bytes, parameters) on the CPU and rebuild programs, buffers and textures in `setupGlObjects`.

## Reduced motion and pause controls

- Read `matchMedia('(prefers-reduced-motion: reduce)')` and listen for `change`. When it matches, render one still frame at a chosen time (not `t = 0` if that frame is empty or flat) and do not start the loop. Vue ShaderGradient does the equivalent by freezing its clock.
- If movement starts automatically, lasts more than five seconds and sits beside other content, WCAG 2.2.2 (Pause, Stop, Hide) calls for a way to pause it. Provide a visible control even when the media query is not set.
- Keep any flicker well below three flashes per second (WCAG 2.3.1). Fast, high-contrast plasma can strobe.
- Slow, low-contrast drift is the safest default; large fast movement is the usual vestibular trigger.

## Feature detection and fallbacks

- Ask for the context with `failIfMajorPerformanceCaveat: true` for decorative effects, so software rendering falls back instead of crawling. Treat a null context as a normal outcome.
- Check shader compile and link results. Use `#ifdef GL_FRAGMENT_PRECISION_HIGH` to choose `highp` where available.
- Put the fallback underneath: a CSS gradient or the real `img`. Show the canvas only after the first successful frame (add a class, fade it in) and remove it on failure or context loss.
- Server rendering: create the context in an effect or `mounted` hook, never during render. Next.js needs a client component; ShaderGradient's starter uses a dynamic import with server rendering off (`shadergradient:apps/examples/example-nextjs/app/page.tsx`).

## Mobile budgets

Cost is roughly pixels times work per pixel times frames per second. Rules of thumb, to be checked on a real mid-range phone:

- Start at 0.5 to 0.75 render scale and 30 fps for ambient effects, then raise only if it looks wrong.
- Keep per-pixel loops short. liquid-logo runs up to 16 iterations per pixel on buffers up to 1500 by 1500; liquid-glass-js reads a texture about 770 times per fragment (my count, see `knowledge/shaders/liquid-glass.md`). Both are heavy for phones.
- Precompute static work on the CPU once (blur maps, normal maps, noise textures) instead of per pixel. The liquid-logo recipe does this.
- Use `highp` for anything time-driven, and wrap time. Use `powerPreference: 'low-power'` for decoration; liquid-logo requests `high-performance`, which can wake a discrete GPU.
- Add dynamic resolution: average frame time over about 30 frames and step the render scale down when it exceeds your budget.

## Accessibility and semantics

Mark decorative canvases `aria-hidden="true"`. Keep meaning in DOM content: a logo stays an `img` with alt text. Check text contrast against the busiest frame, not an average one, and add a scrim where needed. Never rely on a shader alone to convey state.

## What three upstream projects do

| Concern | liquid-logo | liquid-glass-js | ShaderGradient React | ShaderGradient Vue |
|---|---|---|---|---|
| Buffer size | Image size up to 1500 px, shown by CSS at `min(85vw, 700px)` (`liquid-logo:main.js`, `liquid-logo:styles.css`) | CSS pixels (`liquid-glass-js:container.js`) | `pixelDensity` prop, default 1 (`shadergradient:packages/shadergradient/src/consts.ts`) | Same prop |
| DPR handling | None | None | Prop only | Prop only |
| Resize | Not needed | Re-snapshot lives in the demo only (`liquid-glass-js:demo.js`) | R3F offset sizing | Handled by TresCanvas (not checked) |
| Offscreen pause | None | Draws on scroll only; nested buttons loop forever | Unmounts canvas when not visible | Unmounts and releases context |
| Context loss | None | None | None | Releases explicitly |
| Reduced motion | None | Not time-animated | None | Freezes time |
| No WebGL | `alert`, then an exception | Logs an error, no glass | None | SSR fallback slot only |

## Checklist

- Fallback visible with WebGL disabled and with JavaScript errors.
- Still frame with reduced motion; visible pause control if it moves for more than five seconds.
- No console errors, shader logs checked, context loss recovered.
- Buffer capped; frame time measured on a mid-range phone.
- Pauses offscreen and in hidden tabs; context released on teardown.
- Contrast checked on the worst frame; canvas hidden from assistive technology.

## Related

`knowledge/implementation-recipes/animated-shader-gradient-background.md` implements this guide in about 120 lines; `knowledge/implementation-recipes/liquid-metal-logo-integration.md` applies it to an image-driven effect.
