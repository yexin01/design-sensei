---
title: "Maximalism"
kind: design-style
summary: "More-is-more design built from layered collage, pattern on pattern, saturated clashing colour and mixed type at extreme scales, held together by a hidden grid, rest areas and a clear reading path. Includes the legibility, motion and weight risks."
source_ids: [fancy]
pattern_ids: [style-maximalism]
updated: "2026-10-09"
---

# Maximalism

Maximalism is abundance with control. Layered imagery, ornament, pattern, saturated colour and type at extreme sizes are combined on purpose, but a hidden grid, a short reading path and a few calm areas keep the page from collapsing into noise. The test is simple: a first-time visitor must still find the message and the next action within a few seconds.

## Visual characteristics
- Collage: overlapping cut-outs, stickers, textures and patterns with changes of scale and rotation.
- Saturated, clashing palettes with a dominant hue and deliberate accents; pattern sitting on pattern.
- Two or three type families at extreme sizes; outlined, stacked, rotated or path-bound display type.
- Ornament as content: borders, badges, tickers, repeating motifs.
- High information and event density per screen.

## When it fits, when it does not
- Fits: streetwear and fashion drops, music and festival sites, creative studios, children's products, launch microsites, editorial specials, illustrator portfolios.
- Poor fit: tools, forms, checkout, dashboards, documentation, health and finance, long-session reading, low-bandwidth audiences.
- Supporting influences that work: retro-vintage, y2k, vaporwave, kinetic-typography, grain-and-texture, generative-design. Avoid minimalism, swiss-international-typographic and dark-technical-developer-tools.

## Typography
- Two or three families with separate jobs: an expressive display face (Bricolage Grotesque, Syne, Unbounded), a plain text face (Inter, DM Sans, Source Serif 4), and optionally a mono or script for accents. At least 90% of reading text uses the plain face.
- Scale extremes: display 10-20vw, body 14-18 px. Display line-height 0.8-0.95 for stacked words.
- Outlined text (`-webkit-text-stroke`), rotation and text on paths only for five words or fewer, never for paragraphs.
- Variable fonts with a width axis give a wide expressive range from one file.
- Body copy always sits on a solid or near-solid ground.

## Colour
- One dominant hue for roughly half the surface, two secondaries, one accent, and a neutral "rest" colour (cream or black) for reading blocks.
- Clash by hue and saturation but keep a clear light and dark split so foreground reads. Convert the page to greyscale as a quick hierarchy test.
- Text on a saturated fill must be computed: black on #FF3B30 is 5.9:1, white on it is 3.55:1 (large text only).
- Patterns behind text need low internal contrast (about 1.5:1 between the pattern's colours) or a solid label under the words.

## Composition and layout
- Layers on a hidden grid in four or five z-index tiers (pattern, collage, content, stickers). Prefer CSS Grid areas with overlapping cells to absolute positioning so the layout stays responsive.
- Provide at least one calm region per viewport for the headline and the call to action.
- Alternate dense screens with plain "rest" screens as you scroll.
- On phones, recompose rather than shrink: keep two or three overlaps and drop purely decorative layers below about 640 px.
- Cut-outs as transparent WebP, AVIF or SVG, lazy-loaded below the fold, with reserved dimensions to avoid layout shift.

## Interaction and motion
- One hero motion at a time. Everything else static or very slow: ticker bands on 20-60 s loops, cursor parallax on two or three layers, 200 ms wiggles on sticker hover.
- Give every loop longer than five seconds a pause control. Reduced motion: stop tickers, freeze parallax, remove wiggles, keep the layout.
- Optional play features (draggable stickers, sounds) default to off.

## Accessibility cautions
- The main risk is cognitive load. Keep a real heading outline and a skip link, and never encode meaning only in decorative layers.
- Measure text contrast at the worst point of the background, not the average.
- Parallax and tickers can trigger vestibular symptoms; auto-moving content over five seconds needs a stop control (WCAG 2.2.2).
- Mark decoration `aria-hidden` and keep decorative elements out of the tab order.
- Weight is an access issue too: multi-megabyte collages exclude slow connections. Budget the above-the-fold images.

## Common mistakes
- Every element at the same loudness, so nothing leads the eye.
- No rest areas, which produces fatigue within seconds.
- Text on busy pattern; five or more type families with no roles.
- A desktop collage scaled down on a phone; huge PNGs; layout shift as images load.

## Typical mistakes of AI-generated versions
- Gradients, glow, glass and emoji piled onto a standard template: texture without composition.
- Every layer animated at once with the same easing; paragraphs set over busy images.
- Generic Memphis-style shapes scattered with no rhythm or hidden grid.

## How to build it
- Pattern: `style-maximalism`. Build the calm layout first (grid, type, content), then add decoration in tiers, then check at greyscale and at 320 px.
- Ticker bands: `fancy:src/fancy/components/blocks/simple-marquee.tsx` (Motion-based; options include `direction`, `baseVelocity` (5 px/s default), `slowdownOnHover`, `draggable`, `repeat`). It has no pause control or reduced-motion branch, so add both.
- Inline media between two text runs: `fancy:src/fancy/components/blocks/media-between-text.tsx` (`firstText`, `secondText`, `mediaUrl`, `mediaType` image or video).
- Cursor depth parallax: `fancy:src/fancy/components/image/parallax-floating.tsx` (`sensitivity`, `easingFactor`); also without a reduced-motion path.
- A shared grain overlay (see grain-and-texture) unifies mismatched layers cheaply.

## Sources
Original guidance written for this project. fancy is MIT-licensed and cited as reference only.
