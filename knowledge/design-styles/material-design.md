---
title: "Material design (layered surfaces and elevation)"
kind: design-style
summary: "A paper-and-light metaphor in which sheets sit at defined heights, cast restrained shadows and respond with state overlays and purposeful motion. Covers tonal elevation in dark themes, contrast of surface layers, state layers, and a short CSS recipe."
source_ids: [astryx]
pattern_ids: [style-material-design]
updated: "2026-10-09"
---

# Material design (layered surfaces and elevation)

Material design is Google's design language, and this note is about the general idea behind it, not a re-statement of its specification: an interface made of opaque sheets that sit at defined heights above a base plane. A higher sheet covers a lower one, casts a softer and larger shadow, and responds to touch with a spreading highlight. The ideas that travel well are a small set of elevation levels, state feedback that is separate from the base colour, and motion that explains where things come from. For component-level rules, read the current official documentation; this note stays at the level of the visual system and its traps.

## Visual characteristics
- Opaque surfaces at a small set of heights (typically five or six levels), each with a consistent shadow pair: a tight, darker contact shadow and a wide, faint ambient shadow.
- Cards, sheets, menus and dialogs are rectangles with moderate radii (8-16 px, larger for sheets); a floating action button or tonal pill may mark the primary action.
- A key colour with tonal variants for container, on-container text and outline, so a theme is generated from one hue.
- Bold, large imagery and a restrained set of icons drawn on a shared grid.
- A 4 px or 8 px layout rhythm, with generous padding inside surfaces.
- Ripple or overlay feedback that starts at the point of touch.

## When it fits, when it does not
- Fits: productivity and utility apps, dashboards with cards and drawers, forms and settings, Android-first products, multi-platform web apps where users already know the conventions, and teams that want a ready component vocabulary.
- Poor fit: expressive brand sites, editorial storytelling, luxury or craft brands, and interfaces where a distinctive identity is the point. Using it unchanged also makes a product look like every other app built on the same kit.
- Supporting influences that work: flat-design (for the tonal palette), product-led-saas, bento-layouts, minimalism. Avoid brutalism, vaporwave, art-deco and skeuomorphism, which use depth with opposite intent.

## Typography
- One highly legible sans-serif family, such as Roboto, Inter or Noto Sans, in a limited type scale: display, headline, title, body and label roles.
- Typical sizes: body 14-16 px at 1.4-1.5 line height; labels 12-14 px at weight 500 with tracking +0.01em to +0.04em; headlines 24-32 px at weight 400-500.
- Assign sizes by role, not by screen, so a card title always looks like a card title. Sentence case for almost everything; uppercase only for very short labels.
- Provide a dense text style for tables and a comfortable style for reading; do not use one for both.

## Colour
- Light theme example: ink #1B1A22 on white is 17.3:1, and on a tonal container #F1EFF9 it is 15.2:1. Secondary text #4A4856 is 8.9:1 on white and 7.8:1 on the container.
- Primary #4F46B8 with white text is 7.2:1; on the container it is 6.4:1. Hover and pressed overlays of 8% and 12% white lighten the fill but still hold 6.0:1 and 5.5:1 for the white label.
- Layers separate very little by tone alone: white against #F1EFF9 is 1.14:1 and against #E4E0F5 is 1.29:1. This works for grouping, but it is not an edge. Fields and outlined buttons need an outline colour of at least 3:1 on both neighbours; #77758A is 4.47:1 on white and 3.93:1 on the container.
- Small supporting text that must pass 4.5:1 on the container needs a darker tone, for example #6A6880 at 4.7:1.
- Dark theme: shadows are hard to see on dark grounds, so raise the surface colour instead. On a #121212 ground, tonal steps of #1E1E1E (about 5% white) and #2C2C2C (about 11% white) read as higher sheets. Text #E7E5F0 is 15.0:1 on #121212 and 11.2:1 on #2C2C2C; a light primary #C3BDFF is 10.7:1 and 8.0:1 on those grounds.
- Disabled content at 38% opacity is only 2.4:1 on white; treat it as a state cue, not as readable text.
- Error red such as #B42318 with white is 6.6:1, but pair it with an icon and text, not colour alone.

## Composition and layout
- A layout is a stack: base plane, content surfaces, then temporary layers (menu, bottom sheet, dialog, snackbar). Perceived height and actual stacking must agree. A surface that looks higher must cover lower content and must not be clipped by a scrolling parent. This matches the elevation record in `astryx:docs/design/elevation-hierarchy.md` (a draft), which also says that depth should stay quiet and that one edge language, either a defined edge or soft elevation, should lead rather than both at full strength.
- Use a responsive grid with 4, 8 and 12 columns by breakpoint; stack cards at narrow widths and use a navigation rail or drawer on wide screens.
- Raise only what has meaning. Resting cards at level 1, menus at 2-3, dialogs at the top; sticky app bars rise only once content scrolls under them.
- Place the primary action in a consistent, reachable position, and keep one main action per screen.
- Scrims: a 30-40% black layer behind a modal makes the modal read as higher and signals that the page behind is unavailable. A 32% scrim turns a white page into #ADADAD, where ink text is still 7.7:1, so partly visible background content stays legible but clearly secondary.

## Interaction and motion
- State layers: a translucent overlay in the content colour, at about 8% for hover, 12% for focus and press, and 16% for drag. This keeps text contrast predictable and avoids a separate colour per state.
- Ripple from the pointer position, 150-300 ms, ending in the hover overlay. Keyboard focus gets a visible outline or a ring in addition to the overlay.
- Elevation changes on lift (dragging, pressed cards) over 150-250 ms; use one easing curve family, ease-out for entering and ease-in for leaving.
- Transitions should explain relationship: a card expands into a detail view, a menu grows from its trigger. Keep them to 200-400 ms.
- Reduced motion: replace ripples, container transforms and shared-element moves with instant state change or a 100 ms fade; keep the overlay colour change.

## Accessibility cautions
- Shadow is not a boundary. Outline inputs, cards on matching tonal grounds and text buttons as above, and do not rely on elevation for state (WCAG 1.4.11).
- Shadows and tonal differences disappear in forced-colors mode; add a real border there.
- Perceived height is not reading order. Keep DOM order logical, trap focus in modal layers, return it to the trigger on close, and mark background content inert.
- Ripples and overlay colour must not be the only focus indicator. A 2-3 px ring with a 2 px offset works on any tonal surface.
- Target size of at least 44-48 px, with spacing, is part of the style; compact density modes should not go below 24 px (WCAG 2.5.8).
- Snackbars that vanish quickly fail users who read slowly; give them enough time and a way to reach the action.

## Common mistakes
- Shadows on everything, so no level reads as higher than another.
- Stacking shadows at several different light angles, or tinted shadows on some cards only.
- Using the stock palette and components unchanged, with no brand decision.
- A floating action button that competes with a primary button in the same view.
- Elevation used as decoration while z-index and stacking contexts disagree, so menus are clipped by cards.
- Dark themes that keep the same dark shadows on a dark ground and look flat and muddy.
- Ripple effects on text areas, long lists and elements that are not interactive.

## Typical mistakes of AI-generated versions
- Purple primary, white cards and uniform soft shadows on every block, with no distinction between resting and raised surfaces.
- A floating action button added to a landing page for no task.
- Ripple animations on static content, uppercase letter-spaced buttons everywhere and body text set in the label style.
- Dark mode created by inverting colours rather than lightening surfaces.

## How to build it
- Pattern: `style-material-design`. No local source implements a Material-style kit, so this recipe is original. Keep elevation as tokens, give hover and press a separate overlay, and lighten surfaces in dark mode:

```css
:root { --ground: #FFFFFF; --container: #F1EFF9; --ink: #1B1A22; --primary: #4F46B8; --edge: #77758A;
  --lift-1: 0 1px 2px rgb(27 26 34 / .30), 0 1px 3px 1px rgb(27 26 34 / .15);
  --lift-2: 0 1px 2px rgb(27 26 34 / .30), 0 2px 6px 2px rgb(27 26 34 / .15);
  --lift-3: 0 4px 8px 3px rgb(27 26 34 / .15), 0 1px 3px rgb(27 26 34 / .30); }
body { background: var(--ground); color: var(--ink); font: 400 1rem/1.5 Roboto, system-ui, sans-serif; }
.card { background: var(--container); border-radius: 12px; box-shadow: var(--lift-1);
  transition: box-shadow .2s cubic-bezier(.2, 0, 0, 1); }
.card:hover { box-shadow: var(--lift-2); }
.btn { position: relative; overflow: hidden; background: var(--primary); color: #fff; font-weight: 500;
  border: 0; border-radius: 20px; padding: 10px 24px; min-height: 44px; }
.btn::after { content: ""; position: absolute; inset: 0; background: currentColor; opacity: 0; transition: opacity .15s; }
.btn:hover::after { opacity: .08; }
.btn:focus-visible::after, .btn:active::after { opacity: .12; }
.btn:focus-visible { outline: 3px solid var(--ink); outline-offset: 2px; }
.field { background: var(--ground); border: 1px solid var(--edge); border-radius: 4px; padding: 12px 16px; }
@media (prefers-color-scheme: dark) {
  :root { --ground: #121212; --container: #2C2C2C; --ink: #E7E5F0; --primary: #C3BDFF; --edge: #9B99AE; }
  .btn { color: #1F1A5C; } }
@media (forced-colors: active) { .card { border: 1px solid CanvasText; box-shadow: none; } }
```

- The dark primary button text #1F1A5C on #C3BDFF is 8.9:1, and the dark outline #9B99AE is 5.0:1 on the #2C2C2C container.
- Keep stacking real: render menus and dialogs in a top layer (the `dialog` element or a portal) so they are never clipped by a lower scroll container.

## Sources
Original guidance written for this project. astryx is MIT-licensed and cited as reference only. Material design is a Google design language; this note neither reproduces nor replaces its documentation.
