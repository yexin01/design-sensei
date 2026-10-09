---
title: "Recipe: animated shader gradient background"
kind: recipe
summary: "Add an animated gradient behind page content, either with an original dependency-free WebGL fragment shader (CSS gradient fallback, reduced-motion still frame, offscreen pause, DPR and pixel caps, context-loss recovery) or with the ShaderGradient React package as a dependency, wrapped for reduced motion and background use."
source_ids: [shadergradient]
pattern_ids: [shader-gradient-background, shader-gradient-react, shader-gradient-url-config, glsl-background-fundamentals, webgl-effect-fallback-and-reduced-motion]
updated: "2026-10-09"
---

# Recipe: animated shader gradient background

## Goal

A soft, slowly moving gradient behind a hero or section that costs little, never blocks scrolling, stays readable, and degrades to a plain CSS gradient. Two routes: write a small shader yourself (route A, no dependencies), or use ShaderGradient (route B) when you want its 3D-noise look or its presets.

## When to use it, and when not

Use route A for ambient two-to-four-colour gradients. Use route B when you specifically want the displaced-mesh look, a ready-made camera, or Framer and Figma parity. Skip both when a CSS gradient is enough, when the page already runs heavy WebGL, or when users on low-power devices are the main audience; in that case use a pre-rendered image or short muted video.

## Prerequisites

- Route A: none. Plain ES modules and WebGL 1.
- Route B: React 18 or 19 and the packages below. Install command from the README (`shadergradient:README.md`), npm variant:

```
npm i @shadergradient/react @react-three/fiber three three-stdlib camera-controls
npm i -D @types/three
```

- Versions, from the same README and `shadergradient:packages/shadergradient/package.json`: peers are React and React DOM `^18.2.0 || ^19.0.0`, `three` `>=0.150.0`, `@react-three/fiber` `>=8.0.0`. For Next.js 15 App Router the README requires React 19 with `@react-three/fiber` 9 and three 0.158 or newer; other setups use React 18 or 19 with a matching fiber 8 or 9. The package is ESM only.
- Licence: the ShaderGradient repository has no LICENSE file (MIT is declared in its README and package files). This recipe uses its public API only and copies none of its code.

## Route A: your own shader

### A1. Markup and CSS

The CSS gradient is both the fallback and the first paint. Keep its colours equal to the shader's.

```html
<section class="hero">
  <canvas class="hero__bg" aria-hidden="true"></canvas>
  <div class="hero__content"><!-- your content --></div>
</section>
```

```css
.hero { position: relative; isolation: isolate; min-height: 100svh;
        background: linear-gradient(135deg, #0f1b3d, #33307a 55%, #7a3f8f); }
.hero__bg { position: absolute; inset: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none; }
```

### A2. The module (`gradient-background.js`)

```js
const VERT = `
attribute vec2 aPos;
void main() { gl_Position = vec4(aPos, 0.0, 1.0); }`;

const FRAG = `
#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
uniform vec2 uRes;    // drawing-buffer size in pixels, not CSS pixels
uniform float uTime;  // seconds
uniform vec3 uA;
uniform vec3 uB;
uniform vec3 uC;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vnoise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
             mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

void main() {
  vec2 uv = gl_FragCoord.xy / uRes;
  vec2 p = uv * vec2(uRes.x / uRes.y, 1.0) * 1.5;   // keep the pattern round on any aspect ratio
  float t = uTime * 0.06;
  vec2 q = vec2(vnoise(p + vec2(0.0, t)), vnoise(p + vec2(5.2, 1.3) - t));   // warp field
  float n = vnoise(p + 1.6 * q + t);
  vec3 col = mix(uA, uB, smoothstep(0.15, 0.85, n));
  col = mix(col, uC, smoothstep(0.35, 0.95, q.x * 0.6 + uv.y * 0.5));
  col += (hash(gl_FragCoord.xy) - 0.5) / 255.0;                               // dither against banding
  gl_FragColor = vec4(col, 1.0);
}`;

const rgb = (hex) => {
  const n = parseInt(hex.replace('#', ''), 16);
  return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255];
};

function compile(gl, type, src) {
  const s = gl.createShader(type);
  gl.shaderSource(s, src);
  gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s) || 'shader compile failed');
  return s;
}

export function startGradientBackground(canvas, opts = {}) {
  const {
    colors = ['#0f1b3d', '#33307a', '#7a3f8f'],
    renderScale = 0.5,     // a soft gradient does not need full resolution: 0.5 is a quarter of the pixels
    maxDpr = 2,
    maxPixels = 1.2e6,     // hard ceiling for the drawing buffer
    maxFps = 30,
    staticTime = 12,       // the still frame used for reduced motion
    requireHardware = true,
  } = opts;
  const noop = () => {};
  const gl = canvas.getContext('webgl', {
    alpha: false, antialias: false, depth: false, stencil: false,
    powerPreference: 'low-power', failIfMajorPerformanceCaveat: requireHardware,
  });
  if (!gl) return noop; // keep the CSS gradient that sits behind the canvas

  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let loc = {}, raf = 0, inView = true, dead = false, elapsed = staticTime, prev = 0, lastDraw = 0;

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
    for (const n of ['uRes', 'uTime', 'uA', 'uB', 'uC']) loc[n] = gl.getUniformLocation(prog, n);
    gl.uniform3fv(loc.uA, rgb(colors[0]));
    gl.uniform3fv(loc.uB, rgb(colors[1]));
    gl.uniform3fv(loc.uC, rgb(colors[2]));
  }

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, maxDpr) * renderScale;
    let w = canvas.clientWidth * dpr, h = canvas.clientHeight * dpr;
    const k = Math.min(1, Math.sqrt(maxPixels / Math.max(1, w * h)));
    w = Math.max(1, Math.round(w * k)); h = Math.max(1, Math.round(h * k));
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
  }

  function draw() {
    if (gl.isContextLost()) return;
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.uniform2f(loc.uRes, canvas.width, canvas.height);
    gl.uniform1f(loc.uTime, elapsed);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  const shouldAnimate = () => !dead && inView && !document.hidden && !motion.matches;
  function tick(now) {
    raf = 0;
    if (!shouldAnimate()) return;
    if (prev) elapsed += Math.min(0.1, (now - prev) / 1000); // clamp long gaps (tab switches)
    prev = now;
    if (now - lastDraw >= 1000 / maxFps) { lastDraw = now; draw(); }
    raf = requestAnimationFrame(tick);
  }
  function sync() {
    if (dead) return;
    cancelAnimationFrame(raf); raf = 0; prev = 0;
    if (shouldAnimate()) raf = requestAnimationFrame(tick);
    else { if (motion.matches) elapsed = staticTime; draw(); } // paused or reduced motion: show one still frame
  }

  const ro = new ResizeObserver(() => { resize(); sync(); });
  const io = new IntersectionObserver(([e]) => { inView = e.isIntersecting; sync(); });
  const onLost = (e) => { e.preventDefault(); cancelAnimationFrame(raf); raf = 0; canvas.style.visibility = 'hidden'; };
  const onRestored = () => { setup(); resize(); sync(); canvas.style.visibility = ''; };

  try { setup(); } catch (err) { console.warn('gradient background disabled:', err); return noop; }
  resize();
  sync();
  ro.observe(canvas);
  io.observe(canvas);
  document.addEventListener('visibilitychange', sync);
  motion.addEventListener('change', sync);
  canvas.addEventListener('webglcontextlost', onLost);
  canvas.addEventListener('webglcontextrestored', onRestored);

  return function stop() {
    dead = true;
    cancelAnimationFrame(raf);
    ro.disconnect(); io.disconnect();
    document.removeEventListener('visibilitychange', sync);
    motion.removeEventListener('change', sync);
    canvas.removeEventListener('webglcontextlost', onLost);
    canvas.removeEventListener('webglcontextrestored', onRestored);
    gl.getExtension('WEBGL_lose_context')?.loseContext();
  };
}
```

### A3. Start it

```html
<script type="module">
  import { startGradientBackground } from '/js/gradient-background.js';
  const stop = startGradientBackground(document.querySelector('.hero__bg'));
  // call stop() when the section is removed (route change in a single-page app)
</script>
```

### A4. Choose colours for the text on top

One text colour has to work across the whole animation. I rendered two palettes and measured white text against every sampled pixel of a frame: the dark palette above never fell below 7.2 : 1, whereas a palette ending in a light peach (`#f4b6a6`) fell to 1.7 : 1. If you want a light end, put the text on a card or use dark text on an all-light palette. Also avoid mixing complementary hues directly (navy into orange gave a muddy grey in my first test); add a mid-tone or pick analogous colours.

### A5. Tune

| Option | Effect |
|---|---|
| `colors` | Three hex colours; keep the CSS fallback equal |
| `renderScale` | 0.5 means a quarter of the pixels; raise for sharper detail, lower for weak devices |
| `maxFps` | 30 is plenty for slow drift |
| `maxPixels`, `maxDpr` | Cost ceilings |
| `staticTime` | The frozen moment shown for reduced motion |
| `1.5` and `0.06` in `FRAG` | Pattern scale and drift speed |

## Route B: the ShaderGradient package

Wrap it so it behaves as a background: no input capture, reduced motion respected, a CSS fallback behind it. This glue calls the public API only (props read from `shadergradient:packages/shadergradient/src/types.ts`); I did not install or run the package.

```tsx
'use client'
import { useEffect, useState } from 'react'
import { ShaderGradientCanvas, ShaderGradient } from '@shadergradient/react'

function usePrefersReducedMotion() {
  const [reduced, setReduced] = useState(() => matchMedia('(prefers-reduced-motion: reduce)').matches)
  useEffect(() => {
    const mq = matchMedia('(prefers-reduced-motion: reduce)')
    const update = () => setReduced(mq.matches)
    mq.addEventListener('change', update)
    return () => mq.removeEventListener('change', update)
  }, [])
  return reduced
}

export default function HeroGradient() {
  const reduced = usePrefersReducedMotion()
  return (
    <div aria-hidden="true" style={{ position: 'absolute', inset: 0, zIndex: -1 }}>
      <ShaderGradientCanvas pixelDensity={1} pointerEvents="none" style={{ position: 'absolute', inset: 0 }}>
        <ShaderGradient
          type="plane"
          animate={reduced ? 'off' : 'on'}
          uTime={reduced ? 8 : 0}
          uSpeed={0.2}
          uStrength={3}
          uDensity={1.2}
          grain="off"
          lightType="3d"
          brightness={1.1}
          color1="#0f1b3d"
          color2="#33307a"
          color3="#7a3f8f"
          cAzimuthAngle={180}
          cPolarAngle={90}
          cDistance={3.6}
        />
      </ShaderGradientCanvas>
    </div>
  )
}
```

Notes:

- The first `useState` initialiser reads `matchMedia` on render, so load this component on the client only. In Next.js import it from a client component with `dynamic(() => import('./HeroGradient'), { ssr: false })`, as the package's starter does (`shadergradient:apps/examples/example-nextjs/app/page.tsx`); the Vite starter needs nothing special (`shadergradient:apps/examples/example-vite-react/src/App.tsx`).
- Give the parent a real size and put a CSS gradient behind it. `lazyLoad` is on by default and leaves the wrapper empty until it scrolls into view.
- `animate="off"` plus a fixed `uTime` gives a still frame, but the render loop keeps running (see `knowledge/shaders/shadergradient.md`). Changing these props at runtime rebuilds the material, so expect a brief hitch when the preference flips.
- `grain="off"` skips the halftone post-pass, which is on by default. `pixelDensity` 1 is the cheap setting; `lightType="env"` would download three HDR files, so avoid it for backgrounds.
- Colours must be six-digit hex or integer `rgb()`; anything else turns black or throws.
- To reuse a look designed on the vendor's customizer, pass `control="query"` with a complete `urlString`; in React a URL missing `type` or `shader` is likely to fail (my reading of the code, not run).
- The Vue package (`@shadergradient/vue`) was not published at the pinned commit and already respects reduced motion; see the note.

## Verification checklist

- Disable WebGL (browser flag or blocker): the CSS gradient shows and the console has no errors. Route B: wrap the component in an error boundary and test it.
- Turn on reduced motion in the OS or DevTools: the page shows a still gradient and does not animate; toggling live works.
- Scroll the section offscreen and switch tabs: frame callbacks stop (Performance panel).
- Resize and rotate: no stretched or blank canvas; route A never exceeds `maxPixels`.
- Contrast: check text over the lightest and darkest parts of the cycle, not one screenshot.
- Scrolling and clicking work over the background (pointer events are off).
- Throttle the CPU 4x and watch frame time; on a mid-range phone try `renderScale` 0.35 to 0.5 for route A.
- A route A page with the module blocked or the context lost keeps the CSS gradient.

I ran route A in headless Chrome on macOS with software rendering: it compiled and drew at the capped buffer size (a 1200 by 713 CSS-pixel hero at DPR 2 gave a 1200 by 713 buffer), reduced motion drew only the fixed still frame and requested no animation frames, and the palette contrast numbers above were measured on its output. Not checked: real GPUs, Safari, Firefox, phones, and all of route B.

## Upstream references

`shadergradient:README.md` (install, compatibility, props), `shadergradient:packages/shadergradient/src/ShaderGradientCanvas.tsx` (canvas props, lazy loading), `shadergradient:packages/shadergradient/src/ShaderGradient/Mesh/Mesh.tsx` and `shadergradient:packages/shadergradient/src/shaders/defaults/plane/vertex.glsl` (what the default look computes), `shadergradient:packages/shadergradient-vue/src/ShaderGradientCanvas.ts` (reduced motion and context release).

## Licence notes

Route A is original code. Route B depends on `@shadergradient/react`, whose licence file is missing in the repository (MIT is declared in its README and package metadata); keep its attribution (ruucm and stone-skipper) and re-check the licence before shipping commercially.
