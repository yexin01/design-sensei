---
title: "Skeuomorphism"
kind: design-style
summary: "Interfaces that imitate real materials and objects: leather, metal, paper, glass, knobs, switches and keys, lit consistently and behaving physically. Useful for instruments, audio and domain-specific tools; costly and inaccessible when applied to general UI without semantics."
source_ids: [img2threejs, vengeance-ui]
pattern_ids: [style-skeuomorphism]
updated: "2026-10-09"
---

# Skeuomorphism

Skeuomorphic design borrows the look and behaviour of physical objects: a brushed-metal panel, a leather-stitched notepad, a rotary knob, a toggle with a satisfying click. The metaphor helps when users already know the object (a mixer, a synthesizer, a calculator, a keyboard). It hurts when the texture is decoration over an unrelated function. Its strengths are affordance and character; its costs are weight, scaling, localisation and accessibility of custom controls.

## Visual characteristics
- Material fidelity: grain, brushed or anodised metal, leather, paper, glass, rubber, with believable edge bevels and specular highlights.
- One consistent light source (usually top, slightly left): highlights on top edges, shadows below, inner shadows for recesses.
- Controls shaped like their real counterparts: knobs, sliders in grooves, rocker switches, LEDs, meters.
- Embossed or debossed labels, small caps legends, engraved lines.

## When it fits, when it does not
- Fits: audio and music tools, instruments, calculators, camera and hardware companions, games, nostalgic or tactile brand moments, product configurators.
- Poor fit: general productivity UI, content sites, translated apps (textured labels do not localise), performance-limited pages, accessibility-critical flows.
- Supporting influences that work: retro-vintage, organic-tactile, grain-and-texture, art-deco. Avoid minimalism, swiss-international-typographic and neo-brutalism.

## Typography
- Legends like device labels: condensed or geometric sans, uppercase at 10-12 px with +0.06 to +0.12em tracking, weight 500-700. Keep any readable content (values, names) at 14 px or more.
- Emboss with a one-pixel light `text-shadow` below and a dark one above; do not rely on the effect for legibility.
- Numeric displays: seven-segment or mono faces with tabular numerals.

## Colour
- Colour comes from materials: warm leather browns, anodised greys, brass, ivory plastic, with coloured LEDs as the only saturated accents.
- Contrast on textured surfaces is measured against the darkest and lightest local texture values, not the average. Put values on flat inset displays.
- Keep material gradients subtle (6-12% lightness change); more reads as plastic.

## Composition and layout
- Device-like panels with fixed proportions, scaled as a unit (`aspect-ratio`, CSS variables or SVG) instead of reflowing.
- Group controls as on hardware: rows of knobs under a display, sections separated by engraved lines.
- Provide a plain, responsive alternative layout for narrow screens rather than shrinking a panel until knobs are unusable.

## Interaction and motion
- Controls respond physically: knobs rotate with limited range and mild inertia, switches snap with 80-120 ms travel, buttons depress 1-2 px.
- Sound is optional, muted by default, and never required for feedback.
- Reduced motion: remove inertia and decorative needle sweeps; set values instantly.

## Accessibility cautions
- Custom controls need real semantics: a knob is a slider (`role="slider"` with value, min, max and text), arrow-key support and a visible focus ring. A switch is a real checkbox or `role="switch"`.
- Textured backgrounds behind text lower contrast; keep labels on flat plates.
- In forced-colors mode gradients and shadows are removed; keep outlines for controls.
- Do not hide state only in a light or needle position; expose it as text.

## Common mistakes
- Inconsistent lighting between elements.
- Heavy photographic textures in megabytes of PNG instead of CSS gradients, SVG filters or a small tiled texture.
- Skeuomorphic chrome around ordinary forms.
- Custom controls with pointer-only operation.

## Typical mistakes of AI-generated versions
- Linear gradients and a drop shadow standing in for materials, with light coming from three directions.
- Stock leather or wood textures at full size behind readable text; knobs as unlabelled `div`s.

## How to build it
- Pattern: `style-skeuomorphism`. Choose a light model first, then build surfaces with layered gradients, an SVG `feTurbulence` grain tile and inset shadows; add behaviour and semantics last.
- No full skeuomorphic UI kit exists in the local sources. Relevant references: `vengeance-ui:src/components/ui/interactive-keyboard.tsx` draws an on-screen keyboard and maps real key codes to its keys, and `img2threejs:docs/materials/THREEJS_MATERIAL_REFERENCE.md` gives physically based starting values (for example brushed steel at metalness 1, roughness 0.35, anisotropy 0.85; matte leather at roughness 0.62) when a material is rendered in real 3D instead of faked in CSS.
- For real 3D materials use the experimental-3d guidance and keep the same accessibility requirements for controls.

## Sources
Original guidance written for this project. img2threejs (Apache-2.0) and vengeance-ui (MIT) are cited as reference only.
