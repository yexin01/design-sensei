---
title: "Build a KPI and chart section with @astryxdesign/charts"
kind: recipe
summary: "Compose a themed metrics section: a Grid of KPI cards plus a bar-and-line Chart with axes, grid, legend and tooltip, using the canary-only charts package, with locale-aware tick formats, accessibility notes and checks."
source_ids: [astryx]
pattern_ids: [astryx-charts-config-model, astryx-kpi-stat-row, astryx-card-and-grid-collections]
updated: "2026-10-09"
---

# Build a KPI and chart section with @astryxdesign/charts

## Goal

A dashboard section with a row of KPI cards and one themed chart that follows light and dark mode, reads its colours from the active
Astryx theme, and stays understandable without hover.

## When to use, and when not

`@astryxdesign/charts` is a config-model library on d3: marks are factory functions (`bar`, `line`, `area`, `dot`, `band`,
`candlestick`, `errorBar`, `referenceLine`, plus WebGL variants) passed in a `series` array, and the root owns one x and one y scale
that every mark, axis and grid line share (`astryx:packages/charts/README.md`). It is published only under the `@canary` dist-tag
and the package is `private: true` in the repository, so there is no stable release. Choose something else when you need a stable
channel or keyboard-driven data exploration (the chart has none). It has no pie, donut, radar, Sankey or 3D charts; the canary lab
package has `RadialChart` (`astryx:packages/lab/src/Radial/RadialChart.tsx`), `SankeyChart` and `ThreeDChart`.

## Prerequisites

| Package | Version in the checkout | Notes |
|---|---|---|
| `@astryxdesign/charts` | 0.1.9, canary | dependencies `d3-array`, `d3-scale`, `d3-shape`; peers `react >=19`, `@stylexjs/stylex >=0.10.0`, `@astryxdesign/core` exactly `0.6.6` |
| `@astryxdesign/core` | 0.6.6 | `Card`, `Grid`, `Text`, hooks, theme tokens |
| a theme such as `@astryxdesign/theme-neutral` | 0.6.6 | peer-pins core to `0.6.6`; see `knowledge/implementation-recipes/astryx-theme-tokens-in-existing-app.md` for the base setup |

The README tells you to install `npm install @astryxdesign/charts@canary @astryxdesign/core@canary` and to pin exact versions because
canary builds "can break between any two versions". A stable theme package pins core exactly, so mixing it with canary core may
raise peer warnings (not verified: which canary versions satisfy the pin).

## Steps

1. Import styles after the core ones, as the charts README shows (`astryx.css` then `charts.css`), and keep the theme CSS from the
   base recipe. `dist/charts.css` is a build artifact absent from the checkout, so confirm in DevTools that its rules land in the
   Astryx layers you expect.
2. Keep one fresh `series` array per chart. Mark objects are annotated during layout and are single-use, so never share them between
   two `Chart` elements (`astryx:packages/charts/src/Chart.doc.mjs`); `useMemo` keeps the array stable across renders.
3. Compose the section. Original code against the verified API:

   ```tsx
   'use client';
   import {useMemo} from 'react';
   import {Card} from '@astryxdesign/core/Card';
   import {Grid} from '@astryxdesign/core/Grid';
   import {Heading} from '@astryxdesign/core/Heading';
   import {Text} from '@astryxdesign/core/Text';
   import {VStack} from '@astryxdesign/core/VStack';
   import {useMediaQuery} from '@astryxdesign/core/hooks';
   import {useLocale} from '@astryxdesign/core/i18n';
   import {Chart, ChartAxis, ChartGrid, bar, currency, line} from '@astryxdesign/charts';

   type Row = {month: string; revenue: number; target: number};
   type Kpi = {label: string; value: string; note: string};

   export function RevenueSection({rows, kpis}: {rows: Row[]; kpis: Kpi[]}) {
     const locale = useLocale();
     const reduceMotion = useMediaQuery('(prefers-reduced-motion: reduce)');
     const series = useMemo(
       () => [bar('revenue', {label: 'Revenue'}), line('target', {label: 'Target', dots: true})],
       [],
     );
     return (
       <VStack gap={6}>
         <Heading level={2}>Revenue</Heading>
         <Grid columns={{minWidth: 220, max: 4}} gap={4}>
           {kpis.map(k => (
             <Card key={k.label} padding={4}>
               <VStack gap={1}>
                 <Text type="supporting" color="secondary">{k.label}</Text>
                 <Text type="display-3" hasTabularNumbers>{k.value}</Text>
                 <Text type="supporting">{k.note}</Text>
               </VStack>
             </Card>
           ))}
         </Grid>
         <Card padding={4}>
           <Chart
             data={rows}
             xKey="month"
             series={series}
             title="Monthly revenue against target"
             subtitle="Last six months, US dollars"
             height={300}
             grid={<ChartGrid horizontal />}
             axes={
               <>
                 <ChartAxis position="bottom" animated={!reduceMotion} />
                 <ChartAxis position="left" tickFormat={currency('$', locale)} animated={!reduceMotion} />
               </>
             }
             legend
             tooltip
           />
         </Card>
       </VStack>
     );
   }
   ```

   Props used: `Chart` takes `data`, `xKey`, `series`, `height` (default 300), `margin`, `yBaseline`, `yDomain`, `xDomain`, `grid`,
   `axes`, `legend`, `tooltip`, `interactions`, `title`, `subtitle`. `ChartAxis` takes `position`, `tickCount`, `maxTicks`,
   `tickFormat`, `truncate`, `animated`, `showAxisLine`, `showTicks`. `Grid columns={{minWidth, max}}` makes fluid tracks.
4. Format values with the locale. `currency(symbol, locale)` returns a tick formatter; `compactNumber`, `percent`, `shortDate`
   and `monthYear` take `(value, locale)`; read the locale with `useLocale()` (`astryx:packages/charts/src/formatters.ts`).
5. Colours: series without an explicit colour get slots from the theme's ten categorical data tokens in order (blue, orange, purple,
   green, pink, cyan, red, teal, brown, indigo), wrapping after ten. `useChartColors()` or `getChartColors(theme, mode)` return
   concrete values, plus sequential and diverging ramps, semantic positive and negative, and chrome colours
   (`astryx:packages/charts/src/getChartColors.ts`, tokens in `astryx:packages/core/src/theme/dataTokens.stylex.ts`).
6. Pair colour with another cue. Here bars versus a dotted line differ by shape, and the legend names both.

## Accessibility notes

- The SVG is `role="img"` with `title` as its name (or a derived localised name) and `subtitle` as its description. Rows times series
  of 100 or fewer are mirrored into a visually hidden table; above that no table is rendered, so add your own nearby summary or data
  view (`astryx:packages/charts/src/Chart.tsx`).
- The tooltip is pointer-driven and the docs call it supplemental. Never let it be the only way to read a value
  (`astryx:packages/charts/src/Chart.doc.mjs`).
- The core default categorical colours are identical in light and dark (`light-dark(x, x)`). Computing WCAG contrast of the first
  four slots (blue, orange, purple, green) against the default surfaces: blue, orange and green pass 3:1 on white and on the dark
  surface `#1F1F22`; purple (`#6B1EFD`), the third slot, is 2.53:1 on the dark surface and 2.90:1 on the dark body, below the 3:1 the
  chart docs ask of meaningful graphics. On
  the light body `#F1F4F7` orange, pink, teal and indigo fall to about 2.8:1, which is why the chart sits in a white Card here. These
  are my computations from the core defaults; check your theme, or set explicit colours.
- `ChartAxis` tick motion is 150ms and its source has no `prefers-reduced-motion` guard, hence `animated={!reduceMotion}` above. The
  axis group label is the English text "<position> axis".

## Performance and fallbacks

SVG marks are CPU-drawn; a `ResizeObserver` measures the container, and until the width is known `Chart` renders an empty box of the
requested height, so server output has no SVG and reserves space. WebGL marks (`dotGL`, `dotGLInteractive`, `heatmapGL`, `streamGL`)
exist, but a readiness audit in the package marks `dotGLInteractive` and `heatmapGL` as needing work
(`astryx:packages/charts/docs/CHARTV2_READINESS.md`, a historical snapshot). If you use them, provide an SVG or table fallback.

## Verification checklist

- Console clean; `series` not shared between charts; peer warnings reviewed.
- 320px and 1440px: KPI row reflows, chart fills the card, long tick labels thin out (use `truncate` or `maxTicks`).
- Light and dark: series, grid and axis text readable; contrast of each series colour checked on your surface.
- Reduced motion on: no sliding ticks; keyboard-only user can still obtain every value (hidden table, summary or table view).
- Screen reader or accessibility tree: the chart appears as a named image and the hidden table appears after it.

## Upstream references

`astryx:packages/charts/src/Chart.tsx`, `astryx:packages/charts/src/marks/bar.tsx`, `astryx:packages/charts/src/ChartAxis.tsx`,
`astryx:packages/charts/blocks/ChartShowcase.tsx`, `astryx:packages/lab/src/Stat/Stat.doc.mjs` (an experimental KPI tile that takes
a sparkline in a `media` slot and does not format numbers).

## Licence notes

MIT (`astryx:LICENSE`). The code above is original and calls public exports. d3 modules are separate dependencies with their own licences.
