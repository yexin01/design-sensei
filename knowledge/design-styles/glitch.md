---
title: "Glitch"
kind: design-style
summary: "Deliberate signal failure as an aesthetic: RGB channel splits, slice displacement, corrupted characters, scanlines and datamosh-style tearing. Covers short-burst motion over a clean text layer, computed contrast ratios on dark and light grounds, and the WCAG 2.3.1 flash limits that bound any glitch animation."
source_ids: [fancy, react-bits, vengeance-ui]
pattern_ids: [style-glitch]
updated: "2026-10-09"
---

# Glitch

Glitch treats failure as material: a dropped signal, colour channels that no longer line up, frames torn into bands, text that decays into symbols. It is a technique first and a mood second, which separates it from cyberpunk (a whole dystopian world in which glitch is one motif). Glitch can sit on a calm light page, a brutalist grid or a gallery site. Its impact depends on contrast with a stable baseline: a layout that is broken all the time has no glitch left in it, only noise.

## Visual characteristics
- Channel misregistration: two coloured copies of a word or image offset 2-6 px horizontally, as in a badly aligned print or a lens with chromatic aberration.
- Slice displacement: horizontal bands shifted sideways, blocks of an image jumping, torn scanlines.
- Corrupted characters: glyphs swapped for block and box-drawing symbols, partial words, replacement characters.
- Signal artefacts: scanlines, static, tracking bars, low-resolution smears, pixel-sorted streaks.
- Hard, stepped changes instead of eased motion; irregular rhythm rather than a metronome.
- An orderly base underneath: tight grid, mono or grotesque type, flat colour.

## When it fits, when it does not
- Fits: music, club and festival sites, game and film launches, creative-technology and security events, experimental portfolios, 404 and loading states, section transitions, editorial about data and surveillance.
- Poor fit: healthcare, banking, public services, children's products, long reading, and anything the user must trust. A glitching price, consent notice, error message or "Pay now" button reads as a bug, not a style.
- Supporting influences that work: cyberpunk, kinetic-typography, grain-and-texture, dark-technical-developer-tools, brutalism, vaporwave (VHS side). Avoid high-fashion-luxury, organic-tactile, claymorphism and art-deco.

## Typography
- Solid letterforms survive slicing: a heavy grotesque or condensed face for display (Archivo Black, Anton, Space Grotesk 700) and a mono for UI and data (JetBrains Mono, Space Mono, IBM Plex Mono). Hairline faces dissolve when cut into bands.
- Display 48-120 px, weight 700-900, tracking 0 to +0.04em. Body 16 px in a plain sans or mono, never glitched.
- CJK: dense glyphs such as kanji make dramatic slices, but cutting strokes or scrambling from a random pool can produce real characters you did not intend. Draw scramble pools from characters you have read, set `lang` on the element, and keep the true string in the DOM.
- Avoid zalgo text (stacked combining marks): it overflows the line box and is announced as noise by screen readers.

## Colour
- Dark ground #0A0A0F: text #F2F2F2 is 17.6:1, cyan #00E5FF 12.8:1, yellow #FFE600 15.6:1, magenta #FF2D95 5.7:1, red #FF3B3B 5.6:1. Muted text #9A9AAE is 7.2:1, while #5B5B6B is 3.0:1 and fails for text. Pure blue #0000FF is 2.3:1.
- The neon pair does not survive a light ground: cyan #00E5FF on #F5F5F0 is 1.4:1. On light, use ink #111111 (17.3:1) with darker offsets such as magenta #B0006B (6.3:1) and teal #007A8C (4.6:1), or let the offset layers multiply onto the page.
- The base text carries the contrast; offset layers are decoration and must never be the only copy of a word.
- Two split colours plus a base is enough. Red/cyan or magenta/cyan are the cliché; a brand pair, or white and grey offsets, looks less generic.
- Saturated red has a stricter flash threshold than other colours, so keep large red flicker out of the design.

## Composition and layout
- Keep a visible grid and alignment lines, and let the glitch break them locally. Displace by a few percent of the width, not half the screen.
- Glitch decorative or hero material (a headline, an image, a loader, a transition) and keep controls, forms and body copy steady.
- Build text glitch from the real text node plus two `aria-hidden` offset layers. Build image glitch from slices of the image, and ship a frozen glitched still as the resting and print state.
- Leave quiet space around the effect so a burst reads as an event.
- On phones use one offset layer and shorter bursts, and drop shader-based image glitch.

## Interaction and motion
- Triggers: a 150-300 ms burst on hover and focus, once when a headline enters view, 200-400 ms across a route change, or on an error state. Avoid permanent loops.
- Use stepped timing (`steps(1, end)`) and keyframes at uneven positions such as 0, 12, 13, 40, 41 and 100 percent; even spacing looks mechanical.
- Add a cooldown so repeated hovering cannot retrigger within a second (see the flash limits below).
- Ambient motion such as scanline roll should be slow, and anything auto-playing for more than five seconds needs a pause control (WCAG 2.2.2).
- Animate `transform`, `opacity` and `clip-path` on two pseudo-elements; avoid continuous `filter` or SVG displacement over large areas.
- Reduced motion: remove the bursts, show at most a static 2 px offset, and keep every piece of information.

## Accessibility cautions
- Photosensitivity, WCAG 2.3.1 (level A): content must not flash more than three times in any one-second period unless the flash stays below the general and red flash thresholds. A flash is a pair of opposing relative-luminance changes of at least 10 percent of the maximum (when the darker state is below 0.80); WCAG 2.3.1 only counts the flash when the combined flashing area exceeds roughly a quarter of a 10-degree visual field, about 341 by 256 px at 1024 by 768. A full-width band that flips black to white several times a second fails. Level AAA 2.3.2 removes the area allowance.
- Design below the limit rather than at it: two reversals at most per second in any region, small areas, no strobing red, no full-screen inversion. Check video and shader glitch with a photosensitivity analyser (the Harding test is the broadcast standard).
- Honour `prefers-reduced-motion`, and also offer an in-page "reduce effects" control, since many people never set the OS option. Shaking `translate` can trigger vestibular symptoms even without flashing (WCAG 2.3.3 covers animation from interaction).
- Duplicate layers built with `content: attr(data-text)` are read by many screen readers, giving two or three announcements. Use the alternative-text form `content: attr(data-text) / ""` where supported, or build the layers as `aria-hidden` spans.
- Text that is scrambled in the live DOM is announced as garbage. Keep the final string reachable (`aria-label` on a wrapper, or a hidden copy equal to the end state).
- Forced-colors mode replaces your colours, so offset layers overlap the base text and double-print; hide them there. Do not clip the focus ring with `clip-path`.
- Never glitch error text, required legal copy or the label of the primary action.

## Common mistakes
- Looping glitch on every heading, so nothing is stable enough to be disturbed.
- Offsets beyond 8-10 px that make the word unreadable, or glow and blur used instead of a crisp channel offset.
- Metronome timing, and bursts triggered by every pointer move.
- No static version for screenshots, social cards, print and reduced motion.
- A brand logo that exists only in glitched form.

## Typical mistakes of AI-generated versions
- `animation: glitch 1s infinite` on the h1 with red and cyan `text-shadow` at plus or minus 2 px over near-black, together with "SYSTEM ERROR" or "NEURAL INTERFACE" copy.
- Scrambled characters written into the visible node with no accessible final text, glitch on body copy and buttons, no reduced-motion branch, and hover-only triggers that never fire on touch or keyboard.

## How to build it
- Pattern: `style-glitch`. Real text node plus two `aria-hidden` offset layers, sliced with `clip-path`, triggered by a state and not by a loop. This recipe is original:

```css
.glitch { position: relative; color: #F2F2F2; }
.glitch::before, .glitch::after {
  content: attr(data-text) / ""; position: absolute; inset: 0; opacity: 0; pointer-events: none; }
.glitch::before { color: #00E5FF; }
.glitch::after { color: #FF2D95; }
.glitch:is(:hover, :focus-visible)::before { animation: tear-a 260ms steps(1, end) 1; }
.glitch:is(:hover, :focus-visible)::after { animation: tear-b 260ms steps(1, end) 1; }
@keyframes tear-a { 0% { opacity: 1; transform: translateX(-4px); clip-path: inset(10% 0 62% 0); }
  40% { transform: translateX(3px); clip-path: inset(58% 0 12% 0); }
  70% { transform: translateX(-2px); clip-path: inset(30% 0 40% 0); } 100% { opacity: 0; } }
@keyframes tear-b { 0% { opacity: 1; transform: translateX(4px); clip-path: inset(52% 0 20% 0); }
  35% { transform: translateX(-3px); clip-path: inset(8% 0 70% 0); }
  65% { transform: translateX(2px); clip-path: inset(40% 0 30% 0); } 100% { opacity: 0; } }
@media (prefers-reduced-motion: reduce), (forced-colors: active) { .glitch::before, .glitch::after { display: none; } }
```

- Closest local relatives, each with gaps to patch:
  - `vengeance-ui:src/components/ui/cyber-glitch-text.tsx` scrambles in 40 ms steps and adds red and blue `aria-hidden` copies whose 0.2 s opacity cycle repeats forever; the base node holds the scrambled text and there is no reduced-motion branch.
  - `vengeance-ui:src/components/ui/ascii-glitch-ripple.tsx` rewrites `textContent` every frame as a wave of box-drawing characters (1000 ms default), locks the element width to prevent layout shift and restores the original text afterwards. It listens to mouse events only, so keyboard users never trigger it, and it has no reduced-motion check.
  - `fancy:src/fancy/components/text/scramble-hover.tsx` (`scrambleSpeed` 50, `maxIterations` 10, `useOriginalCharsOnly`) mirrors the live scrambled string in its `sr-only` copy, so assistive technology hears the scramble.
  - Described only, because react-bits is licence-restricted: `react-bits:src/content/TextAnimations/GlitchText/GlitchText.css` builds both layers from `attr(data-text)` with clip-path keyframes on infinite alternating loops (an `enableOnHover` variant exists), and `react-bits:src/content/TextAnimations/FuzzyText/FuzzyText.jsx` renders text on a canvas with a `glitchMode` (`glitchInterval` 2000 ms, `glitchDuration` 200 ms) but no DOM text alternative.
  - `react-bits:src/tools/texture-lab/shaders.js` (`GLITCH_FRAGMENT_SHADER`) is a useful parameter vocabulary for image glitch: slice count, RGB shift, block size, angle and seed.

## Sources
Original guidance written for this project. fancy and vengeance-ui are MIT-licensed; react-bits is MIT with the Commons Clause and is described, not quoted. WCAG 2.2 success criteria 2.2.2, 2.3.1, 2.3.2 and 2.3.3 are cited by number only.
