# Data visualization playbook

Build KPI tiles and charts that are readable without hover, themed with the project, accessible by data table, and honest about what the catalog covers.

In this file `design-sensei` means `${CLAUDE_SKILL_DIR}/scripts/design-sensei`.

## When to use / when not

- Use for dashboard sections, metric rows, report pages and landing-page proof blocks that show real data.
- Not for decorative "fake dashboards" built from `div` rectangles; the product-led SaaS note lists them as an AI tell. Show a real screenshot or a real chart.
- Catalog coverage is thin: two patterns, both Astryx (React 19, TypeScript). There is no catalog pattern for Vue, Svelte, plain HTML, pie or donut, maps, or stable-channel charts. In those cases use the project's existing chart library and apply the gates below; do not invent a source id.

## Pick the approach

| Situation | Pick | Reuse class | Notes |
| --- | --- | --- | --- |
| Bar, line, area, dot, band, candlestick, error bar, reference line in React | [[astryx-charts-config-model]] | copy_with_attribution | `@astryxdesign/charts` is canary-only, peer-pins core to 0.6.6, built on d3. Marks are single-use per `Chart`: keep one fresh `series` array per chart. |
| Row of metric tiles | [[astryx-kpi-stat-row]] | copy_with_attribution | Build from `Grid` and `Card` (works without the lab package). The lab `Stat` does not format numbers and is canary-only. |
| Tile container and reflow | [[astryx-card-and-grid-collections]], [[astryx-responsive-layout-primitives]] | copy_with_attribution | `Grid columns={{minWidth, max}}` gives fluid tracks. |
| Dashboard layout language | [[style-bento-layouts]], [[style-dark-technical-developer-tools]] | license_review_required / copy_with_attribution | Priority by tile size; dark-mode contrast traps in the second note. |
| Accessibility method for custom charts | [[astryx-accessibility-spec-contracts]] | copy_with_attribution | Method to copy: expectations as data, evidence layers, known failures recorded exactly. |
| Count-up numbers | [[vengeance-ui-kinetic-text-effects]] or [[react-bits-lightweight-text-effects]] | copy_with_attribution / license_review_required | Show the final value under reduced motion; see [typography effects](typography-effects.md). |
| Pie, donut, radar, Sankey, 3D | none in the catalog | n/a | Astryx lab has `RadialChart`, `SankeyChart`, `ThreeDChart` (canary); otherwise use the project's library. |

Dials: `visual_density` 7-10 suits tabular numerals, small multiples and 14 px axis text; 1-4 means one chart per screen and annotations. `motion_intensity` above 3 allows an entrance of marks (once); axes stay still. `design_variance` high changes framing and annotation, not scale honesty.

## Search commands

```bash
design-sensei search "chart" --category data-visualization
design-sensei search "dashboard kpi" --scope all --limit 6
design-sensei search "metric tiles" --category card-grid,data-visualization
design-sensei search "data table chart accessibility" --scope docs
```

## Implementation steps

1. Write the question each chart answers and choose the form from it (comparison: bars; trend: line; part-to-whole: stacked bar before pie). State the unit and period in the title and subtitle.
2. Inspect the stack. If the project is React with Astryx, or is willing to adopt it, follow the [dashboard recipe](../../../knowledge/implementation-recipes/astryx-charts-dashboard-section.md). Otherwise reuse the project's chart library and map the rules below onto it.
3. Compose the section: heading, KPI `Grid` of `Card`s (label, value in tabular numerals, delta with glyph and text), then one chart in a white or surface `Card`.
4. Format with the locale: currency, compact number, percent and date formatters take the locale (`useLocale()`); never hard-code separators.
5. Colour: take series colours from theme data tokens (or explicit values), add a second cue (shape, dash, direct label), and name every series in a legend or direct label. Set sentiment explicitly for inverted metrics such as error rate.
6. Provide a data equivalent: Astryx mirrors up to 100 cells (rows times series) into a hidden table; above that, add your own summary or table view next to the chart.
7. Tooltips are supplemental. Every value a user needs must also be readable without hover (labels, table, summary).
8. Motion: disable axis tick animation under reduced motion (`animated={!reduceMotion}` in the recipe); chart entrance is optional and short.
9. Server rendering: the chart renders an empty box of the requested height until its width is measured, so reserve height and expect no SVG in the server output.
10. Verify at 320 and 1440 px, light and dark, reduced motion on, and with only the keyboard.

## Accessibility and performance gates

- Text 4.5:1 and graphics (marks, axis lines needed to understand the chart) 3:1 against their surface in light and dark. The recipe computed the default purple categorical colour at 2.53:1 on the default dark surface; check your theme and set explicit colours where needed.
- Colour is never the only carrier of meaning (WCAG 1.4.1): delta glyphs and text, patterns, labels.
- The chart has an accessible name and description (`role="img"` with title and subtitle in Astryx) and a data table or text summary reachable by keyboard and screen reader.
- No pointer-only information. Hover states can enhance, not gate.
- Reduced motion: no sliding ticks or growing marks; static final state.
- SVG marks are CPU-drawn: thousands of marks need aggregation or canvas; WebGL marks in the Astryx package are partly flagged as needing work, so provide an SVG or table fallback if you use them.
- CLS at most 0.1: fixed chart height; LCP is rarely the chart, so lazy-load chart code below the fold.

## Common mistakes

- Truncated or non-zero baselines on bars without saying so; 3D or dual-axis charts that mislead.
- Ten-colour rainbow series with no direct labels; relying on the legend alone.
- Sharing one `series` array between two `Chart` elements (marks are annotated during layout and are single-use).
- Formatting numbers with string concatenation in one locale; unformatted values in `Stat`.
- Using canary packages in a project that needs a stable channel without pinning exact versions.
- Fake data presented as real in a marketing page without saying it is illustrative.

## Where to read more

- Notes: [Astryx](../../../knowledge/components/astryx.md), [Astryx accessibility spec](../../../knowledge/components/astryx-accessibility-spec.md), [Astryx themes and tokens](../../../knowledge/components/astryx-themes-and-tokens.md), [bento layouts](../../../knowledge/design-styles/bento-layouts.md), [dark technical interfaces](../../../knowledge/design-styles/dark-technical-developer-tools.md).
- Recipes: [KPI and chart section](../../../knowledge/implementation-recipes/astryx-charts-dashboard-section.md), [Astryx theme tokens in an existing app](../../../knowledge/implementation-recipes/astryx-theme-tokens-in-existing-app.md).
- Related playbooks: [cards and grids](cards-and-grids.md), [typography effects](typography-effects.md), [responsive layouts](responsive-layouts.md).
- References: [color systems](../references/color-systems.md), [accessibility](../references/accessibility.md), [responsive design](../references/responsive-design.md).
