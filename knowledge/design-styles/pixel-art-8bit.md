---
title: "Pixel art and 8-bit"
kind: design-style
summary: "Hard-edged sprites, small fixed palettes, bitmap type and stepped corners inspired by 8-bit and 16-bit games. Covers integer scaling, image-rendering, palette contrast numbers, step-timed sprite animation, pixel fonts for display only and why a pixelate filter is not pixel art."
source_ids: [fancy]
pattern_ids: [style-pixel-art-8bit]
updated: "2026-10-09"
---

# Pixel art and 8-bit

Pixel art is the visual language of early consoles and home computers: images built from visible square pixels, a handful of colours, stepped diagonals and chunky bitmap lettering. On the web it signals play, nostalgia and craft, and it suits products with a game, indie or maker identity. Its rules come from constraints: a fixed pixel grid, a small palette, and nothing smoother than the grid allows. Break the constraints (blurry scaling, gradients, mixed pixel sizes) and it reads as a cheap filter.

## Visual characteristics
- A single pixel size across the whole composition. Sprites are authored at small sizes (16 or 32 px square) and shown at a whole-number multiple.
- Palettes of 4 to 16 colours with deliberate ramps; shading by hue shift, not by smooth gradient. Optional ordered dither (checkerboard or Bayer patterns) for tone.
- Stepped corners on panels and buttons, 2-4 px outlines, inner highlights one pixel wide, drop shadows as hard offset blocks.
- Sprites and tiles for icons, characters, items and backgrounds; parallax layers; HUD elements such as hearts, bars and coin counters.
- Bitmap or pixel-grid display type, with a calmer font for reading.

## When it fits, when it does not
- Fits: games and game-adjacent products, indie studios, developer and maker communities, retro-computing nostalgia, events and festivals, playful loading, 404 and empty states, achievements and gamified progress, game jams, learning tools for children.
- Poor fit: banking and healthcare flows, long-form reading, information-dense tables, luxury and formal brands, accessibility-critical content set in a pixel font.
- Supporting influences that work: retro-vintage (for era-consistent type and palettes), cyberpunk and vaporwave for neon variants, grain-and-texture (a CRT or dither layer), isometric-illustration for 2:1 isometric scenes, neo-brutalism for hard shadows. Avoid glassmorphism, liquid-materials, aurora-gradient-mesh and high-fashion-luxury.

## Typography
- Pixel fonts such as Press Start 2P, Silkscreen, VT323 and Pixelify Sans are display faces: titles, buttons, scores and short labels, 3-6 words at a time.
- Set a pixel font only at sizes that match its grid. Press Start 2P is built on an 8 px grid, so use 8, 16, 24 or 32 px; odd sizes blur or distort the glyphs. Turn off letter-spacing tweaks and keep line height at 1.4-1.6 because glyphs are tall and dense.
- Body copy and anything longer than a sentence goes in a readable text face (a clean sans or mono at 16-18 px). Large blocks of bitmap type are tiring and poorly suited to dyslexic readers.
- Provide real text, not a screenshot of text; pixel fonts at 8-12 px are unreadable on small phones, so raise the base size on narrow screens.

## Colour
- Night variant: cream #F2E9D0 on ink #14121F is 15.26:1; amber #FFB84D 10.75:1; green #5BD97A 10.26:1; pink #FF6B8B 6.80:1; periwinkle #7C8CFF 6.21:1. Raw blue #4C6FFF is only 4.42:1 on ink, and white text on it is 4.18:1, so use blue for fills with ink text (ink on #7C8CFF is 6.21:1).
- Panels: #231F3A under cream text is 13.05:1 and under muted #8F89B5 is 4.83:1. Borders in #8F89B5 against the ink ground reach 5.65:1; a darker #5A5388 border is only 2.66:1 and fails for field outlines.
- Button faces: ink text on amber #FFB84D is 10.75:1. The darker shade tone under it (#C98A1F) is a bevel detail, not text colour.
- LCD variant: ink #1F2A1C on #C4D3A4 is 9.39:1. A mid-tone #4F6B3D on that ground is only 3.77:1, fine for large shapes but not for small text; use #3C5230 (5.41:1) for secondary text.
- Fix the palette in tokens and use nothing outside it, including shadows and hover states. Gradients, soft shadows and opacity blends break the illusion.

## Composition and layout
- Snap everything to the pixel unit: sizes, padding and borders in multiples of one CSS variable (for example `--px: 4px`). Avoid percentage-based centring that lands on half pixels, which makes edges shimmer.
- Panel and dialog layouts (title bar, inventory grids, health bars) work well as HUD metaphors; keep the information hierarchy plain.
- Backgrounds from tiled sprites or a few parallax strips, at the same pixel size as the foreground. Do not mix 2x and 5x art on one screen.
- Responsive: scale by whole numbers (4x on desktop, 3x or 2x on phones) rather than a fluid percentage; crop scenes instead of resampling them.

## Interaction and motion
- Animate in steps. Sprite frames use `steps(n)` timing at 6-12 frames per second, hover states swap a frame or offset a hard shadow by one pixel unit, and presses move a button down by its shadow height.
- No easing curves on pixel elements, no motion blur, no sub-pixel `transform` values; translate by whole pixel units.
- Typewriter reveals and blinking cursors at 2 Hz or below are in character. Cursor trails of square cells are a natural effect but create many nodes (see below).
- Reduced motion: show a single sprite frame, stop parallax and idle loops, and let state changes be instant.

## Accessibility cautions
- Sprites that convey information (an item, a status, a character class) need alt text; decorative scenery gets `alt=""` or `aria-hidden="true"`. Never draw words into a sprite.
- `image-rendering: pixelated` only affects scaling; it does not make a tiny 8 px glyph readable. Check font sizes at 200% zoom.
- Flashing: blink and hit-flash effects must stay below three flashes per second and avoid large saturated areas; scanline or CRT overlays over text lower contrast, so keep text on flat panels.
- Dither patterns behind text produce visual vibration; use a flat colour behind copy.
- Forced-colors mode removes `box-shadow` and replaces background colours. Stepped borders made from `box-shadow` disappear, so add a real `border` there and make sure focus rings are `outline`, not shadow.
- Interactive sprites at 4x are comfortable targets, but a 16 px icon at 1x falls below the 24 px target-size guideline unless spacing compensates; scale it or pad the hit area.

## Common mistakes
- Bilinear scaling that blurs the art (missing `image-rendering`) or non-integer scale factors that make pixels uneven.
- Mixed pixel sizes, smooth gradients, anti-aliased vector shapes and soft shadows beside sprites.
- A pixel font for body copy, at off-grid sizes, or with added letter-spacing and text-shadow glows.
- A pixelate or mosaic filter slapped on a photo and called pixel art; one div per pixel for large images.
- Retina blur from exporting sprites at the wrong size and letting the browser resample them.

## Typical mistakes of AI-generated versions
- Image models give "pixel art" with mismatched pixel sizes, anti-aliased edges, hundreds of near-duplicate colours and garbled lettering; code versions use a pixel font everywhere, a purple-to-cyan neon gradient, `border-radius` on supposedly stepped panels and a sprite scaled to 3.5x with default smoothing.

## How to build it
- Pattern: `style-pixel-art-8bit`. Tokens: pixel unit, 8-16 palette colours, one pixel display font, one text font, sprite sheet size and frame rate. The recipe is original.

```css
.sprite { width: 64px; height: 64px; background: url(walk.png) 0 0 / 256px 64px; /* 4 frames of 16 px art at 4x */
  image-rendering: crisp-edges; image-rendering: pixelated; animation: walk .5s steps(4) infinite; }
@keyframes walk { to { background-position-x: -256px } }
.px-btn { font: 16px/1 "Press Start 2P", monospace; color: #14121F; background: #FFB84D; border: 0; padding: 14px 18px;
  box-shadow: 0 -4px #14121F, 0 4px #14121F, -4px 0 #14121F, 4px 0 #14121F, inset 0 -4px #C98A1F; }
.px-btn:active { transform: translateY(4px); }
.px-btn:focus-visible { outline: 4px solid #F2E9D0; outline-offset: 8px; }
@media (prefers-reduced-motion: reduce) { .sprite { animation: none } }
@media (forced-colors: active) { .px-btn { border: 4px solid ButtonText; box-shadow: none } }
```

- For canvas scenes, draw at the low native resolution (for example 320 x 180), set `ctx.imageSmoothingEnabled = false`, and scale the element up with CSS plus `image-rendering: pixelated`. Keep the backing size small instead of drawing a huge canvas and filling it with big squares.
- Related local pieces, both reference only:
  - `fancy:src/fancy/components/filter/pixelate-svg-filter.tsx` is an SVG filter (convolution, tile and morphology primitives, with a `size` prop defaulting to 16) that coarsens whatever it is applied to into square blocks. It is a mosaic effect for reveals and hovers, not authentic pixel art, because it ignores palette and grid. Its docs state Safari is not supported, so provide a fallback.
  - `fancy:src/fancy/components/background/pixel-trail.tsx` lays out a grid of square cells that flash and fade under the pointer. It renders one animated div per cell, so use a coarse cell size, keep it behind content and do not mount it for reduced-motion or touch users.

## Sources
Original guidance written for this project. fancy is MIT-licensed and cited as reference only; nothing was copied from it.
