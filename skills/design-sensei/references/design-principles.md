# Design principles

The visual fundamentals Claude applies while building any interface: hierarchy, rhythm, spacing, contrast, grouping, density, consistency and restraint.

## When to load this

Load it when laying out or reviewing any screen, before the more specific [typography](typography.md), [colour](color-systems.md) and
[layout](layout-composition.md) references. Values below are starting points and heuristics unless labelled as a standard. A project's own tokens and
`DESIGN.md` outrank them.

## Decisions to make

| Decision | Options | How the dials change it |
| --- | --- | --- |
| Number of hierarchy levels per viewport | 3 (calm) to 5 (dense) | `visual_density` 1-3: 3 levels; 4-7: 3-4; 8-10: up to 5 with strong role contrast |
| Spacing scale and base unit | 4 px base for dense UI, 8 px base for airy pages | density low: favour the large steps; high: favour the small steps |
| Grouping method | space and alignment first, then dividers, then cards | density high: dividers and tonal bands; low: space alone |
| Emphasis budget | one primary action and one focal element per view | `design_variance` high: allow one deliberate break; never two |
| Rule-breaking | none (low), one planned break per page (mid), several coordinated breaks (high) | `design_variance` |

## Hierarchy

Hierarchy is the order in which the eye moves. Build it deliberately, then test it.

1. Name the one thing the viewer must see first (the focal element) and the one action they should take (the primary action). Everything else is subordinate.
2. Make that element win on at least two channels at once: scale, weight, colour, position, isolation. Size alone is the weakest channel.
3. Use 3 to 5 distinct text roles (display, section heading, body, label, supporting) and keep adjacent roles visibly different in size, weight or
   colour. The Astryx type-role record states this requirement (DR1 and DR2 in `astryx:docs/design/typography-hierarchy.md`, a draft
   record; use it as stated intent).
4. Squint test: blur or shrink a screenshot to thumbnail size. If the primary action and the focal element are not the first two things you see,
   the hierarchy is wrong. Fix by removing emphasis from competitors before adding it to the winner.
5. One filled primary button per local group. Secondary actions use outline or text styles. Never make every action loud.

## Contrast of scale, weight and colour

| Channel | Useful contrast | Failure |
| --- | --- | --- |
| Scale | each text role at least one ratio step (1.2-1.5) from its neighbour; display text 3x or more the body size on marketing pages (heuristic) | many sizes within 10% of each other |
| Weight | pair 400 body with 600-700 emphasis; with a variable font use the axis for a clear step | everything at 500; weight 300 below 18 px |
| Colour | text, muted text, accent: three tones, measured | grey levels with no system; accent used for decoration |
| Position and space | isolate the focal element with space on all sides | focal element surrounded by equal-weight neighbours |
| Case and tracking | uppercase only for 2 to 4 word labels, with +0.06 to +0.12em tracking | uppercase paragraphs |

Hierarchy must not rely on colour alone (WCAG 1.4.1); pair colour changes with weight, position, an icon or text.

## Spacing scale and rhythm

- Pick a base unit (4 px or 8 px) and generate a scale from it. A usable 4 px-based scale: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128. Astryx ships a
  4 px-stepped spacing token set from 2 px to 48 px (`--spacing-0-5` to `--spacing-12`); see [themes and tokens](../../../knowledge/components/astryx-themes-and-tokens.md).
- Expose the scale as tokens: `--space-1` ... `--space-10`. Components use tokens, never raw pixel values.
- Three levels of gap, always increasing outward: local (label to value, icon to text), group (between peer items), section (between concerns).
  Local < group < section, every time. This is DR2 in `astryx:docs/design/spatial-hierarchy.md`.
- Proximity is the grouping signal: related things sit closer to each other than to anything else. Equal gaps everywhere erase the structure.
- Rhythm: choose line-height from the scale (24 px line on a 4 px or 8 px grid) and set vertical spacing as multiples of it. Vary section padding
  deliberately (for example hero larger, proof strip smaller) instead of one padding everywhere.
- Section padding by `visual_density`: low `clamp(5rem, 10vw, 10rem)`; mid `clamp(4rem, 7vw, 6rem)`; high `clamp(1.5rem, 3vw, 3rem)`
  (values from the [dials recipe](../../../knowledge/implementation-recipes/art-direction-brief-from-dials.md)).

```css
:root {
  --space-1: 0.25rem; --space-2: 0.5rem; --space-3: 0.75rem; --space-4: 1rem;
  --space-6: 1.5rem;  --space-8: 2rem;   --space-12: 3rem;   --space-16: 4rem;
  --space-24: 6rem;   --space-32: 8rem;
  --section-pad: clamp(4rem, 7vw, 6rem);   /* swap per visual_density band */
}
```

## Proximity and alignment

- Group by space and alignment before adding a card, border or background (DR3 in `astryx:docs/design/spatial-hierarchy.md`). Add a container only when grouping fails without it.
- Align to a small number of shared edges: left text edge, column edges, baseline. Mixed left, centre and right alignment in one section reads as noise.
- Left-align body text. Centre only short, single-block statements (a hero line, a call to action) and never a paragraph over three lines.
- Optical alignment: large display type has side bearings that look indented; pull it back by a small negative margin (check by eye). Icons next to text align to the text x-height or cap height.
- Reflow must preserve grouping: when columns stack, local, group and section gaps stay distinguishable (DR5 of the same record).

## Density by `visual_density`

| Band | Body size / leading | Gaps | Containers | Notes |
| --- | --- | --- | --- | --- |
| 1-3 airy | 18 px / 1.65 | 40 px between items | space only; card only where a boundary is functional | one idea per screen; large display type acceptable |
| 4-7 balanced | 16 px / 1.6 | 24 px | cards for related groups, hairlines between rows | 2-3 columns; one dense section allowed |
| 8-10 dense | 14 px body, 12 px labels / 1.45 | 12 px | 1 px dividers and tonal bands instead of boxes | 44 px touch targets still apply; tabular numerals |

Dense does not mean small hit areas: keep controls at least 24 x 24 CSS px (WCAG 2.2 AA minimum) and 44 px where touch is expected. Row height of 32-36 px
works with a pointer; use larger rows on coarse pointers.

## Consistency rules

- One token set for colour, type, spacing, radius, shadow and timing. A value that is not a token is a bug.
- One radius rule (all sharp, or one scale of 2-3 steps with a written meaning such as control < container < page).
- One edge language per surface: a defined border or soft elevation, not both at full strength. Focus and validation rings are not elevation
  (`astryx:docs/design/elevation-hierarchy.md`, DR3 and DR4).
- One icon set, one stroke weight, one corner style. No hand-drawn SVG icons mixed with a library.
- One animation system and one easing family for the whole project (see [motion design](motion-design.md)).
- Same component, same behaviour: a button looks and responds the same in the header and in a card. Define hover, focus-visible, pressed and
  disabled once, for every interactive component.
- Name things by role (`--color-surface`, `--text-muted`), not by value (`--grey-600`) in component code.

## Restraint

- Every element earns its place: if removing it changes nothing, remove it. Check by deleting one element at a time.
- One accent, one focal effect per viewport, one marquee or ticker per page. Several effects fighting for attention cancel out.
- Prefer a quiet default and one loud moment over medium volume everywhere.
- Decoration (gradients, glass, grain, glow) is a finishing layer that must stay below text and never reduce measured contrast.
- When unsure between two options, choose the one with fewer parts that still satisfies the brief.

## Checklist before saying done

- [ ] Focal element and primary action identified, and they pass the squint test
- [ ] 3 to 5 type roles, each distinguishable from its neighbour by more than size alone
- [ ] Spacing from the token scale only; local < group < section gaps hold at every width
- [ ] Alignment edges consistent per section; no stray centred paragraphs
- [ ] Density matches `visual_density`; touch targets at least 24 x 24 CSS px (44 where touch is expected)
- [ ] One radius rule, one edge language, one icon set, one easing family
- [ ] Hierarchy and state never depend on colour alone
- [ ] Empty, loading, error and long-text states keep the same hierarchy as the populated state

## Common mistakes

- Equal spacing everywhere, so groups are invisible; then cards added to compensate.
- Every element emphasised (bold, coloured, boxed), leaving no hierarchy.
- Type sizes that are arbitrary nearby values (15 px, 17 px, 19 px) instead of scale steps.
- Padding set per component by feel; sibling sections with different paddings for no reason.
- Dense UI built by shrinking fonts below 12 px instead of tightening spacing and removing chrome.
- Centred everything on a content-heavy page; long centred paragraphs.
- Shadow plus border plus gradient plus glow on one surface.

## Related

Patterns: [[astryx-typography-scale]], [[astryx-theme-token-system]], [[astryx-responsive-layout-primitives]], [[style-minimalism]],
[[style-swiss-international-typographic]], [[taste-skill-anti-generic-ui-checklist]].
Notes: [minimalism](../../../knowledge/design-styles/minimalism.md), [Swiss style](../../../knowledge/design-styles/swiss-international-typographic.md),
[Astryx themes and tokens](../../../knowledge/components/astryx-themes-and-tokens.md), [dials recipe](../../../knowledge/implementation-recipes/art-direction-brief-from-dials.md).
References: [art-direction.md](art-direction.md), [typography.md](typography.md), [color-systems.md](color-systems.md),
[layout-composition.md](layout-composition.md), [accessibility.md](accessibility.md), [responsive-design.md](responsive-design.md).
