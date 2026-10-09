---
title: "Vaporwave"
kind: design-style
summary: "Ironic 1980s-90s digital nostalgia: pastel pink, cyan and purple, perspective grids, sunsets, classical busts, retro operating-system windows and VHS artefacts. Covers palette contrast, CSS 3D grid technique, asset-rights cautions and how it differs from synthwave and cyberpunk."
source_ids: []
pattern_ids: [style-vaporwave]
updated: "2026-10-09"
---

# Vaporwave

Vaporwave grew out of internet music and art culture: a wistful, ironic look at consumer technology and mall culture of the 1980s and 90s. Visually it combines pastel neon gradients, perspective grid floors, sunsets, marble statues, palm trees, Japanese text, early-Windows-style windows and VHS noise. It is related to synthwave (brighter, driving, car and laser imagery) and cyberpunk (grimmer, darker) but its mood is dreamy and deadpan. This note is original; the local sources contain no vaporwave implementation.

## Visual characteristics
- Pink, cyan, lilac and mint pastels against deep purple or a pale gradient sky.
- A perspective grid floor receding to a horizon; a striped, gradient sun.
- Retro-OS windows with title bars, pixel icons, dithered gradients.
- Classical sculpture, palm trees, geometric solids, glitch and VHS tracking lines.
- Katakana or full-width Latin text as ornament.

## When it fits, when it does not
- Fits: music and art projects, indie games, fashion and merch drops, event posters, personal sites, ironic brand campaigns.
- Poor fit: serious services, long reading, accessibility-critical products, brands where irony could be misread.
- Supporting influences that work: y2k, retro-vintage, maximalism, a light cyberpunk, grain-and-texture. Avoid swiss-international-typographic, editorial and minimalism.

## Typography
- Window and UI text in pixel or system-like faces (VT323, Press Start 2P, IBM Plex Mono); display in wide or retro-futurist faces (Orbitron, Major Mono Display, Syne at ExtraBold) or a classical serif for contrast.
- Full-width characters and wide tracking (+0.1 to +0.3em) on short display strings only; sizes 32-96 px for titles, 14-16 px for body, never below 14 px.
- Body copy goes in a plain sans or mono on a solid window panel.

## Colour
- Classic palette: pink (#FF71CE), cyan (#01CDFE), mint (#05FFA1), lilac (#B967FF), pale yellow (#FFFB96).
- On a deep purple ground #1A0B2E pink measures 7.52:1 and cyan 9.87:1, so they can carry text; dark purple on pink is also 7.52:1. White on the pink is 2.47:1 and pale yellow on pink 2.29:1, so avoid those pairings.
- Gradients run pink to cyan or orange to purple at sunset; add faint dithering or grain to prevent banding.

## Composition and layout
- Centred scene: sun, grid and statue stacked on a vertical axis, or windows overlapping like a desktop.
- Perspective floor from CSS 3D: a container with `perspective`, a plane rotated with `rotateX(60deg)` and a repeating linear-gradient grid scrolled with `background-position`.
- Windows have 2 px bevel borders and title bars; content lives inside them.
- Keep the focal message in one window or one band; the rest is atmosphere.

## Interaction and motion
- Slow grid scroll, drifting sun, cursor-sparkles are optional; glitch and tracking-line bursts are short.
- Window dragging and minimise/close behaviour are charming but must work by keyboard too.
- Reduced motion: stop the grid scroll, freeze gradients, remove glitch bursts. Keep static composition.

## Accessibility cautions
- Pastel on pastel fails; compute pairs.
- Constant scrolling grids in the background distract readers; provide a pause beyond five seconds (WCAG 2.2.2).
- Flashing glitch bursts must stay under three flashes per second.
- Do not use full-width Latin characters for real content; screen readers handle them poorly and search does not match them.
- Retro windows with fake chrome must still expose real buttons, headings and labels.

## Common mistakes
- Mixing with synthwave imagery (cars, lasers) and calling it vaporwave.
- Using copyrighted logos, game sprites or commercial photographs; replace them with original or properly licensed assets.
- Heavy filter stacks and PNG collages that weigh several megabytes.
- Gradient overload with no dark ground for text.

## Typical mistakes of AI-generated versions
- A pink-to-cyan gradient, a statue cut-out, a grid floor and an Orbitron headline on every output, with text placed directly on the gradient and no motion handling.

## How to build it
- Pattern: `style-vaporwave`. Tokens: dark purple ground, three pastels, one pixel face, one display face.

```css
.floor { transform: perspective(500px) rotateX(60deg); transform-origin: center top; height: 40vh;
  background: linear-gradient(#FF71CE55 1px, transparent 1px) 0 0 / 100% 48px,
              linear-gradient(90deg, #FF71CE55 1px, transparent 1px) 0 0 / 48px 100%; }
@media (prefers-reduced-motion: no-preference) { .floor { animation: scroll 4s linear infinite; } }
@keyframes scroll { to { background-position: 0 48px, 0 0; } }
```

- Window chrome is plain HTML and CSS with real buttons; keep assets original.

## Sources
Fully original guidance written for this project; no local source files are cited.
