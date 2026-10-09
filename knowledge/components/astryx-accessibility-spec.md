---
title: "Astryx accessibility spec: contracts, implemented behaviours, implementer checklist"
kind: guide
summary: "What the internal a11y-spec package encodes (14 ARIA patterns, 29 completeness dimensions, evidence layers), which keyboard, focus, motion, IME and RTL rules Astryx components implement, the recorded gaps, and a checklist for any custom component."
source_ids: [astryx]
pattern_ids: [astryx-accessibility-spec-contracts, astryx-button-family]
updated: "2026-10-09"
---

# Astryx accessibility spec

Read from `astryx:internal/a11y-spec/`, the `*.a11y.*` bindings under `astryx:packages/core/src/`, `astryx:CONTRIBUTING.md` and
current records in `astryx:docs/`. The package is internal (`private`, version 0.0.0): you cannot install it; you can copy its
method. Nothing here is a conformance claim about Astryx; `astryx:internal/a11y-spec/README.md` itself says it "does not report what an
assistive technology says" and does not replace axe, the visual gate or manual review.

## 1. What the package contains

- A pattern is data (`definePattern` in `astryx:internal/a11y-spec/src/contract.ts`). Each expectation has a stable id
  (`<pattern>.<area>.<outcome>`), a plain-language user outcome, exact normative sources, an applicability condition, an evidence
  layer and an enforcement class. `definePattern` throws if any is missing.
- `required` is earned only when the primary source is a WCAG 2.2 A/AA criterion or a current Astryx record cited with a quoted clause
  and a commit-pinned GitHub URL; everything else is `advisory` and must say why. An APG-primary expectation must name the WCAG outcome
  it supports.
- Every pattern must answer 29 completeness dimensions (`astryx:internal/a11y-spec/src/checklist.ts`): either an expectation covers
  it or an exemption names an owner, a verification method and a real reason ("n/a" is rejected). The dimensions are 25 WCAG 2.2 rows
  (1.1.1, 1.3.1, 1.3.2, 1.3.5, 1.4.1, 1.4.3, 1.4.11, 2.1.1, 2.1.2, 2.4.2, 2.4.3, 2.4.4, 2.4.6, 2.4.7, 2.4.11, 2.5.2, 2.5.3, 2.5.8, 3.1.1,
  3.2.2, 3.2.4, 3.3.1, 3.3.2, 4.1.2, 4.1.3) plus four Astryx rows: `apg-interaction`, `forced-colors`, `reduced-motion` and
  `at-facing-strings` (assistive-technology-facing strings are translated like visible text).
- Evidence layers (`astryx:internal/a11y-spec/src/harness.ts`): `unit`, `dom`, `accessibility-tree`, `axe`, `real-browser`, `visual`,
  `lint`, `manual`, `real-at`. A harness runs only expectations whose layers it can observe; the jsdom lane reports the rest `unrun`,
  never `pass`. The Chromium lane reads the engine's own accessibility tree over CDP (`astryx:internal/a11y-spec/src/harness/chromium.ts`).
- Statuses: `pass`, `fail`, `known-failure`, `unexpected-pass`, `not-applicable`, `unrun`. There is no score; one required failure
  means the pattern is not conformant. A known failure matches one exact message, still runs and still fails; when it starts passing
  the stale record must be deleted.
- Real assistive technology is out of scope for the harness. `astryx:docs/specs/AST-009/spec.md` (current) requires named AT and browser
  pairings only for claims that depend on speech, announcement timing or virtual-cursor behaviour, and says a DOM emulator or snapshot
  is not real-AT evidence.

## 2. The 14 patterns

Counts are expectations (required / advisory) read from `astryx:internal/a11y-spec/src/patterns/`.

| Pattern | Adopted from | Bound components | Count |
|---|---|---|---|
| button | APG button | Button, IconButton, ClickableCard, SideNav collapse button, Chat send button | 12 / 0 |
| toggle-button | APG button (pressed) | ToggleButton, alone and grouped | 14 / 1 |
| switch | APG switch | Switch | 15 / 1 |
| checkbox | APG checkbox | CheckboxInput, CheckboxListItem, menu checkbox item, SelectableCard | 18 / 3 |
| radio-group | APG radio group | RadioList, SegmentedControl, radio roles in DropdownMenu | 21 / 2 |
| text-input | native controls, ARIA textbox | TextInput, TextArea | 21 / 1 |
| spinbutton | WCAG 2.2, APG spinbutton | NumberInput | 10 / 2 |
| listbox | WAI-ARIA 1.2 listbox | Selector and MultiSelector popups | 6 / 0 |
| tabs | APG tabs | `TabList role="tablist"` | 23 / 4 |
| disclosure | APG disclosure | standalone Collapsible | 8 / 0 |
| modal-dialog | APG modal dialog | Dialog | 12 / 0 |
| status-message | WCAG 2.2 4.1.3 | Toast, FieldStatus, Spinner, ProgressBar, chat status parts | 8 / 2 |
| breadcrumb | WCAG 2.2, APG context | Breadcrumbs | 4 / 0 |
| landmark | WCAG 2.2, APG context | LayoutHeader, LayoutContent, LayoutFooter, LayoutPanel | 3 / 1 |

Bindings live beside the component (`<Name>.a11y.states.ts`, `.known-failures.ts`, `.a11y.test.tsx`, `.a11y.chromium.spec.ts`), for
example `astryx:packages/core/src/Switch/__tests__/Switch.a11y.states.ts`. Run with `pnpm test:a11y-contract` after building
Storybook (`astryx:playwright.config.ts`).

## 3. Behaviours the components implement

| Area | Rule (where read) |
|---|---|
| Names | Button-family controls require a non-empty `label`; icon-only uses it as `aria-label` (`astryx:docs/families/buttons.md`, current). Text inputs need a persistent label, not a placeholder (`astryx:internal/a11y-spec/src/patterns/text-input.ts`). |
| Keyboard | Enter and Space both activate a button; Tab reaches and leaves; composites use roving tab stops through `useListFocus`, `useGridFocus`, `useTreeFocus` (`astryx:CONTRIBUTING.md`, `astryx:packages/core/src/TabList/TabList.tsx`). `TabList` is a `<nav>` with `aria-current` unless `role="tablist"` is set. |
| Pointer cancellation | A press slid off and released elsewhere leaves state unchanged (`*.survives-an-aborted-press` in the patterns, WCAG 2.5.2). |
| Disabled | A disabled member never invokes its action; with a tooltip `Button` uses `aria-disabled` so it stays focusable (`astryx:packages/core/src/Button/Button.doc.mjs`). Disabled controls must not paint hover or an interactive cursor (`astryx:CONTRIBUTING.md`, two guards plus lint rules). |
| Focus ring | One ring from `--focus-outline-*` tokens, shown only under `:focus-visible`; a theme can restyle it but not show it to pointer users (`astryx:packages/core/src/utils/focusOutline.stylex.ts`). Last-input modality decides visibility of programmatic focus (`astryx:docs/architecture/interaction-modality.md`, current). |
| Modal dialog | Native `<dialog>` shown with `showModal()`; focus enters visible content after the modal state exists; closing returns focus to the connected invoker; inline preview never steals focus (`astryx:packages/core/src/Dialog/Dialog.spec.md`). |
| Escape stack | One Escape closes only the topmost registered surface; content may claim Escape first (`astryx:docs/families/overlay-dismissal.md`, current). |
| Page shell | AppShell renders the skip link, banner and main landmarks; give every nav slot a `label`; the first heading in content is the page h1 (`astryx:packages/core/src/AppShell/AppShell.doc.mjs`). Layout regions assign no landmark role unless the caller supplies role and label (`astryx:docs/families/layout-regions.md`). |
| Navigation | `isSelected` sets `aria-current="page"`; blocked URL schemes do not navigate through the member components (`astryx:docs/families/navigation-destinations.md`). |
| Announcements | `useAnnounce` keeps polite and assertive regions mounted empty and clears messages after about two seconds (`astryx:packages/core/src/hooks/useAnnounce.doc.mjs`). A hand-wired `aria-live` region is lint-rejected (`astryx:CONTRIBUTING.md`). |
| Reduced motion | Button and Switch set durations to 0s, Dialog and layers set animations to none, Toast uses 0.01ms, under `prefers-reduced-motion: reduce`; Spinner and ProgressBar slow to 3s instead of freezing (`astryx:packages/core/src/Spinner/Spinner.tsx`). |
| Forced colors | Selected or checked state survives `forced-colors: active` through system colours in Calendar, CheckboxIndicator, RadioIndicator and BaseTypeahead (grep `forced-colors` in `astryx:packages/core/src/`). |
| Colour | `color.accent` generation keeps text at 4.5:1 or better and emphasised borders at 3:1 or better (`astryx:packages/core/src/theme/expandColorScale.ts`). Button docs say to measure hover and pressed text on the final overlaid background. |
| Charts | `Chart` exposes an SVG `role="img"` with a name and a hidden table when rows times series are 100 or fewer; tooltips are supplemental (`astryx:packages/charts/src/Chart.tsx`). |
| Direction and strings | Logical CSS properties (lint `no-physical-properties`), directional icons mirrored with `rtlStyles.mirror`, strings through `useTranslator`, 30 locales (`astryx:CONTRIBUTING.md`). |
| Touch text size | Text controls floor at 16px on iOS Safari to avoid focus zoom (`astryx:packages/core/src/inputFontFloor.test.ts`). |

### IME composition

When a person composes Korean, Japanese or Chinese text, the keydown that commits or cancels a candidate fires before
`compositionend`. A naive handler reads it as Enter or Escape and submits, selects or closes. Astryx's rule: `isImeKeyEvent(event)` is
true when `event.isComposing === true` or `event.keyCode === 229` (the legacy signal some IMEs and older Safari still need), and key
handlers return early before running command logic (`astryx:packages/core/src/utils/ime.ts`). Pass `e.nativeEvent` from React handlers.
At least 17 source files call it, including Selector, MultiSelector, TextInput, NumberInput, Typeahead, ContextMenu,
ChatComposerInput, the date and time fields, `useHotkeys` and the layer stack (`astryx:packages/core/src/Layer/layerStack.ts`).
The overlay-dismissal family record makes it a contract (FR6 in `astryx:docs/families/overlay-dismissal.md`): Escape that cancels composition is consumed without dismissing a surface. A
separate approach gates `onInput` through composition start and end handlers in lab `CodeEditor`
(`astryx:packages/lab/src/CodeEditor/CodeEditor.tsx`). `astryx:IME_GUARD_DESIGN.md` is a scratch design note ("Not shipped"); its
seven-site inventory is out of date and it rejects a wrapper hook because several sites mix the check with other conditions.

## 4. Recorded gaps at this commit

- Button and IconButton go natively disabled while a `clickAction` is pending, so a keyboard user loses focus and cannot reach the
  button (`astryx:packages/core/src/Button/__tests__/Button.a11y.known-failures.ts`).
- Dialog: when focus-requesting content mounts only while opening, focus can enter before the modal state, and closing may not return
  focus to the invoker (`astryx:packages/core/src/Dialog/__tests__/Dialog.a11y.known-failures.ts`). Whether native Dialog should wrap
  Tab is an open question in its spec.
- Handlerless controlled checkboxes do not declare `aria-readonly`; a handlerless menu checkbox looks available; TextInput and TextArea
  accept an error status with no message text; Chromium 149 omits read-only state for NumberInput
  (`astryx:packages/core/src/CheckboxInput/__tests__/Checkbox.a11y.known-failures.ts`,
  `astryx:packages/core/src/TextInput/__tests__/TextInput.a11y.known-failures.ts`,
  `astryx:packages/core/src/NumberInput/__tests__/NumberInput.a11y.known-failures.ts`).
- Switch, RadioList, Selector listbox, TabList and status messages have empty known-failure lists, although the package README still
  mentions two listbox failures.
- axe-core covers only a subset of WCAG; `astryx:CONTRIBUTING.md` says a green `pr-a11y` job does not mean a component is accessible.
- `ChartAxis` tick transitions have no reduced-motion guard and its group label is the English string "<position> axis"
  (`astryx:packages/charts/src/ChartAxis.tsx`). The draft design records (motion, system states, typography hierarchy) are not authoritative.

## 5. Checklist for any custom component

Derived from the dimensions and behaviours above; the rule's evidence is in sections 1 to 3.

Semantics
1. Use the native element for the role; add ARIA only where HTML has no equivalent.
2. Give every control a name that is non-empty, persistent (not a placeholder) and contains the visible label text.
3. Expose state with the standard attribute (`aria-pressed`, `aria-expanded` with `aria-controls`, `aria-current`, `aria-invalid`) and keep
   the name the same when state changes.
4. Make every referenced id resolve (`aria-labelledby`, `aria-describedby`, `aria-controls`).
5. Add landmarks deliberately, with names; keep heading levels in order; show errors as text tied to the field.

Keyboard and focus
6. Everything the pointer can do works from the keyboard (Enter and Space for buttons, arrows inside composites with one tab stop).
7. Tab enters and leaves; nothing traps focus; when a disabled reason must be readable use `aria-disabled` and keep focus reachable.
8. Draw the focus ring from tokens under `:focus-visible` only; ensure it is visible and not clipped.
9. Modal surfaces: native `showModal()`, focus into visible content, restore focus to the invoker, one Escape closes one layer.
10. Hover is an enhancement: guard it with `@media (hover: hover)` and keep a keyboard and touch path.

Pointer, touch and text
11. Activate on release and let a press be aborted by sliding off.
12. Disabled controls paint no hover or pressed state and show no interactive cursor; pending controls keep their size and set `aria-busy`.
13. Keep text inputs at 16px or larger where iOS focus zoom matters.
14. In every key handler for Enter, Escape, arrows, Home and End, return early when `isImeKeyEvent(e.nativeEvent)` is true.

Motion, colour, status
15. Guard transitions and animations with `prefers-reduced-motion`; keep busy or status meaning without motion.
16. Text 4.5:1, meaningful non-text boundaries 3:1, in rest, hover, pressed and focus states, light and dark.
17. Check `forced-colors: active`; never use colour alone for selection or status.
18. Announce visual-only changes through a live region mounted before the update; do not move focus for status.
19. Give graphics a name and an equivalent data view; never make hover the only way to read a value.

Language and verification
20. Route every visible and assistive string through your translator; use logical properties; mirror directional icons once.
21. Test at the right layer: jsdom for DOM, a real browser for focus and the accessibility tree, axe for static rules, a screen reader
    for announcement claims. Record any known failure exactly instead of skipping the test, and test reduced motion with
    `page.emulateMedia({reducedMotion: 'reduce'})` (the repository found the Playwright config option did not reach `matchMedia`).
