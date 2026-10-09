# Microinteractions playbook

Choose and build button states, toggles, confirmations, hover effects and small feedback motion that are fast, keyboard-safe and reversible.

In this file `design-sensei` means `${CLAUDE_SKILL_DIR}/scripts/design-sensei`.

## When to use / when not

- Use for buttons, switches, hold-to-confirm, slide-to-commit, code inputs, link hovers and state feedback.
- Not for narrative motion (see [typography effects](typography-effects.md), [scroll storytelling](scroll-storytelling.md)) or decorative pointer effects ([cursor interactions](cursor-interactions.md)).
- Feedback must never wait on an animation. If the effect is slower than the user's next action, cut it.

## Pick the approach

| Situation | Pick | Reuse class | Notes |
| --- | --- | --- | --- |
| Production button, icon button, toggle, group inside a React app | [[astryx-button-family]] | copy_with_attribution | Required accessible label, sizes, pressed feedback. Known failure: a pending `clickAction` makes the button natively disabled and drops keyboard focus; use `isInterruptible` or `aria-disabled` with `aria-busy`. |
| Branded CTA with shine, glow or candy look | [[vengeance-ui-animated-cta-buttons]] | copy_with_attribution | Loops never stop and repaint on the main thread; none checks reduced motion; `pop-button` has no focus style; published candy button lacks the focus ring. Use one per view, behind the motion-safe wrapper. |
| Button border as a live shader | [[vengeance-ui-liquid-metal-button]] | copy_with_attribution | One WebGL canvas per button, `outline-none` on the component. Hero-only; plain bordered fallback. |
| Glass button | [[liquid-glass-css-fallback]] first, [[liquid-glass-button]] only for one showpiece | copy_with_attribution | CSS version needs focus ring, solid fallback, `prefers-reduced-transparency` and `forced-colors` branches. |
| Confirm a destructive action, async commit, toggle with spring, OTP input | [[react-bits-micro-spring-controls]] | license_review_required | HoldButton, SlideCommit, SquishSwitch, CodeSlots. DOM only; the Micro family sets ARIA and reduced-motion handling (still test with a screen reader). Install into your app only. |
| Link or label hover roll | [[fancy-letter-swap-text]] | copy_with_attribution | Recipe listens on focus as well as hover. |
| Gooey blob effects | [[fancy-svg-filters]] | copy_with_attribution | Docs say Safari support is limited or missing: plan a fallback. |
| Animate list or card reorder, filter, expand | [[gsap-flip-layout-transition]] | license_review_required | Under reduce, apply the change immediately. |
| Branch any GSAP effect on motion and viewport | [[gsap-match-media-reduced-motion]] | license_review_required | `gsap.matchMedia` reverts the motion branch if the preference changes. |
| Timing and easing tokens | [[motion-principles]] | original | Source of the duration table below. |

Dials: `motion_intensity` 1-3 keeps colour, outline and 80-150 ms transitions only; 4-7 adds press scale and small springs; 8+ allows playful overshoot on toggles and badges (3 to 8 percent), never in forms, tables or data UI. `design_variance` changes the shape language, not the timing.

## Search commands

```bash
design-sensei search "button hover" --category button --reduced-motion-safe
design-sensei search "toggle confirm hold" --category button,animation
design-sensei search "micro interaction" --scope docs
design-sensei search "spring" --category animation,button --max-gpu none
```

## Implementation steps

1. Inventory states per control: rest, hover, focus-visible, active, disabled, loading, success, error. Write them as CSS first.
2. Use native elements: `button` for actions, `a` for navigation, `input type="checkbox" role="switch"` or a real `button` with `aria-pressed` for toggles. Name icon-only controls.
3. Timing tokens (heuristics from [[motion-principles]]): hover or focus colour 80-150 ms; press scale 0.97 to 0.99 in 80-120 ms and out 120-200 ms; tooltip enter 120-200 ms, exit 80-140 ms; dropdown 180-280 ms. Exits about 70 percent of enter. Animate `transform` and `opacity` only.
4. Keep animation interruptible: reverse from the current state. CSS transitions do this by default; in GSAP use `overwrite: "auto"`.
5. Guard hover with `@media (hover: hover)`; pressed feedback must also work on touch. A press slid off the control and released elsewhere does not activate it.
6. Loading state: keep the button focusable, keep its width, set `aria-busy`, announce the result through a live region mounted before the update.
7. Key handlers for Enter and Escape should return early while an IME is composing (`event.isComposing`), as the [Astryx accessibility note](../../../knowledge/components/astryx-accessibility-spec.md) describes.
8. Wrap looping or WebGL effects with the [motion-safe wrapper](../../../knowledge/implementation-recipes/vengeance-ui-motion-safe-wrapper.md); for React Bits use `MotionGate` from the [install recipe](../../../knowledge/implementation-recipes/react-bits-choose-variant-and-install.md).

## Accessibility and performance gates

- Contrast 4.5:1 for labels and 3:1 for control boundaries in every state, light and dark, including hover and pressed over the final background.
- Visible `:focus-visible` ring on every control; never `outline: none` without a replacement (`pop-button`, `liquid-metal` and `faq-accordion` in Vengeance UI do this).
- Target size at least 24 by 24 CSS px, 44 recommended.
- Loops longer than 5 s need pause or removal (WCAG 2.2.2). Under reduced motion drop movement and loops; keep colour and focus feedback.
- One primary button per view; one decorative animated button per view.
- Disabled controls paint no hover state. Use `aria-disabled` when a reason must be readable and focus must stay reachable.
- INP at most 200 ms: no heavy work in pointer handlers; no state updates every frame (use refs or CSS variables).

## Common mistakes

- Infinite shine or glow on every call to action.
- Bounce, elastic or overshoot on form controls and data UI.
- Feedback slower than about 200 ms; entrances over 800 ms for a control.
- Hover as the only way to reveal an action; hover effects firing on touch.
- Natively disabling a button while pending, which drops keyboard focus.
- Mixing GSAP, Motion and CSS keyframes for the same button.
- Treating the licence lightly: `license_review_required` sources are use-in-app only, GSAP follows its own terms.

## Where to read more

- Notes: [motion principles](../../../knowledge/animations/motion-principles-for-ui.md), [Astryx accessibility spec](../../../knowledge/components/astryx-accessibility-spec.md), [Vengeance UI](../../../knowledge/components/vengeance-ui.md), [React Bits catalog](../../../knowledge/components/react-bits-catalog.md) (Micro table), [GSAP](../../../knowledge/animations/gsap.md), [liquid glass shaders](../../../knowledge/shaders/liquid-glass.md).
- Recipes: [motion-safe wrapper](../../../knowledge/implementation-recipes/vengeance-ui-motion-safe-wrapper.md), [glass with CSS fallback](../../../knowledge/implementation-recipes/liquid-glass-ui-with-css-fallback.md), [React Bits licence use](../../../knowledge/implementation-recipes/react-bits-license-safe-usage.md).
- Related playbooks: [navigation](navigation.md), [cards and grids](cards-and-grids.md), [cursor interactions](cursor-interactions.md), [liquid glass](liquid-glass.md).
- References: [motion design](../references/motion-design.md), [accessibility](../references/accessibility.md).
