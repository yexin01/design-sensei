---
title: "Product-led SaaS"
kind: design-style
summary: "Marketing and product sites where the real product interface is the hero: a clear value proposition, restrained polish, hairline structure, proof and a short path to trying it. Includes page anatomy, tokens, and how to avoid the generic AI-landing-page look."
source_ids: [design-md, taste-skill, vengeance-ui]
pattern_ids: [style-product-led-saas]
updated: "2026-10-09"
---

# Product-led SaaS

Product-led SaaS design lets the product speak. The page states one clear promise, shows the real interface early, backs it with proof and offers a short path to trying the product. The look is restrained and well-crafted: neutral grounds, one brand accent, hairline borders, tidy type and a few well-made micro-interactions. It is a category of trust, not a decoration style, so most of the craft is in structure and honesty.

## Visual characteristics
- A split or centred hero with headline, one-sentence support, a primary and a secondary action, and a real product visual.
- Hairline-divided sections, alternating text and product panels, bento feature grids.
- Neutral light or dark grounds with one accent; subtle gradients used for focus, not mood.
- Logos, quotes and numbers as proof; pricing and FAQ near the end; a repeated final call to action.

## When it fits, when it does not
- Fits: B2B and B2C software, developer tools, AI products, apps with a visible interface.
- Poor fit: products with no interface to show, emotion-led brands (fashion, hospitality), local services, anything where the proof is a physical thing.
- Supporting influences that work: minimalism, bento-layouts, dark-technical-developer-tools, swiss-international-typographic, restrained glassmorphism or aurora-gradient-mesh as a hero backdrop. Avoid maximalism and vaporwave.

## Typography
- A neutral grotesque (Inter, Geist, Public Sans) plus mono for code and identifiers.
- H1 48-72 px at weight 600-700, line-height 1.05-1.1, tracking -0.02 to -0.04em; section titles 28-40 px; body 16-18 px at 1.5-1.6; maximum 12-14 words in the H1.
- Use `text-wrap: balance` for headings and tabular numerals for pricing and metrics.

## Colour
- Tokens: page, surface, border (alpha based), text, muted text, accent, accent-hover, status colours. Dark and light versions defined together.
- The primary button needs 4.5:1 for its label: white on #1F6FEB is 4.63:1, white on #2F81F7 is only 3.75:1.
- Muted text at least 4.5:1 (see minimalism for examples); alpha borders at 8-12% are decoration, not control boundaries.
- Gradients: one soft radial behind the hero at low opacity. Avoid the default indigo-to-violet sweep.

## Composition and layout
- Page anatomy: header with a primary action, hero, proof strip, three to five feature sections (alternate sides or use a bento), a deep-dive on the main workflow, testimonials with real names, pricing, FAQ, final call to action, footer.
- Container 1100-1280 px, section padding 80-128 px, a 12-column grid. Show the product at native fidelity: real screenshots or a live component, never a `div` imitation.
- Keep the primary action visible in the sticky header on scroll.
- On phones stack sections, keep the hero action above the fold and compress the product visual rather than dropping it.

## Interaction and motion
- Short, purposeful: hover states 120-200 ms, section reveals 400-600 ms once, product demos as muted autoplay loops that pause off-screen.
- A moving border or beam on one featured element is enough; do not animate every card.
- Reduced motion: no reveals, demos start paused with a visible play control, loops stop.

## Accessibility cautions
- Autoplaying demo loops longer than five seconds need a pause control (WCAG 2.2.2).
- Gradient or glow backdrops behind headlines must be tested at their lightest point.
- Product screenshots need meaningful alt text describing what the interface shows.
- Pricing tables should be real tables or lists, and toggles (monthly/annual) real buttons with state.

## Common mistakes
- Vague promise copy, no real screenshot, logo strips of invented companies.
- Three identical feature cards with icons.
- Dark mode added as an inversion rather than designed.
- Competing calls to action and no clear primary.

## Typical mistakes of AI-generated versions
- A centred hero, violet-to-blue gradient, three icon cards, "10x faster" claims, invented testimonials with stock names, and a fake dashboard built from div rectangles. This is the stereotype the taste-skill catalogue of "AI tells" lists (generic names, fake round numbers, filler verbs, div-based fake screenshots).
- The same layout whatever the product does.

## How to build it
- Pattern: `style-product-led-saas`. Write the one-sentence promise and gather real proof before designing; then tokens, hero, anatomy.
- `vengeance-ui:src/components/landing/hero.tsx`, `vengeance-ui:src/components/landing/features.tsx` and `vengeance-ui:src/components/landing/cta.tsx` form a hairline-divided landing skeleton: a two-column hero with a primary and a secondary action, alternating two-column feature rows and a closing call to action, with a border-beam accent on one element.
- A consumer-service counterpart with ambient shadows, tonal layers and an 8 px rhythm is described as a DESIGN.md in `design-md:examples/paws-and-paths/DESIGN.md`.
- Anti-generic checklist: `taste-skill:skills/taste-skill/SKILL.md` section on AI tells and `taste-skill:skills/redesign-skill/SKILL.md` audit list. Treat their numeric rules as one opinion.

## Sources
Original guidance written for this project. design-md (Apache-2.0), taste-skill and vengeance-ui (MIT) are cited as reference only.
