---
title: "Japanese minimalism (ma, wabi-sabi)"
kind: design-style
summary: "Restraint in a Japanese key: ma (間, designed pauses and intervals), yohaku (余白, the blank margin), wabi-sabi imperfection, asymmetry and material warmth. Covers Japanese and Latin type pairing, vertical writing, a washi and sumi palette with computed contrast, rhythm of spacing, slow motion and the cultural-costume trap."
source_ids: []
pattern_ids: [style-japanese-minimalism]
updated: "2026-10-09"
---

# Japanese minimalism (ma, wabi-sabi)

This note covers an aesthetic that borrows from Japanese ideas about space and imperfection: ma (間), the interval or pause between things, treated as something you design rather than something left over; yohaku (余白), the blank margin in an ink painting that completes the picture; wabi-sabi, finding beauty in the modest, weathered and impermanent; kanso (simplicity) and fukinsei (asymmetry). It is warmer, more material and more asymmetric than Western minimalism, which tends to be geometric, neutral and rational. Two cautions up front. Many commercial Japanese websites are dense and information-rich, so this is a craft and cultural-brand aesthetic, not a description of Japanese web conventions. And it is not a costume: for a product with no connection to Japan, borrowing the signs without the thinking produces pastiche.

## Visual characteristics
- Asymmetric balance: a small element in a large field, placed off-centre, with the void doing the work.
- Warm paper grounds (washi), ink black (sumi), muted earth tones such as clay, moss and indigo, and at most one small accent, often a vermilion mark like a seal (hanko).
- Material hints: paper fibre, linen, wood grain, glaze. Used lightly and in one place.
- A single gesture line, such as an ensō-like circle or one brushed rule, instead of ornament; hairline dividers.
- Quiet photography: still life, natural light, plenty of empty frame, cropped asymmetrically.
- Short text, vertical captions or titles, and one idea per section.

## When it fits, when it does not
- Fits: ceramics, tea, craft and stationery, ryokan and hospitality, architecture and interiors, slow fashion, wellness, cultural institutions, photographers and essayists, Japanese brands and products.
- Poor fit: dense catalogues, dashboards, price-led or urgency-led commerce, energetic youth brands, and any product whose users need strong affordances. Sparse layouts hide controls.
- Supporting influences that work: minimalism, editorial, high-fashion-luxury, organic-tactile, grain-and-texture, swiss-international-typographic (for grid precision). Avoid maximalism, cyberpunk, y2k, neo-brutalism and vaporwave (which uses Japanese script as kitsch texture).

## Typography
- Set `lang="ja"` on Japanese text (and `lang="en"` on English inserts). It selects the right regional glyph variants for shared Han characters and the right voice for screen readers.
- Mincho (serif) for a literary, quiet tone: Shippori Mincho, Zen Old Mincho, Noto Serif JP. Gothic (sans) for clarity: Zen Kaku Gothic New, Noto Sans JP, BIZ UDPGothic. A round gothic such as Zen Maru Gothic is warmer.
- Body 15-17 px (16 px or more for kanji), line-height 1.8 to 2.0, tracking 0.02 to 0.08em. Headings 24-48 px at weight 400 to 500, tracking 0.08 to 0.2em for short airy titles. Kana strokes are thin: avoid weights under 400 below 18 px.
- `font-feature-settings: "palt"` gives proportional kana spacing; use it for headings and short lines, and test it on body copy before keeping it.
- Latin pairing: list the Latin family first in `font-family` so Latin letters use it and kana and kanji fall through to the Japanese face. Shippori Mincho pairs with Cormorant Garamond or EB Garamond; Zen Kaku Gothic New pairs with Inter or DM Sans. Compare x-heights and adjust the Latin size by a few percent. Japanese has no italic; avoid faux-oblique Japanese and use Latin italics rarely.
- Vertical writing: `writing-mode: vertical-rl` for titles, pull quotes and short captions, with `text-orientation: mixed` and `text-combine-upright: digits 2` for numbers. Long vertical body copy forces horizontal scrolling on the web; keep it short.
- Line breaking: `line-break: strict` avoids small kana and closing punctuation at the start of a line, and `word-break: auto-phrase` breaks at phrase boundaries where supported and is ignored elsewhere.
- Never use kanji as decoration unless a Japanese reader has checked the meaning and context. Random characters are the clearest sign of pastiche.

## Colour
- Washi #F4EFE6 as ground. Sumi #1C1B19 text is 15.0:1; nezumi grey #6B665E 5.0:1; indigo #264A6B 8.1:1; moss #5B6B3A 5.1:1; vermilion #B3261E 5.7:1 (white on vermilion is 6.5:1); the lighter vermilion #C2332B is 4.8:1.
- Faded tones are tempting for text and fail it: #8C867C is 3.2:1, #A39E93 is 2.3:1, and the hairline tone #D9D2C3 is 1.3:1. Keep text at 4.5:1 or better and let the faded tones live in rules, shadows and decoration.
- On a dark variant, #F4EFE6 on #1C1B19 is 15.0:1 and a muted #9A948A is 5.7:1.
- Accent under about five percent of the area: one seal, one number, one underline. If vermilion is the accent, errors need a second cue (icon and message) so the warning is not diluted.
- Avoid pure white and pure black, saturated primaries and gradients. A red circle on white is the flag, not a design.

## Composition and layout
- Ma comes from contrast of spacing, not uniform emptiness. Pair tight groups (8-16 px between related lines) with wide pauses (section padding 120-240 px on desktop, 72-120 px on phones). Uniformly huge gaps read as an unfinished page.
- Use asymmetry on a 12-column grid: put the content block in five or six columns and leave the others empty, anchor vertical text to one edge, crop images to one side.
- One focal element per viewport, with a short caption. Keep a steady baseline grid so the asymmetry has something to push against.
- Navigation of four to six labelled items at an edge. Do not hide hours, price, address or booking: calm layouts often bury exactly what the visitor came for.
- Imperfection once, not everywhere: one hand-brushed mark or one deckled edge. Sprinkled crumpled-paper textures fake it.
- Hairline rules at 15 to 25 percent ink opacity are decoration; real controls need real borders.

## Interaction and motion
- Slow and unemphatic: 500 to 900 ms opacity fades with an 8 to 16 px rise, `cubic-bezier(.2, .6, .2, 1)`.
- A single ink-reveal (a `clip-path` or mask wipe over 900 to 1400 ms) is the one flourish, used once per page.
- Hover deepens colour from nezumi to sumi over 300 ms, or draws an underline in 400 ms. No bounce, no scale pop, no parallax, no scroll-jacking, no auto-advancing carousels.
- Leave moments of stillness; the pause is part of the style.
- Reduced motion: show everything at once, skip the reveal, keep colour transitions.

## Accessibility cautions
- The aesthetic invites faded text, thin Mincho and tiny captions. Hold 4.5:1, 16 px body and weight 400 or more, and use a sans for captions under 14 px.
- Vertical text is read in DOM order by assistive technology, but it can break find-in-page, selection and keyboard scrolling, and it forces horizontal scrolling when zoomed (WCAG 1.4.10 reflow). Keep it to short strings, never use it for essential navigation, and switch to `horizontal-tb` at narrow widths.
- Sparse layouts still need visible focus: a 2 px sumi outline with a 3 px offset, visible labels, and links that look like links (underline).
- Use `<ruby>` readings for rare kanji where the audience may need them, and mark decorative seals and brush marks `aria-hidden`.
- Forced-colors mode removes paper tints and low-alpha rules; give separators and the seal a real border in `CanvasText`.

## Common mistakes
- Mistaking uniform emptiness for ma, or leaving an empty hero with no content.
- Costume: cherry blossoms, red suns, torii, bamboo, brush fonts on Latin text, wave prints on a SaaS page.
- Pale grey text and hairline weights at small sizes.
- Latin type as an afterthought: default Times, missing `lang`, wrong glyph variants.
- Perfect symmetry, centred everything, faux-distressed textures throughout.
- Treating "Japanese" as one look when its web design spans dense portals to quiet craft sites.

## Typical mistakes of AI-generated versions
- A beige page with a centred serif title, a red circle, a cherry-blossom branch, an ensō PNG and "find your balance" copy.
- Random kanji such as 禅 or 道 used as ornament, Japanese text without `lang`, `letter-spacing: 0.3em` on everything, vertical text for the navigation bar, and a brush-script font on the English headline.

## How to build it
- Pattern: `style-japanese-minimalism`. No local source implements this style, so the recipe is original. Set up the tokens, then alternate tight groups and long pauses:

```css
:root { --washi: #F4EFE6; --sumi: #1C1B19; --nezumi: #6B665E; --shu: #B3261E;
        --ma: clamp(5rem, 14vw, 11rem); }
html { background: var(--washi); color: var(--sumi); }
body { font: 400 1rem/1.9 "Zen Kaku Gothic New", "Noto Sans JP", system-ui, sans-serif; line-break: strict; }
h1, h2 { font-family: "Shippori Mincho", "Noto Serif JP", serif; font-weight: 500;
         letter-spacing: .08em; font-feature-settings: "palt"; text-wrap: balance; }
/* English headline: lead with the Latin face, e.g. "Cormorant Garamond", "Shippori Mincho", serif */
.section { padding-block: var(--ma); }                 /* the long pause */
.group { display: grid; gap: .75rem; }                  /* the tight beat */
.tate { writing-mode: vertical-rl; text-orientation: mixed; letter-spacing: .12em; }
.seal { display: inline-block; inline-size: 1.6rem; block-size: 1.6rem; background: var(--shu); border-radius: 2px; }
a { text-decoration: underline 1px; text-underline-offset: .3em; }
a:focus-visible { outline: 2px solid var(--sumi); outline-offset: 3px; }
@media (max-width: 40rem) { .tate { writing-mode: horizontal-tb; } }
@media (forced-colors: active) { .seal { border: 1px solid CanvasText; } }
```

- For the general discipline of reduction (neutral ramp, one accent, designed quiet states), see `minimalism.md` in this folder. Check the finished page by removing one element at a time, then by asking a Japanese reader to review the copy and the typography.

## Sources
Original guidance written for this project; no upstream source files were used. WCAG 2.2 criterion 1.4.10 is cited by number only.
