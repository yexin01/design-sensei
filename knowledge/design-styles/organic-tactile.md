---
title: "Organic and tactile"
kind: design-style
summary: "Soft, natural, hand-made interfaces: earthy palettes, humanist type, blob shapes and squishy spring micro-interactions that feel physical. Covers contrast on muted palettes, bounded spring motion, and reduced-motion handling for tactile effects."
source_ids: [astryx, fancy, react-bits]
pattern_ids: [style-organic-tactile]
updated: "2026-10-09"
---

# Organic and tactile

Organic-tactile design aims for warmth and physicality: earth tones, humanist or soft serif type, rounded irregular shapes, paper and fabric textures, and controls that squish, spring and settle as if they had mass. It suits products about food, wellness, craft and care, and children's learning. The risk is a cute template: pastel, blobs and bounce applied everywhere, with muted colours that fail contrast.

## Visual characteristics
- Earthy, low-saturation palettes: clay, moss, oat, terracotta, sage, with one warm accent.
- Large radii (24-40 px), blob masks, overlapping organic shapes, hand-drawn illustration and imperfect lines.
- Soft textures (paper, linen, grain) kept faint; diffuse shadows tinted to the surface.
- Controls with physical behaviour: squash on press, springy toggles, drag with weight.

## When it fits, when it does not
- Fits: food and drink, wellness, parenting, education, craft marketplaces, consumer apps with a gentle tone.
- Poor fit: trading and precision tools, security products, dense data work where bounce delays reading.
- Supporting influences that work: claymorphism, grain-and-texture, retro-vintage, soft editorial, minimalism with warmth. Avoid cyberpunk, futurism and brutalism.

## Typography
- Soft or humanist faces: Fraunces (use its SOFT axis), Young Serif, Newsreader for display; Nunito, DM Sans or Figtree for text. A hand-lettered accent for one or two words at most.
- Display 40-88 px at weight 500-700, tracking -0.01em. Body 17-19 px with generous 1.55-1.7 leading.
- Avoid thin weights on textured grounds.

## Colour
- Ground: oat or cream such as #EFE6D8. Text: deep brown #3B2F25 (10.5:1 on that ground).
- Muted accents are the trap: sage #8FA886 on oat is 2.09:1, so use it for fills and shapes, and a deeper moss like #4F6B45 (4.82:1) for text and icons.
- Tint shadows toward the ground colour; avoid grey shadows on warm backgrounds.
- Limit to one warm accent and two supporting earth tones.

## Composition and layout
- Generous spacing, centred or loosely staggered blocks, organic masks on photography.
- Keep functional UI (forms, tables, settings) plain and rectangular; reserve blobs and texture for hero and illustration areas.
- Touch targets stay at 44 px or more even when shapes are irregular.

## Interaction and motion
- Springs with mild overshoot (damping ratio near 0.6-0.8, one visible bounce at most), squash and stretch under 8%, durations 250-450 ms.
- Gooey merges and physics play (falling, stacking items) belong to playful moments, not core flows.
- Reduced motion: replace springs with 150 ms fades or instant state changes, remove wobble loops and physics, keep static pressed states.

## Accessibility cautions
- Bounce and wobble loops are vestibular triggers; keep them off by default for repeated or large elements.
- Irregular shapes must not hide focus rings; draw rings as outlines with an offset.
- Custom radios, switches and toggles need native or ARIA semantics. The react-bits JellyRadio exposes a `radiogroup` with `role="radio"` and `aria-checked`, and its stylesheet disables the press squash under `prefers-reduced-motion`.
- Do not use texture behind text.

## Common mistakes
- Pastel and blobs on everything, including data screens.
- Overshoot large enough to delay reading or cause nausea.
- Low-contrast sage or peach text on cream.
- Heavy texture images instead of small tiles.

## Typical mistakes of AI-generated versions
- A "wellness template": pastel gradient, floating blobs, rounded cards everywhere and a spring bounce on every hover.
- Hand-drawn feel faked with wobbly borders on body text.

## How to build it
- Pattern: `style-organic-tactile`. Tokens: warm ground, brown ink, two earth accents, three large radii, one spring preset.
- Theme references: Astryx ships earthy themes described as calm and organic (matcha), warm stone and slate with a handcrafted feel (stone), rich browns with Fraunces headings (chocolate) and creamy yellows (butter): `astryx:packages/themes/matcha/README.md`, `astryx:packages/themes/stone/README.md`, `astryx:packages/themes/chocolate/README.md`, `astryx:packages/themes/butter/README.md`.
- Physics and goo: `fancy:src/fancy/components/physics/gravity.tsx` (matter-js bodies for DOM elements; `gravity`, `resetOnResize`, `autoStart`) and `fancy:src/fancy/components/filter/gooey-svg-filter.tsx` (blur plus alpha-contrast matrix). Neither has a reduced-motion path.
- Tactile micro-interactions, described only because react-bits is licence-restricted: `react-bits:src/content/Micro/JellyRadio/JellyRadio.jsx` and `.css`, `react-bits:src/content/Micro/SquishSwitch/SquishSwitch.jsx`.

## Sources
Original guidance written for this project. astryx and fancy are MIT-licensed; react-bits is MIT with the Commons Clause and is described, not quoted.
