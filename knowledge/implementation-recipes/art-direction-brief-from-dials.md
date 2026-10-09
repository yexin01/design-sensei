---
title: "Art-direction brief from the three dials"
kind: recipe
summary: "Original recipe that turns Design Sensei's three 1-10 dials (design_variance, motion_intensity, visual_density) into concrete typography, colour, layout, spacing, surface and motion decisions, with one decision table per band and tested token code."
source_ids: [taste-skill]
pattern_ids: [taste-skill-three-dials]
updated: "2026-10-09"
---

# Art-direction brief from the three dials

## Goal

Replace vague adjectives ("clean", "bold", "premium") with a written brief of numbers and rules that can be implemented and
checked. The method is original; the three 1-10 dials, the bands 1-3, 4-7 and 8-10, and a few thresholds are inspired by
`taste-skill:skills/taste-skill/SKILL.md` (sections 1, 4 and 7). Background: `knowledge/design-intelligence/taste-skill.md`.

## When to use, when not to

Use it for any new page or redesign before writing code, and whenever the user gives only mood words. Skip it when a
`DESIGN.md` or brand guideline already fixes these decisions (that file outranks this recipe). It targets marketing and
editorial surfaces; for application UI keep `design_variance` low and spend effort on density and states.

## Prerequisites

- The keys `design_variance`, `motion_intensity` and `visual_density` (integers 1-10; defaults 6, 5, 5 in Design Sensei's
  `skills/design-sensei/config/defaults.yaml`). No packages are needed; the code below is dependency-free TypeScript.
- A short brief: page kind, audience, any named references.

## Steps

### 1. Write the design read

One line: page kind for audience; the visual language; the base system or aesthetic. Constraints that override taste
(accessibility-first audience, regulated sector, kids, trust-critical commerce) are recorded here and cap the dials.

### 2. Pick starting dials

| Brief signal | variance | motion | density |
| --- | --- | --- | --- |
| trust-first, public sector, finance, health | 2 | 2 | 5 |
| B2B product or developer-tool marketing | 5 | 4 | 5 |
| editorial, publication, calm product | 5 | 3 | 3 |
| premium consumer, lifestyle | 7 | 5 | 3 |
| studio, portfolio, event, campaign | 8 | 7 | 3 |
| experimental showcase | 9 | 9 | 2-4 |
| dashboard or admin | 3 | 3 | 8 |
| redesign, keep the brand | as existing | existing +1 | as existing |
| redesign, new visual language | existing +2 | existing +2 | as existing |
| no signal | 6 | 5 | 5 |

State a one-sentence reason per dial. A user's explicit request ("make it calmer") moves a dial; do not ask them to edit config.

### 3. Resolve bands and conflicts

Bands are low (1-3), mid (4-7) and high (8-10). Then apply:

- High variance and high density: keep data regions at variance 5 or lower; spend variance on header, navigation, imagery and empty states.
- High motion and high density: motion only for state changes (150-200 ms); no scroll choreography over data.
- Any motion of 4 or more needs a reduced-motion alternative; a page that claims motion 5 or more must contain at least three
  distinct motion moments, otherwise lower the dial.
- Variance 4 or more: layouts collapse to one column below 768 px with a stated reading order.

### 4. Look up the decisions

Each table gives the decision a dial drives in each area; "-" means that dial does not drive it. Values are starting points.

**Band 1-3 (low)**

| Area | design_variance | motion_intensity | visual_density |
| --- | --- | --- | --- |
| Typography | one family (plus mono at most); scale ratio 1.2; one alignment throughout | no kinetic type | body 18 px, leading 1.65, measure 55-70 ch; large display is fine because little competes |
| Colour | neutral ramp plus one accent for the primary action and links; no gradients | - | calm fields; colour never encodes data; 4.5:1 or better for body text |
| Layout | symmetric 12-column grid; centred or 50/50 hero; 2-3 section layouts, repetition accepted | - | one idea per viewport; at most 3 items per row |
| Spacing | equal paddings on an 8 px base | - | section padding 80-160 px, gaps 40 px |
| Surfaces | one radius (about 8 px); flat fills or hairlines; rare shadows | hover and focus change colour or border only | whitespace separates groups; a card only where a boundary is functional |
| Motion | - | hover, focus, active states only; 120-180 ms ease-out; no autoplay, no scroll-linked effects | - |

**Band 4-7 (mid)**

| Area | design_variance | motion_intensity | visual_density |
| --- | --- | --- | --- |
| Typography | display plus text family (or one variable family with strong weight contrast); ratio 1.333; one expressive moment | hero headline may fade and rise 12-24 px; no per-letter animation elsewhere | body 16 px, leading 1.6; tabular numerals in tables; 3-4 sizes per viewport |
| Colour | neutrals tinted toward the accent; one accent plus one supporting tone; gradient only as low-contrast atmosphere | colour transitions on hover only | status colours always paired with text or an icon |
| Layout | asymmetric split (about 7/5), offset headings, mixed image ratios; 3-4 section layouts per 8 sections | - | 2-3 columns; up to 4 items per row; one dense section allowed |
| Spacing | modular rhythm with deliberate breaks; overlaps about 24 px | - | section padding 64-96 px, gaps 24 px |
| Surfaces | two levels (page, raised); radius scale of 2-3 steps with a written rule | raised surfaces lift 2-4 px on hover | cards for related groups; sparing hairlines between rows |
| Motion | one easing family and one timing scale for everything | entrance reveals 300-600 ms, 40-80 ms stagger, once per element; at most one scroll-linked or pinned moment | - |

**Band 8-10 (high)**

| Area | design_variance | motion_intensity | visual_density |
| --- | --- | --- | --- |
| Typography | expressive display, 7-8 times body, tight tracking; at most two families; 4.5:1 on every pair | kinetic type allowed (per line or word) with a static equivalent | body 14 px, labels 12 px, leading 1.45 and 1.3; tabular or mono numerals; uppercase labels with positive tracking |
| Colour | bold limited palette, colour fields, duotone or imagery-led; still one accent role; scrims on images | colour shifts per scroll section only with a stated purpose | colour encodes status or series with a legend; at most 6 categorical hues; never colour alone |
| Layout | fractional or off-grid composition (for example 2fr 1fr 1fr), overlaps, large voids; 4 or more section layouts per 8 sections, none repeated back to back; explicit mobile order | - | multi-column panels, 4 or more items per row, sticky headers and rails, progressive disclosure |
| Spacing | deliberately uneven rhythm on the 4/8 px grid; overlaps up to 64 px | - | section padding 24-48 px, rows 32-44 px (44 px touch targets), gaps 12 px |
| Surfaces | layered materials (glass, paper, metal) with solid fallbacks; one radius rule (all sharp or all large); written z-index scale | shared-element and layout transitions allowed | no card boxes; 1 px dividers and tonal bands |
| Motion | one timing language even when choreography is non-linear | scroll-linked scenes, springs, shared-element transitions, each with a stated purpose; transform and opacity only | - |

### 5. Generate the numeric tokens

Original code; it validates the dials and emits CSS custom properties for the numeric decisions (spacing, type steps, timing).
Tested with Node's TypeScript type stripping.

```ts
export interface Dials {
  design_variance: number; // 1-10
  motion_intensity: number; // 1-10
  visual_density: number; // 1-10
}

export type Band = "low" | "mid" | "high";

export function toBand(value: number): Band {
  if (!Number.isInteger(value) || value < 1 || value > 10) {
    throw new RangeError(`dial must be an integer from 1 to 10, got ${value}`);
  }
  return value <= 3 ? "low" : value <= 7 ? "mid" : "high";
}

// Starting points per band. Treat them as defaults to override, not as laws.
const VARIANCE = {
  low: { ratio: 1.2, overlapPx: 0 },
  mid: { ratio: 1.333, overlapPx: 24 },
  high: { ratio: 1.5, overlapPx: 64 },
} as const;

const DENSITY = {
  low: { sectionPad: "clamp(5rem, 10vw, 10rem)", gap: "2.5rem", bodyRem: 1.125, leading: 1.65 },
  mid: { sectionPad: "clamp(4rem, 7vw, 6rem)", gap: "1.5rem", bodyRem: 1, leading: 1.6 },
  high: { sectionPad: "clamp(1.5rem, 3vw, 3rem)", gap: "0.75rem", bodyRem: 0.875, leading: 1.45 },
} as const;

const MOTION = {
  low: { fast: 120, base: 180, slow: 180, stagger: 0, ease: "ease-out" },
  mid: { fast: 150, base: 300, slow: 600, stagger: 60, ease: "cubic-bezier(0.16, 1, 0.3, 1)" },
  high: { fast: 150, base: 400, slow: 900, stagger: 80, ease: "cubic-bezier(0.16, 1, 0.3, 1)" },
} as const;

export function toCssVars(d: Dials): string {
  const v = VARIANCE[toBand(d.design_variance)];
  const m = MOTION[toBand(d.motion_intensity)];
  const s = DENSITY[toBand(d.visual_density)];
  const rem = (n: number) => s.bodyRem * v.ratio ** n;
  const step = (n: number) => `${rem(n).toFixed(3)}rem`;
  const floor = `${Math.min(2.5, rem(5)).toFixed(3)}rem`;
  const lines = [
    `--section-pad: ${s.sectionPad};`,
    `--gap: ${s.gap};`,
    `--leading-body: ${s.leading};`,
    `--text-body: ${step(0)};`,
    `--text-lg: ${step(1)};`,
    `--text-xl: ${step(2)};`,
    `--text-2xl: ${step(3)};`,
    `--text-display: clamp(${floor}, 1rem + 6vw, ${step(5)});`,
    `--overlap: ${v.overlapPx}px;`,
    `--dur-fast: ${m.fast}ms;`,
    `--dur-base: ${m.base}ms;`,
    `--dur-slow: ${m.slow}ms;`,
    `--stagger: ${m.stagger}ms;`,
    `--ease: ${m.ease};`,
  ];
  return `:root {\n  ${lines.join("\n  ")}\n}`;
}

export const reducedMotionCss = `@media (prefers-reduced-motion: reduce) {
  :root { --dur-fast: 0.01ms; --dur-base: 0.01ms; --dur-slow: 0.01ms; --stagger: 0ms; }
}`;

// JS-driven motion (scroll scenes, canvas, WebGL) must check this itself; CSS variables do not reach it.
export const prefersReducedMotion = (): boolean =>
  typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
```

For the defaults 6 / 5 / 5, `toCssVars` yields a 4-6 rem section padding, 1.333 type steps (display up to about 67 px), 300 ms
base timing and a 60 ms stagger. Ship `reducedMotionCss` with the stylesheet, and gate every JS scene, parallax and pinned
section on `prefersReducedMotion()` with a static layout as the alternative. Do not use scroll event listeners; use
`IntersectionObserver`, CSS scroll-driven animation where supported (with a fallback), or the animation library's ticker.

### 6. Write the brief

Fill this and keep it in the task notes: design read; the three dials with one-line reasons; typography (families, ratio, body
size, leading); colour (neutral ramp, accent, rule for the accent); layout (grid, hero composition, section layouts);
spacing (base unit, section padding); surfaces (radius rule, borders, shadows, glass); motion (easing, timings, which moments
move and why); a don'ts list of three to six items.

### 7. Implement in order

Tokens, then type, layout, surfaces, and motion last. Re-read the band tables after each layer; if a decision no longer fits
its band, change the dial or the decision, not just the CSS.

## Verification checklist

- [ ] Dial honesty: motion 5 or more shows at least three motion moments; motion 3 or less has no autoplay or scroll-linked effects.
- [ ] Reduced motion: emulate `prefers-reduced-motion: reduce`; every moving element has a static equivalent; no pinning or parallax remains.
- [ ] Responsive: inspect 375, 768, 1280 and 1920 px; asymmetric layouts become one column under 768 px; no horizontal scroll.
- [ ] Console and network: no errors, no failed assets, no scroll listeners.
- [ ] Performance: only transform and opacity animate; LCP at most 2.5 s and CLS at most 0.1 (Design Sensei's default budget); heavy effects lazy-loaded.
- [ ] Contrast: 4.5:1 for body text and 3:1 for large text and UI components on real backgrounds, including text over images.
- [ ] Generic-look review: one accent, one radius rule, one theme per page, no placeholder names or numbers; use the rule list in the taste-skill note as defaults to override with a reason.

## Upstream references

Dial definitions and thresholds: `taste-skill:skills/taste-skill/SKILL.md` (sections 1, 1.A, 4.3, 4.4, 6.B, 7); the first-generation
wording: `taste-skill:skills/taste-skill-v1/SKILL.md`; an alternative four-dial table: `taste-skill:skills/stitch-skill/DESIGN.md`;
the v1 to v2 rationale: `taste-skill:CHANGELOG.md`.

## Licence notes

Taste Skill is MIT (`taste-skill:LICENSE`). No upstream text is reproduced; the tables and numbers are original recommendations,
and the dial names and band boundaries are credited above. Design Sensei's own keys are the snake_case names used here.
