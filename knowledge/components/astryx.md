---
title: "Astryx design system (React 19, StyleX, prebuilt CSS)"
kind: component-library
summary: "What Astryx 0.6.6 is, how its packages, StyleX styling and theme model fit together, how a consumer installs it, what its agent-oriented docs contain, and which pitfalls and licence limits apply. Read from the pinned checkout."
source_ids: [astryx]
pattern_ids: [astryx-design-system-react, astryx-theme-token-system, astryx-theme-presets, astryx-typography-scale, astryx-responsive-layout-primitives, astryx-app-shell-navigation, astryx-card-and-grid-collections, astryx-button-family, astryx-charts-config-model, astryx-kpi-stat-row, astryx-accessibility-spec-contracts, astryx-agent-ready-workflow]
updated: "2026-10-09"
---

# Astryx design system

Astryx is a React component library with a token-based theme system, published by Meta Platforms under the MIT licence
(`astryx:LICENSE`, "Copyright (c) 2026 Meta Platforms, Inc."; package author "Meta Open Source" and repository
`github.com/facebook/astryx` in `astryx:packages/core/package.json`). `astryx:README.md` marks it "Currently in Beta". `@astryxdesign/core` is version 0.6.6 and
needs `react` and `react-dom` 19 or later. The README says it grew inside Meta, ships "150+" components and powers "13,000+"
apps; those are the project's own statements. In the pinned checkout (commit `2531d8d`) `astryx:packages/core/src/` holds 105
component folders with an `index.ts` (plus `hooks`, `i18n`, `theme`, `utils`) and 234 `.doc.mjs` files (components, sub-components
and hooks); how the README arrives at "150+" is not stated.
`packages/cli`, Storybook, `packages/build` and `packages/vega` are named by the README but are not in the local checkout, so
CLI behaviour below is "as documented", not read from code.

## Architecture: packages and roles

| Package | Role | Status (manifest) | Source |
|---|---|---|---|
| `@astryxdesign/core` | components, theme runtime, hooks, i18n, utilities | 0.6.6, public, only dependency `intl-messageformat` | `astryx:packages/core/package.json` |
| `@astryxdesign/theme-neutral`, `-butter`, `-chocolate`, `-gothic`, `-matcha`, `-stone`, `-y2k` | seven theme packages, each depends on `lucide-react`, peer `@astryxdesign/core` pinned to 0.6.6 | 0.6.6, public | `astryx:packages/themes/neutral/package.json` |
| `@astryxdesign/theme-probe` | test fixture theme | private | `astryx:packages/themes/probe/package.json` |
| `@astryxdesign/charts` | config-model charts on d3 (`d3-array`, `d3-scale`, `d3-shape`) | 0.1.9, `private: true`, published only as `@canary` | `astryx:packages/charts/package.json` |
| `@astryxdesign/lab` | experimental components (Stat, Drawer, Tour, Sankey, Radial, 3D charts, CodeEditor...) | 0.1.9, canary-only per its README | `astryx:packages/lab/README.md` |
| `@astryxdesign/richtext` | Lexical-based editor and viewer; `lexical` and `@lexical/*` are optional peers | 0.1.9, canary-only | `astryx:packages/richtext/README.md` |
| `@astryxdesign/a11y-spec` | accessibility contracts and test harness | private 0.0.0, never published | `astryx:internal/a11y-spec/README.md` |

`astryx:packages/README.md` and `astryx:README.md` disagree with `astryx:packages/lab/README.md` on whether lab is published
(the first two say it is not published; the lab README and manifest say canary-only). Treat lab as unavailable on `latest`.

## Styling approach and theming model

- Components are authored with StyleX (`stylex.create`, `stylex.props`, tokens declared with `stylex.defineVars`), for example in
  `astryx:packages/core/src/Button/Button.tsx` and `astryx:packages/core/src/theme/tokens.stylex.ts`.
- StyleX is compiled when the package is built (`runtimeInjection: false` in `astryx:packages/core/babel.config.json`). Consumers
  load a prebuilt stylesheet, `@astryxdesign/core/astryx.css`, and need no Babel or PostCSS plugin. `@stylexjs/stylex ^0.19.0` is
  still a required peer dependency (the README install line includes it). A source build through `@astryxdesign/build` is a
  second, documented path (`astryx:packages/themes/neutral/README.md`).
- Three CSS layers in order: `reset` (`astryx:packages/core/src/reset.css`), `astryx-base` (component styles and token
  defaults), `astryx-theme` (theme overrides). Unlayered consumer CSS beats all three (header of `reset.css`).
- A theme is `defineTheme({...})`: token overrides, generated scales (`color`, `typography`, `radius`, `motion`), per-component
  overrides, icons, `onDark`/`onLight` surfaces and ordered `adaptations`. It compiles to CSS scoped with
  `@scope ([data-astryx-theme="name"]) to ([data-astryx-theme])` (`astryx:packages/core/src/theme/generateThemeRules.ts`).
  `Theme` either injects that CSS at runtime or relies on a prebuilt `theme.css`. Details are in
  `knowledge/components/astryx-themes-and-tokens.md`.
- Every component renders a stable class `astryx-<name>` plus `data-*` reflections of its visual props, which is the theming
  target surface (`astryx:packages/core/src/utils/themeProps.ts`). Consumer `className` is appended after StyleX classes and
  consumer `style` after StyleX inline styles (`astryx:packages/core/src/utils/mergeProps.ts`). `BaseProps` adds `xstyle`, which
  must be a `stylex.create()` value (`astryx:packages/core/src/BaseProps.ts`).
- The README says styles can be overridden with `className` (Tailwind, CSS modules, plain CSS) and that `swizzle` ejects a
  component's source; the blog describes a graduated path of as-is, theme tokens, class names, own CSS, then eject
  (`astryx:apps/docsite/src/content/blog/posts/how-astryx-works.md`). Swizzle is a CLI feature and was not verified locally.

## Install and use (as documented)

`astryx:README.md` shows (npm form; pnpm and yarn equivalents are listed there):

```bash
npm install @astryxdesign/core @astryxdesign/theme-neutral @stylexjs/stylex
npm install -D @astryxdesign/cli
```

`astryx:packages/core/README.md` (Quick Start) says the simplest setup is three stylesheet imports, in this order, plus a provider:

```css
@import '@astryxdesign/core/reset.css';
@import '@astryxdesign/core/astryx.css';
@import '@astryxdesign/theme-neutral/theme.css';
```

```tsx
'use client';
import {Theme} from '@astryxdesign/core/theme';
import {LinkProvider} from '@astryxdesign/core/Link';
import {neutralTheme} from '@astryxdesign/theme-neutral/built';
// <Theme theme={neutralTheme}><LinkProvider component={Link}>{children}</LinkProvider></Theme>
```

That README covers Next.js (with `next/link` passed to `LinkProvider`), Next.js with Tailwind (explicit `@layer` order plus
`@astryxdesign/core/tailwind-theme.css`), Vite, and a no-build CDN page using an import map and a `data-astryx-theme` attribute.
Components import per path (`@astryxdesign/core/Button`) or from the package root. Fonts are not bundled: a theme names its
font and the consumer loads it (`astryx:packages/themes/neutral/README.md`).

## Directory map

| Path | Contents |
|---|---|
| `astryx:packages/core/src/Button/` (typical) | one folder per component: `Button.tsx`, `Button.doc.mjs` (props, best practices, anatomy, theming targets), `Button.test.tsx`, `index.ts`, optional `Button.spec.md` (90 component contracts across core) and `__tests__/` (100 `*.a11y.*` files across core) |
| `astryx:packages/core/src/theme/` | tokens, `defineTheme`, `Theme`, `MediaTheme`, scale expanders, adaptations, syntax and data tokens |
| `astryx:packages/core/src/hooks/`, `astryx:packages/core/src/utils/`, `astryx:packages/core/src/i18n/`, `astryx:packages/core/src/Layer/` | focus, announce, hotkeys, media-query hooks; shared utilities; translator and provider; overlay runtime |
| `astryx:packages/core/locales/` | 30 locale catalogs |
| `astryx:packages/themes/` | seven theme packages (`src/<name>Theme.ts`, `fonts.css`) and the private probe |
| `astryx:packages/charts/`, `astryx:packages/lab/`, `astryx:packages/richtext/` | canary packages, each with `blocks/` demo templates and `astryx.integration.mjs` |
| `astryx:docs/` | `architecture/`, `design/`, `families/`, `specs/`, `contributing/`, `themes/`, knowledge templates and schemas |
| `astryx:internal/a11y-spec/` | accessibility contract package |
| `astryx:apps/docsite/src/` | Next.js docs site: `app/llms.txt`, `app/mcp`, blog posts in `content/blog/posts/` |

## Notable component families

Counts below are `category` values in `.doc.mjs` files. "Pattern" is the catalog id in this repository.

| Family | Purpose | Path | Pattern |
|---|---|---|---|
| Layout primitives (Stack, HStack, VStack, Grid, Center) | one- and two-dimensional arrangement with numeric spacing steps | `astryx:packages/core/src/Stack/`, `astryx:packages/core/src/Grid/` | `astryx-responsive-layout-primitives` |
| Layout regions (Layout, Section, Toolbar, AppShell) | five-slot page regions and the page shell | `astryx:packages/core/src/Layout/`, `astryx:packages/core/src/AppShell/` | `astryx-responsive-layout-primitives`, `astryx-app-shell-navigation` |
| Navigation (11) | SideNav, TopNav, MobileNav, Breadcrumbs, TabList, Pagination, Stepper | `astryx:packages/core/src/SideNav/` | `astryx-app-shell-navigation` |
| Action (10) | Button, IconButton, ToggleButton, ButtonGroup, menus, Toolbar | `astryx:packages/core/src/Button/` | `astryx-button-family` |
| Container (5) | Card, ClickableCard, SelectableCard, Carousel, Collapsible | `astryx:packages/core/src/Card/` | `astryx-card-and-grid-collections` |
| Content (15) | Text, Heading, Markdown, CodeBlock, Icon, Avatar, EmptyState | `astryx:packages/core/src/Text/` | `astryx-typography-scale` |
| Form controls (24) | TextInput, Selector family, date and time inputs, Slider, Switch, FileInput, PowerSearch | `astryx:packages/core/src/TextInput/` | none |
| Overlay (11) | Dialog, Popover, Toast, Tooltip, BottomSheet, CommandPalette | `astryx:packages/core/src/Dialog/` | `astryx-accessibility-spec-contracts` |
| Feedback (6) | Banner, Badge, Skeleton, Spinner, ProgressBar, StatusDot | `astryx:packages/core/src/Banner/` | none |
| Table and list (6) | Table with plugin hooks (sort, select, filter, paginate, resize), List, TreeList | `astryx:packages/core/src/Table/` | none |
| Chat (3 plus parts) | conversation layout, composer, message list, tool calls | `astryx:packages/core/src/Chat/` | none |
| Theme (Theme, MediaTheme, `defineTheme`) | tokens and providers | `astryx:packages/core/src/theme/` | `astryx-theme-token-system`, `astryx-theme-presets` |
| Charts (canary) | `Chart`, marks, axis, grid, legend, tooltip | `astryx:packages/charts/src/` | `astryx-charts-config-model` |
| Stat (lab, canary) | KPI tile with delta and sparkline slot | `astryx:packages/lab/src/Stat/` | `astryx-kpi-stat-row` |

## What "agent ready" means here

Described, not endorsed. All of it is in the checkout unless marked.

- `astryx:AGENTS.md` is the single instruction surface; `astryx:CLAUDE.md` only points to it. It tells agents to bootstrap with
  `astryx help`, `astryx docs`, `astryx docs principles --dense`, `astryx docs tokens --dense`, `astryx component --list` and to run
  `astryx component <Name> --dense` before editing a component and `astryx upgrade --from <old> --apply` after a core bump.
- Each component has a typed `.doc.mjs`: keywords, `usage.bestPractices` (do and do-not lists), `accessibility`, `anatomy`, props
  with exact literal types, examples and `theming.targets`. Many prop descriptions correct common mistakes ("the value is
  'horizontal', NOT 'row'", `Stack` gap is a number). Files also carry `docsZh` and `docsDense` (token-light) variants.
- `astryx:packages/core/docs.mjs` and a postinstall nudge (`astryx:packages/core/scripts/postinstall.mjs`) point agents to
  `npx @astryxdesign/cli init`, which writes a block into `AGENTS.md` or `CLAUDE.md` (markers and target files in
  `astryx:packages/core/scripts/agent-doc-state.mjs`). The scoped name matters: bare `npx astryx` resolves to an unrelated package.
- The docs site serves `/llms.txt` and an MCP endpoint with `search` and `get` tools
  (`astryx:apps/docsite/src/app/llms.txt/route.ts`, `astryx:apps/docsite/src/app/mcp/route.ts`).
- `astryx:docs/architecture/cli-surface.md` records the CLI contract (never prompts, one JSON envelope per call, stable error
  codes). Knowledge records carry `authority: draft | current | archived`; only `current` ones govern (`astryx:docs/README.md`).
- Blog posts describe a "vibe test" harness that scores generated code across configurations
  (`astryx:apps/docsite/src/content/blog/posts/vibe-tests.md`). Scores are self-reported and the post says results vary by night.

## Performance, accessibility and dependency observations

- One global stylesheet is the simple path; the blog says a source build keeps roughly a third of it in the authors' reference
  app (self-reported, not measured here).
- An unbuilt theme injects `<style>` elements at runtime and logs a one-time development hint to use the built theme
  (`astryx:packages/core/src/theme/Theme.tsx`). Built themes skip injection.
- `fonts.css` files `@import` Google Fonts (`astryx:packages/themes/butter/fonts.css`), a third-party request unless you self-host.
- Accessibility is tested as contracts per ARIA pattern with recorded known failures; see
  `knowledge/components/astryx-accessibility-spec.md`. Reduced-motion guards are present in components such as Button, Dialog,
  Skeleton and Toast.
- Charts mirror data of at most 100 cells into a hidden table, but tooltips are pointer-only.

## Pitfalls

1. Pre-1.0: the 0.6.6 changelog lists new deprecation windows, and bare value classes are slated for removal in 0.7.0
   (`astryx:packages/core/CHANGELOG.md`, `astryx:packages/core/src/utils/themeProps.ts`).
2. Canary packages (charts, lab, richtext) peer-pin `@astryxdesign/core` to exactly 0.6.6; their READMEs say install
   `@canary` of both and pin exact versions.
3. Stale text exists: theme READMEs show `XDSTheme` (the export is `Theme`), and a blog example passes `gap="md"` where the
   API takes numeric steps (`astryx:packages/core/src/Stack/Stack.doc.mjs`). Prefer `.doc.mjs` and source over READMEs and blog.
4. `Theme` writes `data-theme` and `data-astryx-theme` on `<html>`; an app that already uses `data-theme` collides.
5. `reset.css` is a global reset; in an existing app review its effect on headings, lists, buttons and images first.
6. `Button` with a pending `clickAction` becomes natively disabled, which drops keyboard focus; this is a recorded known failure
   (`astryx:packages/core/src/Button/__tests__/Button.a11y.known-failures.ts`). `isInterruptible` keeps it clickable.
7. `TabList` is a `<nav>` with `aria-current` unless you pass `role="tablist"` and `panelId` per tab
   (`astryx:packages/core/src/TabList/TabList.tsx`).
8. Two different `Chart` APIs exist: `@astryxdesign/charts` (config model) and an older composable one in lab.
9. Do not use it when you need a non-React stack, a stable 1.x API, stable-channel charts or rich text, or marketing-page
   building blocks: core has application UI components and no hero or landing sections.

## Licence and reuse

MIT permits use, modification and redistribution if the copyright and permission notice stay with copies. Syntax palettes are
colour values derived from MIT editor themes (`astryx:packages/core/src/theme/syntax/THIRD_PARTY_LICENSES.md`). Fonts and
Lucide icons are separate works with their own terms (not checked here). `LICENSE` says nothing about the Astryx name, banner or
mascot artwork (docs site media is not checked out); do not reuse brand assets without checking.

## Related

Notes: `knowledge/components/astryx-themes-and-tokens.md`, `knowledge/components/astryx-accessibility-spec.md`. Recipes:
`knowledge/implementation-recipes/astryx-theme-tokens-in-existing-app.md`,
`knowledge/implementation-recipes/astryx-charts-dashboard-section.md`,
`knowledge/implementation-recipes/astryx-agent-conventions.md`.
