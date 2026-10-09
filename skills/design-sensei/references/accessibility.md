# Accessibility

Rules and a test routine for keeping animated, WebGL and glass-heavy interfaces usable by keyboard, screen-reader, low-vision and motion-sensitive visitors.

Load this before building any interactive component, motion, canvas or translucent surface, and again before saying the work is done. Targets WCAG 2.2 level AA unless the project states otherwise. Automated checks only cover a subset of WCAG (the Astryx accessibility package says so about itself: [Astryx accessibility spec](../../../knowledge/components/astryx-accessibility-spec.md)); a green tool run is not a conformance claim.

## Decisions to make

| Decision | Options | How the configuration changes it |
| --- | --- | --- |
| Reduced-motion posture | `respect`: build the motion version, define an alternative per effect. `static_first`: build the static page, add motion only inside `(prefers-reduced-motion: no-preference)` | Read `reduced_motion`. With `static_first`, `design-sensei eval` raises MOT-001 as an error instead of a warning |
| How much may move | `motion_intensity` 1-3 hover/focus only; 4-7 purposeful transitions; 8-10 cinematic | Above 3, define the reduced-motion alternative before building the effect ([motion principles](../../../knowledge/animations/motion-principles-for-ui.md)) |
| GPU effect or CSS | WebGL canvas, CSS gradient/filter, static image | `webgl_enabled: false` means CSS or image only. When enabled, every canvas still needs a static fallback and a reduced-motion path |
| Glass or opaque surface | blurred translucent panel vs solid | High `visual_density` or text-heavy panels: prefer solid or a strong scrim. Glass is for short labels and controls over a known backdrop |
| Text splitting | split headline lines/words vs plain text | Split only short headings. Never split body paragraphs |

## Semantics and structure

- Use the native element: `button` for actions, `a` for navigation, `input`/`select`/`textarea` for fields, `dialog` for modals. Add ARIA only where HTML has no equivalent.
- One `h1`; heading levels in order (eval A11Y-008 flags a second `h1` in an HTML file). Landmarks (`header`, `nav`, `main`, `footer`) with names when there are several of a kind. Provide a skip link when navigation precedes content.
- `lang` on `<html>` (A11Y-003). Every `img` has `alt`; decorative images use `alt=""` (A11Y-001, an error).
- Every control has a persistent accessible name that contains its visible label; a placeholder is not a label. Icon-only buttons need an `aria-label`.
- State uses the standard attribute (`aria-expanded` with `aria-controls`, `aria-pressed`, `aria-current`, `aria-invalid`), and the name does not change when state changes. Every id referenced by `aria-*` must resolve.
- Do not put click handlers on `div`/`span` (A11Y-004). If unavoidable, add role, `tabindex="0"` and Enter/Space handlers.
- Content must not exist only in a canvas, a shader, a hover tooltip or a pseudo-element.

## Keyboard and focus

- Everything the pointer does works from the keyboard: Enter and Space on buttons, arrows inside composites (tabs, menus, carousels) with a single tab stop, Escape closes the top-most layer only.
- Never remove focus outlines without a replacement: A11Y-002 fires on `outline: none` with no `:focus-visible`. Draw the ring from a token, make it at least 3:1 against adjacent colours, and keep it from being clipped by `overflow: hidden`.
- Sticky headers and cookie bars must not cover the focused element (WCAG 2.4.11, new in 2.2). Use `scroll-margin-top` / `scroll-padding-top` equal to the header height.
- Modals: native `dialog.showModal()`, focus into visible content, restore focus to the invoker on close, no trap that cannot be escaped. Smooth scrolling does not move focus: after an anchor jump, move focus to the target yourself.
- Hover is an enhancement. Guard hover-only styles with `@media (hover: hover)` and give keyboard and touch the same information. Do not make tooltips the only way to read a value.
- Custom cursors, magnetic buttons and cursor-follow text must be off for touch and under reduced motion, and must never hide the native cursor on controls. React Bits' target cursor hides the native cursor on the whole page by default ([React Bits](../../../knowledge/components/react-bits.md)).
- In Enter/Escape/arrow key handlers for text fields, return early while an IME composition is active (`event.isComposing`), otherwise Korean, Japanese and Chinese users submit or close by accident (details in the Astryx spec note, section "IME composition").

## Contrast, colour and text

| Requirement (WCAG 2.2 AA) | Value |
| --- | --- |
| Body text | 4.5:1 |
| Large text (about 24 CSS px, or 18.66 px bold) | 3:1 |
| UI component boundaries, icons that carry meaning, focus ring | 3:1 |
| Target size minimum | 24 x 24 CSS px (2.5.8); 44 x 44 is the recommended touch size |

- Check every state: rest, hover, pressed, focus, disabled-but-readable, in light and dark. Measure hover and pressed text on the final overlaid background.
- Never use colour alone for selection, error or status; add text, an icon or a shape.
- Text must survive 200% zoom and reflow at 320 CSS px width without horizontal scrolling or clipped content (1.4.4, 1.4.10). Use `rem`-based sizes (eval TYPO-002 notes many fixed `px` sizes). Do not set `user-scalable=no` or `maximum-scale=1` (A11Y-005, an error).
- Keep text inputs at 16px or larger where iOS focus-zoom matters.
- Text over images, gradients, video or shaders: measure against the worst region and the worst frame, add a scrim. See [color systems](color-systems.md).

## Motion and `prefers-reduced-motion`

`reduce` means remove what triggers discomfort (large movement, parallax, spinning, zoom, scroll-linked motion, autoplay), not all feedback. Hover and focus colour changes stay. Full alternative table: [motion principles](../../../knowledge/animations/motion-principles-for-ui.md); implementation: [[gsap-match-media-reduced-motion]], [[motion-principles]], [[webgl-effect-fallback-and-reduced-motion]].

- Default CSS shows the final content. Hidden initial states (opacity 0, translated) belong inside the motion branch, so reduced-motion and no-script visitors see everything.
- GSAP, R3F and most copy-in components do not read the preference themselves (checked in the [GSAP](../../../knowledge/animations/gsap.md) and [R3F animation](../../../knowledge/animations/r3f-animation-and-performance.md) notes). Gate them with `gsap.matchMedia()`, a media query or a hook, and listen for changes so toggling the setting live works without reload.
- Lenis honours the preference by default (`respectReducedMotion: true`); under `static_first` do not construct it at all while `reduce` matches ([Lenis](../../../knowledge/animations/lenis.md)). Smoothing is allowed, scroll hijacking is not.
- Auto-playing motion that lasts more than 5 seconds needs a pause control (WCAG 2.2.2). Nothing flashes more than 3 times per second (2.3.1); glitch, plasma and noise effects are the usual offenders.
- Use `opacity`, not GSAP `autoAlpha`, for stacked scroll beats: `autoAlpha` sets `visibility: hidden`, which removes inactive beats from the accessibility tree ([scroll storytelling](../../../knowledge/animations/scroll-storytelling.md)). Keep DOM order equal to reading order.
- Libraries differ widely: 95 of 215 React Bits components check reduced motion, 7 of 76 Vengeance UI components, one Fancy component. Treat an unchecked component as unsupported and wrap it ([Vengeance motion-safe wrapper](../../../knowledge/implementation-recipes/vengeance-ui-motion-safe-wrapper.md)).

## WebGL, canvas and shaders

- Decorative canvas: `aria-hidden="true"`, `pointer-events: none`, never focusable. Informative canvas: `role="img"` with a label and a text or table equivalent nearby; a logo stays an `img` with alt text under the canvas.
- Under `reduce`: render one still frame (not time zero if that frame is blank), do not start the loop. R3F idles with `frameloop="demand"`; shader backgrounds freeze their clock ([GLSL UI fundamentals](../../../knowledge/shaders/glsl-ui-fundamentals.md), [R3F canvas with fallback](../../../knowledge/implementation-recipes/r3f-canvas-in-a-page-with-fallback.md)).
- Missing WebGL or a lost context shows a designed static layer (CSS gradient or poster). `webgl_enabled: false` removes the effect entirely.
- Orbit-style controls on a canvas capture wheel and one-finger touch and can break page scrolling and keyboard use; keep them off decorative canvases.
- Camera-based or permission-asking components must not request permission on mount (ReflectiveCard and GridScan in React Bits do).

## Glass, transparency and increased contrast

- Measure text contrast against the worst backdrop region. The glassmorphism note records white text on a 20% white tint at 5.96:1 over deep blue and 1.19:1 over pale yellow; a 50% black scrim lifted the yellow case to 4.75:1 ([Glassmorphism](../../../knowledge/design-styles/glassmorphism.md)).
- Do not animate blur radius. Keep focus rings opaque and outside the blurred layer. Moving or video backdrops need a scrim.
- Provide fallbacks inside `@media (prefers-reduced-transparency: reduce), (prefers-contrast: more)` (limited browser support, so also feature-detect `backdrop-filter` with `@supports`) and `@media (forced-colors: active)` (system colours, a visible 1px border, `Canvas` background). Recipe: [Liquid glass with CSS fallback](../../../knowledge/implementation-recipes/liquid-glass-ui-with-css-fallback.md).
- liquid-glass-js elements are `div`s with click listeners: no role, tabindex or keyboard activation ([Liquid glass](../../../knowledge/shaders/liquid-glass.md)). Wrap a real `button` instead. See [[liquid-glass-css-fallback]].

## Forced colors and user preferences

Under `forced-colors: active` shadows, gradients and translucency are dropped. Selected, checked, current and focus states must survive with borders, outlines or system colours (`CanvasText`, `Highlight`). Emulate it and screenshot. Also honour `prefers-color-scheme` if the design has a dark theme, and `prefers-contrast: more` where you can.

## Text-splitting and kinetic type

Splitting text into spans can make a screen reader read letters, repeat the text or skip it.

- GSAP SplitText with `aria: "auto"` puts an `aria-label` on the container and `aria-hidden` on wrappers. That is dependable on headings and may be ignored on paragraphs: verify, and do not split paragraphs ([GSAP text reveal recipe](../../../knowledge/implementation-recipes/gsap-text-reveal-and-stagger.md), [[gsap-split-text-reveal]]).
- Hand-built splits: one visually hidden (`sr-only`) full-text node and `aria-hidden="true"` on every glyph layer ([Fancy letter swap](../../../knowledge/implementation-recipes/fancy-letter-swap-text.md), [[fancy-letter-swap-text]]). Fancy's 3D swap keeps the visual characters exposed as well, so text may be announced twice.
- Do not leave words in the DOM at `opacity: 0` as a hide technique for rotating text; Vengeance UI's morph text does this. React Bits splitters ship no label handling.
- Test with a screen reader or the browser accessibility tree, plus selection, find-in-page and translation.

## Testing routine

1. `design-sensei eval <project>`: A11Y-001..008, MOT-001. Fix errors; read warnings.
2. Keyboard pass with no mouse: Tab and Shift+Tab through the page; every control reachable, focus visible and not covered by sticky UI, order matches visual order, Enter/Space activate, Escape closes the top layer, no trap, focus never lands on an invisible element.
3. Accessibility tree: take the browser tool's accessibility snapshot (Playwright MCP `browser_snapshot`, Chrome DevTools MCP `take_snapshot`). Check names, roles, headings, landmarks, that decorative canvases are absent and that split text reads once.
4. Automated rules: if the project already has axe-core (for example `@axe-core/playwright`) run it; otherwise run a Lighthouse accessibility audit through Chrome DevTools MCP `lighthouse_audit`. Respect `allowed_dependencies`: do not add a package just to test.
5. Emulate media features: `prefers-reduced-motion: reduce` (toggle live, no reload; with Playwright use `page.emulateMedia({reducedMotion: 'reduce'})`), `forced-colors: active`, dark scheme, 200% zoom, 320 px width.
6. Contrast: compute ratios for text and UI boundaries from computed styles (a short `evaluate` script), including hover, focus and glass over its worst backdrop. Record the numbers.
7. If no browser tool exists, say so and list which of steps 2-6 were not done.

Evidence and scoring: [design QA](design-qa.md).

## Checklist before saying done

- [ ] Semantic elements, one `h1`, landmarks, `lang`, alt text, labelled controls
- [ ] Full keyboard path, visible unclipped focus ring, focus not obscured, modals restore focus
- [ ] Text 4.5:1, UI 3:1 in every state and theme; no colour-only meaning; targets at least 24 px (44 px on touch)
- [ ] Reduced-motion alternative for every animation, canvas and smooth-scroll; toggling live works
- [ ] Canvas has fallback, label or `aria-hidden`; nothing flashes; long motion has a pause control
- [ ] Glass/transparent surfaces pass contrast on the worst backdrop and have forced-colors and increased-contrast fallbacks
- [ ] Split text reads once; hover-only information has a non-hover path
- [ ] Zoom 200% and 320 px width without loss; viewport meta allows zoom

## Common mistakes

- Treating `prefers-reduced-motion` as "shorter durations" instead of removing movement.
- `outline: none` with no replacement; focus ring hidden behind a sticky header.
- Hidden initial states applied in CSS, so no-script and reduced-motion visitors see a blank page.
- Contrast checked on one screenshot of an animated or glass backdrop.
- Click handlers on `div`s; icon buttons without names; placeholder used as the only label.
- Custom cursor or WebGL effect with no touch, keyboard or reduced-motion path.
- Claiming accessibility from a green axe/Lighthouse run.

## Related

Patterns: [[astryx-accessibility-spec-contracts]], [[astryx-button-family]], [[webgl-effect-fallback-and-reduced-motion]], [[r3f-lazy-canvas-webgl-fallback]], [[smooth-scroll-lenis]], [[style-glassmorphism]].
Notes: [Astryx accessibility spec](../../../knowledge/components/astryx-accessibility-spec.md) (21-point component checklist), [Astryx themes and tokens](../../../knowledge/components/astryx-themes-and-tokens.md).
References: [motion design](motion-design.md), [color systems](color-systems.md), [responsive design](responsive-design.md), [performance](performance.md), [design QA](design-qa.md).
