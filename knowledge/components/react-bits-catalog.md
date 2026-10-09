---
title: "React Bits component catalog"
kind: guide
summary: "Table of 100 design-relevant React Bits components (of 215) grouped by role, with render technology (GPU-driven rows flagged), the TS + Tailwind source file, npm imports and the matching catalog pattern."
source_ids: [react-bits]
pattern_ids:
  - react-bits-ogl-shader-backgrounds
  - react-bits-self-pausing-shader-backgrounds
  - react-bits-three-r3f-backgrounds
  - react-bits-webgpu-backgrounds
  - react-bits-canvas-grid-backgrounds
  - react-bits-gsap-text-reveals
  - react-bits-lightweight-text-effects
  - react-bits-target-cursor
  - react-bits-webgl-cursor-trails
  - react-bits-scroll-driven-components
  - react-bits-bento-and-card-grids
  - react-bits-pointer-lit-cards
  - react-bits-animated-navigation-menus
  - react-bits-3d-image-galleries
  - react-bits-glass-surfaces
  - react-bits-micro-spring-controls
updated: "2026-10-09"
---

# React Bits component catalog

How the library is organised, installed and where it is fragile is in `knowledge/components/react-bits.md`. This guide lists 100 of the 215 components that matter most for building distinctive pages. The licence forbids redistributing the components, so every row points at the upstream file and describes the effect in our own words; no code is reproduced (`knowledge/implementation-recipes/react-bits-license-safe-usage.md`).

## How to read the tables

- **Effect** is paraphrased from the metadata in `react-bits:src/constants/Information.js` and checked against the source where a prop, dependency or behaviour is named. Several components were rebuilt on 2026-10-08 and 2026-10-09, so older descriptions elsewhere may not match.
- **Render** is read from the imports and context requests of the file: `WebGL (OGL)`, `WebGL (three)`, `WebGL (R3F)`, `WebGL (raw)` and `WebGPU` rows are GPU-driven and must be budgeted (`knowledge/implementation-recipes/react-bits-heavy-background-budget.md`). `Canvas 2D` and `DOM/CSS` rows do not need a GPU.
- **File** is the TS + Tailwind copy, a single file per component. The same component exists as `react-bits:src/ts-default/` (TS + CSS, with a `.css` file for most), `react-bits:src/content/` (JS + CSS) and `react-bits:src/tailwind/` (JS + Tailwind) under the same `<Category>/<Name>/` path. Props, defaults and live controls are in `<Category>/<Name>Demo.jsx` under `react-bits:src/demo/`.
- **npm imports** come from the import statements of the TS + Tailwind file, React excluded. The CSS twin can differ (ElasticSlider, Ballpit), so re-read the imports of the variant you install (`knowledge/implementation-recipes/react-bits-choose-variant-and-install.md`).
- **Pattern** is the catalog pattern that covers the family; an empty cell means no dedicated pattern.

## Backgrounds: shader and WebGL (GPU-driven)

All rows in this section run on the GPU. Treat each as a budgeted resource, see the heavy-background recipe.

| Component | Effect | Render | File (TS + Tailwind) | npm imports | Pattern |
|---|---|---|---|---|---|
| Aurora | Soft aurora ribbons blended from colour stops; its frame loop never pauses. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/Aurora/Aurora.tsx` | `ogl` | `react-bits-ogl-shader-backgrounds` |
| Balatro | Swirling warped colour field in the style of a card game menu, pointer reactive. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/Balatro/Balatro.tsx` | `ogl` | `react-bits-ogl-shader-backgrounds` |
| DarkVeil | Dim animated veil with optional noise, scanlines and warp; has a resolution-scale prop. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/DarkVeil/DarkVeil.tsx` | `ogl` | `react-bits-ogl-shader-backgrounds` |
| Galaxy | Starfield with parallax depth that reacts to the pointer. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/Galaxy/Galaxy.tsx` | `ogl` | `react-bits-ogl-shader-backgrounds` |
| LiquidChrome | Flowing reflective liquid-metal surface. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/LiquidChrome/LiquidChrome.tsx` | `ogl` | `react-bits-ogl-shader-backgrounds` |
| LightRays | Volumetric light beams fanning out from a chosen direction. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/LightRays/LightRays.tsx` | `ogl` | `react-bits-ogl-shader-backgrounds` |
| SoftAurora | Gentler aurora built from 3D noise and cosine gradient palettes. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/SoftAurora/SoftAurora.tsx` | `ogl` | `react-bits-ogl-shader-backgrounds` |
| Orb | Floating energy orb that reacts when hovered. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/Orb/Orb.tsx` | `ogl` | `react-bits-ogl-shader-backgrounds` |
| Grainient | Grainy gradient swirls with soft wave distortion; pauses offscreen. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/Grainient/Grainient.tsx` | `ogl` | `react-bits-ogl-shader-backgrounds` |
| Plasma | Raymarched plasma gradient; exposes render-scale, max-DPR and target-fps props, pauses offscreen, freezes under reduced motion. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/Plasma/Plasma.tsx` | `ogl` | `react-bits-self-pausing-shader-backgrounds` |
| PatternWaves | Halftone dots, lines or glyphs rolling like cloth, cursor ripples, `paused` prop. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/PatternWaves/PatternWaves.tsx` | `ogl` | `react-bits-self-pausing-shader-backgrounds` |
| MicroSlats | Wall of tiny slats that turns into a rolling sea in perspective, `paused` prop. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/MicroSlats/MicroSlats.tsx` | `ogl` | `react-bits-self-pausing-shader-backgrounds` |
| GhostFibers | Deep-blue recursive fibre field with luminous bands, `fps` and `paused` props. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/GhostFibers/GhostFibers.tsx` | `ogl` | `react-bits-self-pausing-shader-backgrounds` |
| Ferrofluid | Churning magnetic fluid traced by contour lines, the cursor acts as a magnet. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/Ferrofluid/Ferrofluid.tsx` | `ogl` | `react-bits-ogl-shader-backgrounds` |
| Topography | Living contour map with elevation-tinted lines; pauses offscreen. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/Topography/Topography.tsx` | `ogl` | `react-bits-ogl-shader-backgrounds` |
| GradientWaves | Raymarched sine waves rolling toward a hazy horizon; pauses offscreen. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/GradientWaves/GradientWaves.tsx` | `ogl` | `react-bits-ogl-shader-backgrounds` |
| WebThreads | Glowing sine threads converging on a bright point; pauses offscreen. | WebGL (OGL) | `react-bits:src/ts-tailwind/Backgrounds/WebThreads/WebThreads.tsx` | `ogl` | `react-bits-ogl-shader-backgrounds` |
| Iridescence | Stirrable iridescent liquid surface on raw WebGL2, `paused` prop, reduced-motion aware. | WebGL (raw) | `react-bits:src/ts-tailwind/Backgrounds/Iridescence/Iridescence.tsx` | none | `react-bits-self-pausing-shader-backgrounds` |
| Threads | Flowing threads that part around the cursor, raw WebGL2, `paused` prop. | WebGL (raw) | `react-bits:src/ts-tailwind/Backgrounds/Threads/Threads.tsx` | none | `react-bits-self-pausing-shader-backgrounds` |
| GridDistortion | Image that breaks into grid blocks under the cursor, raw WebGL2. | WebGL (raw) | `react-bits:src/ts-tailwind/Backgrounds/GridDistortion/GridDistortion.tsx` | none | `react-bits-self-pausing-shader-backgrounds` |
| Ballpit | Physics ball pit of coloured spheres; the TS variants also import GSAP. | WebGL (three) | `react-bits:src/ts-tailwind/Backgrounds/Ballpit/Ballpit.tsx` | `gsap`, `three` | `react-bits-three-r3f-backgrounds` |
| CRTWarp | Full-canvas CRT plasma with curvature, scanlines and bloom; `fps` and `paused` props. | WebGL (three) | `react-bits:src/ts-tailwind/Backgrounds/CRTWarp/CRTWarp.tsx` | `three` | `react-bits-three-r3f-backgrounds` |
| FloatingLines | 3D lines floating and bending toward the cursor. | WebGL (three) | `react-bits:src/ts-tailwind/Backgrounds/FloatingLines/FloatingLines.tsx` | `three` | `react-bits-three-r3f-backgrounds` |
| GridScan | 3D grid-room scan; optional webcam and gyro tilt; fetches face-api weights from a CDN by default. | WebGL (three) | `react-bits:src/ts-tailwind/Backgrounds/GridScan/GridScan.tsx` | `face-api.js`, `postprocessing`, `three` | `react-bits-three-r3f-backgrounds` |
| Hyperspeed | Night highway of light trails that warps while held, reduced-motion aware. | WebGL (three) | `react-bits:src/ts-tailwind/Backgrounds/Hyperspeed/Hyperspeed.tsx` | `three` | `react-bits-three-r3f-backgrounds` |
| LightPillar | Vertical pillar of glowing light with a `quality` prop. | WebGL (three) | `react-bits:src/ts-tailwind/Backgrounds/LightPillar/LightPillar.tsx` | `three` | `react-bits-three-r3f-backgrounds` |
| LiquidEther | Interactive fluid simulation, the largest background file (about 1,260 lines). | WebGL (three) | `react-bits:src/ts-tailwind/Backgrounds/LiquidEther/LiquidEther.tsx` | `three` | `react-bits-three-r3f-backgrounds` |
| PixelBlast | Pixel particle bursts with optional liquid post-processing; its offscreen-pause flag is never updated. | WebGL (three) | `react-bits:src/ts-tailwind/Backgrounds/PixelBlast/PixelBlast.tsx` | `postprocessing`, `three` | `react-bits-three-r3f-backgrounds` |
| Beams | Crossing animated ribbons; R3F canvas with an always-on frame loop. | WebGL (R3F) | `react-bits:src/ts-tailwind/Backgrounds/Beams/Beams.tsx` | `@react-three/drei`, `@react-three/fiber`, `three` | `react-bits-three-r3f-backgrounds` |
| Dither | Retro dithered noise field with a post-processing pass. | WebGL (R3F) | `react-bits:src/ts-tailwind/Backgrounds/Dither/Dither.tsx` | `@react-three/fiber`, `@react-three/postprocessing`, `postprocessing`, `three` | `react-bits-three-r3f-backgrounds` |
| Silk | Smooth silk-like waves with soft lighting; R3F canvas with an always-on frame loop. | WebGL (R3F) | `react-bits:src/ts-tailwind/Backgrounds/Silk/Silk.tsx` | `@react-three/fiber`, `three` | `react-bits-three-r3f-backgrounds` |
| AeroShards | WebGPU wind sculpture of foil shards; adaptive quality, `paused` and `onError` props. | WebGPU | `react-bits:src/ts-tailwind/Backgrounds/AeroShards/AeroShards.tsx` | `vgpu` | `react-bits-webgpu-backgrounds` |
| ShapeWaves | WebGPU field of triangles, circles or squares swelling along waves, optional text cutout. | WebGPU | `react-bits:src/ts-tailwind/Backgrounds/ShapeWaves/ShapeWaves.tsx` | `vgpu` | `react-bits-webgpu-backgrounds` |

## Backgrounds: canvas 2D and DOM (no shader)

| Component | Effect | Render | File (TS + Tailwind) | npm imports | Pattern |
|---|---|---|---|---|---|
| DotGrid | Dot grid whose dots are pushed with inertia by the cursor (GSAP InertiaPlugin on a canvas). | Canvas 2D | `react-bits:src/ts-tailwind/Backgrounds/DotGrid/DotGrid.tsx` | `gsap` | `react-bits-canvas-grid-backgrounds` |
| LetterGlitch | Matrix-style grid of cycling glitch letters. | Canvas 2D | `react-bits:src/ts-tailwind/Backgrounds/LetterGlitch/LetterGlitch.tsx` | none | `react-bits-canvas-grid-backgrounds` |
| GridMotion | Tilted drifting wall of tiles for images, words or JSX; pauses offscreen, reduced-motion aware. | DOM/CSS | `react-bits:src/ts-tailwind/Backgrounds/GridMotion/GridMotion.tsx` | none | `react-bits-canvas-grid-backgrounds` |

## Text animations

| Component | Effect | Render | File (TS + Tailwind) | npm imports | Pattern |
|---|---|---|---|---|---|
| SplitText | Splits text into chars, words or lines and reveals them once on scroll; `text` must be a string. | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/SplitText/SplitText.tsx` | `@gsap/react`, `gsap` | `react-bits-gsap-text-reveals` |
| ScrollReveal | Words unblur and fade in as the block scrolls into view. | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/ScrollReveal/ScrollReveal.tsx` | `gsap` | `react-bits-gsap-text-reveals` |
| ScrollFloat | Letters float up into place while scrolling. | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/ScrollFloat/ScrollFloat.tsx` | `gsap` | `react-bits-gsap-text-reveals` |
| Shuffle | Characters shuffle before settling, scroll-triggered. | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/Shuffle/Shuffle.tsx` | `@gsap/react`, `gsap` | `react-bits-gsap-text-reveals` |
| TextType | Typewriter effect with a blinking caret and adjustable cadence. | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/TextType/TextType.tsx` | `gsap` | `react-bits-gsap-text-reveals` |
| ScrambledText | Letters scramble near the pointer and resolve back. | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/ScrambledText/ScrambledText.tsx` | `gsap` | `react-bits-gsap-text-reveals` |
| BlurText | Words or letters resolve from blur once in view. | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/BlurText/BlurText.tsx` | `motion` | `react-bits-lightweight-text-effects` |
| DecryptedText | Random glyphs cycle until the real text appears; ships screen-reader text. | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/DecryptedText/DecryptedText.tsx` | `motion` | `react-bits-lightweight-text-effects` |
| ShinyText | Sheen sweeping across text; triggers include continuous, hover and scroll, can follow the pointer. | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/ShinyText/ShinyText.tsx` | none | `react-bits-lightweight-text-effects` |
| GradientText | Animated gradient fill (linear, flowing or conic) with optional glow. | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/GradientText/GradientText.tsx` | none | `react-bits-lightweight-text-effects` |
| CountUp | Animated number counter with formatting and decimals. | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/CountUp/CountUp.tsx` | `motion` | `react-bits-lightweight-text-effects` |
| RotatingText | Cycles through phrases with 3D flip transitions. | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/RotatingText/RotatingText.tsx` | `motion` | `react-bits-lightweight-text-effects` |
| ScrollVelocity | Marquee text whose speed follows the scroll velocity. | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/ScrollVelocity/ScrollVelocity.tsx` | `motion` | `react-bits-lightweight-text-effects` |
| VariableProximity | Letter weight shifts with the pointer distance (needs a variable font). | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/VariableProximity/VariableProximity.tsx` | `motion` | `react-bits-lightweight-text-effects` |
| TextPressure | Variable-font letters change width and weight near the pointer; loads a Google font by default. | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/TextPressure/TextPressure.tsx` | none | `react-bits-lightweight-text-effects` |
| GlitchText | RGB-split glitch effect; the Tailwind variant needs keyframes added to the Tailwind config. | DOM/CSS | `react-bits:src/ts-tailwind/TextAnimations/GlitchText/GlitchText.tsx` | none | `react-bits-lightweight-text-effects` |
| ASCIIText | Waving text drawn with ASCII glyphs that tilts toward the pointer (WebGL). | WebGL (raw) | `react-bits:src/ts-tailwind/TextAnimations/ASCIIText/ASCIIText.tsx` | none |  |
| WarpText | Text bent and refracted around the pointer by a shader. | WebGL (OGL) | `react-bits:src/ts-tailwind/TextAnimations/WarpText/WarpText.tsx` | `ogl` |  |

## Animations: cursor and pointer effects

| Component | Effect | Render | File (TS + Tailwind) | npm imports | Pattern |
|---|---|---|---|---|---|
| TargetCursor | Custom cursor whose corners lock onto elements matching a selector; hides the native cursor by default. | DOM/CSS | `react-bits:src/ts-tailwind/Animations/TargetCursor/TargetCursor.tsx` | `gsap` | `react-bits-target-cursor` |
| Crosshair | Crosshair cursor with live coordinates that frames hovered links and buttons. | Canvas 2D | `react-bits:src/ts-tailwind/Animations/Crosshair/Crosshair.tsx` | none | `react-bits-target-cursor` |
| GlowCursor | Shader light trail that follows the pointer. | WebGL (OGL) | `react-bits:src/ts-tailwind/Animations/GlowCursor/GlowCursor.tsx` | `ogl` | `react-bits-webgl-cursor-trails` |
| SplashCursor | Fluid-simulation splashes under the pointer (one of the largest files, about 1,300 lines). | WebGL (raw) | `react-bits:src/ts-tailwind/Animations/SplashCursor/SplashCursor.tsx` | none | `react-bits-webgl-cursor-trails` |
| GhostCursor | Translucent trailing ghost of the pointer with bloom passes. | WebGL (three) | `react-bits:src/ts-tailwind/Animations/GhostCursor/GhostCursor.tsx` | `three` | `react-bits-webgl-cursor-trails` |
| BlobCursor | Liquid-metal blob cursor that stretches and drips. | WebGL (three) | `react-bits:src/ts-tailwind/Animations/BlobCursor/BlobCursor.tsx` | `three` | `react-bits-webgl-cursor-trails` |
| ImageTrail | Trail of images following the pointer, several built-in variants. | DOM/CSS | `react-bits:src/ts-tailwind/Animations/ImageTrail/ImageTrail.tsx` | `gsap` |  |
| ClickSpark | Spark burst at every click position. | Canvas 2D | `react-bits:src/ts-tailwind/Animations/ClickSpark/ClickSpark.tsx` | none |  |
| Magnet | Wrapper that eases its child toward the pointer inside a padding radius, using CSS transitions. | DOM/CSS | `react-bits:src/ts-tailwind/Animations/Magnet/Magnet.tsx` | none |  |
| GlareHover | Moving glare highlight on any element while hovered. | DOM/CSS | `react-bits:src/ts-tailwind/Animations/GlareHover/GlareHover.tsx` | none | `react-bits-pointer-lit-cards` |
| StarBorder | A star travelling around the outline of any button or card. | Canvas 2D | `react-bits:src/ts-tailwind/Animations/StarBorder/StarBorder.tsx` | none |  |
| ElectricBorder | Jittery electric-arc border with glow. | Canvas 2D | `react-bits:src/ts-tailwind/Animations/ElectricBorder/ElectricBorder.tsx` | none |  |
| Noise | Film-grain overlay from fine grain to dust and TV static; `fps` prop, reduced-motion aware. | Canvas 2D | `react-bits:src/ts-tailwind/Animations/Noise/Noise.tsx` | none |  |
| LogoLoop | Seamless looping logo marquee that pauses on hover, reduced-motion aware. | DOM/CSS | `react-bits:src/ts-tailwind/Animations/LogoLoop/LogoLoop.tsx` | none |  |

## Animations: scroll and reveal

| Component | Effect | Render | File (TS + Tailwind) | npm imports | Pattern |
|---|---|---|---|---|---|
| AnimatedContent | Wrapper animating any children on scroll or mount (direction, distance, easing). | DOM/CSS | `react-bits:src/ts-tailwind/Animations/AnimatedContent/AnimatedContent.tsx` | `gsap` | `react-bits-scroll-driven-components` |
| FadeContent | Directional fade or slide entrance wrapper with threshold activation. | DOM/CSS | `react-bits:src/ts-tailwind/Animations/FadeContent/FadeContent.tsx` | `gsap` | `react-bits-scroll-driven-components` |
| ScrollExpand | Media frame that grows to full bleed while scrolling through the viewport. | DOM/CSS | `react-bits:src/ts-tailwind/Animations/ScrollExpand/ScrollExpand.tsx` | none | `react-bits-scroll-driven-components` |
| GradualBlur | Progressive blur that clears on scroll for a cinematic reveal. | DOM/CSS | `react-bits:src/ts-tailwind/Animations/GradualBlur/GradualBlur.tsx` | none | `react-bits-scroll-driven-components` |
| MetallicPaint | Liquid-metal shader applied to an image or SVG shape passed as `imageSrc`. | WebGL (raw) | `react-bits:src/ts-tailwind/Animations/MetallicPaint/MetallicPaint.tsx` | none |  |
| LaserFlow | Beam of light pouring over content with drifting smoke and dust. | WebGL (raw) | `react-bits:src/ts-tailwind/Animations/LaserFlow/LaserFlow.tsx` | none |  |

## Components: navigation

| Component | Effect | Render | File (TS + Tailwind) | npm imports | Pattern |
|---|---|---|---|---|---|
| PillNav | Pill-shaped nav with a sliding highlight; imports react-router-dom's Link for internal hrefs. | DOM/CSS | `react-bits:src/ts-tailwind/Components/PillNav/PillNav.tsx` | `gsap`, `react-router-dom` | `react-bits-animated-navigation-menus` |
| StaggeredMenu | Slide-in menu with staggered layered panels; default logo points at the upstream repo. | DOM/CSS | `react-bits:src/ts-tailwind/Components/StaggeredMenu/StaggeredMenu.tsx` | `gsap` | `react-bits-animated-navigation-menus` |
| BubbleMenu | Floating circular toggle that expands into staggered bubble links. | DOM/CSS | `react-bits:src/ts-tailwind/Components/BubbleMenu/BubbleMenu.tsx` | `gsap` | `react-bits-animated-navigation-menus` |
| CardNav | Expandable bar revealing card panels with nested links. | DOM/CSS | `react-bits:src/ts-tailwind/Components/CardNav/CardNav.tsx` | `gsap`, `react-icons` | `react-bits-animated-navigation-menus` |
| FlowingMenu | Full-width menu whose hover highlight flows like liquid. | DOM/CSS | `react-bits:src/ts-tailwind/Components/FlowingMenu/FlowingMenu.tsx` | `gsap` | `react-bits-animated-navigation-menus` |
| GooeyNav | Active-item indicator that morphs between items as a gooey blob. | DOM/CSS | `react-bits:src/ts-tailwind/Components/GooeyNav/GooeyNav.tsx` | none | `react-bits-animated-navigation-menus` |
| Dock | macOS-style dock with magnification, badges and context menu; keyboard and reduced-motion aware. | DOM/CSS | `react-bits:src/ts-tailwind/Components/Dock/Dock.tsx` | none | `react-bits-animated-navigation-menus` |

## Components: cards, grids, galleries and glass

| Component | Effect | Render | File (TS + Tailwind) | npm imports | Pattern |
|---|---|---|---|---|---|
| MagicBento | Bento grid with spotlight, border glow, particles and tilt; tile content is hard-coded in the file. | DOM/CSS | `react-bits:src/ts-tailwind/Components/MagicBento/MagicBento.tsx` | `gsap` | `react-bits-bento-and-card-grids` |
| ChromaGrid | Grid of greyscale tiles that regain colour under the pointer; takes an `items` prop. | DOM/CSS | `react-bits:src/ts-tailwind/Components/ChromaGrid/ChromaGrid.tsx` | `gsap` | `react-bits-bento-and-card-grids` |
| Masonry | Responsive masonry layout with animated reflow; `items` is required. | DOM/CSS | `react-bits:src/ts-tailwind/Components/Masonry/Masonry.tsx` | `gsap` | `react-bits-bento-and-card-grids` |
| SpotlightCard | Card lit by a pointer-following spotlight that can be shared across a grid. | DOM/CSS | `react-bits:src/ts-tailwind/Components/SpotlightCard/SpotlightCard.tsx` | none | `react-bits-pointer-lit-cards` |
| TiltedCard | 3D perspective tilt that follows the pointer. | DOM/CSS | `react-bits:src/ts-tailwind/Components/TiltedCard/TiltedCard.tsx` | `motion` | `react-bits-pointer-lit-cards` |
| BorderGlow | Mesh-gradient border glow that follows the cursor direction. | DOM/CSS | `react-bits:src/ts-tailwind/Components/BorderGlow/BorderGlow.tsx` | none | `react-bits-pointer-lit-cards` |
| CircularGallery | Orbiting circular image gallery rendered with OGL; ships remote placeholder images. | WebGL (OGL) | `react-bits:src/ts-tailwind/Components/CircularGallery/CircularGallery.tsx` | `ogl` | `react-bits-3d-image-galleries` |
| DomeGallery | Images placed on a hemisphere you drag around, using DOM 3D transforms. | DOM/CSS | `react-bits:src/ts-tailwind/Components/DomeGallery/DomeGallery.tsx` | `@use-gesture/react` | `react-bits-3d-image-galleries` |
| InfiniteMenu | Draggable sphere of image tiles with title and link (raw WebGL2, keyboard support after rebuild). | WebGL (raw) | `react-bits:src/ts-tailwind/Components/InfiniteMenu/InfiniteMenu.tsx` | none | `react-bits-3d-image-galleries` |
| ScrollStack | Overlapping cards that stack as you scroll; creates its own Lenis instance. | DOM/CSS | `react-bits:src/ts-tailwind/Components/ScrollStack/ScrollStack.tsx` | `lenis` | `react-bits-scroll-driven-components` |
| GlassSurface | Apple-style glass panel using SVG displacement filters, with feature detection and fallbacks. | DOM/CSS | `react-bits:src/ts-tailwind/Components/GlassSurface/GlassSurface.tsx` | none | `react-bits-glass-surfaces` |
| FluidGlass | Glass lens, bar or cube over a 3D scene (R3F); expects GLB models at absolute public paths. | WebGL (R3F) | `react-bits:src/ts-tailwind/Components/FluidGlass/FluidGlass.tsx` | `@react-three/drei`, `@react-three/fiber`, `maath`, `three` | `react-bits-glass-surfaces` |
| SpecularButton | Glass button with a shader specular rim light that follows the cursor. | WebGL (OGL) | `react-bits:src/ts-tailwind/Components/SpecularButton/SpecularButton.tsx` | `ogl` | `react-bits-glass-surfaces` |

## Micro-interactions

| Component | Effect | Render | File (TS + Tailwind) | npm imports | Pattern |
|---|---|---|---|---|---|
| HoldButton | Hold-to-confirm button with a rising liquid fill that snaps back on early release. | DOM/CSS | `react-bits:src/ts-tailwind/Micro/HoldButton/HoldButton.tsx` | none | `react-bits-micro-spring-controls` |
| SlideCommit | Slide-to-confirm handle with pending, success and failure states for an async action. | DOM/CSS | `react-bits:src/ts-tailwind/Micro/SlideCommit/SlideCommit.tsx` | `@hugeicons/core-free-icons`, `@hugeicons/react`, `motion` | `react-bits-micro-spring-controls` |
| SquishSwitch | Drag-scrubbable switch whose thumb stretches with speed. | DOM/CSS | `react-bits:src/ts-tailwind/Micro/SquishSwitch/SquishSwitch.tsx` | `motion` | `react-bits-micro-spring-controls` |
| CodeSlots | One-time-code input where a hidden real input owns focus, paste and autofill. | DOM/CSS | `react-bits:src/ts-tailwind/Micro/CodeSlots/CodeSlots.tsx` | `@hugeicons/core-free-icons`, `@hugeicons/react`, `motion` | `react-bits-micro-spring-controls` |
| PromptBar | Chat composer with @ sources, / commands, model picker, dictation and attachments. | Canvas 2D | `react-bits:src/ts-tailwind/Micro/PromptBar/PromptBar.tsx` | `@hugeicons/core-free-icons`, `@hugeicons/react`, `motion` |  |
| SwipeToast | Swipe-to-dismiss toast with a burning timer fuse and inline mode. | DOM/CSS | `react-bits:src/ts-tailwind/Micro/SwipeToast/SwipeToast.tsx` | `@hugeicons/core-free-icons`, `@hugeicons/react`, `motion` |  |


## Choosing quickly

| Need | Start with | Cost and caveat |
|---|---|---|
| Calm, dark hero atmosphere | Aurora, SoftAurora, Silk, GradientWaves, Grainient | GPU; Aurora, SoftAurora and Silk never pause offscreen |
| Texture without a GPU | DotGrid, LetterGlitch, GridMotion, Noise overlay | canvas or DOM; DotGrid and LetterGlitch loop forever |
| Pointer-reactive backdrop | PatternWaves, MicroSlats, Ferrofluid, Threads, Iridescence | GPU; all five expose `paused`, Ferrofluid has no offscreen pause |
| One-off spectacle | LiquidEther, Hyperspeed, AeroShards, GridScan | judged heavy (large shaders, a simulation or extra downloads); use once per page |
| Headline reveal | SplitText, BlurText, ScrollReveal, ShinyText, GradientText | DOM; add your own reduced-motion branch for the first three |
| Hacker or glitch type | DecryptedText, ScrambledText, GlitchText, LetterGlitch | check flicker against flashing guidance |
| Cursor personality | TargetCursor, Crosshair (DOM or canvas), GlowCursor, BlobCursor (GPU) | pick one; gate on a fine pointer; TargetCursor hides the native cursor by default |
| Section entrance | AnimatedContent, FadeContent | hides content until JS runs; keep it off the LCP element |
| Navigation | PillNav, StaggeredMenu, CardNav, FlowingMenu, Dock | PillNav needs a React Router context; FlowingMenu has no ARIA in the Tailwind copies |
| Feature grid | MagicBento, ChromaGrid, Masonry, SpotlightCard | MagicBento tile content lives in the file |
| Image showcase | CircularGallery, DomeGallery, InfiniteMenu | placeholders are remote images; CircularGallery and DomeGallery expose one ARIA attribute each |
| Glass look | GlassSurface, SpecularButton, FluidGlass | GlassSurface has no WebGL but backdrop filters can be costly on large areas; FluidGlass needs GLB assets |
| Form micro-interactions | HoldButton, SlideCommit, SquishSwitch, CodeSlots | DOM; all 34 Micro components set ARIA and reduced-motion handling |

## Not in the tables

Remaining components, by folder name (all exist in the four variants):

- Backgrounds: AcidSquares, ColorBends, DotField, EvilEye, FaultyTerminal, GradientBlinds, LightTunnel, Lightfall, Lightning, LineWaves, MoltenMetal, Particles, PixelSnow, PlasmaWave, Prism, PrismaticBurst, Radar, RippleGrid, Scanner, ShapeGrid, SideRays, SlicedWaves, Waves.
- TextAnimations: CircularText, CurvedLoop, DepthText, EchoText, FallingText, FoldText, FuzzyText, MaskedHeading, ParticleText, SplitFlapText, StrokeText, TechText, TextCursor, TextLoop, TrueFocus.
- Animations: Antigravity, CrystalizedBall, Cubes, CursorGrid, DitherVeil, ElasticMesh, ElectricLogo, HalftoneReveal, MagicRings, MagnetLines, MetaBalls, OrbitImages, PixelSwap, PixelTrail, PixelTransition, Ribbons, RippleDistortion, ShapeBlur, StickerPeel, Strands, SwarmCursor.
- Components: AccordionGallery, AnimatedList, BounceCards, CardSwap, Carousel, CircularCarousel, Counter, CurvedInput, DecayCard, DepthCarousel, DriftWall, ElasticSlider, FlexCarousel, FlyingPosters, Folder, GlassIcons, HoloCard, InfiniteSpiral, Lanyard, LineSidebar, ModelViewer, MorphSlider, OptionWheel, PixelCard, ProfileCard, ReflectiveCard, Stack, Stepper.
- Micro: BellToggle, BranchedMenu, CallChip, CometDial, DodgeField, FlipCard, FolderFloat, FuseButton, GlideSelect, JellyRadio, LatticeLoader, PaperCrumple, PeekRating, PulseHeart, RefineFrame, RubberSegment, ScrubField, Shredder, SlingButton, SloshGauge, SpringCheck, StatusMark, SwipeRow, TearTicket, ThoughtLine, VoicePill, WakeSlider, WarmTooltip.

Notable among them: Lanyard (rebuilt with three only, no physics package), ModelViewer (R3F, `frameloop` on demand), HoloCard and DecayCard (raw WebGL cards), Folder, Stack and BounceCards (card piles), PaperCrumple and Shredder (heavier Micro pieces, three and canvas), ReflectiveCard (webcam on mount).
