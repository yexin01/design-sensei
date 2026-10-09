# Typography

Choose, scale, load and animate type so it carries hierarchy and personality without hurting readability or performance.

## When to load this

Load it for step 2 (typography decision) and again at implementation time when writing the type tokens, loading fonts or adding text effects. A project
that already ships a type system keeps it; extend it instead of adding a second family. Values are starting points; standards (WCAG) are labelled.

## Decisions to make

| Decision | Options | Dial influence |
| --- | --- | --- |
| Families | 1 family (low variance), display + text (mid), expressive display + text, at most 2 (high); add mono only for code and data | `design_variance` |
| Scale ratio | 1.2 (dense), 1.25 (default), 1.333 (marketing), 1.5 (dramatic) | density 8-10: 1.125-1.2; density 1-3: 1.25-1.333; variance 8-10: 1.5 for the top steps only |
| Body size and leading | 18 / 1.65 (airy), 16 / 1.6 (balanced), 14 / 1.45 (dense) | `visual_density` |
| Fonts source | system stack, self-hosted woff2, hosted service | `performance_budget`, `allowed_dependencies`, privacy needs |
| Type motion | none, reveal on entry, axis morph, cursor proximity | `motion_intensity` (see below) |

## Pairing logic

Pair by contrast of structure, not by taste adjectives. Use one pairing rule per project and write it into the brief.

| Pairing | Why it works | Typical use |
| --- | --- | --- |
| Serif display + neutral sans text | clear role split; the serif carries personality | editorial, hospitality, portfolios ([[style-editorial]]) |
| Heavy grotesque display + same-family text | one voice, hierarchy from weight and size | product, Swiss ([[style-swiss-international-typographic]]) |
| One variable family, wide weight range | cohesion, fewer files | minimal, tools ([[style-minimalism]]) |
| Sans text + mono for data | separates prose from code, ids, numbers | developer tools ([[style-dark-technical-developer-tools]]) |
| Display with animatable axes + stable text sans | motion only on the display line ([[style-kinetic-typography]]) | brand moments, campaigns |

Rules of thumb (heuristics): two families is the usual maximum; do not pair two faces that are similar but not the same (two geometric sans); match x-height
roughly when mixing families at the same size; reserve the display face for display roles and let section headings use the text family.
The Astryx gothic theme limits its decorative face to the three display roles for this reason (`astryx:packages/themes/gothic/src/gothicTheme.ts`).

Families named in the style notes: serif display Newsreader, Fraunces, Source Serif 4, Playfair Display, Instrument Serif; neutral sans Inter, Geist,
Public Sans, DM Sans; mono JetBrains Mono, IBM Plex Mono, Geist Mono; variable families with useful axes Roboto Flex, Bricolage Grotesque, Anybody, Recursive.
Check each font's licence before self-hosting. One opinionated source discourages Inter and some serifs as unexamined defaults
([taste-skill note](../../../knowledge/design-intelligence/taste-skill.md)); the point is to choose on purpose, not to ban a family.

## Type scale as tokens

Generate sizes from a base and ratio, then name them by role. Use `rem` so user font-size settings and 200% zoom work (WCAG 1.4.4); never size text with `vw` alone.

```css
:root {
  /* ratio 1.25 from 1rem; fluid steps use clamp(min, intercept + slope vw, max) between 20rem and 80rem viewports */
  --text-sm: 0.875rem;
  --text-body: clamp(1rem, 0.917rem + 0.417vw, 1.25rem);        /* 16px to 20px */
  --text-lead: clamp(1.125rem, 1rem + 0.625vw, 1.5rem);          /* 18px to 24px */
  --text-h3: clamp(1.25rem, 1.083rem + 0.833vw, 1.75rem);        /* 20px to 28px */
  --text-h2: clamp(1.75rem, 1.333rem + 2.083vw, 3rem);           /* 28px to 48px */
  --text-display: clamp(2.5rem, 1.333rem + 5.833vw, 6rem);       /* 40px to 96px */
  --leading-display: 1.05; --leading-heading: 1.2; --leading-body: 1.6;
  --tracking-display: -0.03em; --tracking-label: 0.08em;
}
```

How the fluid values are derived: `slope = (max - min) / (maxViewport - minViewport)`, `intercept = min - slope * minViewport`, with viewports in rem (20 and 80).
Put the intercept in rem and the slope in `vw` (slope x 100). Verify at both ends. The dials recipe ([art-direction recipe](../../../knowledge/implementation-recipes/art-direction-brief-from-dials.md))
contains a generator that emits a scale from the three dials.

Astryx offers a complete worked model: base 14 px at ratio 1.2 by default, suggested starts dense 12 / 1.125 and airy 16 / 1.25, 4 px-snapped leading, semantic roles
(heading 1-6, body, large, label, supporting, code, display 1-3) and a 16 px mobile base on coarse pointers ([[astryx-typography-scale]],
[themes and tokens](../../../knowledge/components/astryx-themes-and-tokens.md)). Astryx also floors text controls at 16 px on iOS Safari; do the same for form inputs.

## Measure, leading and rhythm

| Property | Value | Notes |
| --- | --- | --- |
| Line length | 55-75 characters; `max-width: 65ch` to `68ch` | heuristic; editorial notes use 60-72, minimal 55-70. Never above about 90 |
| Body leading | 1.5-1.65 | longer lines and smaller x-height need more |
| Heading leading | 1.1-1.25; display 0.95-1.1 | tighten as size grows |
| Tracking | display -0.01 to -0.04em; body 0; small uppercase labels +0.06 to +0.12em | do not animate tracking over large ranges (reflow) |
| Alignment | left-aligned, ragged right | justify only with `hyphens: auto` and a correct `lang` |
| Wrapping | `text-wrap: balance` for headings, `text-wrap: pretty` for body | progressive enhancement; harmless where unsupported |

Respect user text-spacing overrides (WCAG 1.4.12): no fixed-height text containers, no clipping of descenders in masks. Keep real heading levels in order; style a
kicker or eyebrow with a class, not with `h1`.

## Weights

- Use 2 to 3 weights: 400 body, 500 or 600 emphasis and UI labels, 600 or 700 headings. More than 4 weights usually means the hierarchy is made of noise.
- Avoid weight 300 below 18 px and text on tinted or textured backgrounds below weight 400 ([[style-grain-and-texture]] lowers perceived contrast).
- On dark backgrounds keep body at weight 400 or above (thin strokes break up) and avoid maximum-white text on pure black, which glares over long reads.
- With a variable font, load the single variable file and set weights with `font-weight`; use `font-optical-sizing: auto` where an `opsz` axis exists so small sizes get sturdier forms.

## Display versus text

- Display styles start around 28 px: tight leading, negative tracking, one idea per line, 12 words or fewer. Use the optical-size or display cut of the family if one exists.
- Text styles (14-20 px) need open spacing, regular weight, high-contrast ink. Do not set paragraphs in a display face or in monospace.
- UI labels and numbers: sans at 12-14 px, weight 500-600; uppercase only for 2 to 4 words.
- Numerals: `font-variant-numeric: tabular-nums` for tables, prices, counters and anything that updates; `lining-nums` in UI; oldstyle only in running editorial text;
  `slashed-zero` in mono. Feature support depends on the font, so check the specimen.
- Quotes and italics: use the family's real italic. For descender clearance on italic or masked reveals, add line padding.

## Loading fonts

1. Prefer a system stack when the brief allows it. Otherwise self-host `woff2` (privacy, no third-party request) or use a hosted service and accept the extra origin.
2. Declare `@font-face` with `font-display: swap` for text faces (content visible immediately in the fallback). Use `optional` for decorative display faces so a slow
   network never reflows the hero. Avoid `block`.
3. Preload only the one or two files used above the fold, with `as="font" type="font/woff2" crossorigin`. Subset to the needed scripts with `unicode-range`.
4. Budget: at most 2 families and 3 to 4 files on the critical path (heuristic); one variable file usually beats several static weights.
5. Match the fallback to the web font to prevent layout shift (CLS target 0.1 or less):

```css
@font-face {
  font-family: "Body Fallback";
  src: local("Arial");
  size-adjust: <computed>; ascent-override: <computed>; descent-override: <computed>; line-gap-override: <computed>;
}
body { font-family: "Body", "Body Fallback", system-ui, sans-serif; }
```

   Compute the four values from the real font's metrics with a metrics tool; do not guess them. Frameworks that bundle fonts (for example `next/font`) can generate
   the adjusted fallback for you; check the framework docs for the current behaviour.
6. Split or measure text only after fonts load (`document.fonts.ready`), otherwise line splits and widths are wrong.

## Type effects and motion

Static final state first, reduced-motion path second, effect third. Effects belong to display lines of about 12 words or fewer, never to body text, forms or errors.

| Need | Pattern (reuse class) | Notes |
| --- | --- | --- |
| Masked line reveal | [[gsap-split-text-reveal]] (license_review_required) | split lines only; use `gsap.matchMedia` for reduced motion |
| Per-letter or word reveal | [[fancy-vertical-cut-reveal]] (copy_with_attribution) | has `sr-only` copy; add your own reduced-motion branch |
| Axis morph on hover | [[fancy-variable-font-text]] (copy_with_attribution) | needs a variable font with the named axes; reserve width for the heaviest weight |
| Cursor proximity | [[fancy-cursor-proximity-text]] (copy_with_attribution) | measures every glyph each frame; keep strings short; needs a touch alternative |
| Scramble or swap | [[fancy-scramble-text]], [[fancy-letter-swap-text]] (copy_with_attribution) | accessible copy must be the final string |
| Count-up, flip-fade, morph | [[vengeance-ui-kinetic-text-effects]] (copy_with_attribution) | check reduced-motion handling before use |
| Lightweight reveals | [[react-bits-lightweight-text-effects]] (license_review_required) | follow `react-bits` terms; do not republish its code |
| Highlighter underline | [[fancy-text-highlighter]] (copy_with_attribution) | good low-motion emphasis |

`motion_intensity` 1-3: no type animation. 4-7: one headline reveal (400-900 ms, stagger 20-60 ms per character or by word, total near 800 ms), underline hover.
8-10: kinetic type allowed, one kinetic element per viewport, with a static equivalent. When text is split into spans, expose the full string once (`sr-only` text or `aria-label`)
and hide the fragments with `aria-hidden`. Copy only from sources whose reuse class allows it, and keep notices (see [source usage](source-usage.md)).

## Checklist before saying done

- [ ] Families, scale ratio, body size, leading and measure written down and tokenised
- [ ] Sizes in `rem`, fluid steps use `clamp()` with a rem intercept; page still works at 200% zoom
- [ ] At most 2 families, 2 to 3 weights in use; display face confined to display roles
- [ ] `font-display` set; critical files preloaded; fallback metrics adjusted; no visible layout shift on load
- [ ] Body line length within about 55-75 characters at every breakpoint
- [ ] Contrast measured on the real backgrounds (see [colour](color-systems.md)); no text under 12 px; form controls 16 px or larger
- [ ] Tabular numerals where numbers align or update; real heading levels in order
- [ ] Every text effect has a static final state and a reduced-motion path; split text keeps one accessible copy

## Common mistakes

- One family at default sizes, with hierarchy made from bold only.
- A display serif applied to buttons, table headers and form labels.
- Viewport-unit-only font sizes that ignore user zoom.
- Splitting text before fonts load, or splitting paragraphs, which hurts selection, translation and find-in-page.
- Measure set by the grid column instead of the text (lines of 100+ characters).
- Animating weight or tracking on long strings, causing reflow and shift.
- Three or more weights of three families loaded for a page that uses four styles.
- Uppercase paragraphs and widely tracked small text (see `astryx:docs/design/typography-hierarchy.md`).

## Related

Patterns: [[astryx-typography-scale]], [[style-editorial]], [[style-kinetic-typography]], [[style-swiss-international-typographic]].
Notes: [editorial](../../../knowledge/design-styles/editorial.md), [kinetic typography](../../../knowledge/design-styles/kinetic-typography.md),
[Swiss style](../../../knowledge/design-styles/swiss-international-typographic.md), [minimalism](../../../knowledge/design-styles/minimalism.md),
[Fancy components](../../../knowledge/components/fancy.md), [GSAP](../../../knowledge/animations/gsap.md),
[GSAP text reveal recipe](../../../knowledge/implementation-recipes/gsap-text-reveal-and-stagger.md),
[Fancy letter swap recipe](../../../knowledge/implementation-recipes/fancy-letter-swap-text.md).
References: [art-direction.md](art-direction.md), [design-principles.md](design-principles.md), [color-systems.md](color-systems.md),
[layout-composition.md](layout-composition.md), [motion-design.md](motion-design.md), [accessibility.md](accessibility.md), [performance.md](performance.md).
