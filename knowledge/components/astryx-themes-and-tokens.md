---
title: "Astryx themes and tokens: model, customisation, art-direction mapping"
kind: guide
summary: "How Astryx 0.6.6 implements spacing, colour, type, radius, shadow, motion, density and dark mode as semantic tokens, how defineTheme and Theme apply and extend them, and how Design Sensei style decisions map onto those levers."
source_ids: [astryx]
pattern_ids: [astryx-theme-token-system, astryx-theme-presets, astryx-typography-scale]
updated: "2026-10-09"
---

# Astryx themes and tokens

Everything here was read from `astryx:packages/core/src/theme/` and `astryx:docs/architecture/`. Records marked `authority: current`
govern; most `docs/design/*` records are `draft` and are cited only as stated intent. The CLI (`astryx theme build`) is not in the
local checkout; it is described from `astryx:packages/core/src/theme/Theme.tsx` and `astryx:docs/architecture/theme-compilation.md`.

## 1. The model

1. Tokens are CSS custom properties with semantic names, declared once in `astryx:packages/core/src/theme/tokens.stylex.ts` as a
   `*Defaults` object plus a matching `*Vars` group (`stylex.defineVars`). Components read the `*Vars` objects.
2. A theme is `defineTheme(input)` (`astryx:packages/core/src/theme/defineTheme.ts`). It normalises to one flat `DefinedTheme` that
   runtime and build both consume (`astryx:docs/architecture/theme-authoring-contract.md`, current).
3. One web compiler turns it into CSS: a `:scope { --token: value }` block plus component rules, wrapped in
   `@scope ([data-astryx-theme="name"]) to ([data-astryx-theme])` and placed in `@layer astryx-theme`
   (`astryx:packages/core/src/theme/generateThemeRules.ts`). The inner boundary means a nested theme replaces, not stacks.
4. `<Theme theme mode>` mounts it. Built themes (a `theme.css` import) are not recompiled; an unbuilt theme injects `<style>` once and
   warns in development (`astryx:packages/core/src/theme/Theme.tsx`, `astryx:docs/architecture/theme-application.md`, current).
5. Non-CSS code reads the same vocabulary through `tokenVar`, `tokenVars`, `resolveThemeToken(s)` and `useTheme().tokens`
   (`astryx:packages/core/src/theme/tokens.ts`), which follows `var()` references and evaluates supported colour functions.

Token names are semantic (INV3 in `astryx:docs/architecture/theme-tokens.md`): components ask for "surface" or "text-secondary",
never a palette step. A role that differs by mode stays one token holding `light-dark(a, b)` (INV4). Renaming a released token is a
compatibility decision because consumers may use the CSS name directly.

## 2. Token inventory (188 core tokens, plus domain tokens)

| Family | Names (abridged) and core default values |
|---|---|
| Colour, semantic (39) | `--color-accent` `#0064E0`/`#2694FE`; `-background-body`, `-surface`, `-card`, `-popover`, `-muted`, `-inverted`; `-text-primary/secondary/disabled/accent`; `-icon-*`; `-on-accent/-success/-error/-warning/-dark/-light`; `-success/-error/-warning` and `-muted` forms; `-border`, `-border-emphasized`; `-overlay`, `-overlay-hover`, `-overlay-pressed`; `-skeleton`, `-track`, `-shadow`, `-tint-hover` |
| Colour, hues (40) | ten hues (blue, cyan, gray, green, orange, pink, purple, red, teal, yellow) times `background`, `border`, `icon`, `text` |
| Spacing (15) | `--spacing-0` 0, `-0-5` 2px, `-1` 4px, `-1-5` 6px, `-2` 8px, `-3` 12px, `-4` 16px, then +4px steps to `-12` 48px |
| Element size (3) | `--size-element-sm/md/lg` 28, 32, 36px |
| Border, focus (5) | `--border-width` 1px; `--focus-outline-width` 2px, `-style` solid, `-color` accent, `-offset` 3px |
| Radius (7) | `--radius-none` 0, `-inner` 4px, `-element` 8px, `-container` 12px, `-page` 28px, `-chat` 28px, `-full` 9999px |
| Shadow (8) | `--shadow-low/med/high`; inset rings `-inset-hover/-selected/-success/-warning/-error` |
| Motion (10) | durations `fast` 175ms, `medium` 410ms, `slow` 975ms, each with `-min`/`-max`; `--ease-standard` `cubic-bezier(0.24, 1, 0.4, 1)` |
| Type (61) | 3 font families; 12 sizes `--font-size-4xs` (6px) to `-5xl` (42px), base 14px ratio 1.2; 4 weights 400-700; 42 semantic tokens (heading 1-6, body, large, label, code, supporting, display 1-3, each size/weight/leading) |
| Syntax (14), data (56) | `--color-syntax-*` and `--color-data-*` (10 categorical, neutral, nine 5-step ramps); separate imports so apps that do not use them skip them |

Notes: `--color-text-disabled` is calibrated below AA on purpose because WCAG exempts inactive controls
(comment in `astryx:packages/core/src/theme/syntax/tokens.ts`). Component props use `SpacingStep` numbers 0, 0.5, 1, 1.5, 2, 3, 4, 5,
6, 8, 10 (`astryx:packages/core/src/utils/types.ts`); spacing tokens 7, 9, 11 and 12 exist but are not valid step values.

## 3. Customising

`DefineThemeInput` fields: `name`, `extends`, `color`, `typography`, `radius`, `motion`, `tokens`, `localTokens`, `components`,
`icons`, `indicators`, `syntax`, `onDark`, `onLight`, `adaptations`. Token values are a string or a `[light, dark]` tuple. Precedence,
lowest to highest: base theme, generated scales, explicit tokens, generated then explicit component styles, media-surface overrides,
local tokens, icon registries. `extends` must receive a real `DefinedTheme` or it throws.

```ts
import {defineTheme} from '@astryxdesign/core/theme';
import {neutralTheme} from '@astryxdesign/theme-neutral/built';

export const brandTheme = defineTheme({
  name: 'brand',
  extends: neutralTheme,
  color: {accent: ['#9a3412', '#fdba74'], neutralStyle: 'warm', contrast: 'standard'},
  typography: {scale: {base: 16, ratio: 1.25}, heading: {family: 'Fraunces', fallbacks: 'Georgia, serif'}},
  radius: {base: 4, multiplier: 1.5},
  components: {button: {'variant:primary': {fontWeight: '600'}}},
});
```

- `color` is generated with the HCT model from the accent seed (single hex or per-mode tuple), with `neutralStyle` warm, cool or
  neutral and `contrast` standard or high. The file header says tone spacing keeps text at 4.5:1 or better and emphasised borders at
  3:1 or better, asserted in tests (`astryx:packages/core/src/theme/expandColorScale.ts`). `--color-on-accent` is baked from the seed,
  so overriding `--color-accent` directly leaves it out of sync.
- `typography.scale {base, ratio}` regenerates sizes and leading (4px-snapped). Suggested starts in the source: dense 12 / 1.125,
  default 14 / 1.2, airy 16 / 1.25 (`astryx:packages/core/src/theme/expandTypeScale.ts`). Font loading is the consumer's job.
- `radius {base, multiplier}` sets inner, element, container and page to base times 1, 2, 3, 7 times multiplier; multiplier 0 is
  sharp (`astryx:packages/core/src/theme/expandRadiusScale.ts`). `--radius-none` and `--radius-full` stay fixed unless set explicitly.
- `motion {fast, medium, slow, ratio, easing}` expands to nine durations (`astryx:packages/core/src/theme/expandMotionScale.ts`).
- `components` keys are lowercase targets (`button`, `badge`, `text`, hyphenated such as `top-nav-item`). Style keys are `base`, `prop:value` or `a:b+c:d`; pseudo keys
  such as `:hover` are emitted with a disabled guard. The guaranteed property catalog is paint, border and shape, typography and
  padding keys (`astryx:docs/architecture/component-theming-surface.md`); other properties are best effort. Private `--_*` variables
  are not theme API.
- `adaptations` are ordered rules over fixed widths `sm` 640, `md` 768, `lg` 1024, `xl` 1280, `2xl` 1536 (`from` inclusive, `below`
  exclusive) and `pointer`, `contrast`, `motion` conditions, compiled to media queries
  (`astryx:packages/core/src/theme/themeAdaptations.ts`). Example: raise `--size-element-md` for coarse pointers.
- `MediaTheme mode="dark|light|auto|off"` re-points tokens for a local inverted surface (toast, scrim, image overlay); use
  `Theme mode` for page-wide dark mode (`astryx:packages/core/src/theme/MediaTheme.doc.mjs`).
- Tailwind v4 bridge: `@astryxdesign/core/tailwind-theme.css` maps tokens to utilities (`bg-surface`, `text-primary`, `rounded-lg`,
  `p-4` equals `--spacing-4`) with `@theme reference inline` (`astryx:packages/core/src/tailwind-theme.css`).

## 4. Dark mode and density

- Dark mode: tokens use `light-dark()`, `reset.css` sets `color-scheme: light dark`, and `<Theme mode>` takes `system` (default),
  `light` or `dark`. The root provider writes `data-theme` on `<html>`; set it server-side to avoid a flash. Gothic is dark-only: its
  README says it always renders dark whatever the system preference (`astryx:packages/themes/gothic/README.md`).
- Density has no global switch. The levers are spacing tokens, `--size-element-*`, per-component `density` props (Markdown,
  CheckboxList, Chat) and `adaptations`. Y2K and Matcha rescale spacing to a 6px base; controls become 32/40/48px in Y2K (and Butter) and
  36/40/44px in Matcha (`astryx:packages/themes/y2k/src/y2kTheme.ts`, `astryx:packages/themes/matcha/src/matchaTheme.ts`). Component size flows through
  `SizeContext` as explicit prop, nearest provider, then component default (`astryx:docs/architecture/component-size-cascade.md`).
- Mobile type: the current record `astryx:docs/design/mobile-typography.md` raises the mobile base to 16px under
  `(width < 1024px) and (pointer: coarse)` and pins one role to keep its desktop size; text controls also floor at 16px on iOS Safari
  (`astryx:packages/core/src/inputFontFloor.test.ts`).

## 5. Shipped themes (seven packages)

| Theme | Type (body / heading / display) | Scale | Shape and tempo |
|---|---|---|---|
| neutral | Figtree / Figtree | 14 / 1.2 | radii 6, 10, 12, 28px; motion 125/300/700 |
| butter | Outfit / Outfit; Sarina display | 14 / 1.25 | radii 6, 8, 12, 24px; 125/300/700 |
| chocolate | Albert Sans / Fraunces | 14 / 1.2 | radii 6, 10, 12, 24px |
| stone | Figtree / Montserrat | 14 / 1.25 | core default radii; warm stone and slate palette |
| matcha | DM Sans / Playwrite US Trad | 16 / 1.25 | radii 6, 12, 18, 42px; base-6 spacing |
| gothic | Fustat / Fustat; Manufacturing Consent display | 16 / 1.25 | dark only; motion 150/350/800 |
| y2k | Poppins / Poppins; Crimson Text display | 16 / 1.25 | all radii 0; base-6 spacing; motion 100/250/600 |

Each package ships `fonts.css` that imports Google Fonts and `theme.css`; display faces are applied through
`components.text['type:display-1' ... '-3']` overrides (see `astryx:packages/themes/gothic/src/gothicTheme.ts`). Palettes are not
reproduced here; read each `src/<name>Theme.ts`.

## 6. Mapping Design Sensei art-direction decisions

This mapping is Design Sensei's, not Astryx's claim.

| Decision | Astryx lever |
|---|---|
| Palette temperature | `color.neutralStyle`, or explicit surface tuples as in `butter` and `chocolate` |
| Accent and contrast | `color.accent` (hex or tuple), `color.contrast: 'high'`, an `adaptations` rule with `contrast: 'more'` |
| Type personality | `typography` body, heading, code families; display face via `components.text`; scale `{base, ratio}` |
| Rhythm and density | scale ratio, `--spacing-*`, `--size-element-*`, `SizeContext` |
| Shape language | `radius {base, multiplier}`, or per-target `borderRadius` |
| Depth | `--shadow-*`, Card and Button `elevation` (`none`, `low`, `med`, `high`); Neutral adds a 1px inset rim in dark mode |
| Motion tempo | `motion {fast, medium, slow, ratio}`; reduced-motion guards live in components |
| Mode strategy | `Theme mode`, `MediaTheme`, single-value tokens for a one-mode brand |
| Iconography | `icons` registry (shipped themes use Lucide); `indicators` swap control marks |

Limits: no hero, marketing or editorial section components exist in core, so large-scale art direction means composing layout
primitives and your own CSS. `docs/design/` records on hierarchy, shape, elevation and motion are drafts. Palette quality is not
verified here beyond the contrast statements above.
