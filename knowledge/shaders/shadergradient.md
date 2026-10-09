---
title: "ShaderGradient (React, Vue, Framer, Figma)"
kind: shader
summary: "Architecture and parameter model of the ShaderGradient monorepo: a noise-displaced three.js mesh with custom GLSL, React and Vue renderers, a private UI package and Framer and Figma plugin shells, plus how to integrate it and what it costs. Licence status is unresolved, so this note describes only."
source_ids: [shadergradient]
pattern_ids: [shader-gradient-background, shader-gradient-react, shader-gradient-vue, shader-gradient-url-config]
updated: "2026-10-09"
---

# ShaderGradient (React, Vue, Framer, Figma)

Licence status first, because it limits how this note may be used. The repository has no LICENSE file. The README closes with an MIT line crediting ruucm and stone-skipper, and several package.json files declare MIT, so MIT is declared but the licence text and copyright notice are not shipped. The catalog therefore treats it as unresolved. This note describes behaviour and cites paths; it quotes nothing, and the recipes do not reproduce its code. Use the published package as a dependency instead of copying shaders, and keep the README attribution.

## What it is

A moving, 3D-looking colour gradient for web pages, Framer and Figma. It is not a full-screen fragment shader: a plane, sphere or water-plane mesh is deformed by noise in a vertex shader and coloured by mixing three colours according to the displaced position. The result is lit by three.js physical-material lighting and can pass through a halftone post-process.

## Monorepo map

| Path | What it is |
|---|---|
| `shadergradient:packages/shadergradient/` | `@shadergradient/react` 2.4.24: the renderer. ESM only (the exports map has an `import` condition only). Peers: React 18.2 or 19, `three` 0.150 or newer, `@react-three/fiber` 8 or newer. |
| `shadergradient:packages/shadergradient-vue/` | `@shadergradient/vue` 0.1.0 on TresJS. `shadergradient:CONTRIBUTING-VUE.md` and `shadergradient:apps/examples/README.md` say it is not published yet; the starters use a local tarball. |
| `shadergradient:packages/ui/` | Private UI and state package (zustand, Supabase client, Figma export helpers) used by the shadergradient.co site and the Framer and Figma bundles. Its own README (`shadergradient:packages/ui/src/README.md`) says it is not deployed to npm. |
| `shadergradient:apps/figma-plugin/` | Thin Figma plugin shell: an iframe to the hosted plugin page plus message handling that swaps image, GIF or video bytes into selected nodes. |
| `shadergradient:apps/framer-plugin/` | Framer plugin shell: an iframe to the site, and a call that inserts a hosted Framer component. |
| `shadergradient:apps/examples/` | Standalone starters: Next.js App Router, Vite React, Vite Vue, Nuxt. |
| `shadergradient:apps/example-nextjs-dev/` | Workspace dev app for the React package (glass shader and loop demos). |
| `shadergradient:tests/browser/` | Playwright checks for the Vue and Nuxt targets: canvas not blank, animation, pause, reduced motion, SSR fallback. |

`shadergradient:apps/email-previews/` holds marketing email templates and is irrelevant to rendering.

## How the gradient is rendered

Files under `shadergradient:packages/shadergradient/src/`:

- **Canvas.** `ShaderGradientCanvas.tsx` wraps a react-three-fiber `Canvas` in a div (100 percent width and height unless `style` overrides). Defaults: `pixelDensity` 1 (passed as `dpr`), `fov` 45, linear colour, flat tone mapping, `lazyLoad` on. It also patches four entries of three's global `ShaderChunk` table to empty strings on mount, a workaround for chunk names removed in newer three versions; this can affect other three.js content on the same page.
- **Geometry** (`ShaderGradient/Mesh/Geometry.tsx`): plane 10 by 10 units with 1 by 192 segments (386 vertices); waterPlane 10 by 10 with 192 by 192 segments (37,249 vertices); sphere icosahedron radius 1, detail 64 (about 84,500 triangles, my arithmetic from three's subdivision rule).
- **Material** (`ShaderGradient/Mesh/Materials.tsx`): a `MeshPhysicalMaterial` whose `onBeforeCompile` replaces both shaders with the GLSL files chosen by `shader` and `type`. Metalness 0.2 and roughness one minus `reflection` (the glass family sets its own values), double-sided.
- **Shader families** (`shaders/index.ts`, each with plane, sphere and waterPlane variants):

| Family | Vertex stage | Fragment stage |
|---|---|---|
| `defaults` | Classic Perlin noise (a port of public glsl-noise functions, credited in a comment) displaces vertices along normals by `uStrength` at frequency `uDensity`, moving with `uTime * uSpeed`. A loop mode blends four noise samples taken around a circle so the cycle repeats seamlessly. Sphere variants add a twist driven by `uFrequency` and `uAmplitude`. | Mixes the three colours by displaced position (plane and water: along x, then toward colour 3 by z; sphere: by height and distance from the centre), then applies three's physical lighting chunks. |
| `positionMix` | Noise displacement | Plane and water: the three colours weighted by the displaced x, y and z, unlit. Sphere: the same height-and-distance mix as `defaults`, lit. |
| `cosmic` | Several noise octaves plus sine "interference" and slight rotation | Holographic bands, shimmer, per-channel colour shift and iridescence added to the gradient, with some emission |
| `glass` | Sine waves plus simplex noise, reflection and refraction vectors | Fresnel mix of reflection and refraction with chromatic aberration; the env-map branches are guarded by a cube-map define and fall back to constants otherwise (which map type is active in practice was not verified) |

`shaders/base/` exists but nothing imports it. The README's future-plan list says shader code is not yet a separate package.

- **Time** (`Materials.tsx`): a THREE.Clock drives `uTime` when `animate` is on. `loop` plus `loopDuration` wraps time and switches the shader to the four-sample seamless mode; `range` with start and end restarts the clock abruptly. With `animate` off, `uTime` stays at the prop value, which gives a deterministic still frame.
- **Lighting** (`ShaderGradient/Lights/`): `lightType` `3d` is a single ambient light scaled by `brightness`; `env` loads equirectangular HDR files for the `city`, `dawn` or `lobby` preset. The component loads all three files (about 1.5 MB each in `shadergradient:packages/ui/assets/hdr/`) from a default hosted path (`shadergradient:packages/shadergradient/src/consts.ts`) unless `envBasePath` is set. A TODO in `Lights.tsx` says three 0.154 and newer give darker reflections with the existing shader.
- **Grain** (`ShaderGradient/PostProcessing/`): the `grain` prop switches on an extra EffectComposer pass, an RGB halftone with per-channel rotated dot grids. It runs unless `grain` is exactly `off`, and the default preset has it on.
- **Camera** (`ShaderGradient/Controls/`): the `camera-controls` library with left-drag rotate, wheel dolly (zoom on spheres) and one-finger touch rotate; right-drag and two-finger touch are disabled.

## Parameter model

Names and types come from `shadergradient:packages/shadergradient/src/types.ts` and `shadergradient:packages/shadergradient/src/ShaderGradient/Mesh/Mesh.tsx`; defaults come from the `halo` preset in `shadergradient:packages/shadergradient/src/presets.ts`.

| Group | Props | Notes |
|---|---|---|
| Shape | `type` (`plane`, `sphere`, `waterPlane`), `shader` (`defaults`, `positionMix`, `cosmic`, `glass`), `wireframe`, `positionX/Y/Z`, `rotationX/Y/Z` | Angles in degrees. The Framer controls hide the `shader` choice. |
| Motion | `animate` (`on`, `off`), `uTime`, `uSpeed`, `uStrength`, `uDensity`, `uFrequency`, `uAmplitude`, `loop`, `loopDuration`, `range`, `rangeStart`, `rangeEnd` | `uFrequency` and `uAmplitude` only affect sphere shaders. Defaults include speed 0.4, strength 4, density 1.3. |
| Colour | `color1`, `color2`, `color3`, `reflection` | See the colour-format pitfall below. |
| Camera | `cAzimuthAngle`, `cPolarAngle`, `cDistance`, `cameraZoom`, `zoomOut`, `smoothTime`, `enableTransition` | Planes use `cDistance` with zoom 1; spheres use a fixed distance with `cameraZoom`. |
| Light and effects | `lightType`, `brightness`, `envPreset`, `grain`, `toggleAxis` | `grainBlending` is typed but only the Vue package uses it. |
| Source | `control` (`props`, `query`), `urlString`, `onCameraUpdate` | Query mode parses a settings URL; see below. |

Canvas props: `pixelDensity`, `fov`, `pointerEvents`, `className`, `style`, `envBasePath`, `lazyLoad`, `threshold`, `rootMargin`, `preserveDrawingBuffer`, `powerPreference`. Ten presets exist (Halo, Pensive, Mint, Interstella, Nighty night, Viola, Universe, Sunset, Mandarin, Cotton Candy); all use the `defaults` shader.

## React integration

- Install the renderer plus its peers as listed in the README (`shadergradient:README.md`); the recipe shows the command.
- Give the canvas wrapper a real size. The README example positions it absolutely; the Vite starter uses a full-viewport parent (`shadergradient:apps/examples/example-vite-react/src/App.tsx`).
- Compatibility, per the README matrix: Next 15 App Router needs React 19 with `@react-three/fiber` 9 and three 0.158 or newer; Next 14, Next 15 Pages and Vite work with React 18 or 19 and a matching fiber 8 or 9. The Next starter loads the component with `next/dynamic` and `ssr: false` and sets `transpilePackages` and webpack condition names (`shadergradient:apps/examples/example-nextjs/app/page.tsx`, `shadergradient:apps/examples/example-nextjs/next.config.js`), although the README says no such config is needed on supported combinations.
- `control="query"` takes a customizer URL (the README points to shadergradient.co/customize). From reading the code, query mode replaces the whole prop set with the parsed query, so a URL missing `type` or `shader` would fail at shader lookup (not run). The Vue package merges missing values with defaults.
- For a decorative background set `pointerEvents` to none. By default the canvas receives input, so wheel and one-finger touch drive the camera and can interfere with page scrolling.

## Vue integration

`@shadergradient/vue` (`shadergradient:packages/shadergradient-vue/README.md`) requires Vue 3.5, TresJS 5 and three 0.180 or newer, and bundles the React package's shaders and presets from source. Compared with React it adds: an SSR-safe canvas with a `fallback` slot; automatic freezing of time and camera transitions under `prefers-reduced-motion` (`shadergradient:packages/shadergradient-vue/src/ShaderGradientCanvas.ts`); release of the WebGL context when the canvas leaves the viewport; `aria-hidden` and `pointer-events: none` by default; loading only the selected HDR; and `ShaderGradientSource` plus `ShaderGradientView`, which render once and copy frames into 2D canvases so many views share one context (`shadergradient:packages/shadergradient-vue/src/ShaderGradientSource.ts`). It emits `cameraUpdate` and `error`.

## Framer and Figma

`FramerShaderGradient.tsx` regroups flat props into Framer property controls (`FramerControls.ts`). `tsup.framer.config.ts` bundles three, fiber and the reconciler because Framer's sandbox only resolves React, React DOM and Framer. The Figma and Framer shells embed the hosted site in an iframe and receive snapshots or component URLs; the UI package also contains billing and Supabase code that a website integration never needs.

## Performance and fallbacks

- The render loop is always on: no `frameloop` override anywhere, so `animate="off"` stops time but not frames.
- `pixelDensity` defaults to 1, which is cheap and soft on high-DPI screens.
- Vertex cost: waterPlane has 37k vertices each running noise every frame; loop mode runs four noise samples instead of one; cosmic runs several octaves.
- The grain pass renders the scene to an offscreen target and then a halftone shader over the full canvas.
- `lazyLoad` (default on) uses an IntersectionObserver and unmounts the canvas offscreen, so the wrapper is empty until visible. Put a CSS gradient behind it. The React package does not check that IntersectionObserver exists.
- No WebGL detection, no context-loss handling and no reduced-motion handling in the React package (searched). Implement them outside: choose `animate` from a media query, keep a CSS fallback, and wrap the canvas in an error boundary.
- `Mesh.tsx` builds a fresh uniforms object on every render and the material is memoised on it, so re-rendering the component rebuilds the material (my reading, not measured). Keep props stable.

## Pitfalls

- **Colour formats (React package).** Only six-digit hex and integer `rgb(r, g, b)` parse. A three-digit hex or `rgba()` silently becomes black; other strings such as colour names throw. The Vue package uses three's colour parser instead.
- **Sphere-only props.** `uFrequency` and `uAmplitude` do nothing on planes.
- **Remounts.** Changing `pixelDensity` or `fov` remounts the canvas and recreates the context.
- **Query URLs in React** must be complete (see above).
- **Three versions.** Behaviour differs across three releases (see the Lights TODO); pin versions as in the README matrix.
- **Hosted assets.** Env lighting fetches HDR files from the project's host unless you self-host.

## Related

- Recipe: `knowledge/implementation-recipes/animated-shader-gradient-background.md`
- Patterns: `shader-gradient-background`, `shader-gradient-react`, `shader-gradient-vue`, `shader-gradient-url-config`
- Background reading: `knowledge/shaders/glsl-ui-fundamentals.md`
