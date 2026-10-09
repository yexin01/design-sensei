---
title: "Flat design"
kind: design-style
summary: "Interfaces built from solid colour planes, simple geometric icons and type-led hierarchy, with no simulated depth. Covers the semi-flat compromise, contrast of popular flat palettes, how to restore affordance without shadows, and a short CSS recipe."
source_ids: [design-md]
pattern_ids: [style-flat-design]
updated: "2026-10-09"
---

# Flat design

Flat design removes every cue that pretends an element is a physical object: bevels, gloss, textured surfaces and realistic shadows. What remains is solid colour planes, simple geometric glyphs, clean sans-serif type and a lot of spacing. Hierarchy is carried by size, weight, colour and position instead of depth. It rose in the early 2010s as a reaction to heavily textured interfaces and it is now so common that many people no longer name it. Its weakness is also its signature: when nothing is raised, nothing says "press me" unless you design that signal on purpose.

## Visual characteristics
- Solid fills with no gradients; separation by tone, whitespace and alignment rather than by shadow.
- Small radii (0-8 px) or none; consistent stroke weight across icons (usually 1.5-2 px outlined, or one solid family).
- A tight palette: one brand hue, one or two accents, and a neutral ramp of five to seven steps.
- Flat illustration: geometric figures, spot art and simplified diagrams in the same palette as the interface.
- Large type and big touch targets; labels next to icons.
- Semi-flat is the common practical variant: still no gradients or bevels, but one very soft shadow is allowed on floating layers such as menus and dialogs.

## When it fits, when it does not
- Fits: marketing sites, content-first apps, onboarding, icon-led mobile screens, infographics, data summaries with simple charts, and any product that must render fast on weak devices or print cleanly in one colour.
- Poor fit: dense tools where several overlapping layers must read as a stack, interfaces for first-time users who need strong signifiers, and brands whose promise is craft, warmth or luxury.
- Supporting influences that work: minimalism, swiss-international-typographic, product-led-saas, bento-layouts, bauhaus. Avoid skeuomorphism, glassmorphism, neumorphism and liquid-materials, which all depend on simulated depth.

## Typography
- Neutral humanist or grotesque sans-serifs: Inter, Source Sans 3, Work Sans, Nunito Sans or the system UI stack. One family is enough.
- Use only three weights: 400 for body, 600 for labels and buttons, 700 for headings. Avoid weights below 400 on coloured fills.
- Body 16-18 px at line-height 1.5; headings 28-56 px at 1.1-1.2 with tracking 0 to -0.02em; small labels 12-13 px at +0.02em, never below 12 px.
- Since there is no depth to rank things, give each role a distinct size and weight pair and keep it fixed across the product.

## Colour
- Many popular "flat" palettes use bright mid-tone fills that fail with white text: white on #2980B9 is 4.3:1, on #E74C3C 3.8:1, on #16A085 3.3:1, on #27AE60 2.9:1, on #E67E22 2.8:1 and on #F1C40F 1.7:1.
- Either darken the fill until white text passes, or keep the bright fill and switch to dark ink. Verified pairs on a ground of #EEF2F5: white on #0F5BC4 is 6.3:1, white on #0B7A4B is 5.4:1, white on #C2391F is 5.4:1, and #1B2A38 on #F2C94C is 9.2:1.
- A filled control must still stand out from its ground: #1F6FD1 on #EEF2F5 is 4.4:1, but a yellow #F2C94C fill on the same ground is only 1.4:1, so give light fills a 2 px ink border.
- Secondary text #5F6C79 is 5.4:1 on white and 4.8:1 on #EEF2F5. Light-grey placeholder text such as #8A97A3 is 2.98:1 on white, well under the 4.5:1 text minimum.
- White cards on a pale ground (white on #EEF2F5 is only 1.13:1) are a soft grouping cue, not an edge. Do not count them as the boundary of an input or button.
- Dark mode needs its own steps: a light-tinted blue such as #7FB3FF is 7.7:1 on #14202B. Do not invert the light palette.

## Composition and layout
- Build on an 8 px spacing scale and a simple column grid; whitespace does the grouping work that shadows used to do.
- Alternate full-width colour bands to change sections. Place icon and label together, left aligned.
- Use tonal layers (ground, card, selected row) for hierarchy and keep each step visibly different from the previous one. When tones are too close, add a 1-2 px border using a colour with at least 3:1 against both neighbours.
- Reserve the brand hue for the single primary action in a view; neutrals carry everything else.
- State the rule for depth explicitly in the design tokens: either "no elevation at all" or "one overlay shadow only". The design.md specification asks for exactly this, saying a flat design should describe how hierarchy is conveyed through borders and colour contrast (`design-md:docs/spec.md`, Elevation and Depth section).

## Interaction and motion
- Without shadows, state must be carried by colour, outline and shape. Hover darkens the fill by roughly 8-10%, pressed by 16-20%, selected adds a check or a bar, and focus adds a 3 px outline with a 2-3 px offset.
- Disabled controls need a text or icon cue as well as lower opacity; 38% ink on the ground is only 2.2:1, so never use it for anything the user must read.
- Motion is short and plain: 100-200 ms colour fades, 150-250 ms slides, ease-out. No bounce or parallax.
- Reduced motion: state changes are already near-instant; remove slide-ins and keep colour changes.

## Accessibility cautions
- Signifiers: flat buttons, links and fields must be recognisable without hover. Underline inline links or give them a non-colour cue (WCAG 1.4.1), and give inputs a visible border or underline of at least 3:1 (WCAG 1.4.11). A field filled #E5EBF0 on white is 1.2:1 and has no discernible edge.
- Icon-only controls need a text label or an accessible name; flat glyphs are especially ambiguous.
- Do not rely on hue alone for status. Pair red and green with words or shapes.
- Forced-colors mode replaces fills with system colours, so a fill-defined button loses its shape. Give controls a `border: 2px solid transparent`, which becomes a visible system-colour border in forced-colors mode.
- Large flat colour fields can be glaring for people with light sensitivity; offer a dark scheme and avoid pure saturated backgrounds behind long text.

## Common mistakes
- Treating "flat" as "borderless": every element is the same tone, nothing reads as interactive.
- Bright flat fills with white text, and light grey text on white for secondary copy.
- A different accent colour for every section, which dilutes the primary action.
- Mixing styles: a flat layout with large soft shadows and gradient buttons is semi-flat at best and incoherent at worst.
- Ultra-thin type and hairline icons that disappear at small sizes.
- Ignoring touch size because the visuals look small and tidy; keep targets at 44 px or more.

## Typical mistakes of AI-generated versions
- White cards on a near-white page with grey text, a purple-to-blue gradient button and a big diffuse shadow, all labelled "flat".
- Identical rounded rectangles for buttons, inputs and tags so the user cannot tell which are clickable.
- Pastel icon blobs behind every feature with no labels and low-contrast captions.
- Five random accent colours in the first screen.

## How to build it
- Pattern: `style-flat-design`. No local source contains a flat-design implementation, so this recipe is original. Define tokens first, then let tone, border and type carry hierarchy:

```css
:root { --ink: #1B2A38; --ground: #EEF2F5; --card: #FFFFFF; --edge: #5F6C79;
  --brand: #0F5BC4; --brand-hover: #0B4AA2; --brand-press: #083A82; }
body { background: var(--ground); color: var(--ink); font: 400 1rem/1.5 Inter, system-ui, sans-serif; }
.card { background: var(--card); border-radius: 8px; padding: 24px; }
.btn { background: var(--brand); color: #fff; font-weight: 600; padding: 12px 20px;
  border: 2px solid transparent; border-radius: 6px; transition: background-color .15s ease-out; }
.btn:hover { background: var(--brand-hover); }
.btn:active { background: var(--brand-press); }
.btn:focus-visible { outline: 3px solid var(--ink); outline-offset: 3px; }
.field { background: var(--card); color: var(--ink); border: 2px solid var(--edge); border-radius: 6px; padding: 10px 12px; }
a { color: var(--brand); text-decoration: underline; text-underline-offset: .2em; }
@media (forced-colors: active) { .card { border: 1px solid CanvasText; } }
```

- The pairs in this recipe: white on #0B4AA2 is 8.4:1 and on #083A82 is 10.8:1, #0F5BC4 on #EEF2F5 is 5.6:1 for links, and the #5F6C79 field border is 5.4:1 on white.
- For a semi-flat variant, add a single overlay token such as `0 8px 24px rgb(27 42 56 / .16)` and use it only on menus and dialogs.

## Sources
Original guidance written for this project. design-md is Apache-2.0 licensed and cited as reference only.
