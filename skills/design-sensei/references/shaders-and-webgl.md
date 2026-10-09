# Shaders and WebGL

Decide whether a shader effect is justified, build or choose one that stays cheap, and make it degrade safely. Load this before adding a fragment-shader background, a liquid or glass effect, an animated gradient or any raw WebGL canvas.

Figures marked "rule of thumb" are heuristics from [GLSL UI fundamentals](../../../knowledge/shaders/glsl-ui-fundamentals.md); none was measured. Verify on a real mid-range phone.

## Is a shader justified?

A shader canvas is decoration the GPU paints. It has no DOM, no text, no accessibility tree. Use one only when the effect carries the art direction and CSS cannot reach it.

| Need | Use | Why |
| --- | --- | --- |
| Soft two-to-four colour gradient, static | CSS gradient | Zero JS, zero GPU, first paint. |
| Drifting blobs, aurora, grain | CSS or SVG layers with `transform`/`opacity` animation | Compositor-only, easy reduced-motion. See [[fancy-animated-gradient-svg]], [[vengeance-ui-aurora-hero-backgrounds]]. |
| Frosted glass panel | CSS `backdrop-filter` with `@supports` fallback | See [[liquid-glass-css-fallback]]. |
| Moving gradient with depth, noise, refraction, metal, plasma | Fragment shader | Per-pixel maths that CSS cannot do. |
| Effect must react to pointer or scroll per pixel | Fragment shader | Uniforms. |
| Loop is the same every time | Pre-rendered video or image sequence | Cheaper than live GPU on low-power targets. |

Dial and config gates:

| Setting | Effect on shader work |
| --- | --- |
| `webgl_enabled: false` | No WebGL. Use CSS or video. `design-sensei eval` raises PERF-005 as an error if WebGL is found. |
| `motion_intensity` 1-3 | No shader motion; at most a still frame. |
| `motion_intensity` 4-6 | One slow ambient shader background, low contrast. |
| `motion_intensity` 7-10 | One hero shader plus at most one supporting effect; still within `max_webgl_canvases`. |
| `max_webgl_canvases` (default 1) | Hard ceiling on simultaneous canvases. |
| `reduced_motion: static_first` | Render the still frame first; start the loop only under `no-preference`. |
| `allowed_dependencies` | `none`/`existing`: write the shader yourself (about 120 lines, see recipe below). |

Skip shaders when: text-heavy pages, low-power audience, pages that already run another canvas, content that must be crisp behind the effect, or when nobody will notice the difference.

## Fragment-shader background: build rules

Model: one oversized triangle covers the canvas, the fragment shader runs once per drawing-buffer pixel and returns a colour from a few inputs. Cost is roughly pixels x work per pixel x frames per second.

| Concern | Rule |
| --- | --- |
| Geometry | One triangle with corners (-1,-1), (3,-1), (-1,3): one draw call, no seam. |
| Uniforms | `uRes` (buffer pixels, not CSS), `uTime` (accumulated seconds, kept small, wrapped), `uPointer` (smoothed, optional), palette as `vec3` uniforms so design tokens drive colour. |
| Precision | `highp` for time-driven maths where available (`GL_FRAGMENT_PRECISION_HIGH`). |
| Buffer size | Let CSS size the canvas; set `width`/`height` attributes only on change (assigning clears the buffer). |
| DPR | Cap: `Math.min(devicePixelRatio, 2)` times a render scale of 0.5-1. Soft gradients look the same at half resolution. Rule of thumb: 1-2 million pixels for a full-screen ambient effect. |
| Resize | `ResizeObserver` on the canvas, not window `resize`. |
| Frame loop | Use the `requestAnimationFrame` timestamp, clamp delta (about 100 ms), skip frames to 30 fps for ambient effects. Never `setInterval`. |
| Pointer | Listen on the section or window; smooth with damping; never `preventDefault` wheel or touch. |
| Per-pixel loops | Keep short. Precompute static work (blur, normal map, noise texture) on the CPU once. |
| Power | `powerPreference: 'low-power'` for decoration. |
| Dynamic quality | Average frame time over about 30 frames; step render scale down when over budget. |
| Errors | Check `COMPILE_STATUS` and `LINK_STATUS`; print the info log. |

Pause, release, recover:

- Pause with `IntersectionObserver` and `visibilitychange`. Better, unmount offscreen.
- Teardown: cancel the frame, disconnect observers, delete buffers/textures/programs, then `getExtension('WEBGL_lose_context')?.loseContext()`. Browsers cap live contexts and evict the oldest.
- Context loss: on `webglcontextlost` call `preventDefault()`, stop the loop, show the fallback; on `webglcontextrestored` rebuild every GL object from CPU-held data.
- Many views, one context: render once and copy into 2D canvases.

## Feature detection and fallbacks

1. Static layer first: a CSS gradient or the real `img` underneath, equal in colour to the shader. It is the LCP candidate.
2. Request the context with `failIfMajorPerformanceCaveat: true` for decorative effects; a null context is a normal outcome, not an error.
3. Fade the canvas in only after the first successful frame; remove it on failure or context loss.
4. Gate on `prefers-reduced-motion`, small viewport or coarse pointer (policy choice, for example under 768 px), and data-saver. See the effect-mode hook in the [heavy background budget recipe](../../../knowledge/implementation-recipes/react-bits-heavy-background-budget.md).
5. Reduced motion: render one still frame at a chosen time (not an empty `t = 0`), no loop. If movement is automatic, lasts over 5 seconds and sits beside content, provide a visible pause control (WCAG 2.2.2). Keep flicker well under three flashes per second (WCAG 2.3.1).
6. SSR: create the context in an effect or `mounted`, never in render. Next.js: client component or dynamic import with SSR off.
7. Mark decorative canvases `aria-hidden="true"`. Meaning stays in DOM content (a logo stays an `img` with alt). Check text contrast against the busiest frame, add a scrim if needed.

## Choosing a source

Search first: `design-sensei search "<effect words>" --category background-shader` (also `--category liquid-glass`, `--category gradient`, or `--webgl`, `--max-gpu low`). Then read the note and open the files before copying anything.

| Need | Pattern | Reuse class | Cost and caveats |
| --- | --- | --- | --- |
| Ambient gradient, no dependency | [[glsl-background-fundamentals]] with [recipe](../../../knowledge/implementation-recipes/animated-shader-gradient-background.md) route A | `license_review_required` in the catalog because the note cites shadergradient; the recipe code is original | Cheapest. Write it yourself. |
| 3D-noise displaced mesh gradient, presets | [[shader-gradient-react]], [[shader-gradient-background]], [[shader-gradient-url-config]] | `license_review_required` (MIT declared, no LICENSE file shipped: licence unverified) | Always-on frame loop; waterPlane is about 37k vertices; no WebGL detection, context-loss or reduced-motion handling in the React package. Use as a dependency, do not copy shaders. Set `pointerEvents` to none for backgrounds. |
| Same, Vue/Nuxt | [[shader-gradient-vue]] | `license_review_required` | Freezes time under reduced motion, releases context offscreen. Not yet published to npm per the note. |
| Logo as liquid metal | [[liquid-metal-logo]] with [recipe](../../../knowledge/implementation-recipes/liquid-metal-logo-integration.md) | `copy_with_attribution` (MIT, keep notice) | Upstream has no pause, no DPR cap, no fallback, buffer up to 1500 px; the recipe fixes these with a simpler technique. One logo only. |
| Liquid metal button | [[vengeance-ui-liquid-metal-button]] | `copy_with_attribution` | Live shader border per button; budget it as a canvas. |
| WebGL glass panel | [[liquid-glass-container]], [[liquid-glass-button]] | `copy_with_attribution` | Static html2canvas snapshot, about 770 texture reads per fragment (the note's count), one context per element, no keyboard semantics. Prefer [[liquid-glass-css-fallback]] for most cases. |
| Many ready-made shader backgrounds | [[react-bits-ogl-shader-backgrounds]], [[react-bits-three-r3f-backgrounds]], [[react-bits-webgpu-backgrounds]] | `license_review_required` (custom terms: use per terms, never bundle or republish) | 26 of 53 per the recipe's scan have no offscreen pause. Wrap with the budget slot. |
| Backgrounds with safeguards | [[react-bits-self-pausing-shader-backgrounds]] | `license_review_required` | Pause offscreen, freeze under reduced motion, expose `paused`, fps and pixel-ratio props. Prefer these for always-visible heroes. |
| Any WebGL effect resilience | [[webgl-effect-fallback-and-reduced-motion]] | `license_review_required` (catalog) | Checklist pattern; applies to every row above. |

Licence gate: `copy_with_attribution` means adapt freely and keep the upstream copyright and licence notice (add to `THIRD_PARTY_NOTICES.md`). `license_review_required` means read `design-sensei sources show <id>` first, use as a dependency per its terms, never vendor or republish. Do not copy anything from `reimplement_only`, `reference_only` or `verify_first` sources. See `source-usage.md`. Never run scripts from downloaded upstream repos.

Never copy upstream tags that load external analytics, fonts or GUI libraries (liquid-logo's demo page loads several). Brand logos in demo assets are third-party marks.

## Verification

- Disable WebGL (browser flag or devtools) and confirm the fallback looks designed.
- Emulate `prefers-reduced-motion: reduce`, toggle live: still frame, no loop.
- Console clean; shader logs checked; context loss recovered (`WEBGL_lose_context` in devtools or code).
- Scroll the effect offscreen and confirm the loop stops (check idle GPU/CPU).
- Frame time on a mid-range phone or 4x CPU throttle; buffer size at DPR 2.
- Count canvases against `max_webgl_canvases`.

## Checklist before saying done

- [ ] A shader was justified against a CSS or video alternative.
- [ ] Static fallback underneath, same palette; canvas fades in after the first frame.
- [ ] DPR capped, buffer sized from layout, `ResizeObserver` used.
- [ ] Paused offscreen and in hidden tabs; context released on teardown; context loss handled.
- [ ] Reduced motion: still frame; pause control if motion is long-running.
- [ ] `aria-hidden` on decorative canvas; contrast checked on the worst frame.
- [ ] Canvas count within `max_webgl_canvases`; licence class respected, notices kept.
- [ ] `design-sensei eval` clean for PERF-004, PERF-005, PERF-006, MOT-001, MOT-006.

## Common mistakes

- Shader where a CSS gradient would do; full-viewport effect behind reading text with no scrim.
- `devicePixelRatio` used uncapped; buffer fixed at image size regardless of display.
- Render loop that never stops; one context per small element.
- Canvas hidden-state only, with no `img` or gradient fallback; `alert` on missing WebGL.
- Orbit controls left on a decorative canvas, capturing wheel and touch.
- Copying a `license_review_required` shader into the project.
- Large time values at `mediump`, producing banding or jitter.

## Related

- Notes: [GLSL UI fundamentals](../../../knowledge/shaders/glsl-ui-fundamentals.md), [liquid glass](../../../knowledge/shaders/liquid-glass.md), [liquid metal logo](../../../knowledge/shaders/liquid-metal-logo.md), [ShaderGradient](../../../knowledge/shaders/shadergradient.md), [React Bits catalog](../../../knowledge/components/react-bits-catalog.md).
- Recipes: [shader gradient background](../../../knowledge/implementation-recipes/animated-shader-gradient-background.md), [heavy background budget](../../../knowledge/implementation-recipes/react-bits-heavy-background-budget.md), [liquid glass with CSS fallback](../../../knowledge/implementation-recipes/liquid-glass-ui-with-css-fallback.md).
- Other references: `performance.md`, `motion-design.md`, `three-dimensional-design.md`, `accessibility.md`, `source-usage.md`.
