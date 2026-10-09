# Design QA

The evaluation protocol for finishing a Design Sensei task: a ten-category rubric, how to collect evidence for each, how to verify in a real browser, and the report to hand back.

Load this at step 5 of the workflow, and earlier when planning how you will prove the result. The aim is evidence, not praise.

## Ground rules

1. Report what you measured and saw, with its source (command output, screenshot name, number). Label judgement as judgement.
2. **Never claim objective visual superiority.** Do not write "best", "stunning", "award-winning", "better than the original" or "looks professional". Taste is not measurable. Write instead: "matches the brief's editorial direction: serif display at 72 px, one accent, 12-column grid (screenshot 1280)" or "the hero is more distinctive than the previous version in these three listed respects".
3. Four statuses per category: **pass**, **concern** (works, with a named weakness), **fail** (blocks done), **not verified** (could not check; say why). Never report `pass` for something you did not check.
4. No total score. A fail in accessibility, responsive behaviour or technical correctness blocks "done" until fixed or explicitly accepted by the user.
5. `design-sensei eval` is a heuristic linter. It sees source text only: no rendered output, contrast, layout quality or taste. A clean run is not a pass.

## Run order

1. Project checks: build, type-check, lint, tests (the project's own commands from `package.json`).
2. `${CLAUDE_SKILL_DIR}/scripts/design-sensei eval <project-dir>`; add `--verbose` for info findings, `--json` to parse, `--strict` to fail on warnings. Exit 1 means at least one error (or any warning with `--strict`).
3. Browser verification (below).
4. Score the ten categories, write the report.

## The rubric

Eval codes are the rule ids printed by `design-sensei eval`; "partial" means the linter covers a thin slice.

### 1. Art direction

- Check: the brief from step 2 (audience, style, type, colour, layout, surfaces, motion) is visible in the result; tokens exist and are used; one primary style and at most one supporting influence.
- Evidence: the written brief; token definitions (`:root` custom properties, Tailwind theme, DESIGN.md); screenshots at 1280 and 375.
- Pass: every brief decision can be pointed at in code and in a screenshot. Concern: one decision drifted or is applied inconsistently. Fail: no recognisable direction, or contradicts the brief.
- Automated: partial. ART-002 (no custom properties/tokens), TYPO-005 (only default UI fonts). Both are info level.

### 2. Visual differentiation

- Check against the generic tells in SKILL.md: default indigo-violet gradient, one typeface everywhere, centred hero over three identical cards, glass or glow on everything, stock-icon rows, effects that do not serve the message. See [[taste-skill-anti-generic-ui-checklist]] and [[taste-skill-redesign-audit-protocol]].
- Evidence: list each tell found or ruled out, with a screenshot reference; note the one major decision that was deliberately changed from the default.
- Pass: no unexplained tells (heuristic). Concern: tells present with a stated reason, or direction rests on one trick. Fail: reads as the default template.
- Automated: partial. ART-001 counts Tailwind indigo/violet hex values (info).
- State differentiation relative to the brief or the previous version, never in absolute terms.

### 3. Typography and hierarchy

- Check: a deliberate pairing (display + text, optional mono), a defined scale, readable line length (about 45-75 characters, heuristic), visible hierarchy in the first screen, `font-display` set, no invisible text while fonts load, no fake bold/italic.
- Evidence: computed `font-family`, sizes and line-heights of h1/h2/body/caption (browser evaluate); squint test on the screenshot (is the order of importance clear?).
- Pass: scale and pairing are consistent across sections. Concern: more than one off-scale size or three-plus families. Fail: hierarchy unreadable or body text below legible size.
- Automated: TYPO-001 (more than 3 families), TYPO-002 (many `px` sizes, info), TYPO-003 (`@font-face` without `font-display`), PERF-008 (Google Fonts URL without `display=swap`). See [typography](typography.md).

### 4. Layout consistency

- Check: one grid and spacing scale, aligned edges, consistent radii/borders/shadows, section rhythm, no overlap or clipping, consistent component states.
- Evidence: full-page screenshots; a count of distinct padding/gap values from computed styles; list of off-scale values.
- Pass: spacing comes from the scale and alignment holds. Concern: a few off-scale values or one misaligned section. Fail: arbitrary spacing, overlaps, clipped content. See [layout composition](layout-composition.md).
- Automated: none (RESP-002 only checks that a responsive technique exists).

### 5. Responsive behaviour

- Check: no horizontal scroll, reflow at 320 px, sensible in-between widths, touch targets, hover alternatives, dvh/svh, heavy effects gated. Details: [responsive design](responsive-design.md).
- Evidence: screenshots at 375, 768, 1280, 1920; `scrollWidth` vs `clientWidth` per width.
- Pass: all four widths composed with no overflow. Concern: awkward at an in-between width. Fail: overflow, clipped or unreachable content, desktop-only interactions.
- Automated: RESP-001 (missing viewport meta, error), RESP-002, RESP-003 (`100vh`, info), A11Y-005 (zoom blocked, error).

### 6. Motion quality

- Check: tempo and easing match the brief; transform/opacity only; stagger and duration within bands; entrances do not replay needlessly; reduced-motion alternative exists and toggles live; one animation system; cleanup on unmount. Bands: [motion principles](../../../knowledge/animations/motion-principles-for-ui.md), [motion design](motion-design.md).
- Evidence: frame screenshots at intervals through an animation; DevTools Performance trace for long frames; emulated `prefers-reduced-motion` screenshots; count of live `ScrollTrigger`s after a route change (should return to 0).
- Pass: purposeful and complete static alternative. Concern: motion works but is decorative or crowded. Fail: no reduced-motion path, layout-property animation, content invisible until script runs, scroll hijacking.
- Automated: MOT-001 (motion code with no reduced-motion handling; error when `reduced_motion` is `static_first`), MOT-004 (animates layout property), MOT-005 (`transition: all`), MOT-006 (missing cleanup for Lenis, GSAP or `requestAnimationFrame`).

### 7. Accessibility

- Check everything in [accessibility](accessibility.md): semantics, keyboard, focus, contrast, target size, reduced motion, canvas alternatives, forced colors.
- Evidence: keyboard walk notes; accessibility-tree snapshot; measured contrast ratios; axe or Lighthouse accessibility output if available.
- Pass: no violations found, with the checks you ran listed. Concern: minor issues with a plan. Fail: unreachable controls, missing names, contrast below 4.5:1 / 3:1, trapped focus, no reduced-motion path.
- Automated: A11Y-001 (img without alt, error), A11Y-002 (outline removed, no `:focus-visible`), A11Y-003 (`lang`), A11Y-004 (click on non-interactive element), A11Y-005 (zoom blocked, error), A11Y-007 (autoplay video not muted), A11Y-008 (multiple `h1`). Contrast, focus order and names are not automated.

### 8. Performance

- Check: Core Web Vitals "good" thresholds (LCP at or under 2.5 s, INP at or under 200 ms, CLS at or under 0.1) and the project's `performance_budget` (`initial_js_kb`, `lcp_ms`, `cls`, `max_webgl_canvases`); number of live WebGL canvases; DPR cap; offscreen pause; image dimensions; fonts; dependency count. See [performance](performance.md).
- Evidence: Lighthouse or a performance trace; network request list with transfer sizes (JS total, largest assets); canvas count; throttled-CPU frame behaviour. Lab numbers are not field numbers: say "lab".
- Pass: within budget, measured. Concern: over budget on one metric or not measured on a mid-range device. Fail: LCP/CLS well outside thresholds, unbounded render loops, multiple full-viewport canvases.
- Automated: PERF-001 (`<img>` without width/height), PERF-003 (more than 3 `will-change`), PERF-004 (canvases over budget), PERF-005 (WebGL while `webgl_enabled` is false, error), PERF-006 (uncapped `devicePixelRatio`), PERF-007 (dependencies outside `allowed_dependencies`), PERF-008.

### 9. Source provenance

- Check: every borrowed pattern traces to a source id; reuse class respected ([source usage](source-usage.md)); notices kept; no copied media; new dependencies listed.
- Evidence: list of pattern ids and source ids used with their reuse class (`design-sensei sources show <id>`); `THIRD_PARTY_NOTICES.md` entries; `package.json` diff.
- Pass: each borrowed item has id, class and notice. Concern: attribution incomplete. Fail: code copied from `reimplement_only`, `reference_only` or `verify_first` sources; media reused; licence terms ignored.
- Automated: PROV-001 (code comment credits a source but no notice file at the project root), PROV-002 (comment mentions a source whose class forbids copying; confirm you only followed its terms).

### 10. Technical correctness

- Check: build, types, lint and tests pass; no console errors or hydration warnings; no failed network requests; no duplicate component or animation system; no leaked listeners or GPU resources; no placeholder content.
- Evidence: command exit codes and tail of output; console and network logs from the browser; route-change teardown check.
- Pass: all green and logs clean. Concern: warnings left with an explanation. Fail: broken build, console errors, 404 assets, leftover `debugger`, lorem ipsum.
- Automated: TECH-001 (`debugger`), TECH-002 (lorem ipsum), TECH-003 (several `href="#"`, info), plus dependency checks in PERF-007.

## Browser verification procedure

Use whatever browser tool the session has: Playwright MCP (`browser_navigate`, `browser_resize`, `browser_take_screenshot`, `browser_snapshot`, `browser_console_messages`, `browser_network_requests`, `browser_evaluate`, `browser_emulate_media` where present), Chrome DevTools MCP (`resize_page`, `emulate`, `take_screenshot`, `take_snapshot`, `list_console_messages`, `list_network_requests`, `lighthouse_audit`, `performance_start_trace`), or a headless-browser skill. Tool names vary; use equivalents. Start the app with the project's own dev command and keep screenshots outside the repository (scratch directory).

1. Load the page. Wait for fonts and the first animation to settle. Read the console and network: every error, every non-2xx request.
2. For each width 375, 768, 1280, 1920: resize, screenshot the viewport and the full page, check horizontal overflow with `scrollWidth > clientWidth`, scroll through each section (scroll-triggered content must appear).
3. Emulate `prefers-reduced-motion: reduce`, reload and repeat 375 and 1280; toggle it live once without reloading. Also emulate `forced-colors: active` and the dark scheme if the design has one.
4. Keyboard: Tab through from the top with real key presses; screenshot or record the focused element at key points; open and close every modal/menu with keyboard only.
5. Fallbacks: disable WebGL (launch the browser with WebGL off, or inject a script that makes `getContext('webgl')` and `'webgl2'` return null) and reload; confirm the static layer shows with no thrown error. Disable JavaScript once: content should still be present.
6. Performance: run a Lighthouse audit or trace for the page at a mobile profile; record LCP, CLS, INP/TBT and JS transfer size; count `canvas` elements; throttle CPU and watch scroll.
7. Interaction states: hover, focus, active, disabled and error states of the main components; screenshot each at 1280.
8. Compare screenshots with the brief and fix, then re-run the affected steps. Record what changed.

### When no browser tool exists

State it in the first line of the report. Then: run steps 1-2 of "Run order"; read the markup and CSS for semantics, tokens, breakpoints and reduced-motion branches; compute contrast from token values; check that every WebGL or animation path has a fallback in code. Mark responsive behaviour, motion quality, performance and the visual half of art direction as **not verified**, list the exact checks the user should do (the four widths, reduced motion, keyboard, console), and never describe how it "looks". If a headless Chrome binary exists you may take still screenshots at set window sizes; note that this does not cover interaction or animation.

## Report template

```markdown
## Design QA: <project / page>

Config: design_variance N, motion_intensity N, visual_density N, reduced_motion respect|static_first, webgl_enabled bool
Tools used: <build/test commands>, design-sensei eval, <browser tool or "no browser tool: visual checks not performed">

| Category | Status | Evidence | Notes / follow-up |
| --- | --- | --- | --- |
| Art direction | pass | brief + tokens in src/styles/tokens.css; screenshots 1280/375 | ... |
| Visual differentiation | concern | tells checked: ...; one deliberate change: ... | ... |
| Typography and hierarchy | | | |
| Layout consistency | | | |
| Responsive behaviour | | screenshots 375/768/1280/1920; no overflow | |
| Motion quality | | | |
| Accessibility | | keyboard walk; axe: 0 violations; contrast table | |
| Performance | | lab LCP x s, CLS x, JS x kB (mobile profile) | |
| Source provenance | | patterns: <ids> / sources: <ids> (reuse class) | |
| Technical correctness | | build ok; console clean | |

eval: N errors, N warnings (codes: ...). Fixed: ... Remaining: ...
New dependencies: <name and reason> or none.
Not verified: <list with reason>.
Limitations and next steps: <list>.
```

## Checklist before reporting

- [ ] Project build, types, lint and tests run; results quoted
- [ ] `design-sensei eval` run and every error resolved or explained
- [ ] Each of the ten categories has a status backed by evidence or marked not verified
- [ ] Four widths inspected, or the gap is stated
- [ ] No superlatives; differences described against the brief or previous version
- [ ] Dependencies, sources and licence classes listed

## Common mistakes

- Reporting `pass` from a clean `eval` alone.
- Checking one width, or only the first screen.
- Reviewing a page before fonts and animations settled.
- Testing reduced motion by reading code instead of emulating it.
- Judging contrast by eye on glass or animated backgrounds.
- Fixing an eval warning by silencing it (for example adding a comment) instead of fixing the cause.
- Describing the result as "premium", "modern" or "stunning" with no criteria.

## Related

References: [accessibility](accessibility.md), [responsive design](responsive-design.md), [performance](performance.md), [motion design](motion-design.md), [source usage](source-usage.md), [component selection](component-selection.md).
Patterns: [[taste-skill-anti-generic-ui-checklist]], [[taste-skill-redesign-audit-protocol]], [[webgl-effect-fallback-and-reduced-motion]], [[gsap-match-media-reduced-motion]].
Notes: [scroll storytelling test protocol](../../../knowledge/animations/scroll-storytelling.md), [Taste Skill](../../../knowledge/design-intelligence/taste-skill.md), [Astryx accessibility spec](../../../knowledge/components/astryx-accessibility-spec.md) (test-layer guidance).
