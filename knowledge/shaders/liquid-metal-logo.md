---
title: "Liquid metal logo (liquid-logo)"
kind: shader
summary: "How liquid-logo animates a transparent-background logo as liquid metal: an alpha mask and edge detection feeding a plasma-style WebGL fragment shader, with its uniforms, presets, render loop, PNG and MP4 export, and the performance, fallback and accessibility gaps to close before embedding it in a site."
source_ids: [liquid-logo]
pattern_ids: [liquid-metal-logo, image-background-removal-for-logos, logo-video-export]
updated: "2026-10-09"
---

# Liquid metal logo (liquid-logo)

## Concept

Liquid Logo is a client-side browser tool by collidingScopes (MIT; the copyright line in `liquid-logo:LICENSE.txt` names Alan Ang). You give it a logo image and it renders the logo as a flowing, chrome-like surface in a WebGL canvas, with PNG and MP4 export. It is a single page of plain scripts, not a library: nothing is exported and there is no package to install. What is reusable is the technique and the shader.

Read the shader before trusting the README. The README talks about edge detection, vector fields and fluid dynamics, but the code contains no distance transform, normal map or fluid simulation. The look is a procedural plasma pattern (the README credits XorDev's "Plasma" shader as the starting point) evaluated only inside the logo's alpha mask, with the logo's edges used to bend and brighten the pattern.

## Files

| File | Role |
|---|---|
| `liquid-logo:fragment-shader.glsl` | All visual logic, about 310 lines of GLSL ES 1.00 |
| `liquid-logo:vertex-shader.glsl` | Pass-through for a full-canvas quad (attribute `aVertexPosition`) |
| `liquid-logo:shaders.js` | Fetches both shader files, compiles and links, logs errors, returns null on failure |
| `liquid-logo:main.js` | Context creation, logo texture, uniform upload, render loop, image loading, PNG save |
| `liquid-logo:gui-controls.js` | `params` defaults, dat.GUI sliders, `applyPreset`, quad buffer, randomize, hotkeys |
| `liquid-logo:presets.js` | Ten named presets |
| `liquid-logo:background-removal.js` | Corner-sampled flood fill for plain black or white backgrounds |
| `liquid-logo:canvasVideoExport.js` | PNG export, MP4 via WebCodecs plus mp4-muxer, MediaRecorder path |
| `liquid-logo:mp4-muxer-main/` | Vendored mp4-muxer 4.3.3 with its own MIT licence |
| `liquid-logo:index.html` | Page shell; scripts load in the order shaders, presets, muxer, export, removal, controls, main |

`liquid-logo:index.html` also loads dat.GUI and Font Awesome from cdnjs, a Google font and an analytics script from an external host. Do not copy those tags into a product page. Because the shaders are loaded with `fetch`, the page needs HTTP, not `file://` (the README tells you to run a local server).

## Pipeline

1. **Input.** A file chooser (`accept="image/*"`) or a demo PNG from `assets/`.
2. **Mask preparation, uploads only.** `processLogoImage` calls `removeBackground` with threshold 30 and flood fill on. It samples the four corners; when they agree and the average colour is clearly black or white (luminance below 30 or above 200) it flood-fills from the corners and zeroes alpha. Otherwise it logs a message and keeps the image as is. Demo logos skip this step.
3. **Square texture.** `resizeAndCreateLogoTexture` scales the image to at most 1500 px on its long side, rounds both sides down to a multiple of 4, centres it in a transparent square 2D canvas, sets the WebGL canvas to that square size and uploads it with `LINEAR` filtering, `CLAMP_TO_EDGE` wrapping and no mipmaps.
4. **Fragment shader.** One full-canvas quad (4-vertex triangle strip); every pixel runs the shader below.
5. **Compositing.** The context uses `alpha: true` and `premultipliedAlpha: false`, blending is SRC_ALPHA / ONE_MINUS_SRC_ALPHA, and pixels outside the mask are `discard`ed so the page background shows through.

## What the fragment shader does

Per pixel, in order (`liquid-logo:fragment-shader.glsl`):

1. Convert `gl_FragCoord` to logo-texture coordinates, scaled about the centre by `u_logoScale` and flipped vertically.
2. Sample the logo; alpha above 0.1 counts as inside. Inside the texture bounds but outside the mask the pixel is written transparent and returns early. Outside the bounds (possible when `logoScale` is below 1) it falls through and is discarded only at the end.
3. Edge strength: the summed colour difference to the four neighbours one canvas pixel away, through `smoothstep(0, 0.2, ...)`, times `u_logoInteractStrength`.
4. Plasma setup: centred coordinates divided by canvas height, a radial term `abs(u_dotFactor - dot(p, p)) * u_dotMultiplier`, a push from the edge value, and a 3D simplex-noise flow scaled by `u_noiseIntensity`.
5. A loop of at most 16 iterations (early exit at `u_iterations`) warps the vector with cosine terms and accumulates sinusoidal intensity; near edges the offsets are amplified up to five times.
6. Optional channel rotation (`u_colorShift`), then a hand-written tanh-style squash of `exp(p.y * colorFactors) * exp(-u_expFactor * l.x) / o`. This is where the red, green and blue components tint the result.
7. Film grain from a hash of pixel coordinates, an edge highlight and clamping. Inside the mask the colour is blended 30 percent toward a lightened copy that carries the logo alpha, plus an additive pale-blue highlight along edges.

The loop header that caps the iteration count, verbatim (`liquid-logo:fragment-shader.glsl:250-251`):

```glsl
for(float i = 0.0; i < 16.0; i++) {
    if (i >= u_iterations) break;
```

Inert code, confirmed by search: `u_logoOpacity`, `u_logoAspectRatio` and `u_logoBlendMode` are declared and uploaded but never read by `main()`; `applyBlendMode` and `applyNoiseDistortion` are never called; the time and ripple terms inside `liquidMetalEffect` are multiplied by zero.

## Parameters

Verified against `liquid-logo:gui-controls.js` and `liquid-logo:presets.js`. The initial value is what the page starts with after the default preset (Galaxy) is applied.

| Uniform (JS param) | GUI label | Slider range | Initial | Effect |
|---|---|---|---|---|
| `u_speed` (`speed`) | Speed | 0.1 to 2.0 | 0.44 | Time multiplier |
| `u_iterations` (`iterations`) | Color Smoothing | 3 to 24, step 1 | 8 | Loop count; the shader stops at 16 |
| `u_scale` (`scale`) | Pattern Scale | 0.1 to 4.0 | 2.63 | Divides the coordinate field |
| `u_dotFactor` (`dotFactor`) | Dot Factor | 0.1 to 1.2 | 0.03 | Radius of the radial warp |
| `u_dotMultiplier` (`dotMultiplier`) | Dot Multiplier | 0 to 2 | 0.61 | Strength of the radial warp |
| `u_vOffset` (`vOffset`) | Pattern Offset | 0 to 10 | 0.0 | Constant added every iteration |
| `u_intensityFactor` (`intensityFactor`) | Intensity | 0.05 to 0.5 | 0.37 | Gain per iteration |
| `u_expFactor` (`expFactor`) | Exp Factor | 0.1 to 5 | 0.5 | Radial falloff in the squash |
| `u_noiseIntensity` (`noiseIntensity`) | Noise Intensity | 0 to 10 | 4.0 | Simplex flow inside the mask |
| `u_colorFactors` (`redFactor`, `greenFactor`, `blueFactor`) | Red, Green, Blue Component | -3 to 3 | 1.0, -0.3, 1.6 | Per-channel exponent on vertical position |
| `u_colorShift` (`colorShift`) | Color Shift | 0 to 2 | 0.1 | Mix with a channel-rotated copy |
| `u_logoScale` (`logoScale`) | Logo Scale | 0.5 to 3 | 1.0 | Scales the mask about the centre |
| `u_logoInteractStrength` (`logoInteractStrength`) | Edge Interaction | 0 to 0.3 | 0.1 | Edge bend and highlight strength |

`main.js` also sets `u_resolution`, `u_time` (seconds since start, from `Date.now()`) and `u_logoTexture` (unit 0). Presets: Glow, Wisp, Smoke, Oil Slick, Chrome, Rainbow, Liquid, Magic, Dusk, Galaxy.

Preset caveats, verified: the `params` object has its own defaults (speed 2.2, iterations 13, scale 0.05) but `main.js` ends with `applyPreset(defaultPreset)`, so preset values win. Presets are partial: only Glow and Magic set `noiseIntensity`, and Wisp also omits `dotMultiplier`, so the look of a preset depends on the one loaded before it. Some preset values fall outside the sliders (Glow sets `logoInteractStrength` to 0.66; the slider stops at 0.3).

## Render loop and controls

- `animate()` calls `drawScene()` and re-queues itself with `requestAnimationFrame` forever. `drawScene()` clears, enables blending, re-sends every uniform and draws the strip.
- The WebGL context is requested with `antialias`, `alpha`, `preserveDrawingBuffer: true` (needed for export) and `powerPreference: "high-performance"`.
- Controls: a dat.GUI panel (closed at start), dice, camera and video buttons, and hotkeys Space (pause), R (randomize), S (save PNG) and V (record). The GUI has no pause control; only Space pauses.
- The canvas buffer is the image-sized square; CSS shows it at `min(85vw, 700px)` wide (`liquid-logo:styles.css`).

## Export

- **PNG.** `saveImage` redraws, flushes, copies the WebGL canvas into a 2D canvas and downloads `toDataURL('image/png')`; transparency is kept.
- **MP4 on desktop (not Firefox).** WebCodecs `VideoEncoder` with an H.264 codec string and 16 Mbit/s variable bitrate feeds the vendored mp4-muxer (`ArrayBufferTarget`, in-memory fast start). A 30 fps `setInterval` redraws the scene and encodes `new VideoFrame(canvas)`.
- **iOS, Android, Firefox.** `canvas.captureStream(30)` into `MediaRecorder`. The options object passes `type`, whereas the MediaRecorder API names that option `mimeType`, so the output container is probably browser-chosen (not tested here).
- Browser choice is by user-agent sniffing. Upstream's page suggests a screen recorder if export fails.

## Performance

- The page itself warns that the animation is resource-intensive and may lag on weak or low-battery machines.
- Per masked pixel: 6 texture reads (1 logo sample, 5 for edges), one 3D simplex noise, and up to 16 loop iterations with a vec2 cosine and a vec4 sine each. Cost scales with mask area, but GPU groups that straddle the mask edge still pay.
- The drawing buffer is up to 1500 by 1500 px regardless of display size, and nothing reads `devicePixelRatio`. On a phone showing the canvas about 330 CSS px wide at 2x DPR (660 px), that is roughly five times the pixels needed.
- Nothing pauses the loop offscreen, handles context loss, or throttles the frame rate. `powerPreference: "high-performance"` can select the discrete GPU on laptops.
- Mitigations used in the recipe: size the buffer from layout and a DPR cap, cap iterations, pause offscreen, one still frame when motion is reduced.

## Fallback and accessibility

- No WebGL: `main.js` calls `alert('WebGL not supported in your browser')` and then continues, so `init` throws on the first `gl` call.
- No `prefers-reduced-motion` handling, no text alternative for the canvas, and a global keydown handler that calls `preventDefault` on Space (it blocks page scrolling with the space bar). Do not carry these into a site.
- Recommended structure (see the recipe): keep the logo as a real `img` with alt text, put the canvas on top with `aria-hidden="true"`, show a still frame for reduced motion.

## Pitfalls

- **Image preparation.** The shader needs alpha. Removal only handles uniform near-black or near-white backgrounds found from the four corners; otherwise it is skipped. A fill from the corners cannot reach enclosed background such as the counter of an "O", so those regions stay opaque and get filled with the effect. Prefer a PNG or SVG with real transparency.
- **Hard mask.** Inside versus outside is a threshold at alpha 0.1 plus `discard`, so edges alias; upstream's own to-do list in `liquid-logo:main.js` mentions edge pixelation. Use a `smoothstep` on alpha instead.
- **Large uploads.** Background removal runs on the full-size image before the 1500 px downscale, on the main thread, with an array used as a queue; very large images may freeze the page (not measured).
- **Iteration slider.** Values above 16 have no effect.
- **Textures.** Cross-origin logos taint the canvas and `texImage2D` then throws; use same-origin files.
- **Brand assets.** The demo logos (Apple, Nike, GitHub and others in `liquid-logo:assets/`) depict third-party marks and characters. The MIT licence covers the code, not those marks.

## Licence and reuse

MIT, so code may be reused with the copyright and permission notice kept (`liquid-logo:LICENSE.txt`). The vendored muxer has its own MIT notice (`liquid-logo:mp4-muxer-main/LICENSE`). The README credits XorDev's Plasma shader. Attribution used by this project: Liquid Logo by collidingScopes (https://github.com/collidingScopes/liquid-logo). The recipe linked below uses original code and a different, simpler technique.

## Related

- Recipe: `knowledge/implementation-recipes/liquid-metal-logo-integration.md`
- Patterns: `liquid-metal-logo`, `image-background-removal-for-logos`, `logo-video-export`
- General WebGL practice: `knowledge/shaders/glsl-ui-fundamentals.md`
