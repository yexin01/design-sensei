---
title: "Y2K"
kind: design-style
summary: "Late-1990s and early-2000s digital optimism: translucent candy plastics, chrome gradients, bubble shapes, stars and holographic foils. Shows how to get the look with controlled contrast, a clear hierarchy and optional, pausable decoration."
source_ids: [astryx, react-bits]
pattern_ids: [style-y2k]
updated: "2026-10-09"
---

# Y2K

Y2K design recalls the turn of the millennium: techno-optimism, translucent coloured plastic, chrome, glossy buttons, bubbles and blobs, lens flares, sparkles and web 1.0 furniture. It is a digital, shiny aesthetic, different from the paper-and-ink logic of retro-vintage and from the nightlife mood of cyberpunk. The risk is clutter and pastel-on-pastel text.

## Visual characteristics
- Glossy, rounded, bubble-like shapes; pill buttons with highlights; translucent "plastic" panels.
- Chrome and metallic gradients, holographic or iridescent foils, lens flares.
- Soft periwinkle, baby blue, lilac and silver bases with hot pink, lime or cyan accents.
- Stars, sparkles, orbs, wavy dividers and sticker clusters as decoration.
- On the playful end, web 1.0 furniture: tickers, small badges, windows with chunky borders.

## When it fits, when it does not
- Fits: music and fashion for younger audiences, nostalgia campaigns, creator merch, playful consumer apps, events, portfolios with attitude.
- Poor fit: regulated or serious services, dense data products, long reading. Gloss and sparkle compete with information.
- Supporting influences that work: liquid-materials, maximalism, vaporwave, a restrained glassmorphism, neo-brutalism for the pop end. Avoid minimalism, dark-technical-developer-tools and art-deco.

## Typography
- Rounded or geometric sans for text and headings (Nunito, Quicksand, Poppins), bold weights 600-800, with a serif or an extended techno face for contrast. Overused techno faces (Orbitron, Michroma) belong in one accent role only.
- Display 48-96 px; lowercase headings are on-style. Tracking -0.01 to +0.02em; do not letter-space chrome text.
- Pixel fonts (VT323, Press Start 2P) as small accents, sized in multiples of their design grid to stay crisp.
- Chrome text via `background-clip: text` only for one or two short display words, with a solid `color` fallback for forced-colors mode.

## Colour
- A pastel base with strong darks for text. The Astryx Y2K theme puts text #2D241B on a periwinkle body (#CCCFFA) at 10.05:1; its secondary text #675D52 drops to 4.25:1 on that body, so keep secondary text on white card surfaces (6.43:1).
- Hot pink is a fill, not a text colour: #FF3CAC on white is 3.23:1. White on #DB2777 is 4.60:1, which is fine for large and bold text.
- Build chrome from five to seven alternating light and dark gradient stops so it reads as metal; flat two-stop gradients read as plastic.
- Holographic effects: low-saturation conic gradients or shader foils over a neutral base. Keep them behind or around content, not under paragraphs.

## Composition and layout
- Floating panels with chunky borders and drop shadows, pill controls, glossy icons, and sticker clusters at the page periphery.
- One headline and one primary action per screen; keep decoration out of the reading path.
- Wavy or star-bullet dividers, tickers and badges as secondary structure.
- Responsive: reduce sticker counts on phones and keep tap targets at 44 px or more even on small pills.

## Interaction and motion
- Bouncy hovers (scale 1.04 with a spring), a single glint sweep across a glossy button (about 600 ms, once), sparkle bursts on click, a slow ticker.
- Cursor trails were a period staple. Skip them: they harm performance and accessibility.
- Reduced motion: remove glints, sparkles and tickers, and keep the static gloss.
- Keep any flashing or blinking below three flashes per second (WCAG 2.3.1).

## Accessibility cautions
- Pastel on pastel and white on bright fills are the standard failures. Compute every pair, including text on gradients at the lightest point.
- Gradient-clipped text can vanish in forced-colors mode; always set a fallback `color` and test.
- Decorative stars and orbs should be `aria-hidden` and outside the tab order.
- Chunky borders are good for non-text contrast; make sure the focus ring is distinct from them.

## Common mistakes
- Chrome gradient on all text, which lowers legibility and loses the effect.
- Orbitron or Michroma for every heading.
- Stickers covering content, and gloss with no hierarchy.
- Mixing Y2K with flat modern UI components so the two languages fight.
- Treating Y2K as vaporwave or cyberpunk; the mood is bright and optimistic.

## Typical mistakes of AI-generated versions
- A pink-to-purple gradient background, chrome headline and sparkle emoji dropped onto a standard landing template.
- White text on pastel fills, because every colour was picked for mood rather than measured.
- One techno typeface for all text, and a holographic gradient standing in for the whole style.

## How to build it
- Pattern: `style-y2k`. Define a pastel base, one dark text colour, two accents, and a chrome gradient token; add gloss with an inset highlight and a soft outer shadow.
- A complete design-system reading is the Astryx Y2K theme: periwinkle body, charcoal accent, Poppins for body and headings, Crimson Text for the display roles, square element radii with pill badges, pastel categorical fills with dark text (`astryx:packages/themes/y2k/README.md`, `astryx:packages/themes/y2k/src/y2kTheme.ts`). Its package description talks about hot pinks and lime greens, but the shipped tokens are periwinkle and pastel; trust the tokens.
- WebGL foils, described only because react-bits is licence-restricted: a tilt-driven holographic card with eight foil presets (`react-bits:src/content/Components/HoloCard/HoloCard.jsx`), an iridescent background with `color`, `speed`, `amplitude` and `mouseReact` options (`react-bits:src/content/Backgrounds/Iridescence/Iridescence.jsx`), and a liquid chrome background (`react-bits:src/content/Backgrounds/LiquidChrome/LiquidChrome.jsx`). Each needs a static gradient fallback and a pause path.

## Sources
Original guidance written for this project. astryx is MIT-licensed; react-bits is MIT with the Commons Clause and is described, not quoted.
