---
title: "Brutalism"
kind: design-style
summary: "Raw, exposed-structure web design: default or heavy type, hard borders, harsh contrast, no gloss. Covers the raw-HTML and industrial flavours, where each works, and how to keep an unpolished look usable and accessible."
source_ids: [astryx, taste-skill]
pattern_ids: [style-brutalism]
updated: "2026-10-09"
---

# Brutalism

Web brutalism rejects polish. Structure is exposed, defaults are kept, contrast is harsh and decoration is treated as dishonest. Two flavours are common. The raw-HTML flavour keeps system fonts, blue underlined links, tables and dense text. The industrial flavour uses rigid grids, a heavy grotesque, monospace labels and 1-bit imagery. What they share is a refusal of gloss, not a licence for disorder.

## Visual characteristics
- Visible structure: 2-4 px borders, table-like grids, stacked blocks, abrupt section edges and zero border radius.
- Default or system type (Times, Courier, Arial) or a very heavy grotesque; frequent uppercase; extreme scale contrast.
- Near-pure colours: black, white, system blue, primary red, occasionally one acid colour.
- Unsmoothed imagery: raw photos at hard crops, halftone or dithered treatments, overlaps.
- Text-first density with little reassuring microcopy.

## When it fits, when it does not
- Fits: art, music and culture projects, independent publishers, designer portfolios, manifestos, zine-like and activist sites, technical projects that want to look uncompromising.
- Poor fit: healthcare, finance, public services, early-years education, mainstream e-commerce, any brand whose promise is reassurance through polish, or audiences who need guidance through a task.
- Supporting influences that work: swiss-international-typographic (grid discipline), generative-design, a raw kinetic-typography, the terminal flavour of cyberpunk. Avoid high-fashion-luxury, glassmorphism, claymorphism and organic-tactile.

## Typography
- Raw flavour: system stacks (`"Times New Roman", serif`, `"Courier New", monospace`, `Arial, sans-serif`) with default link styling left intact.
- Industrial flavour: a heavy grotesque for display (Archivo Black, Anton, Inter Black) with a mono for data (JetBrains Mono, IBM Plex Mono, Space Mono).
- Scale contrast does the work: display at `clamp(4rem, 12vw, 14rem)` with line-height 0.85-0.95 and tracking -0.03 to -0.06em; body 14-18 px at 1.4 or more; small uppercase labels at +0.05 to +0.1em.
- Use two weights only, 400 and 900. Keep text as real text; overlap it through layout, never by flattening it into images.

## Colour
- A two-tone base (black and white, or paper #F4F4F0 and ink #0A0A0A) plus one hard accent.
- No gradients, translucency or soft shadows. A hard offset shadow belongs to neo-brutalism, not here.
- Check vibrating pairs: pure red on pure blue is 2.15:1; red on white is 4.00:1 (large text only). Default link blue #0000EE is 9.4:1 on white but only 2.2:1 on black.
- Dark substrate: #0A0A0A to #121212 rather than #000. A phosphor green is acceptable for a single status element, not for body text.

## Composition and layout
- A hard grid with visible rules, full-width `<hr>` dividers and tables for tabular data. A grid with `gap: 1px` over a contrasting parent background draws razor-thin lines without border bookkeeping.
- Bimodal density: tightly packed mono metadata beside large areas of empty space around oversized type.
- Plain, always-visible text navigation; dense footers.
- Break one rule on purpose (an overlap, a giant word clipped by the viewport), not every rule at once.
- Responsive: stack blocks on narrow screens and test overlaps at 320 px; avoid fixed-pixel tables.

## Interaction and motion
- Abrupt on purpose: no easing, hard cuts, instant inversion on hover (black and white swap), thicker underlines.
- Visible focus: a 3 px solid outline in a contrasting colour. Keep the default cursor and native scrolling.
- Optional marquee or ticker, always pausable. Halftone, dither and scanline effects are for the industrial flavour and edge towards cyberpunk.
- Reduced motion: stop marquees and tickers; everything else is already instantaneous.

## Accessibility cautions
- Overlapped or clipped giant type can hide text. Keep DOM order equal to reading order and test at 200% zoom and 320 px reflow.
- Fixed-pixel layouts break zoom; size in `rem` and use flexible tracks.
- Auto-moving content longer than five seconds needs a pause control (WCAG 2.2.2).
- A default look is not automatically accessible: dense link lists still need spacing, and focus must stay visible.

## Common mistakes
- Rounded corners, soft shadows or gradients slipped in, which turns it into generic UI.
- Chaos without an internal rule: random overlaps and random fonts instead of one consistent structure.
- Hostile navigation: unlabeled icons or a hidden menu. Raw should not mean unusable.
- Text over busy images with no solid ground; no mobile pass.
- Using it for a client whose audience needs trust signals.

## Typical mistakes of AI-generated versions
- Black and white with a mono font and huge headings but comfortable padding, rounded buttons and subtle shadows still present.
- Cards rotated by a few degrees and called brutalist, with no structural honesty behind them.
- Neon accents or glass panels added, mixing flavours the style guide says to keep separate.

## How to build it
- Pattern: `style-brutalism`. Tokens: `--radius: 0`, `--border: 2px solid var(--ink)`, system font stacks, semantic HTML (real tables, `hr`, `dl`).
- If you use a themeable design system, zero the radius at the token level. Astryx shows the idea with a single multiplier, `{ base: 4, multiplier: 0 }`, documented as the sharp/brutalist setting (`astryx:packages/core/src/theme/defineTheme.ts`). Its comment notes the fully round token is not scaled by the multiplier, so set it to 0 explicitly as the y2k theme does (`astryx:packages/themes/y2k/src/y2kTheme.ts`).
- The industrial flavour, with ASCII framing, halftone, dither and scanline recipes and the instruction to pick one flavour per project, is described in `taste-skill:skills/brutalist-skill/SKILL.md`.
- Keep any effect layers (noise, scanlines) on a fixed `pointer-events: none` layer, never on the scrolling container.

## Sources
Original guidance written for this project. astryx and taste-skill are MIT-licensed and cited as reference only.
