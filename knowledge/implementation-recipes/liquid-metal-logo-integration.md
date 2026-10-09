---
title: "Recipe: liquid metal logo with image fallback and reduced motion"
kind: recipe
summary: "Embed an animated liquid-metal logo in a page with original code: logo alpha becomes a bevel normal map on the CPU, a small WebGL shader fakes a chrome reflection, and the real img stays as fallback with a still frame for reduced motion, offscreen pausing, a DPR cap and context-loss recovery."
source_ids: [liquid-logo]
pattern_ids: [liquid-metal-logo, webgl-effect-fallback-and-reduced-motion]
updated: "2026-10-09"
---

# Recipe: liquid metal logo with image fallback and reduced motion

## Goal

Show a brand logo as a slowly moving chrome surface, without the gaps of the upstream tool: it should work with no WebGL, show a still frame for people who ask for reduced motion, stop when offscreen, cap its cost, survive context loss and keep an accessible name.

## When to use it, and when not

Use it for a single hero or intro logo with a transparent PNG or SVG. Do not use it for several logos at once (each takes a WebGL context), for logos with hairline strokes (thin features get little bevel), or where the logo must match brand colours exactly: the surface is a stylised reflection, not the brand palette.

## Prerequisites

- No dependencies. Plain ES modules and WebGL 1 in the browser.
- A same-origin logo with real alpha. Cross-origin images taint the canvas and are skipped by the code, which leaves the image fallback in place.
- The upstream project has no package or install step (`liquid-logo:README.MD` describes a local server and static files). This recipe does not copy its shader; it uses a different, simpler technique.

## How it works

The upstream tool evaluates a plasma pattern inside the logo mask (`liquid-logo:fragment-shader.glsl`). This recipe takes the other route: logo alpha is blurred into a soft height field on the CPU once, the slope of that field is stored as a normal map in two texture channels, and a cheap shader reflects a procedural light pattern off that surface while slow ripples move the normals. Per pixel it needs one texture read.

## Steps

### 1. Prepare the logo

Export a PNG or SVG with transparency, trimmed tight, at least 512 px on the long side. Solid shapes work best. Give an SVG explicit `width` and `height`, otherwise some browsers report a natural size of 0. If you only have a flat image on a plain background, remove the background in your design tool; upstream's browser-side removal (`liquid-logo:background-removal.js`) cannot reach enclosed holes such as the inside of an "O".

### 2. Markup and CSS

The `img` is the accessible content and the fallback. The canvas is decoration.

```html
<div class="logo-hero" id="logo-hero">
  <img src="/brand/logo.png" alt="Acme" width="640" height="640">
  <canvas aria-hidden="true"></canvas>
</div>
```

```css
.logo-hero { position: relative; width: min(100%, 480px); aspect-ratio: 1; }
.logo-hero img, .logo-hero canvas { position: absolute; inset: 0; width: 100%; height: 100%; }
.logo-hero img { object-fit: contain; transition: opacity .3s; }
.logo-hero canvas { opacity: 0; transition: opacity .3s; }
.logo-hero.is-live canvas { opacity: 1; }
.logo-hero.is-live img { opacity: 0; }      /* opacity keeps the img in the accessibility tree */
@media (prefers-reduced-motion: reduce) { .logo-hero img, .logo-hero canvas { transition: none; } }
```

### 3. The module (`liquid-logo-embed.js`)

```js
const VERT = `
attribute vec2 aPos;
varying vec2 vUv;
void main() {
  vUv = aPos * 0.5 + 0.5;
  gl_Position = vec4(aPos, 0.0, 1.0);
}`;

const FRAG = `
#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
varying vec2 vUv;
uniform sampler2D uMap;   // RG = surface slope (x, y), A = logo alpha
uniform float uTime;
uniform float uBevel;
uniform vec3 uShadow;
uniform vec3 uLight;

void main() {
  vec4 m = texture2D(uMap, vec2(vUv.x, 1.0 - vUv.y));
  float cover = smoothstep(0.05, 0.55, m.a);
  if (cover <= 0.0) { gl_FragColor = vec4(0.0); return; }

  vec3 n = vec3((m.rg * 2.0 - 1.0) * uBevel, 1.0);

  // slow ripples over the whole surface so flat interiors also move
  vec2 w = vUv * 4.0;
  w += 0.5 * vec2(sin(w.y * 1.7 + uTime * 0.5), cos(w.x * 1.3 - uTime * 0.4));
  n.xy += 0.22 * vec2(sin(w.x * 1.9 + uTime * 0.7), cos(w.y * 1.5 - uTime * 0.6));
  n = normalize(n);

  vec3 r = reflect(vec3(0.0, 0.0, -1.0), n);
  float s = smoothstep(0.2, 0.8, sin(r.x * 5.0 + r.y * 3.0 + uTime * 0.35) * 0.5 + 0.5);
  vec3 col = mix(uShadow, uLight, s) + pow(1.0 - n.z, 3.0) * 0.4;
  gl_FragColor = vec4(col * cover, cover);   // premultiplied alpha
}`;

const STATIC_TIME = 6.0; // seconds: the frame shown when motion is reduced or the effect is paused

function boxBlur(src, w, h, r) {
  const tmp = new Float32Array(src.length);
  const out = new Float32Array(src.length);
  const k = 1 / (2 * r + 1);
  const cl = (v, max) => (v < 0 ? 0 : v > max ? max : v);
  for (let y = 0; y < h; y++) {
    let acc = 0;
    for (let x = -r; x <= r; x++) acc += src[y * w + cl(x, w - 1)];
    for (let x = 0; x < w; x++) {
      tmp[y * w + x] = acc * k;
      acc += src[y * w + cl(x + r + 1, w - 1)] - src[y * w + cl(x - r, w - 1)];
    }
  }
  for (let x = 0; x < w; x++) {
    let acc = 0;
    for (let y = -r; y <= r; y++) acc += tmp[cl(y, h - 1) * w + x];
    for (let y = 0; y < h; y++) {
      out[y * w + x] = acc * k;
      acc += tmp[cl(y + r + 1, h - 1) * w + x] - tmp[cl(y - r, h - 1) * w + x];
    }
  }
  return out;
}

async function buildMap(img, size, radius) {
  await img.decode(); // rejects when the image failed to load
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const ctx = c.getContext('2d', { willReadFrequently: true });
  const fit = Math.min(size / img.naturalWidth, size / img.naturalHeight); // "contain"
  const w = img.naturalWidth * fit, h = img.naturalHeight * fit;
  ctx.drawImage(img, (size - w) / 2, (size - h) / 2, w, h);
  const px = ctx.getImageData(0, 0, size, size).data; // throws SecurityError for cross-origin images
  const alpha = new Float32Array(size * size);
  for (let i = 0; i < alpha.length; i++) alpha[i] = px[i * 4 + 3] / 255;
  const height = boxBlur(boxBlur(alpha, size, size, radius), size, size, radius);
  const gain = (2 * radius + 1) / 2; // a straight edge has a peak slope of about 1 / gain per texel
  const at = (x, y) => height[Math.min(size - 1, Math.max(0, y)) * size + Math.min(size - 1, Math.max(0, x))];
  const out = new Uint8Array(size * size * 4);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const i = (y * size + x) * 4;
      const sx = (at(x - 1, y) - at(x + 1, y)) * gain; // slope scaled to about -1..1
      const sy = (at(x, y + 1) - at(x, y - 1)) * gain;
      out[i] = Math.round((Math.max(-1, Math.min(1, sx)) * 0.5 + 0.5) * 255);
      out[i + 1] = Math.round((Math.max(-1, Math.min(1, sy)) * 0.5 + 0.5) * 255);
      out[i + 3] = Math.round(alpha[y * size + x] * 255);
    }
  }
  return out;
}

function compile(gl, type, src) {
  const s = gl.createShader(type);
  gl.shaderSource(s, src);
  gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s) || 'shader compile failed');
  return s;
}

export async function mountLiquidLogo(root, opts = {}) {
  const { mapSize = 512, blurRadius = 9, bevel = 1.6, maxDpr = 2, maxBuffer = 1024, requireHardware = true } = opts;
  const img = root.querySelector('img');
  const canvas = root.querySelector('canvas');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const noop = () => {};

  const gl = canvas.getContext('webgl', {
    alpha: true, premultipliedAlpha: true, antialias: false, depth: false, stencil: false,
    powerPreference: 'low-power', failIfMajorPerformanceCaveat: requireHardware,
  });
  if (!gl) return noop; // no (hardware) WebGL: the <img> stays visible

  let map;
  try { map = await buildMap(img, mapSize, blurRadius); } catch (err) { console.warn('liquid logo disabled:', err); return noop; }

  let loc = {}, raf = 0, inView = true, dead = false;
  const started = performance.now();

  function setup() { // also re-run after a context restore
    const prog = gl.createProgram();
    gl.attachShader(prog, compile(gl, gl.VERTEX_SHADER, VERT));
    gl.attachShader(prog, compile(gl, gl.FRAGMENT_SHADER, FRAG));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
    gl.useProgram(prog);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW); // one oversized triangle
    const a = gl.getAttribLocation(prog, 'aPos');
    gl.enableVertexAttribArray(a);
    gl.vertexAttribPointer(a, 2, gl.FLOAT, false, 0, 0);
    gl.bindTexture(gl.TEXTURE_2D, gl.createTexture());
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, mapSize, mapSize, 0, gl.RGBA, gl.UNSIGNED_BYTE, map);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    for (const n of ['uMap', 'uTime', 'uBevel', 'uShadow', 'uLight']) loc[n] = gl.getUniformLocation(prog, n);
    gl.uniform1i(loc.uMap, 0);
    gl.uniform1f(loc.uBevel, bevel);
    gl.uniform3f(loc.uShadow, 0.05, 0.06, 0.09);
    gl.uniform3f(loc.uLight, 0.92, 0.95, 1.0);
  }

  function resize() { // buffer follows layout size, capped DPR and a hard ceiling
    const dpr = Math.min(window.devicePixelRatio || 1, maxDpr);
    const px = Math.max(1, Math.min(maxBuffer, Math.round(canvas.clientWidth * dpr)));
    if (canvas.width !== px) { canvas.width = px; canvas.height = px; }
  }

  function draw(seconds) {
    if (gl.isContextLost()) return;
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.uniform1f(loc.uTime, seconds);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  const shouldAnimate = () => !dead && inView && !document.hidden && !motion.matches;
  function tick(now) {
    raf = 0;
    if (!shouldAnimate()) return;
    draw((now - started) / 1000);
    raf = requestAnimationFrame(tick);
  }
  function sync() {
    if (dead) return;
    cancelAnimationFrame(raf); raf = 0;
    if (shouldAnimate()) raf = requestAnimationFrame(tick);
    else draw(STATIC_TIME); // one still frame
  }

  const ro = new ResizeObserver(() => { resize(); sync(); });
  const io = new IntersectionObserver(([e]) => { inView = e.isIntersecting; sync(); });
  const onLost = (e) => { e.preventDefault(); cancelAnimationFrame(raf); raf = 0; root.classList.remove('is-live'); };
  const onRestored = () => { setup(); resize(); sync(); root.classList.add('is-live'); };

  try { setup(); } catch (err) { console.warn('liquid logo disabled:', err); return noop; }
  resize();
  sync();
  root.classList.add('is-live'); // first frame is on screen: swap the image for the canvas
  ro.observe(canvas);
  io.observe(root);
  document.addEventListener('visibilitychange', sync);
  motion.addEventListener('change', sync);
  canvas.addEventListener('webglcontextlost', onLost);
  canvas.addEventListener('webglcontextrestored', onRestored);

  return function dispose() {
    dead = true;
    cancelAnimationFrame(raf);
    ro.disconnect(); io.disconnect();
    document.removeEventListener('visibilitychange', sync);
    motion.removeEventListener('change', sync);
    canvas.removeEventListener('webglcontextlost', onLost);
    canvas.removeEventListener('webglcontextrestored', onRestored);
    gl.getExtension('WEBGL_lose_context')?.loseContext();
    root.classList.remove('is-live');
  };
}
```

### 4. Mount it

```html
<script type="module">
  import { mountLiquidLogo } from '/js/liquid-logo-embed.js';
  const dispose = await mountLiquidLogo(document.getElementById('logo-hero'));
  // call dispose() when the element is removed (route change in a single-page app)
</script>
```

In a framework, call it in an effect or `mounted` hook and return the disposer as cleanup. Never call it during server rendering.

### 5. Tune

| Option or constant | Effect |
|---|---|
| `blurRadius` (map pixels, default 9) | Width of the bevel; larger is softer and rounder |
| `bevel` (default 1.6) | How strongly the bevel tilts the surface |
| `uShadow`, `uLight` | The dark and light ends of the reflection |
| ripple constants in `FRAG` | Speed and size of the liquid movement |
| `STATIC_TIME` | Which moment is frozen for reduced motion; pick one that looks good |
| `maxBuffer`, `maxDpr` | Cost ceiling; 1024 and 2 suit a 480 px logo |

### 6. Optional: use upstream's plasma look instead

The MIT-licensed shader in `liquid-logo:fragment-shader.glsl` can be vendored with its notice (`liquid-logo:LICENSE.txt`). Keep the wrapper above and change four things. Use its vertex attribute name `aVertexPosition`. Upload the logo as a square RGBA texture to `u_logoTexture`, with `u_resolution` and `u_time` set per frame. Set every parameter listed in `knowledge/shaders/liquid-metal-logo.md` for one preset, because upstream presets are partial. Expect much higher cost (a loop of up to 16 iterations per pixel), so lower `u_iterations` and the buffer size on phones, and replace its hard alpha cut with a `smoothstep`.

## Verification checklist

- Disable WebGL (browser flag or a blocker): the image shows, no console errors.
- Enable reduced motion in the OS or DevTools: a still frame shows and no animation frames are requested; toggling the setting live starts and stops the motion.
- Scroll the logo offscreen and switch tabs: the loop stops (check the performance panel).
- Resize the window and rotate a phone: the canvas stays crisp and the buffer never exceeds `maxBuffer`.
- Screen reader announces the logo once, from the `img` alt text; the canvas is ignored.
- Console is clean; throttle CPU 4x in DevTools and confirm the page stays responsive.
- Try a logo with a hole and with thin strokes; adjust `blurRadius` if the bevel disappears.

I ran the code above in headless Chrome on macOS with software rendering. Checked: a frame renders, animated mode advances the time uniform, reduced motion draws only still frames at the fixed time and requests no animation frames, losing and restoring the context hides and re-shows the canvas, and with WebGL disabled the image stays visible. Not checked: real GPUs, Safari, Firefox, phones, SVG logos.

## Upstream references

`liquid-logo:fragment-shader.glsl` (plasma shader), `liquid-logo:main.js` (render loop and texture creation), `liquid-logo:background-removal.js`, `liquid-logo:canvasVideoExport.js` (PNG and MP4 export, which can produce a poster image or looping video fallback), `liquid-logo:README.MD`.

## Licence notes

The code in this recipe is original. Upstream liquid-logo is MIT; if you vendor any of its files, keep `liquid-logo:LICENSE.txt` and attribute Liquid Logo by collidingScopes (https://github.com/collidingScopes/liquid-logo). Its demo logos depict third-party brands and characters; do not reuse them, and use your own logo.
