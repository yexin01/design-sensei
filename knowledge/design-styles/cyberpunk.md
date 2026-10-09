---
title: "Cyberpunk"
kind: design-style
summary: "Neon-lit dystopian tech: deep purple-black grounds, magenta, cyan and acid-yellow accents, glitch, CRT and terminal motifs, hazard markings and dense signage layouts. Focus on keeping glitch short, text legible and effects safe for photosensitive users."
source_ids: [fancy, react-bits, vengeance-ui]
pattern_ids: [style-cyberpunk]
updated: "2026-10-09"
---

# Cyberpunk

Cyberpunk interfaces borrow from neon-lit, over-networked, run-down futures: saturated light on dark, glitching signal, CRT hardware, terminal prompts, hazard stripes and dense signage. The mood is gritty and ironic. It is not the same as futurism (cleaner, optimistic, product-led) or vaporwave (pastel, nostalgic irony). Used continuously, its effects destroy legibility, so the craft lies in short bursts and clean reading areas.

## Visual characteristics
- Deep purple-black or blue-black grounds with neon magenta, cyan and acid yellow as flat or glowing accents.
- Glitch: RGB splits, slice displacement, scrambled characters, noise.
- CRT and terminal motifs: scanlines, screen curvature, phosphor tints, ASCII framing, prompts.
- Industrial markings: hazard stripes, barcodes, serials, coordinates, katakana accents, warning labels.
- Chamfered panels, thin neon borders, overlapping stacks and ticker bands.

## When it fits, when it does not
- Fits: games, nightlife and music, esports, security and hacker events, sci-fi fiction and film promotion, art projects, some web3 and tooling brands with a deliberate edge.
- Poor fit: healthcare, mainstream finance, children's products, public services, long reading. A dystopian tone also harms trust where reassurance matters.
- Supporting influences that work: dark-technical-developer-tools (terminal), futurism, grain-and-texture, kinetic-typography, generative-design. Avoid organic-tactile, minimalism, high-fashion-luxury and claymorphism.

## Typography
- Mono for UI and data (Share Tech Mono, JetBrains Mono, IBM Plex Mono; VT323 for pixel flavour); condensed or techno sans for headings (Rajdhani, Chakra Petch, Oxanium; Orbitron only as a sparing accent).
- Headings 40-96 px, weight 600-800, uppercase, tracking +0.04 to +0.12em. Mono body 14-16 px at line-height 1.5; set longer reading text in a plain sans.
- Keep a clean, unglitched DOM text node under every effect, for assistive technology, search and the final resting state.

## Colour
- Ground #0B0614; neon magenta #FF2BD6 (6.25:1), cyan #00F0FF (14.2:1), acid yellow #FCEE0A (16.5:1). Pure blue #0000FF on black is 2.44:1 and fails; use lighter blues.
- One dominant neon, one secondary, one reserved for warnings. Body text stays off-white (#EDEAF5); neon is for accents and large display words.
- Glows from `text-shadow` at 6-12 px blur and low alpha. Heavy bloom smears small text.
- Red and cyan split layers belong to display words and transitions only.

## Composition and layout
- Chamfered panels via `clip-path` (original code below), thin neon borders, terminal windows, tickers and HUD brackets.
- Diagonal dividers and hazard-stripe bands (a 45 degree repeating gradient) at section edges.
- Dense data is acceptable if there is a central reading column, consistent panel titles and one underlying grid.
- On phones stack panels, keep the chamfers, and remove overlays and heavy shaders.

## Interaction and motion
- Short bursts rather than loops: glitch on hover or transition (150-300 ms), character scramble reveals on load (400-800 ms), occasional neon flicker, typing caret.
- Idle motion should be slow: scanline roll, gentle CRT warp.
- Reduced motion: disable glitch, scramble, flicker and scanline roll; show final static text.
- Offer a "reduce effects" control. Looping effects longer than five seconds need a pause (WCAG 2.2.2).

## Accessibility cautions
- Scrambled text written into the DOM can be read aloud as garbage. Hide the visual layer from assistive technology and expose the final string.
- Chromatic aberration and scanlines over body text lower readability; keep paragraphs on clean panels.
- Flicker and glitch bursts must stay under three flashes per second and away from large areas, especially red (WCAG 2.3.1).
- `clip-path` also clips outlines. Draw focus rings inside the clipped shape or use an inner pseudo-element.

## Common mistakes
- Everything glitching all the time, which removes both impact and legibility.
- Saturated neon used for body copy or coloured text on coloured panels.
- Decorative katakana that nobody has checked for meaning.
- Stacking CRT shader, particles and bloom until mobile devices throttle.

## Typical mistakes of AI-generated versions
- A magenta-to-cyan gradient over black, a glitching headline, glass cards and "NEURAL INTERFACE" copy; the same palette in every output.
- `infinite` glitch animations on all headings and blurry text-shadow glows.
- Invented terminal commands that no real system would print.

## How to build it
- Pattern: `style-cyberpunk`. Define neon tokens, a chamfered panel, a hazard stripe and a glow utility, then add one signature effect, not all of them.
- Text scramble: `fancy:src/fancy/components/text/scramble-hover.tsx` (`scrambleSpeed` 50, `maxIterations` 10, `revealDirection`, `useOriginalCharsOnly`, `characters`). Its `sr-only` copy mirrors the live scrambled string, so give the wrapper a stable `aria-label` or keep the hidden copy equal to the final text.
- `vengeance-ui:src/components/ui/cyber-glitch-text.tsx` scrambles on mount at 40 ms steps and, on hover, adds red and blue copies and a slice overlay that repeat a 0.2 s opacity cycle indefinitely. It writes scrambled characters into the visible node with no hidden final copy and no reduced-motion branch; patch it before shipping.
- CRT and terminal backgrounds, described only because react-bits is licence-restricted: `react-bits:src/content/Backgrounds/FaultyTerminal/FaultyTerminal.jsx` (`pause`, `scanlineIntensity`, `glitchAmount`, `flickerAmount`, `curvature`, `dpr`), `react-bits:src/content/Backgrounds/CRTWarp/CRTWarp.jsx` (`paused`, `fps`, `scanlineStrength`, `rgbShift`), `react-bits:src/content/Backgrounds/LetterGlitch/LetterGlitch.jsx` (`glitchSpeed`, `glitchColors`) and the CSS-only `react-bits:src/content/TextAnimations/GlitchText/GlitchText.css`, whose duplicated pseudo-element layers loop forever with no pause path.

```css
.panel { clip-path: polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 16px 100%, 0 calc(100% - 16px)); }
```

## Sources
Original guidance written for this project. fancy and vengeance-ui are MIT-licensed; react-bits is MIT with the Commons Clause and is described, not quoted.
