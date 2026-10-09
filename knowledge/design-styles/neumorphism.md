---
title: "Neumorphism"
kind: design-style
summary: "Soft UI in which controls are extruded from a single-colour surface by paired light and dark shadows. Honest guidance: it fails non-text contrast by default, so use it for a few hardware-like controls with explicit borders and state indicators, not for whole apps."
source_ids: [astryx]
pattern_ids: [style-neumorphism]
updated: "2026-10-09"
---

# Neumorphism

Neumorphism, or soft UI, makes elements look pressed out of (or into) a single-colour surface. A light shadow falls toward the top-left, a dark shadow toward the bottom-right, and the pressed state swaps them for inset shadows. It looks calm and tactile in a screenshot. Because shapes are defined only by low-contrast shadow, a naive implementation fails boundary contrast, hides disabled states and disappears in forced-colors mode. The honest use is a handful of dial-like or toggle-like controls with explicit indicators, not a whole product.

## Visual characteristics
- One mid-light surface colour shared by page and components (for example #E0E5EC).
- Paired shadows: light at the top-left, dark at the bottom-right, offsets of 4-12 px and blur at about twice the offset.
- Raised, flat and inset (pressed or selected) as the only depth states; large radii (16-32 px); circular icon buttons.
- Almost no colour: one accent marks the active state.
- Thin, single-weight icons.

## When it fits, when it does not
- Fits: music and audio controls, smart-home and thermostat panels, calculators, dial and toggle showpieces, concept work, hardware-like dashboards with a few large controls.
- Poor fit: most real products. Forms, tables, content pages, dark mode and anything accessibility-critical, because affordance and state are weak.
- Supporting influences that work: minimalism, claymorphism, organic-tactile. Avoid dark-technical-developer-tools, glassmorphism and brutalism.

## Typography
- A rounded or geometric sans (Nunito, Poppins, DM Sans, Manrope). Because shapes are quiet, type carries the interface: weight 500-700 for labels, 14 px or larger.
- Dark slate text: #2E3440 on #E0E5EC is 9.87:1, #4A5568 is 5.94:1; a mid grey such as #8A94A6 is 2.42:1 and fails.
- Spell out state in words ("On", "Off", "Muted") instead of relying on the shape alone.

## Colour
- The surface cannot be white: a white highlight needs a surface darker than itself. #E0E5EC works with a #FFFFFF light shadow and an #A3B1C6 dark shadow.
- Those shadows measure 1.27:1 and 1.72:1 against the surface, well under the 3:1 required for the visual boundary of a control (WCAG 1.4.11). Add a 1 px border: #6B7686 gives 3.64:1.
- Accent for active and focus: #1D4ED8 is 5.29:1 on the surface, and white on #2563EB is 5.17:1.
- Dark variants have even less headroom for shadow contrast and rarely work; if attempted, add borders from the start.

## Composition and layout
- Define shadow distance as a token and derive blur from it; keep one light source on every element.
- Space at least 24 px between raised elements so shadows do not merge. Avoid dense lists.
- Inputs and containers are inset wells; sliders and progress bars are inset tracks with raised thumbs.
- Keep neumorphic elements to roughly ten per screen and use plain flat styles for everything else.
- On small screens reduce offsets to 3-4 px.

## Interaction and motion
- Pressed state: swap the outer shadows for inset ones over 120-180 ms with a 1 px translate. Toggles slide a knob; no springs.
- Avoid animating `box-shadow` on many elements at once; cross-fade a pseudo-element's opacity instead.
- Focus is a 2 px outline in the accent colour, never only a shadow change.
- Reduced motion: switch states instantly.

## Accessibility cautions
- Boundaries below 3:1 need a border, outline or accent indicator.
- Enabled and disabled controls look nearly identical; add a text, icon or opacity cue and `aria-disabled`.
- Forced-colors mode removes `box-shadow`, so the control would vanish; add a system-colour border there.
- Bright outdoor screens and low-vision users lose the soft shapes first.
- Never leave a text field defined by shadow alone.

## Common mistakes
- White page with white cards, so the highlight shadow is invisible.
- Mixed light directions, or neumorphic and flat controls combined without a rule.
- Neumorphism on large content areas, tables and text inputs.
- No pressed, disabled or focus states.
- Reusing the same offsets in dark mode.

## Typical mistakes of AI-generated versions
- `box-shadow: 8px 8px 16px #bebebe, -8px -8px 16px #fff` on every div over #e0e0e0, grey #999 text, no borders and no focus styles, labelled "soft UI".
- A pure white background that makes the light shadow disappear.

## How to build it
- Pattern: `style-neumorphism`. No neumorphic implementation exists in the local sources, so this is original code (shadow tokens, raised and pressed states, forced-colors border):

```css
:root { --nm-surface: #E0E5EC; --nm-light: #FFFFFF; --nm-dark: #A3B1C6; --nm-d: 8px; }
.nm { background: var(--nm-surface); border-radius: 20px; border: 1px solid #6B7686; }
.nm-raised { box-shadow: calc(var(--nm-d) * -1) calc(var(--nm-d) * -1) calc(var(--nm-d) * 2) var(--nm-light),
                         var(--nm-d) var(--nm-d) calc(var(--nm-d) * 2) var(--nm-dark); }
.nm-pressed { box-shadow: inset calc(var(--nm-d) * -.6) calc(var(--nm-d) * -.6) var(--nm-d) var(--nm-light),
                          inset calc(var(--nm-d) * .6) calc(var(--nm-d) * .6) var(--nm-d) var(--nm-dark); }
@media (forced-colors: active) { .nm { border-color: ButtonText; } }
```

- Supporting principle: `astryx:docs/design/elevation-hierarchy.md` (a draft record) says one edge language should lead rather than combining a defined edge and soft elevation at full strength, and that high-contrast presentation must keep clear boundaries when soft shadows are unavailable. Treat the border above as the minimum edge, not decoration.

## Sources
Original guidance written for this project. astryx is MIT-licensed and cited as reference only.
