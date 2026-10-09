# Colour systems

Build a token-based palette with measured contrast, light and dark themes, safe gradients and glass, and semantic state colours.

## When to load this

Load it when choosing the palette (step 2), when writing colour tokens, and whenever text sits on gradients, images, glass or texture. Contrast numbers in this file
were computed from the exact hex values shown (WCAG relative luminance); re-measure after changing any value. Standards: WCAG 2.2 AA needs 4.5:1 for body text,
3:1 for large text (24 px, or about 18.7 px bold) and 3:1 for UI component boundaries, focus indicators and meaningful graphics. Everything else is a heuristic.

## Decisions to make

| Decision | Options | Dial influence |
| --- | --- | --- |
| Neutral temperature | warm, cool, pure neutral; tint toward the accent hue slightly | brand and mood; `design_variance` high allows tinted or coloured grounds |
| Accent count | one accent role (default), one supporting tone (mid), bold limited palette still with one action colour (high) | `design_variance` |
| Theme strategy | light only, dark only, both designed together | audience and context; dark-first for [[style-dark-technical-developer-tools]] |
| Gradients | none, low-contrast atmosphere, shader/mesh field | `design_variance`, `motion_intensity`, `performance_budget`, `webgl_enabled` |
| Colour as data | never (low density), status only (mid), series and status with legend, at most 6 categorical hues (high) | `visual_density` |

## Token structure

Name tokens by role. Components read roles, never raw hex or palette steps. Define light and dark together so neither is an afterthought.

| Token | Role | Rule |
| --- | --- | --- |
| `--bg` | page background | the calmest, largest area |
| `--surface` | cards, panels, inputs | one or two steps from `--bg` |
| `--text` | primary text | 7:1 or better on `--bg` and `--surface` is comfortable |
| `--text-muted` | secondary text, captions | at least 4.5:1 on both; must still look different from disabled |
| `--border` | decorative dividers | may be low contrast (decoration only) |
| `--border-strong` | input, button and control edges | at least 3:1 against the surface (WCAG 1.4.11) |
| `--accent` | primary action, links, focus | one role; 4.5:1 as text on `--bg` and `--surface`, or use `--accent-strong` for text |
| `--on-accent` | text on filled accent | 4.5:1 against `--accent` |
| `--success` `--warning` `--danger` `--info` | state | each paired with icon or text; each 4.5:1 as text on `--bg` |
| `--overlay`, `--scrim` | hover tint, text-over-image protection | alpha-based so they combine with the surface beneath |

Astryx structures its tokens the same way (semantic `surface`, `text-primary`, `text-secondary`, `on-accent`, `border`, `border-emphasized`, mode-dependent values held as
one `light-dark()` token) and shows how a theme is generated from an accent seed; see [[astryx-theme-token-system]] and
[themes and tokens](../../../knowledge/components/astryx-themes-and-tokens.md). For copy-paste component sets, a two-layer token approach is described in
[[vengeance-ui-theme-token-layer]].

## A worked, measured palette (warm paper, orange accent)

Use it as a starting point for warm editorial or craft briefs, or as a pattern for your own values. Ratios in brackets are text on `--bg` / `--surface`.

| Token | Light | Dark |
| --- | --- | --- |
| `--bg` | `#FAF8F4` | `#14130F` |
| `--surface` | `#F1EEE7` | `#1E1C17` |
| `--text` | `#1B1A17` (16.4 / 15.0) | `#ECE9E2` (15.3 / 14.0) |
| `--text-muted` | `#5F5B53` (6.4 / 5.8) | `#A8A398` (7.4 / 6.8) |
| `--border` | `#D8D3C8` (1.4, decorative) | a step above `--surface`, decorative |
| `--border-strong` | `#857F72` (3.8 / 3.4) | `#857F72` (4.7 / 4.3) |
| `--accent` | `#C2410C` (4.9 / 4.5 borderline) | `#FB923C` (8.2 / 7.5) |
| `--accent-strong` (text on surfaces) | `#9A3412` (6.9 / 6.3) | `#FB923C` |
| `--on-accent` | `#FFFFFF` on `#C2410C` = 5.2 | `#14130F` on `#FB923C` = 8.2 |
| `--success` / `--danger` / `--warning` / `--info` | `#15803D` 4.7, `#B91C1C` 6.1, `#B45309` 4.7, `#1D4ED8` 6.3 | `#4ADE80` 10.7, `#F87171` 6.7, `#FBBF24` 11.1, `#60A5FA` 7.3 |

The lesson in the accent row: `#C2410C` passes on the page colour (4.88) but misses 4.5 on the surface (4.47), so link text inside cards uses `--accent-strong`.
Always measure a colour on each surface it will meet.

```css
:root {
  color-scheme: light dark;
  --bg: #FAF8F4; --surface: #F1EEE7; --text: #1B1A17; --text-muted: #5F5B53;
  --border: #D8D3C8; --border-strong: #857F72;
  --accent: #C2410C; --accent-strong: #9A3412; --on-accent: #FFFFFF;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #14130F; --surface: #1E1C17; --text: #ECE9E2; --text-muted: #A8A398;
    --border-strong: #857F72; --accent: #FB923C; --accent-strong: #FB923C; --on-accent: #14130F;
  }
}
:root[data-theme="dark"] { /* same dark values: keep both blocks in sync, or generate them from one source */ }
```

Offer a manual theme switch in addition to `prefers-color-scheme`, and set `data-theme` before first paint to avoid a flash. `light-dark()` can replace the duplicated blocks where
browser support is acceptable for the project; Astryx uses it with `color-scheme`.

## Palette construction method

1. Anchor: take the brand colour, or choose one hue from the mood words and the style note ([[style-editorial]] paper and ink; [[style-swiss-international-typographic]] black, white and one signal colour).
2. Neutrals: build a 9 to 11 step ramp from near-white to near-black with low chroma, tinted slightly toward the accent hue. Avoid pure `#000` and `#FFF` for large areas.
3. Roles: assign ramp steps to `--bg`, `--surface`, borders, text and muted text. Never pick colours per component.
4. Measure every text/surface pair and every control boundary. Adjust lightness, not hue, until it passes.
5. States: pick success, warning, danger and info hues, then match their lightness to the accent so they have equal visual weight; give each a text/icon cue.
6. Dark theme: derive it, do not invert. Surfaces get lighter as they rise; raise lightness and reduce saturation of accents; recheck every pair.
7. Stress test: grayscale screenshot (hierarchy survives), colour-blindness emulation, forced-colors mode, text at 200% zoom over its real background.

Astryx generates scales from an accent seed with a perceptual model and asserts 4.5:1 text and 3:1 emphasised borders in tests
(`astryx:packages/core/src/theme/expandColorScale.ts`), which is the same loop automated. For hand-built palettes a lint pass on a `DESIGN.md`
checks component contrast ([[design-md-lint-and-export]]).

## Contrast pairs to remember

- Common greys: `#767676` on white is 4.5:1 (the lowest pass); `#9CA3AF` on white is 2.5:1 and fails; `#6B7280` on white is 4.8:1 (see [minimalism](../../../knowledge/design-styles/minimalism.md)).
- Muted text on near-black: `#8B949E` on `#0D1117` is 6.2:1; `#666` on `#0A0A0A` is 3.5:1 and fails ([dark technical](../../../knowledge/design-styles/dark-technical-developer-tools.md)).
- Alpha borders at 8-12% white are about 1.2-1.4:1: fine as separators, wrong as an input edge.
- Disabled text is exempt from WCAG contrast but must still read differently from muted text.

## Gradients, glass and texture

- Interpolate in a perceptual space (`linear-gradient(in oklch, ...)`) so midpoints stay clean instead of going grey. Build from the brand hue plus one neighbour and one contrast; avoid the
  default indigo-violet-pink sweep. See [aurora and gradient mesh](../../../knowledge/design-styles/aurora-gradient-mesh.md).
- Text over any gradient or image: measure the worst region (lightest and most saturated), not the average. Add a scrim at 35-55% black or put text on a solid panel. Examples from the notes:
  white on `#5227FF` is 6.8:1 but white on `#7CFF67` is 1.3:1.
- Glass: define a solid fallback colour, a scrim token and a visible 1 px border; white text on 20% white glass is 6.0:1 over `#1E3A8A` but 1.2:1 over `#FDE68A`
  ([glassmorphism](../../../knowledge/design-styles/glassmorphism.md)). Keep at most two or three glass layers; support `@supports not (backdrop-filter)` and `forced-colors`.
- Banding on large smooth fields: add 2-6% neutral grain or dither, text above the grain layer ([grain and texture](../../../knowledge/design-styles/grain-and-texture.md)).
- Motion in colour: slow drifts only (cycles of 20-60 s), pause offscreen, freeze at a good frame for `prefers-reduced-motion`. Animating `filter: blur()` on large layers is expensive.
- Build cheapest first: static CSS gradient, then SVG/CSS motion ([[fancy-animated-gradient-svg]], [[vengeance-ui-aurora-hero-backgrounds]]), then shader gradient
  ([[shader-gradient-background]], license_review_required) only if `webgl_enabled` and the budget allow. CSS glass fallback: [[liquid-glass-css-fallback]].

## Colour-blind safety and semantic colour

- Never encode meaning in hue alone, especially red versus green: pair with an icon, label, pattern or position. This is WCAG 1.4.1.
- Charts: at most 6 categorical hues, direct labels or a legend, distinct lightness steps, sequential ramps for ordered data. Astryx separates data colours into their own token import
  ([[astryx-charts-config-model]], [[astryx-kpi-stat-row]]).
- Semantic names, not hue names: `--danger`, not `--red`. Keep one meaning per colour; if orange means warning, it does not also mean a promotion.
- Hover and press are overlays of the text colour at 4-8% alpha (combine with the surface below), not new opaque colours. Never make hover tint the only state cue (touch and keyboard users).
- Focus ring: 2 px, offset 2 px, accent or text colour, at least 3:1 against both adjacent colours, opaque and outside blur or glass.

## Checklist before saying done

- [ ] Roles tokenised for light and dark; components use roles only
- [ ] Every text/surface pair measured on the surface it really meets (cards, glass, images, textured areas)
- [ ] Body 4.5:1, large text 3:1, control edges, focus rings and meaningful icons 3:1
- [ ] One accent role; status colours paired with icon or text
- [ ] Gradients interpolated in OKLCH or checked for muddy midpoints; scrim or panel under text
- [ ] Glass and shader backgrounds have solid fallbacks, forced-colors handling and a still frame for reduced motion
- [ ] Dark theme designed (not inverted); theme switch works without a flash
- [ ] Grayscale and colour-blind emulation checked; chart colours limited and labelled

## Common mistakes

- Pale grey secondary text (`#9CA3AF` class) and ghost buttons that fail contrast.
- Accent measured on the page background only, then used on tinted surfaces.
- Dark mode made by inverting, so shadows, borders and accents look wrong.
- Pure black with pure white text; neon accents that vibrate on dark.
- One purple-to-blue gradient everywhere, glass on every card, text over the busiest part of a hero image.
- Colour as the only difference between states, or red and green as the only status pair.
- Low-alpha border as the only visible edge of a form control.

## Related

Patterns: [[astryx-theme-presets]], [[astryx-theme-token-system]], [[style-glassmorphism]], [[style-aurora-gradient-mesh]], [[style-grain-and-texture]], [[style-dark-technical-developer-tools]], [[design-md-spec]].
Notes: [Astryx themes and tokens](../../../knowledge/components/astryx-themes-and-tokens.md), [DESIGN.md format](../../../knowledge/design-intelligence/design-md-format.md),
[Astryx accessibility contracts](../../../knowledge/components/astryx-accessibility-spec.md), [theme tokens in an existing app](../../../knowledge/implementation-recipes/astryx-theme-tokens-in-existing-app.md),
[liquid glass with CSS fallback](../../../knowledge/implementation-recipes/liquid-glass-ui-with-css-fallback.md).
References: [art-direction.md](art-direction.md), [design-principles.md](design-principles.md), [typography.md](typography.md), [layout-composition.md](layout-composition.md), [accessibility.md](accessibility.md).
