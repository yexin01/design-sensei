---
title: "Minimalism"
kind: design-style
summary: "Remove everything that does not serve the task or message, then make what remains carry more: one typeface, a near-neutral palette, generous space and carefully designed quiet states. Includes the accessibility traps that minimal interfaces fall into."
source_ids: [astryx, taste-skill]
pattern_ids: [style-minimalism]
updated: "2026-10-09"
---

# Minimalism

Minimalism is reduction with a purpose. Each remaining element has to carry more weight, so typography, spacing, alignment and the quality of a few components do the work that ornament would otherwise do. It is not emptiness: a page with no content, vague copy and low-contrast grey text is unfinished, not minimal.

## Visual characteristics
- Few elements per screen and one idea per section; whitespace is the main structural tool.
- One type family (optionally plus a mono), restrained weights, no ornament.
- Near-neutral palette with a single accent; flat or nearly flat surfaces; low-alpha borders instead of heavy shadows.
- Quiet interaction states built from small tonal shifts, which means they must be designed deliberately.
- Product imagery or content is the only decoration.

## When it fits, when it does not
- Fits: portfolios, single-message product pages, focused tools, documentation, settings and forms, brands built on craft or restraint.
- Poor fit: dense dashboards, discovery-led commerce, products whose capability needs explaining, audiences who need strong affordances (low vision, older users), brands built on emotion or ornament. Minimalism moves complexity from the screen into the user's memory.
- Supporting influences that work: swiss-international-typographic, editorial, product-led-saas, dark-technical-developer-tools, bento-layouts, very light grain-and-texture. Avoid maximalism, cyberpunk and y2k.

## Typography
- A neutral grotesque or humanist sans: Inter, Geist, Public Sans, DM Sans (commercial: Soehne, Helvetica Now). One serif is acceptable for display only.
- Base 16-18 px with a ratio of 1.2-1.25. Display 40-72 px, tracking -0.02 to -0.03em, line-height 1.05-1.15. Body line-height 1.5-1.6, measure 55-70 characters.
- Weights 400, 500 and 600. Avoid 300 below 18 px. Let size and weight carry hierarchy, not colour alone.
- Balance headlines with `text-wrap: balance`; align text left.

## Colour
- Three or four neutral steps (page, surface, border, text) plus one accent for the primary action and focus; reserve status colours for status.
- Secondary text must still pass: #6B7280 on white is 4.83:1, while the very common #9CA3AF is 2.54:1 and fails. Disabled text must remain distinguishable from secondary text.
- A 1 px low-alpha border is decoration. If a border is the only thing that identifies an input or checkbox it needs 3:1 against its surface (WCAG 1.4.11).
- The Astryx neutral theme is a worked example: a quiet grayscale foundation whose status and interaction states stay recognisable in both colour modes (`astryx:packages/themes/neutral/neutral.spec.md`).

## Composition and layout
- Section padding 96-160 px on desktop and 64-96 px on phones; text column 640-720 px inside a 1100-1280 px container.
- Group by space and alignment first; add a card or border only when grouping fails without it (`astryx:docs/design/spatial-hierarchy.md`).
- Use one edge language per surface, either a hairline border or a soft shadow, not both at full strength (`astryx:docs/design/elevation-hierarchy.md`).
- Four to six visible navigation items with text labels. Do not hide primary navigation behind a hamburger on desktop.
- One filled primary button per view; everything else secondary.

## Interaction and motion
- Motion should be invisible: opacity plus an 8-12 px translate over 150-300 ms with a gentle ease-out; no parallax.
- Hover is a 4-8% tonal overlay, focus-visible is a 2 px ring in the accent with an offset, pressed is a darker tone or `scale(0.98)`.
- Loading uses quiet skeletons or a fixed-size spinner so layout does not jump.
- Reduced motion: keep opacity changes, drop translate and scale.

## Accessibility cautions
- The characteristic failure is low contrast and missing affordance: pale grey text, ghost buttons, icon-only controls with no label or tooltip.
- Keep targets at least 24 by 24 CSS px (WCAG 2.5.8), preferably 44 px on touch.
- Never remove focus outlines for aesthetics; restyle them instead.
- Fields need visible labels; placeholder text is not a label.

## Common mistakes
- Absence of content mistaken for minimalism: an empty hero, vague copy and no proof.
- Light grey text and thin weights at small sizes.
- Hover-only controls and gestures with no visible hint.
- Eight greys with no system, or no hierarchy at all because everything is the same size.

## Typical mistakes of AI-generated versions
- A centred hero, a soft gradient blob, three feature cards and pale grey body text, described as "clean and modern".
- Default heavy shadows and large pill radii applied to every container.
- Decorative glass or gradients added "for depth" in the same breath as asking for minimalism.

## How to build it
- Pattern: `style-minimalism`. Tokens: a four-step neutral ramp, one accent, six to eight spacing steps, two radii.
- Theme reference: `astryx:packages/themes/neutral/README.md` (a restrained theme with one sans family) and its spec above.
- A warm-monochrome, flat variant with muted pastel tags and flat bento tiles is written up in `taste-skill:skills/minimalist-skill/SKILL.md`. Its bans on particular typefaces are taste, not rules.
- Check the finished page by removing one element at a time: if nothing is lost, it should not have been there.

## Sources
Original guidance written for this project. astryx and taste-skill are MIT-licensed and cited as reference only.
