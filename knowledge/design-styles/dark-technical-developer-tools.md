---
title: "Dark technical / developer tools"
kind: design-style
summary: "Dark-first, dense, keyboard-centric interfaces for developers and operators: cool near-black surfaces, alpha borders, monospace for code and identifiers, syntax colours and fast, quiet motion. Includes dark-mode contrast numbers and the traps of grey-on-black."
source_ids: [astryx, taste-skill, vengeance-ui]
pattern_ids: [style-dark-technical-developer-tools]
updated: "2026-10-09"
---

# Dark technical / developer tools

This is the visual language of terminals, editors, observability dashboards and API documentation: dark by default, information-dense, keyboard-first and unadorned. The user is in the interface for hours, so the style optimises for sustained legibility, scanning and speed. It is a functional style; its "cool" comes from precision, not effects.

## Visual characteristics
- Near-black cool surfaces (not pure black) in three or four steps; borders drawn as low-alpha white lines.
- Monospace for code, identifiers, hashes and logs; sans for UI; syntax-highlight palettes.
- Dense tables, split panes, sidebars with collapsible sections, command palettes, keyboard hint chips.
- One accent hue plus status colours; terminal motifs (prompts, caret, command output) in marketing.

## When it fits, when it does not
- Fits: developer tools, infrastructure and observability, API docs, security consoles, data and ML workbenches, CLI product sites.
- Poor fit: consumer, wellness and children's products, or audiences who read in bright environments without a light mode.
- Supporting influences that work: minimalism, swiss-international-typographic, bento-layouts, product-led-saas, restrained glassmorphism, the terminal side of cyberpunk and brutalism. Avoid organic-tactile, claymorphism and y2k.

## Typography
- UI sans at 13-14 px in product (16 px on marketing pages), weights 400-600, tracking 0 to -0.01em. Mono at 12-13 px, line-height 1.5-1.6; enable tabular numerals and, where wanted, programming ligatures.
- Candidate families: Inter or Geist for UI; JetBrains Mono, IBM Plex Mono or Geist Mono for code.
- Do not set paragraphs in monospace. Use mono for data and the technical voice only.

## Colour
- Surfaces such as #0D1117 for the page with the next step up for panels. Primary text near #E6EDF3 (16.0:1), muted text #8B949E (6.15:1). Grey #666 on #0A0A0A is only 3.45:1 and fails.
- Avoid maximum-white text on pure black; the glare and halation tire eyes over long sessions.
- Alpha borders: white at 12% on #0D1117 is about 1.4:1. That is fine for separators and wrong for the edge of an input or button, which needs 3:1 (WCAG 1.4.11).
- Accent: #58A6FF is 7.5:1 on that surface. White on #1F6FEB is 4.63:1 for filled buttons.
- Status never relies on red versus green alone; add icons or words. Design a real light theme too, not an afterthought.
- Syntax palettes need light and dark pairs; the Astryx themes define each syntax token as a [light, dark] pair (`astryx:packages/themes/y2k/src/y2kTheme.ts`).

## Composition and layout
- Panels and split panes with resizable gutters, sticky table headers, a persistent sidebar, a top bar with search or a command palette.
- Prioritise density without crowding: 4 px grid, 32-36 px row height, 8-12 px cell padding.
- Code blocks have a language label, copy button and horizontal scroll rather than wrapping.
- Marketing pages for tools reuse product components with real data, not drawings.

## Interaction and motion
- Fast and quiet: 80-160 ms transitions, no entrance choreography in product screens. Skeletons for loading.
- Keyboard first: visible shortcuts (`kbd` chips), command palette, focus management, a focus ring that is visible on dark (2 px, accent or white).
- Terminal typing demos are pausable and finite; blinking carets blink at about 1 Hz and stop under reduced motion.
- Reduced motion: remove typing animation and show the final output; keep state changes instant.

## Accessibility cautions
- Grey-on-near-black text is the commonest failure; measure every muted token.
- Dark-on-dark focus rings disappear. Test keyboard navigation in the dark theme specifically.
- Respect `prefers-color-scheme` but also provide a manual switch; some users need light mode for astigmatism or glare.
- Dense tables need real table semantics, sortable column state announced, and zoom reflow.

## Common mistakes
- Pure `#000` backgrounds with `#fff` text, or a neon-green "hacker" palette everywhere.
- Fake terminals showing commands that do not exist; decorative glow on panels.
- Borders as the only separation for interactive controls.
- Mono type for body copy; no light theme.

## Typical mistakes of AI-generated versions
- Black page, green or purple glow, glass cards, a fake terminal, and `text-gray-500` secondary text that measures below 4.5:1.
- Code samples that are invented rather than taken from the product.

## How to build it
- Pattern: `style-dark-technical-developer-tools`. Define paired light and dark tokens first; verify muted text and focus rings; then components.
- A dark-only theme reference: the Astryx gothic theme uses a deep neutral body (#101314) and keeps its decorative display face for display sizes only (`astryx:packages/themes/gothic/src/gothicTheme.ts`).
- Small components: `vengeance-ui:src/components/ui/kbd.tsx` (keyboard chip with an optional group), `vengeance-ui:src/components/ui/command.tsx` (cmdk-based palette), `vengeance-ui:src/components/ui/code-block.tsx` (server-side Shiki highlighting with a copy button).
- The tactical-telemetry archetype in `taste-skill:skills/brutalist-skill/SKILL.md` (dark substrate, mono, ASCII framing, scanlines) is the decorative end of this family; use it for marketing flourishes only.

## Sources
Original guidance written for this project. astryx, taste-skill and vengeance-ui are MIT-licensed and cited as reference only.
