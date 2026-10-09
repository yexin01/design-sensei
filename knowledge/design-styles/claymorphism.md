---
title: "Claymorphism"
kind: design-style
summary: "Inflated, matte, clay-like shapes made with large radii, soft outer shadows and paired inner highlights and shadows, in friendly pastel colours. Covers a CSS recipe, contrast on pastel fills, squishy press feedback and where the style does not belong."
source_ids: [vengeance-ui]
pattern_ids: [style-claymorphism]
updated: "2026-10-09"
---

# Claymorphism

Claymorphism makes interface elements look like pieces of modelling clay: puffy, rounded, matte and softly lit. The recipe is a very large corner radius, a saturated pastel fill, a soft outer drop shadow and two inner shadows (a light one top-left, a darker one bottom-right) that fake roundness. It is friendlier and more readable than neumorphism because fills are coloured and distinct from the page. It stays a style for playful, low-density interfaces.

## Visual characteristics
- Radii of 24-48 px, or full pills; elements that look inflated.
- Pastel or mid-saturation fills on a lighter or complementary ground.
- Outer shadow: soft, offset down, tinted toward the fill. Inner shadows: a light highlight and a deeper tone.
- Chunky 3D-style icons and illustrations in the same material language.
- Generous spacing so the puffy shapes do not collide.

## When it fits, when it does not
- Fits: children's and education products, onboarding, playful consumer apps, fintech for younger audiences, empty states and illustrated marketing sections.
- Poor fit: dense data, enterprise tools, long-form text, dark technical products, premium or formal brands.
- Supporting influences that work: organic-tactile, bento-layouts, y2k for a glossier cousin, neumorphism only in small doses. Avoid dark-technical-developer-tools, swiss-international-typographic, brutalism and art-deco.

## Typography
- Rounded, friendly faces: Nunito, Fredoka, Baloo 2, DM Sans. Weights 600-800 for headings and buttons, 400-500 for body.
- Headings 32-72 px, tracking 0 to -0.01em; body 16-18 px with leading 1.5. Round terminals match the shapes, so avoid sharp grotesques.

## Colour
- Choose pastel fills with dark, saturated text: #2B2A4C on #FFD6E0 is 10.4:1 and on #C9E4FF is 10.4:1. White on pastel fails (white on #FF90E8 is 2.0:1).
- Tint shadows with a darker version of the fill rather than grey.
- Keep a neutral ground (off-white or very light tint) so fills stand out; three to four fill colours with assigned meanings.

## Composition and layout
- Large cards floating on a calm ground; two-column or card-stack layouts; characters or objects as 3D-style illustrations overlapping card edges.
- Keep forms and text content on simpler rounded rectangles; reserve the full clay treatment for hero elements, buttons and icons.
- Maintain one light direction (top-left) for every element.

## Interaction and motion
- Press feedback: scale to 0.96 with a spring back over 150-250 ms, inner shadows deepen. Idle float animations of 4-6 s with small amplitude, optional.
- Animate `transform` only; repainting large shadows on many elements is costly.
- Reduced motion: drop the idle float and spring, keep a static pressed state.

## Accessibility cautions
- Pastel on pastel is the main risk. Compute every fill and text pair and check borders of inputs against the ground (3:1).
- Highlights and inner shadows disappear in forced-colors mode; add a real border there.
- Puffy elements can look the same enabled or disabled; add a text or icon difference.
- Large floating decoration must be `aria-hidden`.

## Common mistakes
- Heavy gradients and strong shadows that look like cheap 3D buttons instead of matte clay.
- Mixed light directions, and clay applied to tables and long text.
- Low-contrast pastel text; animated shadows on dozens of elements.

## Typical mistakes of AI-generated versions
- Glossy gradients with thick black drop shadows labelled "clay", white text on pastel buttons and inconsistent highlight positions.

## How to build it
- Pattern: `style-claymorphism`. No pure claymorphism implementation exists in the local sources, so this recipe is original:

```css
.clay { background: #FFD6E0; color: #2B2A4C; border-radius: 32px;
  box-shadow: 0 16px 28px rgb(120 60 90 / .25), inset 6px 6px 12px rgb(255 255 255 / .7),
              inset -8px -8px 14px rgb(190 90 130 / .35); }
.clay:active { transform: scale(.96); }
@media (forced-colors: active) { .clay { border: 2px solid ButtonText; } }
```

- Closest local relative: `vengeance-ui:src/components/ui/candy-button.tsx` is a glossy radial-gradient button with an inset highlight, a coloured glow shadow, and an active press (`scale-95`, slight rotation). It is shinier than clay, but its structure (gradient fill, inset highlight, tinted shadow, press feedback) is the same building block.

## Sources
Original guidance written for this project. vengeance-ui is MIT-licensed and cited as reference only.
