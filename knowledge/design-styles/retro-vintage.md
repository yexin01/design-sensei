---
title: "Retro and vintage"
kind: design-style
summary: "Nostalgia built from print and analogue production logic: spot-colour palettes on paper, era-specific type, badges and stamps, halftone and grain, mechanical motion. Explains how to commit to one era, keep text legible and avoid the sepia-filter shortcut."
source_ids: [react-bits, taste-skill]
pattern_ids: [style-retro-vintage]
updated: "2026-10-09"
---

# Retro and vintage

Retro design borrows the logic of printing and analogue media from roughly the 1940s to the 1990s: limited spot inks on paper, overprint, halftone dots, letterpress type, enamel badges, early computing. It works when the production logic is respected (flat inks, hard shadows, one era) and fails when it is reduced to a brown filter. It is distinct from y2k, which is about glossy digital optimism.

## Visual characteristics
- Three to five spot colours on cream or kraft paper; overlapping inks combine with multiply and sometimes sit slightly out of register.
- Era-specific lettering: slab and soft serifs, condensed poster sans, script for short accents, bitmap or mono type for computing nostalgia.
- Badges, stamps, ticket shapes, ribbons and double-rule frames.
- Print artefacts used lightly: halftone, paper grain, rough edges.
- Poster-like, centred or framed compositions with ornamental dividers.

## When it fits, when it does not
- Fits: food and drink, craft and hospitality, record labels and venues, events, publications, toys, heritage brands, retro games.
- Poor fit: products whose promise is novelty or speed (AI, infrastructure), medical or financial services, long-form reading set in faux-distressed type, low-power devices if heavy texture overlays are stacked.
- Supporting influences that work: grain-and-texture, editorial, organic-tactile, art-deco, maximalism. Avoid futurism, glassmorphism and dark-technical-developer-tools.

## Typography
- Choose one era and stay in it. 1950s: script plus condensed sans. 1960s-70s: soft serifs (Fraunces with its SOFT axis, Young Serif) and slabs (Zilla Slab, Roboto Slab, Arvo). 1980s computing: monospace and bitmap faces (VT323, Press Start 2P), used for labels and display only.
- Display 56-120 px; slab and soft serifs at tracking -0.01 to -0.02em; condensed poster sans uppercase at +0.02em; mono labels at +0.05em.
- Body set in a robust text face (Source Serif 4, Libre Baskerville, or a humanist sans) at 17-19 px. Never set body text in a distressed or display face.
- Apply rough-edge or distress treatments to display only and keep counters open. Use old-style numerals (`onum`) where the font offers them.

## Colour
- Ink on paper: #2B2118 on #F3E9D2 is 13.05:1.
- Spot inks from earth and enamel hues (mustard, rust, teal, olive, navy), not pure RGB primaries. Mustard #D9A441 on cream is only 1.86:1 and belongs in fills and shapes; set text on mustard in ink (7.0:1).
- Rust #B5472B on cream is 4.46:1, just under AA for small text; #A63F25 gives 5.18:1. Teal #2F6F6B on cream is 4.82:1.
- Overprint with `mix-blend-mode: multiply`; avoid translucent gradients, which no printing process produced.
- 1980s computing variant: amber (#FFB000) or green phosphor on near-black (10.8:1 and 14.6:1).
- Define the palette explicitly. A sepia CSS filter flattens every image and every contrast decision.

## Composition and layout
- Poster logic: centred or framed layouts, double rules, corner ornaments, badges as highlights or secondary navigation.
- A looser grid than modern UI, but the reading column stays single and narrow.
- Imagery as cut-outs with spot offsets, pre-processed halftones or engraved-style illustration.
- Responsive: frames collapse to simple borders on phones, badges keep a minimum of about 64 px so they stay legible.

## Interaction and motion
- Mechanical and unhurried: flip-board counters, typewriter reveals, a stamp that lands (scale 1.15 to 1 with a small rotation over 200-300 ms), page-turn wipes. CRT scanline roll for computing nostalgia.
- Pick one or two signature moves; avoid modern springs and blur.
- Reduced motion: show final states, switch off flicker and scanline roll, keep the static textures.
- Sound is nostalgic but must default to off.

## Accessibility cautions
- Faux ageing hurts legibility. Draw text above the texture, keep grain over text at 12% opacity or less and test contrast with the texture visible.
- Pale spot colours fail as text. Use ink for words and spot colours for fills.
- Scanlines, curvature and flicker over text reduce readability and can affect photosensitive users; keep text outside the CRT layer and never flash more than three times a second.
- Script and condensed faces below 18 px are hard to read; keep them for short display strings, as real text rather than images.

## Common mistakes
- A sepia or "vintage" filter instead of a designed palette.
- Mixing eras: 1950s script, 1980s neon and 1970s earth tones on one page.
- Distressed body copy, and gradients, blur or soft shadows that no print process could produce.
- Multi-megabyte texture images instead of a small tileable texture.

## Typical mistakes of AI-generated versions
- A brown tint, a script face and a torn-paper PNG standing in for the whole idea.
- A synthwave sunset gradient mixed into a supposedly mid-century layout.
- Distressed fonts applied to every piece of text, including navigation and forms.

## How to build it
- Pattern: `style-retro-vintage`. Tokens: paper, ink, three or four spot colours, one tileable texture under 64 KB, a halftone made from a CSS radial-gradient pattern or a pre-processed image.
- Vocabulary for print-and-analogue treatments (grain, halftone, Bayer dither at 2, 4 and 8 sizes, scanlines, CRT, duotone, paper and dust overlays) is enumerated in `react-bits:src/tools/texture-lab/types.js`, which also holds named presets such as Analog Film, Newsprint, Risograph and Retro CRT. Reference only: react-bits is licence-restricted, so use it as a dependency per its terms and do not copy code.
- A film-grain, dust, scratch and scanline overlay with a `fps` option that freezes under `prefers-reduced-motion` is `react-bits:src/content/Animations/Noise/Noise.jsx`; a CRT shader with `paused`, `fps` and `scanlineStrength` props is `react-bits:src/content/Backgrounds/CRTWarp/CRTWarp.jsx`.
- CSS recipes for halftone dots with multiply blending and scanlines from a repeating linear gradient appear in the industrial section of `taste-skill:skills/brutalist-skill/SKILL.md`.

## Sources
Original guidance written for this project. taste-skill is MIT-licensed; react-bits is MIT with the Commons Clause and is described, not quoted.
