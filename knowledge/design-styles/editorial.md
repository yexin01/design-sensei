---
title: "Editorial design"
kind: design-style
summary: "Magazine and long-form publishing aesthetics for the web: a strong typographic hierarchy, deliberate image crops, hairline rules and asymmetric column grids that let copy and photography carry the page without app-style chrome."
source_ids: [astryx, fancy, taste-skill]
pattern_ids: [style-editorial]
updated: "2026-10-09"
---

# Editorial design

Editorial design takes its structure from magazines, newspapers and long-form journalism. The page is organised by reading roles (kicker, headline, standfirst, byline, body, caption, pull quote) and each role is visibly different from the others. Boxes, cards and icons are replaced by type, rules, space and photography. It only works with real copy and real images.

## Visual characteristics
- Five to six distinct text roles whose hierarchy is readable at a glance, before any word is read.
- Large display type over a quiet text face; image crops chosen on purpose (full-bleed, tight, or inset with a caption).
- Hairline rules, column rules and generous margins do the grouping work that cards do in app UI.
- Asymmetric multi-column grids; pull quotes and figures break the text measure deliberately.
- A restrained palette: paper tone, ink, and one accent used for kickers, links and rules.

## When it fits, when it does not
- Fits: publications, long-form journalism, essays, case studies, annual reports, cultural institutions, portfolios that include writing, brand storytelling.
- Poor fit: dashboards, checkout and other transactional flows, admin tools, filter-heavy catalogues, anything users scan for controls rather than read. Also poor when no real copy or photography will be supplied.
- Supporting influences that work: minimalism, swiss-international-typographic, grain-and-texture, a restrained motion-led-storytelling. Avoid mixing with glassmorphism or neumorphism.

## Typography
- Display face: a serif with stroke contrast (transitional, old-style or Didone: Playfair Display, Newsreader, Fraunces, Instrument Serif, Source Serif 4; commercial options include Tiempos and GT Sectra) or a heavy grotesque. 56-120 px on desktop via `clamp()`, line-height 0.95-1.1, tracking -0.01 to -0.03em.
- Text face: 17-20 px, line-height 1.5-1.65, weight 400, measure 60-72 characters (`max-width: 68ch`). Prefer fonts with an optical-size axis (Newsreader, Fraunces, Source Serif 4) so small sizes get sturdier forms.
- Kickers, bylines and captions: sans or mono at 11-13 px, uppercase only for two to four words, tracking +0.06 to +0.12em, weight 500-600.
- Reserve the display face for display sizes and let section headings use the text family. The Astryx gothic theme does exactly this: its distressed face is limited to the three display roles (`astryx:packages/themes/gothic/src/gothicTheme.ts`).
- Balance headlines with `text-wrap: balance` and body with `text-wrap: pretty` where supported. Left-aligned, ragged-right text is the safe default on the web.

## Colour
- Paper and ink: warm off-white (about #F7F3EA) with near-black ink (#1A1A1A) gives roughly 15:1. Pure white with pure black is harsher over long reads.
- One accent. A deep red such as #B3261E on that paper measures 5.9:1, so it can carry small link text; pale accents belong to rules and fills only.
- Keep secondary text honest. The common grey #767676 is only 4.1:1 on #F7F3EA; use #6B6B6B (4.8:1) or darker for captions and bylines.
- Photography supplies most of the colour. Grade images consistently (temperature, contrast) instead of tinting them with CSS filters.
- Dark variant: warm near-black (#14110F) with ivory text (#F5F0E6, about 16.6:1); keep body weight at 400 or above to limit halation.

## Composition and layout
- A 12-column grid with asymmetric spans (7/5, 8/4). Body copy in 6-7 columns, with a margin column for captions, notes or pull quotes.
- Section padding 96-160 px on desktop; vertical rhythm set by multiples of the body line-height.
- Use `<figure>` and `<figcaption>` with fixed `aspect-ratio` boxes so late-loading images do not shift the text.
- Break long text with a full-bleed image or colour block every three to five screens.
- On phones collapse to one column, keep kicker-headline-standfirst order, and turn pull quotes into inline blocks.

## Interaction and motion
- Motion supports reading, it does not perform. Fade and translate figures in (8-16 px, 400-700 ms, ease-out); never animate paragraphs line by line.
- Link underlines can animate offset or thickness over 150-200 ms. Image hover zoom stays at or below 1.03 inside an overflow-hidden frame.
- Optional extras: a reading-progress bar, mask reveals on lead images, parallax limited to a few percent of image height.
- Reduced motion: render every reveal in its final state, drop parallax, keep the progress bar static.

## Accessibility cautions
- Text over photography needs a scrim or a reserved text area; test the busiest region of the image, not the average.
- Do not justify text without controlled hyphenation (`hyphens: auto` with a correct `lang`); rivers hurt readers with dyslexia.
- Keep real heading levels (a kicker is not an `h1`), landmarks and a skip link. Mark repeated pull quotes `aria-hidden` so they are not read twice.
- Uppercase, widely tracked labels are fine for short strings and harmful for paragraphs; the Astryx typography note makes the same point (`astryx:docs/design/typography-hierarchy.md`).

## Common mistakes
- A display serif used for buttons, table headers and form labels.
- A measure over 90 characters because the grid column is wider than the text should be.
- Drop cap, pull quote, rule and kicker repeated in every section until none feels special.
- Hierarchy made from size alone instead of size, weight, case, colour and position together.
- Low-resolution lead images and mismatched photo grading, which undo the whole look.

## Typical mistakes of AI-generated versions
- "Editorial" becomes an oversized serif H1 above a centred three-card grid with an italic accent word; measure, captions and bylines are missing.
- One display serif (often Playfair Display) is applied to every heading level, so the hierarchy collapses.
- Placeholder copy and stock-photo grids hide the fact that the layout was never tested against real text lengths.

## How to build it
- Pattern: `style-editorial`. Define tokens first (type scale, measure, paper, ink, accent, rule weights), then the article template, then index pages.
- Headline reveal: `fancy:src/fancy/components/text/vertical-cut-reveal.tsx` (Motion-based; options `splitBy`, `staggerDuration`, `staggerFrom`, `autoStart`; it renders an `sr-only` copy and hides the split pieces from assistive tech). It has no reduced-motion branch, so wrap it and render plain text when `prefers-reduced-motion: reduce` matches.
- Hierarchy principles to check against: `astryx:docs/design/typography-hierarchy.md` (a draft record that distinguishes dense and editorial personalities while keeping role order).
- The Editorial Luxury archetype in `taste-skill:skills/soft-skill/SKILL.md` pairs warm paper tones, variable serifs and a faint grain overlay; treat its numbers as one opinion, not a rule.

## Sources
Original guidance written for this project. Local code is cited as reference only: astryx, fancy and taste-skill are MIT-licensed.
